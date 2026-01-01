#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot控制器模块
负责启停、异常处理、日志记录
"""

import time
import threading
import logging

class BotController:
    """Bot控制器，负责管理Bot的生命周期"""
    
    def __init__(self, input_ctrl, combat_logic, config):
        """初始化Bot控制器
        
        Args:
            input_ctrl (InputController): 输入控制器
            combat_logic (CombatLogic): 战斗逻辑
            config (dict): 配置字典
        """
        self.input_ctrl = input_ctrl
        self.combat_logic = combat_logic
        self.config = config
        
        # 状态标志
        self.running = False
        self.program_active = True
        
        # 线程管理
        self.bot_thread = None
        
        # 日志记录器
        self.logger = logging.getLogger()
        
        # 设置各模块的日志记录器
        self.input_ctrl.set_logger(self.logger)
        self.combat_logic.set_logger(self.logger)
    
    def start(self):
        """启动Bot
        
        Returns:
            bool: 是否成功启动
        """
        if self.running:
            self.logger.warning("Bot已经在运行中")
            return False
        
        try:
            self.logger.info("[系统] 启动Bot...")
            self.running = True
            
            # 启动Bot线程
            self.bot_thread = threading.Thread(target=self._bot_loop)
            self.bot_thread.daemon = True
            self.bot_thread.start()
            
            self.logger.info("[系统] Bot启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"[系统] Bot启动失败: {e}")
            self.running = False
            return False
    
    def stop(self):
        """停止Bot
        
        Returns:
            bool: 是否成功停止
        """
        if not self.running:
            self.logger.warning("Bot已经停止")
            return False
        
        try:
            self.logger.info("[系统] 停止Bot...")
            self.running = False
            
            # 等待线程结束
            if self.bot_thread is not None and self.bot_thread.is_alive():
                self.logger.info("[系统] 等待Bot线程结束...")
                self.bot_thread.join(timeout=2.0)
                if self.bot_thread.is_alive():
                    self.logger.warning("[系统] Bot线程未响应，强制终止")
            
            # 重置战斗逻辑状态
            self.combat_logic.reset()
            
            self.logger.info("[系统] Bot停止成功")
            return True
            
        except Exception as e:
            self.logger.error(f"[系统] Bot停止失败: {e}")
            return False
    
    def exit(self):
        """退出程序
        
        Returns:
            bool: 是否成功退出
        """
        try:
            self.logger.info("[系统] 正在退出程序...")
            
            # 停止Bot
            if self.running:
                self.stop()
            
            # 关闭资源
            self.input_ctrl.close()
            self.combat_logic.close()
            
            # 设置程序为非活动状态
            self.program_active = False
            
            self.logger.info("[系统] 程序退出成功")
            return True
            
        except Exception as e:
            self.logger.error(f"[系统] 程序退出失败: {e}")
            return False
    
    def _bot_loop(self):
        """Bot主循环
        """
        self.logger.info("[系统] Bot主循环开始")
        
        try:
            while self.running:
                # 执行战斗逻辑循环
                if not self.combat_logic.run_cycle():
                    self.logger.warning("[系统] 战斗逻辑循环返回失败，重置状态")
                    self.combat_logic.reset()
                    
                # 检查是否需要继续运行
                if not self.running:
                    break
            
        except Exception as e:
            self.logger.error(f"[系统] Bot主循环异常: {e}", exc_info=True)
        finally:
            self.logger.info("[系统] Bot主循环结束")
            self.running = False
    
    def is_running(self):
        """检查Bot是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.running
    
    def get_state(self):
        """获取Bot当前状态
        
        Returns:
            str: 当前状态
        """
        return self.combat_logic.state
    
    def set_log_level(self, level):
        """设置日志级别
        
        Args:
            level (str): 日志级别 (DEBUG, INFO, WARNING, ERROR)
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        
        if level in level_map:
            self.logger.setLevel(level_map[level])
            self.logger.info(f"[系统] 日志级别已设置为: {level}")
            return True
        else:
            self.logger.error(f"[系统] 无效的日志级别: {level}")
            return False
