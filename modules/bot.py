import time
import random
try:
    from . import config
except ImportError:
    import config
from .vision import Vision
from .hardware_input import HardwareInput
from .window_manager import WindowManager

class Bot:
    """守护星自动战斗核心类，实现状态机模式"""
    
    # 状态定义
    STATE_IDLE = 'idle'  # 空闲状态，寻怪
    STATE_COMBAT = 'combat'  # 战斗状态，卡刀循环
    STATE_LOOT = 'loot'  # 拾取状态
    STATE_REST = 'rest'  # 休息状态
    
    def __init__(self, logger=None):
        """初始化Bot核心
        :param logger: 日志记录函数
        """
        self.logger = logger or self._default_logger
        self.state = self.STATE_IDLE
        self.running = False
        self.program_active = True
        
        # 初始化各个模块
        self.vision = Vision(logger=self.logger)
        self.hardware = HardwareInput(logger=self.logger)
        self.window_manager = WindowManager(logger=self.logger)
        
        # 技能状态跟踪
        self.skill_cooldowns = {}
        self.skill_uses = {}
        
        # 防卡死机制变量
        self.stuck_counter = 0
        self.MAX_STUCK_COUNT = 10  # 连续10次循环无进展则认为卡住
        
        # 战斗相关标志
        self.is_first_attack = True  # 标记是否为战斗中的第一次攻击
        
    def _default_logger(self, message):
        """默认日志记录函数"""
        print(f"[Bot] {message}")
    
    def smart_sleep(self, duration, jitter_range=0.01):
        """智能睡眠函数，可以被外部事件中断，并添加随机Jitter"""
        # 使用高斯分布生成更自然的随机延迟，符合人类操作模式
        # 高斯分布的均值为0，标准差为jitter_range/2
        jitter = random.gauss(0, jitter_range / 2)
        # 确保jitter在指定范围内
        jitter = max(-jitter_range, min(jitter_range, jitter))
        actual_duration = max(0.01, duration + jitter)  # 确保延迟至少为10ms
        end_time = time.time() + actual_duration
        while time.time() < end_time and self.running:
            time.sleep(0.01)
        return self.running
    
    def select_target(self):
        """智能选怪逻辑 - 包含目标确认"""
        for attempt in range(config.SELECTION_MAX_ATTEMPTS):
            self.logger(f"[选怪] 第 {attempt+1} 次尝试选怪")
            
            # 按tab键选怪
            self.hardware.press_key(config.KEY_SELECT_TARGET, running=self.running)
            
            # 等待选怪动作完成
            if not self.smart_sleep(config.SELECTION_DELAY, jitter_range=0.02):  # 添加±20ms的随机Jitter
                return False
            
            # 检查是否选中了目标
            if self.vision.check_has_target():
                self.logger("[选怪] 成功选中目标")
                return True
            
            # 未选中目标，继续尝试
            self.logger("[选怪] 未选中目标，继续尝试")
            
            # 加入随机延迟，模拟人类操作
            if not self.smart_sleep(0.2, jitter_range=0.1):
                return False
        
        # 多次尝试后仍未选中目标
        self.logger("[选怪] 多次尝试后仍未选中目标")
        return False
    
    def estimate_target_count(self):
        """估计当前目标数量"""
        # 保守策略：默认返回1，除非能确切通过图像识别看到屏幕上有多个血条
        return 1
    
    def manage_hate(self):
        """仇恨管理逻辑 - 守护星专业仇恨控制"""
        # 确保游戏窗口在前台
        self.window_manager.activate_game_window()
        time.sleep(0.05)
        
        self.logger("执行仇恨管理逻辑")
        
        # 记录已使用的仇恨技能
        used_hate_skills = []
        
        # 检查当前是否有目标
        has_target = self.vision.check_has_target()
        
        if not has_target:
            self.logger("未检测到目标，跳过仇恨管理")
            return
        
        # 仇恨技能使用计数
        hate_skills_used = 0
        max_hate_skills = 1  # 每次最多使用1个仇恨技能
        
        # 获取当前目标数量
        target_count = self.estimate_target_count()
        self.logger(f"当前目标数量估计: {target_count}")
        
        # 首先使用挑衅技能确保仇恨稳定（单体目标优先）
        if self.running and 'provoke' in config.HATE_SKILLS and config.HATE_SKILLS['provoke'] and target_count <= 2:
            skill_key = config.HATE_SKILLS['provoke']
            if skill_key not in used_hate_skills:
                self.logger(f"使用主要仇恨技能: 挑衅 ({skill_key})")
                self.hardware.press_key(skill_key, running=self.running)
                used_hate_skills.append(skill_key)
                hate_skills_used += 1
                if not self.smart_sleep(0.5):
                    return
        
        # 如果是多目标场景，优先使用AOE仇恨技能
        elif self.running and 'provoke_roar' in config.HATE_SKILLS and config.HATE_SKILLS['provoke_roar'] and target_count > 2:
            skill_key = config.HATE_SKILLS['provoke_roar']
            if skill_key not in used_hate_skills:
                self.logger(f"使用AOE仇恨技能: 挑衅的咆哮 ({skill_key})")
                self.hardware.press_key(skill_key, running=self.running)
                used_hate_skills.append(skill_key)
                hate_skills_used += 1
                if not self.smart_sleep(0.8):
                    return
        
        # 如果已经使用了仇恨技能，检查是否需要额外的仇恨技能
        if self.running and hate_skills_used < max_hate_skills:
            # 遍历仇恨技能优先级列表
            for skill_name in config.HATE_SKILL_PRIORITIES:
                if not self.running:
                    return
                    
                if hate_skills_used >= max_hate_skills:
                    break
                    
                if skill_name in config.HATE_SKILLS and config.HATE_SKILLS[skill_name]:
                    skill_key = config.HATE_SKILLS[skill_name]
                    
                    # 避免重复使用同一个技能
                    if skill_key in used_hate_skills:
                        continue
                        
                    # 特殊处理不同场景下的技能使用
                    use_skill = True
                    
                    # 单体目标场景避免使用AOE技能
                    if skill_name == 'provoke_roar' and target_count <= 2:
                        use_skill = False
                    
                    # 多目标场景优先使用AOE技能
                    elif skill_name == 'provoke' and target_count > 2:
                        use_skill = False
                    
                    if use_skill:
                        self.logger(f"使用仇恨技能: {skill_name} ({skill_key})")
                        self.hardware.press_key(skill_key, running=self.running)
                        used_hate_skills.append(skill_key)
                        hate_skills_used += 1
                        
                        # 根据技能类型调整延迟
                        if skill_name == 'provoke_roar':
                            if not self.smart_sleep(0.8):  # AOE技能需要更长延迟
                                return
                        else:
                            if not self.smart_sleep(0.5):
                                return
                        break  # 使用一个仇恨技能后暂时退出，避免连续使用
        
        # 补充：如果没有使用仇恨技能，使用一个高仇恨的输出技能来保持仇恨
        if self.running and hate_skills_used == 0:
            self.logger("使用高仇恨输出技能保持仇恨")
            # 使用猛烈一击（左键）来保持仇恨
            self.hardware.click_mouse(button="left", running=self.running)
            self.smart_sleep(0.1)
    
    def use_defense_skills(self):
        """使用防御技能逻辑 - 守护星专业防御控制"""
        # 确保游戏窗口在前台
        self.window_manager.activate_game_window()
        time.sleep(0.05)
        
        self.logger("执行防御技能逻辑")
        
        # 获取当前生命值
        health_percentage = self.vision.check_health()
        
        # 记录已使用的技能
        used_skills = []
        
        # 技能使用计数
        skills_used = 0
        max_skills_per_check = 2  # 每次最多使用2个防御技能，避免技能滥用
        
        # 遍历防御技能优先级列表
        for skill_name, health_threshold in config.DEFENSE_SKILL_PRIORITIES:
            if not self.running:
                return
                
            if skills_used >= max_skills_per_check:
                break  # 达到最大技能使用次数，退出循环
                
            # 检查技能是否配置
            if skill_name not in config.DEFENSE_SKILLS or not config.DEFENSE_SKILLS[skill_name]:
                continue
                
            # 检查生命值是否低于阈值
            if health_percentage <= health_threshold:
                skill_key = config.DEFENSE_SKILLS[skill_name]
                
                # 检查技能是否在冷却中
                if skill_name in self.skill_cooldowns:
                    if time.time() < self.skill_cooldowns[skill_name]:
                        self.logger(f"[调试] 技能 {skill_name} 仍在冷却中")
                        continue
                
                # 避免重复使用同一个技能
                if skill_key in used_skills:
                    continue
                    
                self.logger(f"[调试] 生命值低于 {health_threshold}%，使用防御技能: {skill_name} ({skill_key})")
                
                # 使用技能
                self.hardware.press_key(skill_key, running=self.running)
                used_skills.append(skill_key)
                skills_used += 1
                
                # 记录技能冷却时间
                if skill_name in config.SKILL_COOLDOWNS:
                    cooldown_time = config.SKILL_COOLDOWNS[skill_name]
                    self.skill_cooldowns[skill_name] = time.time() + cooldown_time
                    self.logger(f"[调试] 技能 {skill_name} 进入冷却，冷却时间: {cooldown_time}秒")
                
                # 技能使用间隔
                if not self.smart_sleep(config.SKILL_DELAY):
                    return
                
                # 如果使用了一个主要防御技能，暂时退出，避免连续使用
                if skill_name in ['dual_armor', 'god_armor', 'nazeal_shield']:
                    break
    
    def check_skill_condition(self, skill_name):
        """检查技能条件是否满足
        :param skill_name: 技能名称
        :return: bool - 条件是否满足
        """
        try:
            # 检查技能是否存在
            if skill_name not in config.SKILL_DATABASE:
                return True  # 技能不存在，默认允许使用
            
            skill = config.SKILL_DATABASE[skill_name]
            
            # 检查技能是否有条件
            if 'condition' not in skill:
                return True  # 没有条件，允许使用
            
            condition = skill['condition']
            self.logger(f"[技能条件] 检查技能 {skill_name} 的条件: {condition}")
            
            # 根据条件类型进行检查
            if condition == 'low_health':
                # 生命值低于50%时允许使用
                health = self.vision.check_health()
                return health < 50
            elif condition == 'boss_target':
                # 假设当前目标是BOSS（简化实现）
                return True
            elif condition == 'multiple_targets':
                # 多个目标时允许使用
                target_count = self.estimate_target_count()
                return target_count > 1
            elif condition == 'after_block':
                # 格挡后允许使用（简化实现，假设可以使用）
                return True
            else:
                # 未知条件，默认允许使用
                return True
                
        except Exception as e:
            self.logger(f"[错误] 技能条件检查失败: {e}")
            return True  # 出错时默认允许使用
    
    def weave_skill(self, skill_key, attack_windup_base=None):
        """
        守护星卡刀函数
        :param skill_key: 要释放的技能键位
        :param attack_windup_base: 你的当前攻速对应的平A前摇时间 (秒)，如果为None则使用配置文件中的设置
        """
        # 如果没有提供前摇时间，使用配置文件中的当前档位设置
        if attack_windup_base is None:
            attack_windup_base = config.WEAVE_ATTACK_WINDUP.get(config.CURRENT_WEAVE_GEAR, 0.85)
        
        self.logger(f"[卡刀] 执行卡刀: 平A -> {skill_key}, 前摇时间: {attack_windup_base}秒")
        
        # 1. 发起普通攻击 (平A)
        min_dur, max_dur = config.WEAVE_CONFIG['attack_keypress_delay']
        self.hardware.press_key(config.KEY_AUTO_ATTACK, min_duration=min_dur, max_duration=max_dur, running=self.running)
        
        # 2. 等待平A伤害出来 (这是最关键的延迟)
        # 必须根据面板攻速调整。如果太快，平A会被吞；如果太慢，会发呆。
        # 加入微量随机抖动，防检测
        jitter = random.gauss(0, config.WEAVE_CONFIG['jitter_range'] / 2)
        jitter = max(-config.WEAVE_CONFIG['jitter_range'], min(config.WEAVE_CONFIG['jitter_range'], jitter))
        real_delay = attack_windup_base + jitter
        self.logger(f"[卡刀] 等待平A伤害: {real_delay:.3f}秒 (前摇+抖动)")
        
        if not self.smart_sleep(real_delay):
            return False
        
        # 3. 立即释放技能 (打断平A后摇)
        min_dur, max_dur = config.WEAVE_CONFIG['skill_keypress_delay']
        if not self.hardware.press_key(skill_key, min_duration=min_dur, max_duration=max_dur, running=self.running):
            return False
        
        # 4. 等待技能动作（公共CD或技能后摇），防止连发太快
        # 这一步通常由游戏GCD决定，一般是 0.5 - 1.0秒
        if not self.smart_sleep(config.WEAVE_CONFIG['after_skill_delay']):
            return False
        
        self.logger(f"[卡刀] 卡刀完成: 平A -> {skill_key}")
        return True
    
    def moving_weave(self, skill_key, attack_windup_base=None):
        """
        守护星移动卡刀函数（走砍）
        :param skill_key: 要释放的技能键位
        :param attack_windup_base: 你的当前攻速对应的平A前摇时间 (秒)
        """
        # 如果没有提供前摇时间，使用配置文件中的当前档位设置
        if attack_windup_base is None:
            attack_windup_base = config.WEAVE_ATTACK_WINDUP.get(config.CURRENT_WEAVE_GEAR, 0.85)
        
        self.logger(f"[卡刀] 执行移动卡刀: 平A -> {skill_key}, 前摇时间: {attack_windup_base}秒")
        
        # 1. 确保按住 W (前进)
        self.logger("[卡刀] 开始移动卡刀，按住前进键")
        
        # 构造前进键的按下指令（文本格式）
        press_w_cmd = "KEY_DOWN,W"
        if not self.hardware.send_serial_command(press_w_cmd, wait_ack=False):
            return False
        
        # 短暂延迟，确保角色开始移动
        if not self.smart_sleep(0.05):
            # 释放前进键
            release_w_cmd = "KEY_UP,W"
            self.hardware.send_serial_command(release_w_cmd, wait_ack=False)
            return False
        
        # 2. 执行卡刀
        try:
            # 发起普通攻击 (平A)
            min_dur, max_dur = config.WEAVE_CONFIG['attack_keypress_delay']
            self.hardware.press_key(config.KEY_AUTO_ATTACK, min_duration=min_dur, max_duration=max_dur, running=self.running)
            
            # 等待平A伤害出来 (关键延迟)
            jitter = random.gauss(0, config.WEAVE_CONFIG['jitter_range'] / 2)
            jitter = max(-config.WEAVE_CONFIG['jitter_range'], min(config.WEAVE_CONFIG['jitter_range'], jitter))
            real_delay = attack_windup_base + jitter
            self.logger(f"[卡刀] 等待平A伤害: {real_delay:.3f}秒 (前摇+抖动)")
            
            if not self.smart_sleep(real_delay):
                return False
            
            # 立即释放技能 (打断平A后摇)
            min_dur, max_dur = config.WEAVE_CONFIG['skill_keypress_delay']
            if not self.hardware.press_key(skill_key, min_duration=min_dur, max_duration=max_dur, running=self.running):
                return False
            
            # 技能释放后的等待时间
            if not self.smart_sleep(config.WEAVE_CONFIG['after_skill_delay']):
                return False
                
        finally:
            # 3. 技能放完后，松开前进键
            release_w_cmd = "KEY_UP,W"
            self.hardware.send_serial_command(release_w_cmd, wait_ack=False)
            self.logger("[卡刀] 移动卡刀完成，松开前进键")
        
        self.logger(f"[卡刀] 移动卡刀完成: 平A -> {skill_key}")
        return True
    
    def bot_loop(self):
        """主循环 - 守护星自动战斗逻辑，实现状态机模式"""
        # 初始化串口连接
        if not self.hardware.init_serial():
            self.logger("[错误] 无法初始化串口连接，脚本将退出")
            return
        
        try:
            while self.running:
                # 根据当前状态执行不同的逻辑
                if self.state == self.STATE_IDLE:
                    # 空闲状态，寻怪
                    self.logger("[状态] 空闲 - 寻找目标")
                    has_target = self.vision.check_has_target()
                    if not has_target:
                        self.logger("未检测到目标，尝试选择目标")
                        if self.select_target():
                            self.state = self.STATE_COMBAT
                            self.stuck_counter = 0
                            self.is_first_attack = True  # 重置起手标志
                        else:
                            self.stuck_counter += 1
                            self.logger(f"[防卡死] 第 {self.stuck_counter} 次无法选中目标")
                            if self.stuck_counter >= self.MAX_STUCK_COUNT:
                                self.logger("[防卡死] 检测到卡住状态，执行防卡死机制")
                                # 随机按S后退几步
                                for _ in range(2):
                                    self.hardware.press_key('s', min_duration=0.1, max_duration=0.2, running=self.running)
                                # 按Space跳跃一下
                                self.hardware.press_key('space', min_duration=0.05, max_duration=0.1, running=self.running)
                                # 重置卡住计数器
                                self.stuck_counter = 0
                    else:
                        self.state = self.STATE_COMBAT
                        self.stuck_counter = 0
                        self.is_first_attack = True  # 重置起手标志
                
                elif self.state == self.STATE_COMBAT:
                    # 战斗状态，卡刀循环
                    self.logger("[状态] 战斗 - 执行卡刀循环")
                    has_target = self.vision.check_has_target()
                    if not has_target:
                        self.state = self.STATE_IDLE
                        self.stuck_counter = 0
                    else:
                        # 执行起手技能
                        if self.is_first_attack:
                            if config.KEY_STARTER:
                                self.logger(f"[战斗] 使用起手技能: {config.KEY_STARTER}")
                                self.hardware.press_key(config.KEY_STARTER, running=self.running)
                                self.smart_sleep(config.DELAY_STARTER)
                            self.is_first_attack = False # 标记已开怪
                        
                        # 1. 检查生命值，使用防御技能
                        self.use_defense_skills()
                        
                        # 2. 检查状态效果
                        status_list = self.vision.detect_status()
                        if status_list:
                            self.logger(f"[状态效果] 检测到状态效果: {status_list}")
                            # 简化实现：不做任何处理
                        
                        # 3. 执行卡刀机制（核心输出）
                        # 使用猛烈一击作为主要输出技能进行卡刀
                        if config.WEAVE_CONFIG['moving_weave_enabled']:
                            # 使用移动卡刀（走砍）
                            self.moving_weave(config.SKILL_DATABASE['violent_strike']['key'])
                        else:
                            # 使用普通卡刀
                            self.weave_skill(config.SKILL_DATABASE['violent_strike']['key'])
                        
                        # 4. 仇恨管理
                        self.manage_hate()
                        
                        # 5. 检查是否战斗结束
                        # 简化实现：假设战斗持续进行，直到目标消失
                
                elif self.state == self.STATE_LOOT:
                    # 拾取状态
                    self.logger("[状态] 拾取 - 自动拾取物品")
                    # 简化实现：不做任何处理
                    self.state = self.STATE_IDLE
                
                elif self.state == self.STATE_REST:
                    # 休息状态
                    self.logger("[状态] 休息 - 恢复生命值")
                    # 简化实现：不做任何处理
                    self.state = self.STATE_IDLE
                
                # 循环间隔，添加随机Jitter
                if not self.smart_sleep(config.LOOP_DELAY, jitter_range=0.05):  # 添加±50ms的随机Jitter
                    break
                    
        except Exception as e:
            self.logger(f"[错误] 主循环异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 关闭各个模块
            self.hardware.close()
            self.vision.close()
    
    def start(self):
        """启动Bot"""
        self.running = True
        self.logger("[系统] 守护星辅助已启动")
        # 启动主循环
        self.bot_loop()
    
    def stop(self):
        """停止Bot"""
        self.running = False
        self.logger("[系统] 守护星辅助已停止")
    
    def exit(self):
        """退出程序"""
        self.logger("[系统] 正在退出程序...")
        self.running = False
        self.program_active = False
        # 关闭各个模块
        self.hardware.close()
        self.vision.close()
        self.logger("[系统] 程序已退出")