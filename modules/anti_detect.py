#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
防封机制模块
实现随机化操作、人类行为模拟，降低被检测风险
"""

import time
import random
import sys
import os

class AntiDetection:
    """防封机制类
    提供各种防检测功能，模拟人类操作行为
    """
    
    def __init__(self, config=None):
        """初始化防封机制
        
        Args:
            config (dict): 防封配置
        """
        self.config = config or {
            # 随机延迟配置
            'randomize_delays': True,
            'delay_min': 0.8,
            'delay_max': 1.2,
            'delay_distribution': 'gaussian',
            
            # 人类行为模拟配置
            'human_like_pauses': True,
            'pause_probability': 0.1,
            'max_pause_duration': 0.5,
            
            # 随机移动配置
            'random_movement': True,
            'max_move_distance': 20,
            'move_probability': 0.05,
            
            # 技能取消配置
            'skill_cancellation': True,
            'cancel_probability': 0.02,
            
            # 按键随机化配置
            'key_press_randomize': True,
            'key_press_min': 0.05,
            'key_press_max': 0.15
        }
        
        self.logger = None
        self.last_move_time = time.time()
    
    def set_logger(self, logger):
        """设置日志记录器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
    
    def get_random_delay(self, base_delay=1.0):
        """获取随机延迟时间
        
        Args:
            base_delay (float): 基础延迟时间（秒）
            
        Returns:
            float: 随机化后的延迟时间
        """
        if not self.config['randomize_delays']:
            return base_delay
        
        # 根据配置生成随机延迟
        delay = random_delay(
            self.config['delay_min'],
            self.config['delay_max'],
            self.config['delay_distribution']
        )
        
        return delay
    
    def apply_random_delay(self, base_delay=1.0):
        """应用随机延迟
        
        Args:
            base_delay (float): 基础延迟时间（秒）
            
        Returns:
            float: 实际延迟的时间
        """
        delay = self.get_random_delay(base_delay)
        time.sleep(delay)
        return delay
    
    def simulate_human_behavior(self):
        """模拟人类随机行为
        包括：随机停顿、随机移动、随机取消技能
        
        Returns:
            dict: 执行的行为记录
        """
        behaviors = {
            'paused': False,
            'moved': False,
            'cancelled_skill': False
        }
        
        # 随机停顿
        if self.config['human_like_pauses']:
            if human_like_pause(
                self.config['pause_probability'],
                self.config['max_pause_duration']
            ):
                behaviors['paused'] = True
                if self.logger:
                    self.logger.debug("执行随机停顿")
        
        # 随机移动
        if self.config['random_movement']:
            if random.random() < self.config['move_probability']:
                behaviors['moved'] = True
                if self.logger:
                    self.logger.debug("执行随机移动")
        
        # 随机取消技能
        if self.config['skill_cancellation']:
            if random.random() < self.config['cancel_probability']:
                behaviors['cancelled_skill'] = True
                if self.logger:
                    self.logger.debug("执行随机取消技能")
        
        return behaviors
    
    def get_random_key_press_duration(self):
        """获取随机的按键持续时间
        
        Returns:
            float: 按键持续时间（秒）
        """
        if not self.config['key_press_randomize']:
            return 0.1  # 默认值
        
        return random.uniform(
            self.config['key_press_min'],
            self.config['key_press_max']
        )
    
    def randomize_skill_order(self, skills):
        """随机化技能顺序（轻微调整，保持优先级）
        
        Args:
            skills (list): 技能列表
            
        Returns:
            list: 随机化后的技能列表
        """
        # 只对相同优先级的技能进行随机化
        if len(skills) <= 1:
            return skills
        
        # 简单实现：随机交换相邻技能（10%概率）
        randomized = skills.copy()
        for i in range(len(randomized) - 1):
            if random.random() < 0.1:
                randomized[i], randomized[i+1] = randomized[i+1], randomized[i]
        
        return randomized
    
    def should_perform_action(self, base_chance=1.0):
        """根据随机概率决定是否执行某个动作
        
        Args:
            base_chance (float): 基础概率（0-1之间）
            
        Returns:
            bool: 是否执行动作
        """
        # 添加随机波动
        chance = random.gauss(base_chance, 0.05)
        chance = max(0.0, min(1.0, chance))
        
        return random.random() < chance

# 工具函数（从utils.py导入或复制，避免循环依赖）
def random_delay(min_delay, max_delay, distribution="uniform"):
    """生成随机延迟"""
    if distribution == "uniform":
        return random.uniform(min_delay, max_delay)
    elif distribution == "gaussian":
        mean = (min_delay + max_delay) / 2
        std_dev = (max_delay - min_delay) / 6
        delay = random.gauss(mean, std_dev)
        return max(min_delay, min(max_delay, delay))
    else:
        raise ValueError(f"不支持的分布类型: {distribution}")

def human_like_pause(probability=0.1, max_duration=0.5):
    """模拟人类随机停顿"""
    if random.random() < probability:
        pause_duration = random.uniform(0, max_duration)
        time.sleep(pause_duration)
        return True
    return False
