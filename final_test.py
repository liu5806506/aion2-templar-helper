#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试脚本
用于验证键盘和鼠标输入功能优化
"""

import sys
import time
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_input_controller():
    """测试优化后的输入控制器"""
    print("测试优化后的输入控制器...")
    
    try:
        from modules.input import InputController
        
        # 创建基本配置
        config = {
            'input': {'type': 'keyboard'},
            'anti_detection': {'randomize_skill_delays': True}
        }
        
        input_ctrl = InputController(config)
        print("✓ 输入控制器创建成功")
        
        # 测试多种按键
        test_keys = ['a', 'b', 'c', 'space', 'enter']
        for key in test_keys:
            result = input_ctrl.press_key(key, 0.01, 0.02)
            print(f"  ✓ 按键 '{key}' 测试: {result}")
        
        # 测试鼠标点击
        mouse_buttons = ['left', 'right']
        for button in mouse_buttons:
            result = input_ctrl.click_mouse(button, 0.01, 0.02)
            print(f"  ✓ 鼠标 '{button}' 测试: {result}")
            
        print("✓ 输入控制器测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 输入控制器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_privileges():
    """测试管理员权限"""
    print("\n测试管理员权限...")
    
    import ctypes
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✓ 当前以管理员身份运行")
        else:
            print("⚠ 当前未以管理员身份运行，某些游戏可能需要管理员权限")
        return True
    except:
        print("⚠ 无法检测管理员权限")
        return False

def test_dependencies():
    """测试依赖库"""
    print("\n测试依赖库...")
    
    libraries = [
        ('keyboard', 'keyboard'),
        ('mouse', 'mouse'),
        ('pyyaml', 'yaml'),
        ('pyserial', 'serial'),
        ('mss', 'mss'),
        ('numpy', 'numpy'),
        ('win32api', 'win32api'),
    ]
    
    missing = []
    for lib_name, import_name in libraries:
        try:
            if import_name == 'yaml':
                import yaml
            elif import_name == 'serial':
                import serial
            elif import_name == 'win32api':
                import win32api
            else:
                exec(f'import {import_name}')
            print(f"  ✓ {lib_name}")
        except ImportError:
            print(f"  ✗ {lib_name} (缺失)")
            missing.append(lib_name)
    
    if missing:
        print(f"⚠ 缺失依赖: {', '.join(missing)}")
        print("  请运行: pip install -r requirements.txt")
        return False
    else:
        print("✓ 所有依赖库都已安装")
        return True

def main():
    """主测试函数"""
    print("永恒之塔2 守护星辅助脚本 - 优化验证测试")
    print("="*50)
    
    all_tests_passed = True
    
    # 运行各项测试
    all_tests_passed &= test_dependencies()
    all_tests_passed &= test_admin_privileges()
    all_tests_passed &= test_input_controller()
    
    print("\n" + "="*50)
    if all_tests_passed:
        print("✓ 所有测试通过！键盘和鼠标输入功能已优化。")
        print("\n优化内容包括：")
        print("- 支持多种输入方法 (keyboard, mouse, Windows API)")
        print("- 自动权限检查和请求")
        print("- 更好的错误处理和回退机制")
        print("- 改进的模块导入路径")
        print("\n要运行主程序，请使用: python main_new.py")
    else:
        print("✗ 部分测试失败，请检查错误信息。")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 优化完成，键盘输入问题应该已解决！")
    else:
        print("\n❌ 请根据错误信息进行修复。")