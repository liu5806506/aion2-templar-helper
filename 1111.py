#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arduino 键盘模拟测试脚本 (智能端口版)
自动检测可用端口，避免 COM 口写错的问题
"""

import serial
import serial.tools.list_ports
import time
import sys

def get_arduino_port():
    """列出所有端口并让用户选择"""
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ 未发现任何 COM 端口！请检查 USB 线是否插好。")
        return None
    
    print("\n🔍 发现以下设备:")
    for i, p in enumerate(ports):
        # 尝试识别 Arduino (不同克隆板描述可能不同)
        desc = p.description
        is_arduino = "Arduino" in desc or "USB Serial" in desc or "CH340" in desc
        mark = "🌟" if is_arduino else "  "
        print(f"{mark} [{i}] {p.device} - {desc}")

    # 如果只有一个端口，直接尝试使用
    if len(ports) == 1:
        print(f"\n检测到只有一个端口，自动选择: {ports[0].device}")
        return ports[0].device

    # 如果有多个，让用户输入
    while True:
        try:
            selection = input(f"\n请输入序号 [0-{len(ports)-1}] 选择端口 (默认 0): ").strip()
            if selection == "":
                idx = 0
            else:
                idx = int(selection)
            
            if 0 <= idx < len(ports):
                return ports[idx].device
            else:
                print("❌ 序号无效，请重新输入。")
        except ValueError:
            print("❌ 输入无效，请输入数字。")

def test_number_keys():
    # 1. 获取端口
    port_name = get_arduino_port()
    if not port_name:
        return

    print(f"\n正在尝试连接 {port_name} ...")

    ser = None
    try:
        # 2. 打开串口
        ser = serial.Serial(port_name, 115200, timeout=1)
        
        # Leonardo/Micro 特有：打开串口会复位，必须等待较长时间
        print("等待 Arduino 复位和初始化 (2秒)...")
        time.sleep(2)  
        
        print(f"✅ 成功连接到 {port_name}")
        
        # 3. 开始测试
        print("\n=== 开始测试数字按键 1-9 ===")
        print("⚠️ 请将光标移到一个可以输入的文本框中 (你有3秒钟准备)!")
        for i in range(3, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
        print("开始!\n")

        for i in range(1, 10):
            key = str(i)
            # 发送按下指令
            cmd_down = f"KEY_DOWN,{key}\n"
            ser.write(cmd_down.encode('utf-8'))
            print(f"发送: [按住] {key}")
            
            time.sleep(0.3)  # 按住 0.3 秒
            
            # 发送松开指令
            cmd_up = f"KEY_UP,{key}\n"
            ser.write(cmd_up.encode('utf-8'))
            print(f"发送: [松开] {key}")
            
            time.sleep(0.5)  # 间隔 0.5 秒

        print("\n🎉 测试全部完成！")

    except serial.SerialException as e:
        print(f"\n❌ 串口错误: 无法打开 {port_name}")
        print(f"原因: {e}")
        print("提示: 请检查端口是否被其他程序(如Arduino IDE串口监视器)占用。")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("串口已安全关闭。")

if __name__ == "__main__":
    test_number_keys()