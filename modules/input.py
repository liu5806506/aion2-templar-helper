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
import ctypes
import sys
from .hardware_input import HardwareInput


# 检查并请求管理员权限
if sys.platform.startswith("win"):
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    
    if not is_admin:
        # 以管理员权限重新运行程序
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

class InputController:
    """输入控制器，统一管理所有输入操作"""
    
    def __init__(self, config):
        """初始化输入控制器
        
        Args:
            config (dict): 配置字典
        """
        self.config = config
        self.input_type = config['input']['type']  # keyboard/mouse/arduino
        
        # 初始化logger为None
        self.logger = None
        
        # 根据输入类型初始化不同的输入设备
        if self.input_type == 'arduino':
            self.hardware = HardwareInput()
            self._init_arduino()
        else:
            self.hardware = None
        
        # 确保配置中包含必要的键
        if 'anti_detection' not in self.config:
            self.config['anti_detection'] = {'randomize_skill_delays': True}
    
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
            # 设置硬件输入模块的串口参数
            self.hardware.serial_port = self.config['input']['serial_port']
            self.hardware.baud_rate = self.config['input']['baud_rate']
            
            self.hardware.init_serial()
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
                # 尝试多种输入方法以提高兼容性
                success = False
                
                # 方法1: 使用keyboard库的更底层方法
                try:
                    pykeyboard.press_and_release(key)
                    success = True
                except Exception as e1:
                    if self.logger:
                        self.logger.warning(f"keyboard.press_and_release失败: {e1}")
                    
                    # 方法2: 使用keyboard.send方法
                    try:
                        pykeyboard.send(key)
                        success = True
                    except Exception as e2:
                        if self.logger:
                            self.logger.warning(f"keyboard.send失败: {e2}")
                        
                        # 方法3: 使用press/release方法（原方法）
                        try:
                            pykeyboard.press(key)
                            time.sleep(duration)
                            pykeyboard.release(key)
                            success = True
                        except Exception as e3:
                            if self.logger:
                                self.logger.warning(f"keyboard.press/release失败: {e3}")
                            
                            # 方法4: 尝试使用Windows API
                            if sys.platform.startswith("win"):
                                try:
                                    # 模拟更真实的人类按键行为
                                    import win32api, win32con
                                    from ctypes import windll, wintypes
                                    
                                    # 将按键转换为虚拟键码
                                    vk_code = self._get_vk_code(key)
                                    if vk_code:
                                        # 按下
                                        win32api.keybd_event(vk_code, 0, 0, 0)
                                        time.sleep(duration)
                                        # 释放
                                        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                                        success = True
                                except Exception as e4:
                                    if self.logger:
                                        self.logger.warning(f"Windows API方法失败: {e4}")
                
                return success and running
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
                # 尝试多种鼠标点击方法以提高兼容性
                success = False
                
                # 方法1: 使用mouse库的click方法
                try:
                    pymouse.click(button=button)
                    success = True
                except Exception as e1:
                    if self.logger:
                        self.logger.warning(f"mouse.click失败: {e1}")
                    
                    # 方法2: 使用mouse的press/release方法
                    try:
                        pymouse.press(button=button)
                        time.sleep(duration)
                        pymouse.release(button=button)
                        success = True
                    except Exception as e2:
                        if self.logger:
                            self.logger.warning(f"mouse.press/release失败: {e2}")
                        
                        # 方法3: 使用Windows API
                        if sys.platform.startswith("win"):
                            try:
                                import win32api, win32con
                                
                                # 根据按钮确定鼠标事件
                                if button == 'left':
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                                    time.sleep(duration)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                                elif button == 'right':
                                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
                                    time.sleep(duration)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
                                elif button == 'middle':
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0)
                                    time.sleep(duration)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0)
                                success = True
                            except Exception as e3:
                                if self.logger:
                                    self.logger.warning(f"Windows API鼠标点击失败: {e3}")
                
                return success and running
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
    
    def _get_vk_code(self, key):
        """将按键字符转换为Windows虚拟键码
        
        Args:
            key (str): 按键字符
            
        Returns:
            int: 虚拟键码，如果无法转换则返回None
        """
        # 定义常用按键的虚拟键码映射
        vk_map = {
            'backspace': 0x08,
            'tab': 0x09,
            'enter': 0x0D,
            'shift': 0x10,
            'ctrl': 0x11,
            'alt': 0x12,
            'pause': 0x13,
            'capslock': 0x14,
            'esc': 0x1B,
            'space': 0x20,
            'pageup': 0x21,
            'pagedown': 0x22,
            'end': 0x23,
            'home': 0x24,
            'left': 0x25,
            'up': 0x26,
            'right': 0x27,
            'down': 0x28,
            'printscreen': 0x2C,
            'insert': 0x2D,
            'delete': 0x2E,
            '0': 0x30,
            '1': 0x31,
            '2': 0x32,
            '3': 0x33,
            '4': 0x34,
            '5': 0x35,
            '6': 0x36,
            '7': 0x37,
            '8': 0x38,
            '9': 0x39,
            'a': 0x41,
            'b': 0x42,
            'c': 0x43,
            'd': 0x44,
            'e': 0x45,
            'f': 0x46,
            'g': 0x47,
            'h': 0x48,
            'i': 0x49,
            'j': 0x4A,
            'k': 0x4B,
            'l': 0x4C,
            'm': 0x4D,
            'n': 0x4E,
            'o': 0x4F,
            'p': 0x50,
            'q': 0x51,
            'r': 0x52,
            's': 0x53,
            't': 0x54,
            'u': 0x55,
            'v': 0x56,
            'w': 0x57,
            'x': 0x58,
            'y': 0x59,
            'z': 0x5A,
            'f1': 0x70,
            'f2': 0x71,
            'f3': 0x72,
            'f4': 0x73,
            'f5': 0x74,
            'f6': 0x75,
            'f7': 0x76,
            'f8': 0x77,
            'f9': 0x78,
            'f10': 0x79,
            'f11': 0x7A,
            'f12': 0x7B,
            'numlock': 0x90,
            'scrolllock': 0x91,
            'lshift': 0xA0,
            'rshift': 0xA1,
            'lctrl': 0xA2,
            'rctrl': 0xA3,
            'lalt': 0xA4,
            'ralt': 0xA5,
            'mouse1': 0x01,  # 左键
            'mouse2': 0x02,  # 右键
            'mouse3': 0x04,  # 中键
        }
        
        # 转换为小写并查找
        key_lower = key.lower()
        return vk_map.get(key_lower)
