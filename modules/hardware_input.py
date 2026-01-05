import time
import serial
import serial.tools.list_ports
import random

class HardwareInput:
    """硬件输入模块，负责与Arduino的通信和键盘鼠标输入"""
    
    def __init__(self, logger=None):
        """初始化硬件输入模块
        :param logger: 日志记录函数
        """
        self.logger = logger or self._default_logger
        self.serial_conn = None
        self.baud_rate = 115200  # 提升波特率以降低输入延迟
        self.serial_timeout = 1
        self.serial_port = None  # 自动检测或手动指定
        
    def _default_logger(self, message):
        """默认日志记录函数"""
        print(f"[HardwareInput] {message}")
    
    def init_serial(self):
        """初始化串口通信"""
        try:
            # 如果未指定串口，自动检测Arduino设备
            if not self.serial_port:
                ports = serial.tools.list_ports.comports()
                for port in ports:
                    if "Arduino" in port.description or "USB Serial Device" in port.description:
                        self.serial_port = port.device
                        self.logger(f"自动检测到Arduino设备: {self.serial_port}")
                        break
            
            if not self.serial_port:
                self.logger("[错误] 未检测到Arduino设备，请确保设备已连接并正确安装驱动")
                return False
            
            # 初始化串口连接
            self.serial_conn = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=self.serial_timeout
            )
            
            # 等待串口稳定
            time.sleep(2)
            
            # 检查是否收到Arduino的就绪信号
            self.logger("等待Arduino就绪信号...")
            self.serial_conn.flushInput()
            time.sleep(0.5)
            if self.serial_conn.in_waiting > 0:
                response = self.serial_conn.readline().decode('utf-8').strip()
                if response:
                    self.logger(f"[串口] {response}")
            
            self.logger(f"已连接到Arduino设备: {self.serial_port}")
            return True
            
        except Exception as e:
            self.logger(f"[错误] 串口初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_serial_command(self, command, wait_ack=False):
        """发送串口命令到Arduino
        :param command: 要发送的命令
        :param wait_ack: 是否等待Arduino的OK响应
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            # 如果串口未连接，尝试重新连接
            if not self.init_serial():
                return False
        
        try:
            # 清空输入缓冲区
            self.serial_conn.flushInput()
            
            # 发送命令，添加换行符作为结束标志
            full_command = command + '\n'
            self.logger(f"[串口] 发送指令: {full_command.strip()}")
            self.serial_conn.write(full_command.encode('utf-8'))
            self.serial_conn.flush()
            
            # 优化：普通按键不需要等待Arduino回复OK，提高并发速度
            if wait_ack:
                # 等待Arduino响应
                response = self.serial_conn.readline().decode('utf-8').strip()
                if response == 'OK':
                    return True
                else:
                    self.logger(f"[警告] Arduino响应错误: {response}")
                    return False
            return True
            
        except Exception as e:
            self.logger(f"[错误] 发送串口命令失败: {e}")
            # 关闭串口以便下次重新连接
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            return False
    
    def generate_bezier_curve(self, start, end, control_points=2, steps=20):
        """生成从起点到终点的贝塞尔曲线路径
        :param start: 起点坐标 (x, y)
        :param end: 终点坐标 (x, y)
        :param control_points: 控制点数量
        :param steps: 曲线上的点数量
        :return: 曲线上的坐标点列表
        """
        # 生成控制点
        points = [start]
        
        # 生成随机控制点，使曲线更自然
        for i in range(control_points):
            # 控制点在起点和终点之间随机偏移
            cp_x = start[0] + (end[0] - start[0]) * (i + 1) / (control_points + 1) + random.randint(-5, 5)
            cp_y = start[1] + (end[1] - start[1]) * (i + 1) / (control_points + 1) + random.randint(-5, 5)
            points.append((cp_x, cp_y))
        
        points.append(end)
        
        # 生成贝塞尔曲线上的点
        curve_points = []
        for t in range(steps + 1):
            # 贝塞尔曲线参数 t (0 到 1)
            t_param = t / steps
            
            # 使用De Casteljau算法计算贝塞尔曲线上的点
            temp_points = list(points)
            n = len(temp_points) - 1
            while n > 0:
                for i in range(n):
                    x = (1 - t_param) * temp_points[i][0] + t_param * temp_points[i + 1][0]
                    y = (1 - t_param) * temp_points[i][1] + t_param * temp_points[i + 1][1]
                    temp_points[i] = (x, y)
                n -= 1
            
            curve_points.append((int(temp_points[0][0]), int(temp_points[0][1])))
        
        return curve_points
    
    def send_mouse_input(self, dx=0, dy=0, running=True):
        """通过串口发送鼠标移动命令到Arduino
        :param dx: 鼠标水平移动距离
        :param dy: 鼠标垂直移动距离
        :param running: 运行状态标志
        """
        self.logger(f"[调试] 发送鼠标移动指令: ({dx}, {dy})")
        
        # 生成贝塞尔曲线移动路径
        start = (0, 0)
        end = (dx, dy)
        # 生成平滑的曲线路径，包含2个控制点，20个路径点
        curve_points = self.generate_bezier_curve(start, end, control_points=2, steps=20)
        
        # 沿曲线移动
        for i in range(1, len(curve_points)):
            if not running:
                return False
            
            # 计算当前步的移动距离
            prev_x, prev_y = curve_points[i-1]
            curr_x, curr_y = curve_points[i]
            move_x = curr_x - prev_x
            move_y = curr_y - prev_y
            
            # 构造指令（文本格式）：MOUSE_MOVE,dx,dy
            cmd = f"MOUSE_MOVE,{move_x},{move_y}"
            
            # 发送指令，不等待响应，提高移动速度
            if not self.send_serial_command(cmd, wait_ack=False):
                return False
            
            # 移动之间的随机延迟，使用高斯分布，使移动更自然
            delay = random.gauss(0.015, 0.005)
            delay = max(0.005, min(0.03, delay))  # 确保延迟在合理范围内
            time.sleep(delay)
        
        self.logger(f"[调试] 已完成鼠标移动: ({dx}, {dy})")
        return True
    
    def click_mouse(self, button="left", clicks=1, min_duration=0.05, max_duration=0.15, running=True):
        """通过串口发送鼠标点击指令到Arduino
        :param button: "left", "right", "middle"
        :param clicks: 点击次数
        :param min_duration: 点击按下的最小时间
        :param max_duration: 点击按下的最大时间
        :param running: 运行状态标志
        """
        self.logger(f"[调试] 执行鼠标点击: {button}键, 次数: {clicks}")
        
        # 选择鼠标按键对应的指令（文本格式）
        if button == "left":
            mouse_code = "MOUSE1"
        elif button == "right":
            mouse_code = "MOUSE2"
        else:
            self.logger(f"[错误] 未知的鼠标按键: {button}")
            return False
        
        # 构造按下和松开的指令
        press_cmd = f"KEY_DOWN,{mouse_code}"
        release_cmd = f"KEY_UP,{mouse_code}"
        
        # 执行点击
        for i in range(clicks):
            if not running:
                return False
            
            # 按下鼠标键
            if not self.send_serial_command(press_cmd, wait_ack=False):
                return False
            
            # 随机延迟，模拟人类按键的不确定性，使用高斯分布
            delay = random.gauss((min_duration + max_duration) / 2, (max_duration - min_duration) / 4)
            delay = max(min_duration, min(max_duration, delay))
            time.sleep(delay)
            
            # 松开鼠标键
            if not self.send_serial_command(release_cmd, wait_ack=False):
                return False
            
            # 如果是多点击，点击之间的间隔也要随机，使用高斯分布
            if i < clicks - 1:
                interval = random.gauss(0.1, 0.02)
                interval = max(0.08, min(0.12, interval))  # 缩小范围，添加更自然的随机Jitter
                time.sleep(interval)
        
        self.logger(f"[调试] 已完成鼠标{button}键点击")
        return True
    
    def press_key(self, key, min_duration=0.05, max_duration=0.15, running=True):
        """处理单个按键的按下和释放，通过串口发送指令到Arduino
        :param key: 要按下的按键字符
        :param min_duration: 按键按下的最小时间
        :param max_duration: 按键按下的最大时间
        :param running: 运行状态标志
        """
        self.logger(f"[调试] 尝试按下按键: {key}")
        
        # 处理鼠标按键
        if key == 'mouse1':
            # 左键点击
            return self.click_mouse(button="left", clicks=1, min_duration=min_duration, max_duration=max_duration, running=running)
        elif key == 'mouse2':
            # 右键点击
            return self.click_mouse(button="right", clicks=1, min_duration=min_duration, max_duration=max_duration, running=running)
        
        # 处理键盘按键
        key_char = key.upper()  # 将按键转换为大写，与固件要求一致
        
        # 构造按下和松开的指令（文本格式）
        press_cmd = f"KEY_DOWN,{key_char}"
        release_cmd = f"KEY_UP,{key_char}"
        
        # 按下按键
        if not self.send_serial_command(press_cmd, wait_ack=False):
            return False
        
        # 随机延迟，模拟人类按键的不确定性，使用高斯分布
        delay = random.gauss((min_duration + max_duration) / 2, (max_duration - min_duration) / 4)
        delay = max(min_duration, min(max_duration, delay))
        time.sleep(delay)
        
        # 松开按键
        if not self.send_serial_command(release_cmd, wait_ack=False):
            return False
        
        # 按键之间的随机间隔，添加更自然的随机Jitter
        # 根据按键类型设置不同的随机范围，增强防封效果
        if key in ['mouse1', 'mouse2']:
            # 鼠标点击后间隔更大的随机范围
            interval = random.gauss(0.15, 0.05)
            interval = max(0.1, min(0.2, interval))
        elif key in ['w', 'a', 's', 'd']:
            # 移动按键后间隔较小的随机范围
            interval = random.gauss(0.075, 0.025)
            interval = max(0.05, min(0.1, interval))
        else:
            # 技能按键后间隔中等随机范围
            interval = random.gauss(0.125, 0.025)
            interval = max(0.1, min(0.15, interval))
        
        time.sleep(interval)
        
        self.logger(f"[调试] 已完成按键: {key}")
        return True
    
    def close(self):
        """关闭串口连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger("已关闭串口连接")