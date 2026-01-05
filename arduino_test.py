#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arduino通信测试脚本
用于验证Arduino设备是否正常工作
"""

import time
import serial
import serial.tools.list_ports
from modules.hardware_input import HardwareInput

def test_arduino_connection():
    """测试Arduino连接"""
    print("开始测试Arduino连接...")
    
    # 创建HardwareInput实例
    hardware = HardwareInput()
    
    # 初始化串口
    if hardware.init_serial():
        print("✅ Arduino连接成功！")
        
        # 测试发送几个命令
        print("\n测试发送按键命令...")
        try:
            # 测试按键
            hardware.press_key('A')
            print("✅ 成功发送按键A")
            
            time.sleep(0.5)
            
            # 测试鼠标移动
            hardware.send_mouse_input(10, 5)
            print("✅ 成功发送鼠标移动(10, 5)")
            
            time.sleep(0.5)
            
            # 测试鼠标点击
            hardware.click_mouse('left')
            print("✅ 成功发送鼠标左键点击")
            
            print("\n🎉 Arduino测试完成！一切正常。")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
        # 关闭连接
        hardware.close()
    else:
        print("❌ Arduino连接失败，请检查:")
        print("   1. Arduino是否正确连接到电脑")
        print("   2. Arduino固件是否正确上传")
        print("   3. 串口端口是否正确")
        print("   4. 波特率是否设置为115200")

if __name__ == "__main__":
    test_arduino_connection()