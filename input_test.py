#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入测试脚本
用于测试键盘和鼠标输入功能
"""

import sys
import time
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_keyboard_input():
    """测试键盘输入功能"""
    print("开始测试键盘输入功能...")
    
    # 首先测试keyboard库
    try:
        import keyboard
        print("✓ keyboard库导入成功")
        
        # 测试不同的键盘输入方法
        print("测试keyboard库的不同方法...")
        
        # 方法1: press_and_release
        try:
            keyboard.press_and_release('a')
            print("✓ keyboard.press_and_release() 工作正常")
        except Exception as e:
            print(f"✗ keyboard.press_and_release() 失败: {e}")
        
        # 方法2: send
        try:
            keyboard.send('b')
            print("✓ keyboard.send() 工作正常")
        except Exception as e:
            print(f"✗ keyboard.send() 失败: {e}")
        
        # 方法3: press/release
        try:
            keyboard.press('c')
            time.sleep(0.05)
            keyboard.release('c')
            print("✓ keyboard.press/release() 工作正常")
        except Exception as e:
            print(f"✗ keyboard.press/release() 失败: {e}")
            
    except ImportError as e:
        print(f"✗ keyboard库导入失败: {e}")
        return False
    
    # 测试mouse库
    try:
        import mouse
        print("✓ mouse库导入成功")
        
        # 测试鼠标点击
        try:
            mouse.click('left')
            print("✓ mouse.click() 工作正常")
        except Exception as e:
            print(f"✗ mouse.click() 失败: {e}")
            
        # 测试鼠标按下/释放
        try:
            mouse.press('left')
            time.sleep(0.05)
            mouse.release('left')
            print("✓ mouse.press/release() 工作正常")
        except Exception as e:
            print(f"✗ mouse.press/release() 失败: {e}")
            
    except ImportError as e:
        print(f"✗ mouse库导入失败: {e}")
        return False
    
    # 测试Windows API (如果在Windows上)
    if sys.platform.startswith("win"):
        try:
            import win32api
            import win32con
            print("✓ win32api库导入成功")
            
            # 测试Windows API键盘输入
            try:
                # 按下A键
                win32api.keybd_event(0x41, 0, 0, 0)  # A键的虚拟键码
                time.sleep(0.05)
                win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放A键
                print("✓ Windows API键盘输入工作正常")
            except Exception as e:
                print(f"✗ Windows API键盘输入失败: {e}")
                
            # 测试Windows API鼠标输入
            try:
                # 左键点击
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                print("✓ Windows API鼠标输入工作正常")
            except Exception as e:
                print(f"✗ Windows API鼠标输入失败: {e}")
                
        except ImportError as e:
            print(f"✗ win32api库导入失败: {e}")
    
    print("键盘输入测试完成")
    return True

def test_input_controller():
    """测试输入控制器"""
    print("\n开始测试输入控制器...")
    
    try:
        # 尝试加载配置
        try:
            from modules.config import load_config
            try:
                config = load_config("config.yaml")
                print("✓ 配置文件加载成功")
            except FileNotFoundError:
                print("⚠ 配置文件不存在，使用默认配置")
                config = {
                    'input': {'type': 'keyboard'},
                    'control': {'key_toggle': 'F9', 'key_exit': 'F12'},
                    'keys': {'select_target': 'tab', 'loot': 'z', 'auto_attack': 'r'},
                    'anti_detection': {'randomize_skill_delays': True}
                }
            
            # 初始化输入控制器
            from modules.input import InputController
            input_ctrl = InputController(config)
            print("✓ 输入控制器初始化成功")
        except ImportError as e:
            print(f"✗ 无法导入模块: {e}")
            # 如果模块导入失败，创建一个简化版本进行测试
            print("⚠ 创建简化配置进行测试")
            config = {
                'input': {'type': 'keyboard'},
                'control': {'key_toggle': 'F9', 'key_exit': 'F12'},
                'keys': {'select_target': 'tab', 'loot': 'z', 'auto_attack': 'r'},
                'anti_detection': {'randomize_skill_delays': True}
            }
            
            # 重新导入模块
            from modules.config import load_config
            from modules.input import InputController
            input_ctrl = InputController(config)
            print("✓ 输入控制器初始化成功")
        
        # 测试按键
        try:
            input_ctrl.press_key('a', 0.01, 0.02)
            print("✓ 输入控制器按键功能工作正常")
        except Exception as e:
            print(f"✗ 输入控制器按键功能失败: {e}")
            
        # 测试鼠标点击
        try:
            input_ctrl.click_mouse('left', 0.01, 0.02)
            print("✓ 输入控制器鼠标功能工作正常")
        except Exception as e:
            print(f"✗ 输入控制器鼠标功能失败: {e}")
            
    except Exception as e:
        print(f"✗ 输入控制器测试失败: {e}")
        return False
    
    print("输入控制器测试完成")
    return True

if __name__ == "__main__":
    print("输入功能测试工具")
    print("="*30)
    
    # 执行测试
    test_keyboard_input()
    test_input_controller()
    
    print("\n测试完成。请检查以上输出以确定问题所在。")
    input("按回车键退出...")