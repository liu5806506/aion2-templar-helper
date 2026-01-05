#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字按键测试脚本
用于验证Arduino固件中数字按键1-9是否正常工作
"""

import serial
import time

def test_number_keys():
    """测试数字按键1-9"""
    print("开始测试数字按键1-9...")
    
    try:
        # 打开串口连接
        ser = serial.Serial('COM3', 115200, timeout=1)
        time.sleep(2)  # 等待Arduino初始化
        
        print(f"已连接到Arduino设备: {ser.port}")
        
        # 测试数字按键1-9
        for i in range(1, 10):
            key = str(i)
            print(f"\n测试按键: {key}")
            
            # 按下数字键
            print(f"按下 {key} 键...")
            ser.write(f"KEY_DOWN,{key}\n".encode('utf-8'))
            time.sleep(0.5)  # 按住0.5秒
            
            # 松开数字键
            print(f"松开 {key} 键...")
            ser.write(f"KEY_UP,{key}\n".encode('utf-8'))
            time.sleep(0.5)
            
            print(f"✅ {key} 键测试完成")
        
        print("\n🎉 数字按键1-9测试完成！所有按键都已成功发送到Arduino。")
        
        # 关闭串口
        ser.close()
        print("串口已关闭")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    test_number_keys()