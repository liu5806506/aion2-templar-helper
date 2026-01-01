#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
战斗逻辑模块
负责技能释放策略、选怪逻辑、拾取逻辑
"""

import time
import random
from modules.vision import Vision
from modules.window_manager import WindowManager

class CombatLogic:
    """战斗逻辑类，处理所有战斗相关的决策"""
    
    # 状态定义
    STATE_IDLE = 'idle'      # 空闲状态，寻怪
    STATE_COMBAT = 'combat'  # 战斗状态
    STATE_LOOT = 'loot'      # 拾取状态
    STATE_REST = 'rest'      # 休息状态
    
    def __init__(self, input_ctrl, config):
        """初始化战斗逻辑
        
        Args:
            input_ctrl (InputController): 输入控制器
            config (dict): 配置字典
        """
        self.input_ctrl = input_ctrl
        self.config = config
        self.state = self.STATE_IDLE
        
        # 初始化视觉模块
        self.vision = Vision()
        self.window_manager = WindowManager()
        
        # 技能状态跟踪
        self.skill_cooldowns = {}
        self.is_first_attack = True
        
        # 防卡死机制
        self.stuck_counter = 0
        self.MAX_STUCK_COUNT = 10
        
        self.logger = None
    
    def set_logger(self, logger):
        """设置日志记录器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        self.vision.logger = logger
        self.window_manager.logger = logger
        self.input_ctrl.set_logger(logger)
    
    def smart_sleep(self, duration, jitter_range=0.05):
        """智能睡眠，带随机抖动
        
        Args:
            duration (float): 基础睡眠时间
            jitter_range (float): 抖动范围
            
        Returns:
            bool: 是否继续运行
        """
        # 防封机制：随机化延迟
        if self.config.get('anti_detection', {}).get('randomize_skill_delays', True):
            jitter = random.gauss(0, jitter_range / 2)
            jitter = max(-jitter_range, min(jitter_range, jitter))
            actual_duration = max(0.01, duration + jitter)
        else:
            actual_duration = duration
        
        # 防封机制：模拟人类偶尔停顿
        if self.config.get('anti_detection', {}).get('human_like_pauses', True):
            if random.random() < self.config['anti_detection']['pause_probability']:
                pause_duration = random.uniform(0, self.config['anti_detection']['max_pause_duration'])
                actual_duration += pause_duration
        
        end_time = time.time() + actual_duration
        while time.time() < end_time:
            time.sleep(0.01)
        
        return True
    
    def select_target(self):
        """智能选怪逻辑
        
        Returns:
            bool: 是否成功选中目标
        """
        for attempt in range(self.config['selection']['max_attempts']):
            if self.logger:
                self.logger.info(f"[选怪] 第 {attempt+1} 次尝试选怪")
            
            # 按tab键选怪
            self.input_ctrl.press_key(
                self.config['keys']['select_target'],
                running=True
            )
            
            # 等待选怪动作完成
            self.smart_sleep(self.config['selection']['delay'], jitter_range=0.02)
            
            # 检查是否选中了目标
            if self.vision.check_has_target():
                if self.logger:
                    self.logger.info("[选怪] 成功选中目标")
                return True
            
            if self.logger:
                self.logger.info("[选怪] 未选中目标，继续尝试")
            
            # 加入随机延迟
            self.smart_sleep(0.2, jitter_range=0.1)
        
        if self.logger:
            self.logger.info("[选怪] 多次尝试后仍未选中目标")
        return False
    
    def use_starter_skill(self):
        """使用起手技能
        
        Returns:
            bool: 是否成功执行
        """
        if self.logger:
            self.logger.info(f"[战斗] 使用起手技能: {self.config['starter']['key']}")
        
        self.input_ctrl.press_key(
            self.config['starter']['key'],
            running=True
        )
        
        self.smart_sleep(self.config['starter']['delay'])
        self.is_first_attack = False
        return True
    
    def use_defense_skills(self):
        """使用防御技能
        
        Returns:
            bool: 是否成功执行
        """
        if self.logger:
            self.logger.info("[防御] 执行防御技能逻辑")
        
        # 获取当前生命值
        health_percentage = self.vision.check_health()
        
        # 技能使用计数
        skills_used = 0
        max_skills = 2
        
        # 遍历防御技能优先级列表
        for skill_name, health_threshold in self.config['defense']['priorities']:
            if skills_used >= max_skills:
                break
            
            # 检查技能是否配置
            if skill_name not in self.config['defense']['skills']:
                continue
            
            # 检查生命值是否低于阈值
            if health_percentage <= health_threshold:
                skill_key = self.config['defense']['skills'][skill_name]
                
                # 检查技能冷却
                if skill_name in self.skill_cooldowns:
                    if time.time() < self.skill_cooldowns[skill_name]:
                        continue
                
                if self.logger:
                    self.logger.info(f"[防御] 生命值 {health_percentage}%，使用技能: {skill_name} ({skill_key})")
                
                # 使用技能
                self.input_ctrl.press_key(skill_key, running=True)
                
                # 记录技能冷却
                if skill_name in self.config['skills']:
                    cooldown = self.config['skills'][skill_name]['cooldown']
                    self.skill_cooldowns[skill_name] = time.time() + cooldown
                
                # 技能释放延迟
                self.smart_sleep(self.config['delays']['skill'])
                skills_used += 1
        
        return True
    
    def use_hate_skills(self):
        """使用仇恨技能
        
        Returns:
            bool: 是否成功执行
        """
        if self.logger:
            self.logger.info("[仇恨] 执行仇恨技能逻辑")
        
        # 技能使用计数
        skills_used = 0
        max_skills = 1
        
        # 遍历仇恨技能优先级
        for skill_name in self.config['hate']['priorities']:
            if skills_used >= max_skills:
                break
            
            # 检查技能是否配置
            if skill_name not in self.config['hate']['skills']:
                continue
            
            skill_key = self.config['hate']['skills'][skill_name]
            
            # 检查技能冷却
            if skill_name in self.skill_cooldowns:
                if time.time() < self.skill_cooldowns[skill_name]:
                    continue
            
            if self.logger:
                self.logger.info(f"[仇恨] 使用技能: {skill_name} ({skill_key})")
            
            # 使用技能
            self.input_ctrl.press_key(skill_key, running=True)
            
            # 记录技能冷却
            if skill_name in self.config['skills']:
                cooldown = self.config['skills'][skill_name]['cooldown']
                self.skill_cooldowns[skill_name] = time.time() + cooldown
            
            # 技能释放延迟
            self.smart_sleep(self.config['delays']['skill'])
            skills_used += 1
        
        return True
    
    def weave_skill(self, skill_key):
        """卡刀技能释放
        
        Args:
            skill_key (str): 技能按键
            
        Returns:
            bool: 是否成功执行
        """
        # 1. 发起普通攻击
        self.input_ctrl.press_key(
            self.config['keys']['auto_attack'],
            min_duration=self.config['weave']['config']['attack_keypress_delay'][0],
            max_duration=self.config['weave']['config']['attack_keypress_delay'][1],
            running=True
        )
        
        # 2. 等待平A前摇
        current_gear = self.config['weave']['current_gear']
        windup_time = self.config['weave']['attack_windup'][current_gear]
        self.smart_sleep(windup_time)
        
        # 3. 释放技能
        self.input_ctrl.press_key(
            skill_key,
            min_duration=self.config['weave']['config']['skill_keypress_delay'][0],
            max_duration=self.config['weave']['config']['skill_keypress_delay'][1],
            running=True
        )
        
        # 4. 技能后摇
        self.smart_sleep(self.config['weave']['config']['after_skill_delay'])
        
        return True
    
    def combat_cycle(self):
        """战斗循环
        
        Returns:
            bool: 是否继续运行
        """
        try:
            # 确保游戏窗口在前台
            self.window_manager.activate_game_window()
            
            # 使用防御技能
            self.use_defense_skills()
            
            # 使用起手技能
            if self.is_first_attack:
                self.use_starter_skill()
            
            # 执行卡刀
            violent_strike_key = self.config['skills']['violent_strike']['key']
            if self.config['weave']['config']['moving_weave_enabled']:
                # 移动卡刀（走砍）
                self.moving_weave(violent_strike_key)
            else:
                # 普通卡刀
                self.weave_skill(violent_strike_key)
            
            # 仇恨管理
            self.use_hate_skills()
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[战斗] 战斗循环异常: {e}")
            return False
    
    def moving_weave(self, skill_key):
        """移动卡刀（走砍）
        
        Args:
            skill_key (str): 技能按键
            
        Returns:
            bool: 是否成功执行
        """
        # 1. 按住前进键
        self.input_ctrl.send_serial_command("KEY_DOWN,W", wait_ack=False)
        self.smart_sleep(0.05)
        
        try:
            # 2. 执行卡刀
            self.weave_skill(skill_key)
        finally:
            # 3. 松开前进键
            self.input_ctrl.send_serial_command("KEY_UP,W", wait_ack=False)
        
        return True
    
    def run_cycle(self):
        """主运行循环
        
        Returns:
            bool: 是否继续运行
        """
        try:
            # 根据当前状态执行不同逻辑
            if self.state == self.STATE_IDLE:
                self.logger.info("[状态] 空闲 - 寻找目标")
                
                has_target = self.vision.check_has_target()
                if not has_target:
                    if self.select_target():
                        self.state = self.STATE_COMBAT
                        self.stuck_counter = 0
                        self.is_first_attack = True
                    else:
                        self.stuck_counter += 1
                        if self.stuck_counter >= self.MAX_STUCK_COUNT:
                            self.logger.warning("[防卡死] 检测到卡住状态，执行防卡死机制")
                            # 随机移动
                            for _ in range(2):
                                self.input_ctrl.press_key('s', min_duration=0.1, max_duration=0.2, running=True)
                            self.input_ctrl.press_key('space', min_duration=0.05, max_duration=0.1, running=True)
                            self.stuck_counter = 0
                else:
                    self.state = self.STATE_COMBAT
                    self.stuck_counter = 0
                    self.is_first_attack = True
            
            elif self.state == self.STATE_COMBAT:
                self.logger.info("[状态] 战斗 - 执行战斗循环")
                
                has_target = self.vision.check_has_target()
                if not has_target:
                    self.state = self.STATE_LOOT
                else:
                    # 执行战斗循环
                    self.combat_cycle()
            
            elif self.state == self.STATE_LOOT:
                self.logger.info("[状态] 拾取 - 自动拾取物品")
                
                # 使用拾取技能
                self.input_ctrl.press_key(self.config['keys']['loot'], running=True)
                self.smart_sleep(self.config['delays']['after_loot'])
                
                # 回到空闲状态
                self.state = self.STATE_IDLE
            
            elif self.state == self.STATE_REST:
                self.logger.info("[状态] 休息 - 恢复生命值")
                # 简化实现：回到空闲状态
                self.state = self.STATE_IDLE
            
            # 主循环延迟
            self.smart_sleep(self.config['delays']['loop'])
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[运行] 主循环异常: {e}")
            return False
    
    def close(self):
        """关闭资源
        """
        if self.logger:
            self.logger.info("[系统] 关闭战斗逻辑模块...")
        
        self.vision.close()
    
    def reset(self):
        """重置状态
        """
        self.state = self.STATE_IDLE
        self.skill_cooldowns.clear()
        self.is_first_attack = True
        self.stuck_counter = 0
