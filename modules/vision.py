import mss
import numpy as np
try:
    from . import config
except ImportError:
    import config

class Vision:
    """图像识别模块，负责所有与图像相关的检测功能"""
    
    def __init__(self, logger=None):
        """初始化视觉模块
        :param logger: 日志记录函数
        """
        self.logger = logger or self._default_logger
        self.sct = mss.mss()
        
    def _default_logger(self, message):
        """默认日志记录函数"""
        print(f"[Vision] {message}")
    
    def grab_screenshot(self, region):
        """截取指定区域的屏幕图像
        :param region: 区域坐标 (x, y, width, height)
        :return: RGB格式的图像数组
        """
        x, y, width, height = region
        monitor = {"top": y, "left": x, "width": width, "height": height}
        
        try:
            screenshot = np.array(self.sct.grab(monitor))
            # 转换为RGB格式（mss截图默认为BGRA）
            screenshot_rgb = screenshot[:, :, :3]  # 去掉alpha通道
            screenshot_rgb = screenshot_rgb[:, :, ::-1]  # BGR转RGB
            return screenshot_rgb
        except Exception as e:
            self.logger(f"[错误] 截图失败: {e}")
            return None
    
    def check_has_target(self):
        """检查当前是否有目标（使用图像识别检测目标血条）"""
        try:
            # 获取目标血条区域配置
            target_config = config.IMAGE_RECOGNITION['target_bar']
            region = target_config['region']
            
            # 截取目标血条区域
            screenshot_rgb = self.grab_screenshot(region)
            if screenshot_rgb is None:
                return True  # 出错时返回True，避免影响正常功能
            
            width = region[2]
            height = region[3]
            
            # 简单算法：检查目标血条区域是否有红色像素
            # 假设目标血条是红色的 (R>150, G<100, B<100)
            
            # 检查多个点，提高检测可靠性
            check_points = []
            for i in range(10):  # 检查10个点
                check_x = int(width * (0.1 + i * 0.08))  # 均匀分布在血条区域
                check_y = int(height / 2)  # 垂直方向取中间位置
                check_points.append((check_x, check_y))
            
            # 遍历检查点
            for (check_x, check_y) in check_points:
                if check_x < screenshot_rgb.shape[1] and check_y < screenshot_rgb.shape[0]:
                    r, g, b = screenshot_rgb[check_y, check_x]
                    # 检查是否为红色（目标血条颜色）
                    if r > 150 and g < 100 and b < 100:
                        self.logger("[调试] 检测到目标血条")
                        return True
            
            # 未检测到目标血条
            self.logger("[调试] 未检测到目标血条")
            return False
            
        except Exception as e:
            self.logger(f"[错误] 目标检测失败: {e}")
            # 出错时返回True，避免影响正常功能
            return True
    
    def check_health(self):
        """检查当前生命值（使用简单的像素颜色检测）"""
        try:
            # 获取血条区域配置
            hb_config = config.IMAGE_RECOGNITION['health_bar']
            region = hb_config['region']
            
            # 截取血条区域
            screenshot_rgb = self.grab_screenshot(region)
            if screenshot_rgb is None:
                return 0  # 出错时返回0%，触发保护机制
            
            # 简单算法：检查特定百分比位置的像素颜色
            # 假设血条是红色的 (R>150, G<100, B<100)
            img_width = screenshot_rgb.shape[1]
            img_height = screenshot_rgb.shape[0]
            
            # 检查点列表，从右到左检查（血条从左到右减少）
            check_points = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]  # 从90%到10%检查
            current_hp_pct = 0
            
            # 遍历检查点，找到第一个不是红色的位置
            for pct in check_points:
                # 计算检查点坐标（水平方向检查，垂直方向取中间位置）
                check_x = int(img_width * pct)
                check_y = int(img_height / 2)
                
                # 确保坐标在图像范围内
                if check_x < img_width and check_y < img_height:
                    # 获取像素颜色
                    r, g, b = screenshot_rgb[check_y, check_x]
                    
                    # 检查是否为红色（血条颜色）
                    if r > 150 and g < 100 and b < 100:
                        current_hp_pct = pct * 100
                        break
            
            # 确保生命值在0-100之间
            health_percentage = max(0, min(100, current_hp_pct))
            
            self.logger(f"[调试] 当前生命值: {health_percentage:.1f}%")
            return health_percentage
            
        except Exception as e:
            self.logger(f"[错误] 生命值检测失败: {e}")
            # 如果检测失败，返回0%触发保护机制
            return 0
    
    def detect_status(self):
        """检测当前状态效果"""
        # 简化实现：返回一个空列表
        # 在实际应用中，可以使用图像识别检测游戏界面上的状态图标
        return []
    
    def close(self):
        """关闭mss截图器"""
        self.sct.close()