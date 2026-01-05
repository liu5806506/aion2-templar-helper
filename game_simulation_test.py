#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏模拟测试脚本
用于验证Arduino在游戏中的操作是否正常
"""

import time
import random
from modules.input import InputController
from modules.config import load_config

def test_game_simulation():
    """测试游戏中的模拟操作"""
    print("开始游戏模拟测试...")
    
    # 加载配置
    config = load_config("config.yaml")
    print(f"当前输入类型: {config['input']['type']}")
    
    # 创建输入控制器
    input_ctrl = InputController(config)
    
    print("\n开始测试游戏相关操作...")
    
    try:
        # 测试普通攻击键 (R键)
        print("\n1. 测试普通攻击键 (R键)")
        input_ctrl.press_key('r')
        print("✅ 成功发送普通攻击键")
        
        time.sleep(0.5)
        
        # 测试选怪键 (Tab键)
        print("\n2. 测试选怪键 (Tab键)")
        input_ctrl.press_key('tab')
        print("✅ 成功发送选怪键")
        
        time.sleep(0.5)
        
        # 测试技能键 (3键)
        print("\n3. 测试技能键 (3键)")
        input_ctrl.press_key('3')
        print("✅ 成功发送技能键")
        
        time.sleep(0.5)
        
        # 测试移动键 (WASD)
        print("\n4. 测试移动键 (WASD)")
        for key in ['w', 'a', 's', 'd']:
            input_ctrl.press_key(key)
            print(f"✅ 成功发送移动键: {key}")
            time.sleep(0.3)
        
        # 测试鼠标点击
        print("\n5. 测试鼠标点击")
        input_ctrl.click_mouse('left')
        print("✅ 成功发送鼠标左键点击")
        
        input_ctrl.click_mouse('right')
        print("✅ 成功发送鼠标右键点击")
        
        # 测试鼠标移动 (模拟视角转动)
        print("\n6. 测试鼠标移动 (模拟视角转动)")
        input_ctrl.move_mouse(100, 50, duration=0.5)
        print("✅ 成功发送鼠标移动")
        
        print("\n🎉 游戏模拟测试完成！所有操作都已成功发送到Arduino。")
        print("\n提示：现在你可以运行主程序来使用Arduino控制游戏了。")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭输入控制器
    input_ctrl.close()

if __name__ == "__main__":
    test_game_simulation()