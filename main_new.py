#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永恒之塔2 守护星辅助脚本 - 模块化版本

架构设计：
- 输入层：负责键盘/鼠标/Arduino HID的统一接口
- 逻辑层：技能释放策略、选怪逻辑、拾取逻辑
- 控制层：启停、异常处理、日志记录
"""

import os
import sys
import time
import logging
import threading
from logging.handlers import RotatingFileHandler

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from modules.config import load_config
from modules.input import InputController
from modules.logic import CombatLogic
from modules.controller import BotController

# 从utils模块导入日志设置函数
from modules.utils import setup_logging

# 全局变量
bot_controller = None
global_logger = None
bot_thread = None

# 切换机器人运行状态
def toggle_bot():
    """切换机器人的运行状态"""
    global bot_controller, bot_thread
    
    if bot_controller is None:
        global_logger.error("Bot控制器未初始化")
        return
    
    if not bot_controller.running:
        # 启动前确保旧线程已结束
        if bot_thread is not None and bot_thread.is_alive():
            global_logger.warning("等待旧线程结束...")
            bot_thread.join(timeout=2.0)
            if bot_thread.is_alive():
                global_logger.error("旧线程未响应，无法启动新实例")
                return
        
        # 启动Bot
        global_logger.info("守护星辅助已启动...")
        bot_controller.start()
    else:
        # 停止Bot
        global_logger.info("守护星辅助已停止...")
        bot_controller.stop()

# 退出程序
def exit_program():
    """退出程序"""
    global bot_controller, bot_thread
    
    global_logger.info("正在退出程序...")
    
    if bot_controller:
        bot_controller.exit()
    
    # 等待线程结束
    if bot_thread is not None and bot_thread.is_alive():
        bot_thread.join(timeout=3.0)
    
    global_logger.info("程序已退出")
    sys.exit(0)

# 主程序入口
def main():
    """主程序入口"""
    global bot_controller, global_logger
    
    # 设置日志
    global_logger = setup_logging()
    global_logger.info("守护星硬件辅助脚本已加载")
    
    try:
        # 加载配置
        config = load_config("config.yaml")
        global_logger.info("配置文件加载成功")
        
        # 初始化输入控制器
        input_ctrl = InputController(config)
        global_logger.info("输入控制器初始化成功")
        
        # 初始化战斗逻辑
        combat_logic = CombatLogic(input_ctrl, config)
        global_logger.info("战斗逻辑初始化成功")
        
        # 初始化Bot控制器
        bot_controller = BotController(input_ctrl, combat_logic, config)
        global_logger.info("Bot控制器初始化成功")
        
        # 导入键盘监听模块（延迟导入，避免启动问题）
        import keyboard
        
        # 设置键盘监听
        keyboard.add_hotkey(config["control"]["key_toggle"], toggle_bot)
        keyboard.add_hotkey(config["control"]["key_exit"], exit_program)
        
        global_logger.info(f"按 {config['control']['key_toggle']} 键开始/停止辅助")
        global_logger.info(f"按 {config['control']['key_exit']} 键退出程序")
        global_logger.info("请确保游戏窗口在前台，并且Arduino设备已正确连接")
        
        # 主循环
        while bot_controller.program_active:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        exit_program()
    except Exception as e:
        global_logger.error(f"程序异常: {e}", exc_info=True)
        exit_program()

if __name__ == "__main__":
    main()
