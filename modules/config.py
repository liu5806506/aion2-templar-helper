#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和解析YAML配置文件
"""

import os
import yaml

# 配置缓存
_config_cache = {}

def load_config(config_file):
    """加载配置文件
    
    Args:
        config_file (str): 配置文件路径
        
    Returns:
        dict: 配置字典
    """
    global _config_cache
    
    # 检查文件是否存在
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    # 检查缓存
    if config_file in _config_cache:
        return _config_cache[config_file]
    
    # 加载配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 验证配置
    validate_config(config)
    
    # 缓存配置
    _config_cache[config_file] = config
    
    return config

def validate_config(config):
    """验证配置文件的完整性
    
    Args:
        config (dict): 配置字典
        
    Raises:
        ValueError: 配置不完整时抛出异常
    """
    # 检查必要的配置项
    required_sections = [
        'control', 'input', 'keys', 'delays', 'skills',
        'selection', 'defense', 'weave', 'image_recognition'
    ]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"配置文件缺少必要的配置项: {section}")
    
    # 检查控制热键
    if 'key_toggle' not in config['control']:
        raise ValueError("配置文件缺少控制热键: key_toggle")
    
    if 'key_exit' not in config['control']:
        raise ValueError("配置文件缺少控制热键: key_exit")
    
    # 检查技能配置
    if not isinstance(config['skills'], dict):
        raise ValueError("技能配置必须是字典类型")
    
    return True

def get_config_value(config, path, default=None):
    """获取配置值，支持路径访问
    
    Args:
        config (dict): 配置字典
        path (str): 配置路径，如 "control.key_toggle"
        default: 默认值
        
    Returns:
        配置值或默认值
    """
    keys = path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
