#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含日志初始化、随机延迟、异常处理等通用功能
"""

import os
import time
import random
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file="logs/bot.log", max_bytes=10*1024*1024, backup_count=5):
    """设置日志记录
    
    Args:
        log_file (str): 日志文件路径
        max_bytes (int): 单个日志文件最大字节数
        backup_count (int): 保留的日志文件数量
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清空现有的处理器（防止重复记录）
    logger.handlers.clear()
    
    # 控制台日志格式
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件日志格式（带时间戳和行号）
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def random_delay(min_delay, max_delay, distribution="uniform"):
    """生成随机延迟
    
    Args:
        min_delay (float): 最小延迟时间（秒）
        max_delay (float): 最大延迟时间（秒）
        distribution (str): 分布类型，支持 "uniform"（均匀分布）和 "gaussian"（高斯分布）
        
    Returns:
        float: 随机延迟时间
    """
    if distribution == "uniform":
        # 均匀分布
        return random.uniform(min_delay, max_delay)
    elif distribution == "gaussian":
        # 高斯分布，均值为中间值，标准差为范围的1/6
        mean = (min_delay + max_delay) / 2
        std_dev = (max_delay - min_delay) / 6
        delay = random.gauss(mean, std_dev)
        # 确保延迟在指定范围内
        return max(min_delay, min(max_delay, delay))
    else:
        raise ValueError(f"不支持的分布类型: {distribution}")

def human_like_pause(probability=0.1, max_duration=0.5):
    """模拟人类随机停顿
    
    Args:
        probability (float): 停顿的概率（0-1之间）
        max_duration (float): 最大停顿时间（秒）
        
    Returns:
        bool: 是否执行了停顿
    """
    if random.random() < probability:
        pause_duration = random.uniform(0, max_duration)
        time.sleep(pause_duration)
        return True
    return False

def clamp(value, min_value, max_value):
    """将值限制在指定范围内
    
    Args:
        value: 要限制的值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        限制后的值
    """
    return max(min_value, min(max_value, value))

def calculate_cooldown_remaining(last_used, cooldown):
    """计算技能冷却剩余时间
    
    Args:
        last_used (float): 上次使用时间（时间戳）
        cooldown (float): 冷却时间（秒）
        
    Returns:
        float: 剩余冷却时间（秒），0表示冷却完成
    """
    elapsed = time.time() - last_used
    remaining = cooldown - elapsed
    return max(0, remaining)

def get_timestamp():
    """获取当前时间戳（格式化）
    
    Returns:
        str: 格式化的时间戳，如 "2023-12-01 12:00:00"
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def safe_divide(numerator, denominator, default=0):
    """安全除法，避免除以零
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 分母为零时的默认返回值
        
    Returns:
        除法结果或默认值
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default
