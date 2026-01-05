#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Combat System
State machine based auto combat and navigation logic
"""

import time
import random
import numpy as np
import cv2
import threading
from modules.vision import Vision
from modules.window_manager import WindowManager

class StateMachine:
    """State machine manager"""
    
    # State definitions
    STATE_IDLE = 'idle'          # Idle: Find nearest monster
    STATE_APPROACH = 'approach'  # Approach: Move to attack range
    STATE_COMBAT = 'combat'      # Combat: Execute skill rotation, monitor health
    STATE_LOOT = 'loot'          # Loot: Scan floor items after combat
    STATE_REST = 'rest'          # Rest: Sit down or use potions when low HP/MP
    STATE_EMERGENCY_HEAL = 'emergency_heal'  # Emergency heal
    STATE_ROAMING = 'roaming'    # Roaming: Random navigation to find monsters
    STATE_UNSTUCK = 'unstuck'    # Unstuck
    
    def __init__(self, input_controller, vision, logger=None):
        self.input_controller = input_controller
        self.vision = vision
        self.logger = logger or self._default_logger
        self.state = self.STATE_IDLE  # Current state
        self.target = None  # Current target
        self.last_state_change = time.time()
        self.state_duration = 0
        self.hp_threshold = 0.3  # Health threshold
        self.mp_threshold = 0.2  # Mana threshold
        self.skills_cooldown = {}  # Skill cooldowns
        self.combat_rotation_index = 0  # Skill rotation index
        self.running = True
        self.target_monster_type = None  # Current target monster type
        self.target_distance = 0  # Distance to target
        self.last_target_check = 0  # Last target check time
        self.loot_items = []  # Items to loot
        self.is_stuck = False  # Whether stuck
        self.stuck_timer = 0  # Stuck timer
        
    def _default_logger(self, message):
        """Default logger function"""
        print(f"[StateMachine] {message}")
    
    def update(self):
        """Update state machine"""
        current_time = time.time()
        self.state_duration = current_time - self.last_state_change
        
        # Get current game state
        frame = self.vision.capture_screen()
        if frame is not None:
            self_hp = self.get_self_hp(frame)
            self_mp = self.get_self_mp(frame)
            skills_status = self.get_skills_status(frame)
            
            # Execute logic based on current state
            if self_hp < self.hp_threshold:
                self.change_state(self.STATE_EMERGENCY_HEAL)
            elif self_mp < self.mp_threshold:
                self.change_state(self.STATE_REST)
            else:
                self.execute_state_logic()
        
        # Add random delay
        time.sleep(random.uniform(0.1, 0.3))
    
    def change_state(self, new_state):
        """Change state"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.last_state_change = time.time()
            self.logger(f"State changed: {old_state} -> {new_state}")
    
    def execute_state_logic(self):
        """Execute logic for current state"""
        if self.state == self.STATE_IDLE:
            self.execute_idle_logic()
        elif self.state == self.STATE_APPROACH:
            self.execute_approach_logic()
        elif self.state == self.STATE_COMBAT:
            self.execute_combat_logic()
        elif self.state == self.STATE_LOOT:
            self.execute_loot_logic()
        elif self.state == self.STATE_REST:
            self.execute_rest_logic()
        elif self.state == self.STATE_ROAMING:
            self.execute_roaming_logic()
        elif self.state == self.STATE_EMERGENCY_HEAL:
            self.execute_emergency_heal_logic()
        elif self.state == self.STATE_UNSTUCK:
            self.execute_unstuck_logic()
    
    def execute_idle_logic(self):
        """Idle state logic"""
        # Find monsters
        frame = self.vision.capture_screen()
        if frame is not None:
            monsters = self.detect_monsters(frame)
            
            if monsters:
                # Select closest monster
                self.target = self.select_closest_monster(monsters)
                if self.target:
                    self.target_monster_type = self.target.get('type', 'unknown')
                    self.change_state(self.STATE_APPROACH)
            else:
                # Start roaming to find monsters
                self.change_state(self.STATE_ROAMING)
    
    def execute_approach_logic(self):
        """Approach state logic"""
        if not self.target:
            self.change_state(self.STATE_IDLE)
            return
        
        # Calculate distance
        distance = self.calculate_distance_to_target(self.target)
        self.target_distance = distance
        
        if distance < self.get_attack_range():
            self.change_state(self.STATE_COMBAT)
        else:
            # Move to target
            self.move_to_target_smoothly(self.target)
    
    def execute_combat_logic(self):
        """Combat state logic"""
        if not self.target or not self.is_target_alive():
            self.target = None
            self.target_monster_type = None
            self.change_state(self.STATE_IDLE)
            return
        
        # Check target status (stunned, knocked down for combo conditions)
        target_status = self.get_target_status()
        if target_status and target_status in ['stunned', 'knocked_down']:
            # Use high damage finisher
            self.use_high_damage_skill()
        else:
            # Execute combat rotation
            self.execute_combat_rotation()
    
    def execute_loot_logic(self):
        """Loot state logic"""
        # Loot dropped items
        items = self.detect_items()
        if items:
            for item in items:
                self.move_to_and_loot(item)
        else:
            self.change_state(self.STATE_IDLE)
    
    def execute_rest_logic(self):
        """Rest state logic"""
        # Sit down or use potions
        if self.should_rest():
            self.use_rest_skill()
        else:
            self.change_state(self.STATE_IDLE)
    
    def execute_roaming_logic(self):
        """Roaming state logic"""
        # Navigate to monster area using vision
        self.navigate_minimap()
        
        # Check if stuck
        if self.is_stuck():
            self.unstuck_maneuver()
    
    def execute_emergency_heal_logic(self):
        """Emergency heal state logic"""
        # Use heal skill or potion
        self.use_heal_skill()
        
        frame = self.vision.capture_screen()
        if frame is not None:
            self_hp = self.get_self_hp(frame)
            if self_hp > self.hp_threshold + 0.1:
                self.change_state(self.STATE_IDLE)
    
    def execute_unstuck_logic(self):
        """Unstuck state logic"""
        self.unstuck_maneuver()
        self.change_state(self.STATE_IDLE)
    
    def detect_monsters(self, frame):
        """Detect monsters - Improved vision algorithm (simulating YOLO)"""
        # This could integrate YOLO or other advanced detection algorithms
        # Using improved color detection but with monster type recognition
        
        # Detect monster HP bar color
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define monster HP bar color range (example)
        health_bar_lower = np.array([0, 100, 100])
        health_bar_upper = np.array([10, 255, 255])
        
        mask = cv2.inRange(hsv, health_bar_lower, health_bar_upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        monsters = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:  # Filter small areas
                x, y, w, h = cv2.boundingRect(contour)
                
                # Try to identify monster type (by size, color, etc.)
                monster_type = self.classify_monster(frame, x, y, w, h)
                
                monsters.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2,
                    'area': cv2.contourArea(contour),
                    'type': monster_type,
                    'is_alive': True
                })
        
        return monsters
    
    def classify_monster(self, frame, x, y, w, h):
        """Classify monster type (by size, color, etc.)"""
        # Extract monster region
        monster_region = frame[y:y+h, x:x+w]
        
        # Analyze region features to classify monster
        # Simplified implementation, can use more complex feature extraction in real app
        avg_color = np.mean(monster_region, axis=(0, 1))
        
        # Classify based on color and size
        if h > 100:  # Height > 100 pixels might be large monster
            return 'large_monster'
        elif w * h > 5000:  # Area > 5000 might be elite
            return 'elite_monster'
        else:
            return 'normal_monster'
    
    def select_closest_monster(self, monsters):
        """Select closest monster (prioritize specific types)"""
        if not monsters:
            return None
        
        # Prioritize elites, then normal
        priority_order = ['elite_monster', 'large_monster', 'normal_monster']
        
        for priority_type in priority_order:
            priority_monsters = [m for m in monsters if m['type'] == priority_type]
            if priority_monsters:
                return min(priority_monsters, key=lambda m: self.calculate_distance_to_point(m['center_x'], m['center_y']))
        
        # If no specific type, select closest
        return min(monsters, key=lambda m: self.calculate_distance_to_point(m['center_x'], m['center_y']))
    
    def calculate_distance_to_target(self, target):
        """Calculate distance to target"""
        # This needs to be implemented based on game reality
        # Can use screen coordinates estimation or minimap data
        return self.calculate_distance_to_point(target['center_x'], target['center_y'])
    
    def calculate_distance_to_point(self, x, y):
        """Calculate distance to specified point"""
        # Temporarily return an estimated value
        # Actually needs minimap positioning
        center_x, center_y = self.get_screen_center()
        return ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
    
    def get_screen_center(self):
        """Get screen center coordinates"""
        # Temporarily return fixed screen center
        # Actually should dynamically get screen size
        return 960, 540  # Assume 1920x1080 center
    
    def move_to_target_smoothly(self, target):
        """Smoothly move to target (using Bezier curve)"""
        center_x, center_y = self.get_screen_center()
        target_x = target['center_x']
        target_y = target['center_y']
        
        # Use Bezier curve to generate smooth mouse movement path
        self.bezier_mouse_move(center_x, center_y, target_x, target_y)
        
        # Simulate click to move
        self.input_controller.click_mouse()
    
    def bezier_mouse_move(self, start_x, start_y, end_x, end_y):
        """Use Bezier curve for smooth mouse movement"""
        # Generate points on Bezier curve
        steps = 20
        points = []
        
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve (can extend to cubic)
            x = (1 - t) * (1 - t) * start_x + 2 * (1 - t) * t * (start_x + (end_x - start_x) / 2) + t * t * end_x
            y = (1 - t) * (1 - t) * start_y + 2 * (1 - t) * t * (start_y + (end_y - start_y) / 2) + t * t * end_y
            points.append((int(x), int(y)))
        
        # Move point by point, add random delay
        for i, (x, y) in enumerate(points):
            self.input_controller.move_mouse(x, y, duration=0.01)
            # Add random delay to simulate human behavior
            if i < len(points) - 1:  # Don't add delay at last point
                time.sleep(random.uniform(0.01, 0.03))
    
    def execute_combat_rotation(self):
        """Execute combat skill rotation"""
        # Execute skills based on cooldown and priority
        combat_skills = self.get_combat_skills_priority()
        
        for skill in combat_skills:
            if self.is_skill_ready(skill):
                self.use_skill(skill)
                break  # Use only one skill per cycle
    
    def get_combat_skills_priority(self):
        """Get combat skill priority list"""
        # Define skill usage priority
        # Can dynamically adjust based on monster type, current state
        return ["skill_1", "skill_2", "skill_3", "attack"]
    
    def is_skill_ready(self, skill_name):
        """Check if skill is ready"""
        # Check skill cooldown
        if skill_name in self.skills_cooldown:
            return time.time() >= self.skills_cooldown[skill_name]
        return True
    
    def use_skill(self, skill_name):
        """Use skill"""
        # Send skill key via Arduino
        skill_keys = {
            "skill_1": "1",
            "skill_2": "2", 
            "skill_3": "3",
            "attack": "F"
        }
        
        if skill_name in skill_keys:
            key = skill_keys[skill_name]
            self.input_controller.press_key(key)
            
            # Record skill cooldown
            if skill_name in self.config_skills():
                cooldown = self.config_skills()[skill_name].get('cooldown', 1.0)
                self.skills_cooldown[skill_name] = time.time() + cooldown
    
    def config_skills(self):
        """Return skill config (mock config)"""
        return {
            "skill_1": {"cooldown": 1.5},
            "skill_2": {"cooldown": 2.0},
            "skill_3": {"cooldown": 3.0},
            "attack": {"cooldown": 0.5}
        }
    
    def is_target_alive(self):
        """Check if target is alive"""
        # Visually detect if target still has HP bar
        frame = self.vision.capture_screen()
        if frame is not None and self.target:
            # Detect HP bar in target region
            x, y, w, h = self.target['x'], self.target['y'], self.target['width'], self.target['height']
            target_region = frame[y:y+h, x:x+w]
            
            # Detect if there's HP bar color
            hsv = cv2.cvtColor(target_region, cv2.COLOR_BGR2HSV)
            health_bar_lower = np.array([0, 100, 100])
            health_bar_upper = np.array([10, 255, 255])
            
            mask = cv2.inRange(hsv, health_bar_lower, health_bar_upper)
            if cv2.countNonZero(mask) > 10:  # If enough HP bar pixels detected
                return True
        
        return False
    
    def get_target_status(self):
        """Get target status (stunned, knocked down, etc.)"""
        # Check if target is in special state (stunned, knocked down, etc.)
        # This needs status icon recognition
        frame = self.vision.capture_screen()
        if frame is not None and self.target:
            # Check status icons around target
            x, y, w, h = self.target['x'], self.target['y'], self.target['width'], self.target['height']
            status_region = frame[y:y+h//2, x:x+w]  # Check area above monster
            
            # Can implement status icon recognition here
            # Temporarily return random status for demo
            if random.random() < 0.1:  # 10% chance target is stunned
                return 'stunned'
            elif random.random() < 0.05:  # 5% chance target is knocked down
                return 'knocked_down'
        
        return None
    
    def use_high_damage_skill(self):
        """Use high damage skill (combo finisher)"""
        # Release high damage skill
        self.input_controller.press_key('4')  # Assume 4 is high damage skill
        
        # Record skill cooldown
        self.skills_cooldown['high_damage'] = time.time() + 5.0
    
    def get_self_hp(self, frame):
        """Get own HP (by UI recognition)"""
        # Need to implement HP bar recognition
        # Temporarily return random value for simulation
        return random.uniform(0.6, 0.9)  # Simulate 60-90% HP
    
    def get_self_mp(self, frame):
        """Get own MP"""
        # Temporarily return random value for simulation
        return random.uniform(0.5, 0.8)  # Simulate 50-80% MP
    
    def get_skills_status(self, frame):
        """Get skill status (by recognizing skill icons)"""
        # Temporarily return empty status
        return {}
    
    def detect_items(self):
        """Detect dropped items"""
        # Temporarily return random item list for simulation
        if random.random() < 0.3:  # 30% chance of item drop
            return [{'x': random.randint(100, 1800), 'y': random.randint(100, 900)}]
        return []
    
    def move_to_and_loot(self, item):
        """Move to item and loot"""
        # Move to item position
        center_x, center_y = self.get_screen_center()
        self.bezier_mouse_move(center_x, center_y, item['x'], item['y'])
        self.input_controller.click_mouse()
        
        # Use loot key
        self.input_controller.press_key('F')
    
    def should_rest(self):
        """Determine if need to rest"""
        frame = self.vision.capture_screen()
        if frame is not None:
            self_hp = self.get_self_hp(frame)
            self_mp = self.get_self_mp(frame)
            return self_hp < 0.9 or self_mp < 0.8
        return False
    
    def use_rest_skill(self):
        """Use rest skill (sit down)"""
        self.input_controller.press_key('R')  # Assume R is sit down
    
    def use_heal_skill(self):
        """Use heal skill"""
        self.input_controller.press_key('H')  # Assume H is heal
    
    def navigate_minimap(self):
        """Navigate using minimap"""
        # Temporarily implement simple random movement
        # Actually needs:
        # 1. Recognize player arrow in minimap
        # 2. Recognize target point
        # 3. Calculate direction
        directions = ['W', 'A', 'S', 'D']
        random_direction = random.choice(directions)
        self.input_controller.press_key(random_direction, min_duration=0.5, max_duration=1.0)
    
    def is_stuck(self):
        """Detect if stuck (using optical flow)"""
        # Temporarily return random value for simulation
        # Actually needs comparing consecutive frames' optical flow
        return random.random() < 0.05  # 5% chance of detecting stuck
    
    def unstuck_maneuver(self):
        """Unstuck maneuver"""
        # Execute unstuck action
        self.input_controller.press_key('SPACE')  # Jump
        time.sleep(0.5)
        
        # Random move direction
        directions = ['A', 'D']
        random_dir = random.choice(directions)
        self.input_controller.press_key(random_dir, min_duration=0.5, max_duration=1.0)
    
    def get_attack_range(self):
        """Get attack range"""
        # Return attack range (in pixels)
        return 100  # Temporarily set to 100 pixels

class LogicController:
    """Logic controller"""
    
    def __init__(self, input_controller, vision, logger=None):
        self.input_controller = input_controller
        
        # If no vision object is passed, initialize one
        if vision is None:
            from modules.vision import Vision
            self.vision = Vision()
        else:
            self.vision = vision
            
        self.logger = logger or self._default_logger
        self.running = True
        
        # Initialize state machine
        self.state_machine = StateMachine(input_controller, self.vision, logger)
    
    def _default_logger(self, message):
        """Default logger function"""
        print(f"[LogicController] {message}")
    
    def set_logger(self, logger):
        """Set logger for the controller"""
        self.logger = logger
    
    def start(self):
        """Start main loop"""
        self.logger("Starting smart combat system")
        
        while self.running:
            try:
                # Update state machine
                self.state_machine.update()
                
                # Add random delay to simulate human behavior
                time.sleep(random.uniform(0.1, 0.5))
                
            except KeyboardInterrupt:
                self.logger("Received stop signal")
                break
            except Exception as e:
                self.logger(f"Main loop error: {e}")
                time.sleep(1)  # Brief delay after error
    
    def stop(self):
        """Stop main loop"""
        self.running = False
        self.logger("Stopping smart combat system")
    
    def close(self):
        """Close resources"""
        self.stop()
        self.logger("Logic controller resources closed")