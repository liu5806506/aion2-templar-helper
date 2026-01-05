#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化输入测试脚本
用于验证键盘和鼠标输入功能优化
"""

import sys
import time
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_input_methods():
    """测试多种输入方法"""
    print("测试多种输入方法...")
    
    # 方法1: 使用keyboard库
    try:
        import keyboard
        print("✓ keyboard库可用")
        
        # 测试不同方法
        try:
            keyboard.press_and_release('a')
            print("  ✓ press_and_release方法正常")
        except:
            print("  ✗ press_and_release方法异常")
        
        try:
            keyboard.send('b')
            print("  ✓ send方法正常")
        except:
            print("  ✗ send方法异常")
            
        try:
            keyboard.press('c')
            time.sleep(0.05)
            keyboard.release('c')
            print("  ✓ press/release方法正常")
        except:
            print("  ✗ press/release方法异常")
            
    except ImportError:
        print("✗ keyboard库不可用")
    
    # 方法2: 使用mouse库
    try:
        import mouse
        print("✓ mouse库可用")
        
        try:
            mouse.click('left')
            print("  ✓ mouse.click方法正常")
        except:
            print("  ✗ mouse.click方法异常")
            
        try:
            mouse.press('left')
            time.sleep(0.05)
            mouse.release('left')
            print("  ✓ mouse.press/release方法正常")
        except:
            print("  ✗ mouse.press/release方法异常")
            
    except ImportError:
        print("✗ mouse库不可用")
    
    # 方法3: 使用Windows API
    if sys.platform.startswith("win"):
        try:
            import win32api
            import win32con
            print("✓ Windows API可用")
            
            # 测试键盘输入
            try:
                # 模拟按下A键
                win32api.keybd_event(0x41, 0, 0, 0)  # A键
                time.sleep(0.05)
                win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放A键
                print("  ✓ Windows API键盘输入正常")
            except Exception as e:
                print(f"  ✗ Windows API键盘输入异常: {e}")
                
            # 测试鼠标输入
            try:
                # 模拟左键点击
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                print("  ✓ Windows API鼠标输入正常")
            except Exception as e:
                print(f"  ✗ Windows API鼠标输入异常: {e}")
                
        except ImportError:
            print("✗ win32api库不可用")
    
    print("输入方法测试完成")

def test_optimized_input_controller():
    """测试优化后的输入控制器"""
    print("\n测试优化后的输入控制器...")
    
    try:
        # 导入并测试输入控制器
        from modules.input import InputController
        
        # 创建基本配置
        config = {
            'input': {'type': 'keyboard'},
            'anti_detection': {'randomize_skill_delays': True}
        }
        
        input_ctrl = InputController(config)
        print("✓ 输入控制器创建成功")
        
        # 测试按键功能
        try:
            result = input_ctrl.press_key('a', 0.01, 0.02)
            print(f"✓ 按键测试完成，结果: {result}")
        except Exception as e:
            print(f"✗ 按键测试失败: {e}")
        
        # 测试鼠标功能
        try:
            result = input_ctrl.click_mouse('left', 0.01, 0.02)
            print(f"✓ 鼠标测试完成，结果: {result}")
        except Exception as e:
            print(f"✗ 鼠标测试失败: {e}")
            
    except Exception as e:
        print(f"✗ 输入控制器测试失败: {e}")

if __name__ == "__main__":
    print("简化输入测试")
    print("="*30)
    
    test_input_methods()
    test_optimized_input_controller()
    
    print("\n测试完成")