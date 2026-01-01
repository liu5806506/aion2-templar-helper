import time
import config

class WindowManager:
    """窗口管理模块，负责激活和管理游戏窗口"""
    
    def __init__(self, logger=None):
        """初始化窗口管理模块
        :param logger: 日志记录函数
        """
        self.logger = logger or self._default_logger
        self.window_management_available = False
        self.win32gui = None
        self.win32con = None
        
        # 尝试导入窗口管理库
        try:
            import win32gui
            import win32con
            self.win32gui = win32gui
            self.win32con = win32con
            self.window_management_available = True
            self.logger("窗口管理库已成功导入")
        except ImportError:
            self.logger("警告: 窗口管理库未安装，将无法自动激活游戏窗口")
    
    def _default_logger(self, message):
        """默认日志记录函数"""
        print(f"[WindowManager] {message}")
    
    def activate_game_window(self):
        """激活游戏窗口"""
        if not self.window_management_available or not config.WINDOW_CONFIG['always_activate']:
            return
        
        try:
            def enum_windows_callback(hwnd, extra):
                window_text = self.win32gui.GetWindowText(hwnd)
                # 过滤掉输入法窗口和空窗口
                if window_text in ['Default IME', 'MSCTFIME UI', '']:
                    return
                
                # 不区分大小写，并且检查进程名称
                if ('AION2' in window_text.upper() or 'Aion2.exe' in window_text) and self.win32gui.IsWindowVisible(hwnd):
                    extra.append(hwnd)
                    self.logger(f"[调试] 匹配到游戏窗口: {window_text}")
            
            windows = []
            self.win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                game_hwnd = windows[0]
                window_title = self.win32gui.GetWindowText(game_hwnd)
                self.logger(f"[调试] 检测到游戏窗口: {window_title}")
                
                # 尝试获取窗口状态，不强制激活
                try:
                    # 获取窗口矩形，确认窗口存在
                    rect = self.win32gui.GetWindowRect(game_hwnd)
                    self.logger(f"[调试] 游戏窗口坐标: {rect}")
                    
                    # 只尝试一次温和的窗口激活，不强制
                    try:
                        self.win32gui.SetForegroundWindow(game_hwnd)
                        self.logger(f"[调试] 尝试激活游戏窗口成功: {window_title}")
                    except Exception as e:
                        self.logger(f"[提示] 无法自动激活游戏窗口: {e}")
                        self.logger(f"[提示] 请手动确保游戏窗口 '{window_title}' 在前台，然后按 f9 键开始")
                    
                    time.sleep(config.WINDOW_CONFIG['activation_delay'])
                except Exception as e:
                    self.logger(f"[错误] 获取游戏窗口信息失败: {e}")
            else:
                self.logger(f"[错误] 未找到包含 'AION2' 的游戏窗口")
                self.logger(f"[提示] 请确保游戏已启动，窗口标题包含 'AION2'")
        except Exception as e:
            self.logger(f"[错误] 窗口管理功能异常: {e}")