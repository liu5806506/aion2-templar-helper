#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入控制器模块
提供统一的输入接口，支持键盘、鼠标、Arduino HID
"""

import time
import random
import serial
import keyboard as pykeyboard
import mouse as pymouse
from modules.hardware_input import HardwareInput

class InputController:
    """输入控制器，统一管理所有输入操作"""
    
    def __init__(self, config):
        """初始化输入控制器
        
        Args:
            config (dict): 配置字典
        """
        self.config = config
        self.input_type = config['input']['type']  # keyboard/mouse/arduino
        
        # 根据输入类型初始化不同的输入设备
        if self.input_type == 'arduino':
            self.hardware = HardwareInput()
            self._init_arduino()
        else:
            self.hardware = None
        
        self.logger = None
    
    def set_logger(self, logger):
        """设置日志记录器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        if self.hardware:
            self.hardware.logger = logger
    
    def _init_arduino(self):
        """初始化Arduino设备"""
        if self.logger:
            self.logger.info("初始化Arduino设备...")
        
        try:
            self.hardware.init_serial(
                port=self.config['input']['serial_port'],
                baud_rate=self.config['input']['baud_rate']
            )
            if self.logger:
                self.logger.info(f"Arduino设备初始化成功，端口: {self.config['input']['serial_port']}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Arduino设备初始化失败: {e}")
            raise
    
    def press_key(self, key, min_duration=0.05, max_duration=0.1, running=True):
        """按下并释放按键
        
        Args:
            key (str): 按键名称
            min_duration (float): 按键最小持续时间
            max_duration (float): 按键最大持续时间
            running (bool): 是否继续运行
            
        Returns:
            bool: 是否成功执行
        """
        # 防封机制：随机化按键间隔
        if self.config.get('anti_detection', {}).get('randomize_skill_delays', True):
            duration = random.uniform(min_duration, max_duration)
        else:
            duration = (min_duration + max_duration) / 2
        
        if self.logger:
            self.logger.debug(f"按下按键: {key}, 持续时间: {duration:.3f}秒")
        
        try:
            if self.input_type == 'arduino':
                # 使用Arduino HID
                return self.hardware.press_key(key, min_duration=min_duration, max_duration=max_duration, running=running)
            else:
                # 使用Python键盘库
                pykeyboard.press(key)
                time.sleep(duration)
                pykeyboard.release(key)
                return running
        except Exception as e:
            if self.logger:
                self.logger.error(f"按键操作失败: {e}")
            return False
    
    def click_mouse(self, button='left', min_duration=0.05, max_duration=0.1, running=True):
        """点击鼠标
        
        Args:
            button (str): 鼠标按键
            min_duration (float): 按键最小持续时间
            max_duration (float): 按键最大持续时间
            running (bool): 是否继续运行
            
        Returns:
            bool: 是否成功执行
        """
        # 防封机制：随机化点击间隔
        if self.config.get('anti_detection', {}).get('randomize_skill_delays', True):
            duration = random.uniform(min_duration, max_duration)
        else:
            duration = (min_duration + max_duration) / 2
        
        if self.logger:
            self.logger.debug(f"点击鼠标: {button}, 持续时间: {duration:.3f}秒")
        
        try:
            if self.input_type == 'arduino':
                # 使用Arduino HID
                return self.hardware.click_mouse(button=button, min_duration=min_duration, max_duration=max_duration, running=running)
            else:
                # 使用Python鼠标库
                pymouse.press(button=button)
                time.sleep(duration)
                pymouse.release(button=button)
                return running
        except Exception as e:
            if self.logger:
                self.logger.error(f"鼠标点击失败: {e}")
            return False
    
    def move_mouse(self, x, y, duration=0.5, running=True):
        """移动鼠标到指定位置
        
        Args:
            x (int): 目标X坐标
            y (int): 目标Y坐标
            duration (float): 移动持续时间
            running (bool): 是否继续运行
            
        Returns:
            bool: 是否成功执行
        """
        if self.logger:
            self.logger.debug(f"移动鼠标到: ({x}, {y}), 持续时间: {duration:.3f}秒")
        
        try:
            if self.input_type == 'arduino':
                # 使用Arduino HID
                return self.hardware.move_mouse(x, y, duration=duration, running=running)
            else:
                # 使用Python鼠标库
                current_x, current_y = pymouse.get_position()
                steps = int(duration * 60)  # 60fps
                for i in range(steps):
                    if not running:
                        return False
                    
                    t = i / steps
                    # 简单的线性插值
                    new_x = int(current_x + (x - current_x) * t)
                    new_y = int(current_y + (y - current_y) * t)
                    pymouse.move(new_x, new_y)
                    time.sleep(duration / steps)
                return running
        except Exception as e:
            if self.logger:
                self.logger.error(f"鼠标移动失败: {e}")
            return False
    
    def send_serial_command(self, command, wait_ack=True):
        """发送串口命令（仅Arduino模式有效）
        
        Args:
            command (str): 命令字符串
            wait_ack (bool): 是否等待ACK
            
        Returns:
            bool: 是否成功执行
        """
        if self.input_type != 'arduino' or not self.hardware:
            if self.logger:
                self.logger.error("当前输入类型不支持串口命令")
            return False
        
        return self.hardware.send_serial_command(command, wait_ack=wait_ack)
    
    def get_position(self):
        """获取当前鼠标位置
        
        Returns:
            tuple: (x, y) 坐标
        """
        if self.input_type == 'arduino':
            # Arduino模式下返回0,0（无法获取）
            return (0, 0)
        else:
            return pymouse.get_position()
    
    def close(self):
        """关闭输入控制器，释放资源"""
        if self.logger:
            self.logger.info("关闭输入控制器...")
        
        if self.hardware:
            self.hardware.close()
