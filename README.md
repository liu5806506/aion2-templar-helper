# 永恒之塔2 守护星辅助脚本

一个基于Python的模块化永恒之塔2守护星辅助脚本，支持配置化、防封机制和多职业扩展。

## 📁 项目结构

```
aion2-templar-helper/
│── main.py                # 主程序入口
│── main_new.py            # 模块化版本主程序
│── config.yaml            # YAML配置文件
│── requirements.txt       # 依赖库列表
│── README.md              # 项目说明
│
├── modules/               # 核心模块
│   ├── __init__.py
│   ├── config.py          # 配置加载工具
│   ├── controller.py      # Bot控制器
│   ├── hardware_input.py  # 硬件输入控制
│   ├── input.py           # 统一输入接口
│   ├── logic.py           # 战斗逻辑
│   ├── anti_detect.py     # 防封机制
│   ├── utils.py           # 工具函数
│   ├── vision.py          # 视觉识别
│   └── window_manager.py  # 窗口管理
│
├── tests/                 # 测试目录
│
└── logs/                  # 日志目录
```

## 🚀 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置技能与按键

编辑 `config.yaml` 文件，根据你的游戏设置配置技能、按键和其他参数：

```yaml
# 示例配置
sstarter:
  key: "3"  # 起手技能
  delay: 1.5

keys:
  select_target: "tab"  # 选怪键
  loot: "z"             # 拾取键
  auto_attack: "r"      # 普通攻击

skills:
  violent_strike:
    key: "mouse1"
    name: "猛烈一击"
    priority: 1
    cooldown: 0.5
```

### 3. 运行脚本

运行模块化版本：

```bash
python main_new.py
```

## ⚙️ 核心功能

### 1. 模块化架构
- **输入层**：统一的键盘/鼠标/Arduino HID接口
- **逻辑层**：技能释放策略、选怪逻辑、拾取逻辑
- **控制层**：启停管理、异常处理、日志记录
- **配置层**：YAML配置加载和验证

### 2. 防封机制
- 随机化技能延迟（高斯分布）
- 模拟人类行为：随机停顿、移动、取消技能
- 动态调整按键和点击延迟
- 多线程异步执行

### 3. 配置化设计
- 支持YAML配置文件
- 不同职业只需切换配置文件
- 可配置技能优先级、冷却时间、按键绑定
- 支持不同分辨率和游戏设置

### 4. 完善的日志系统
- 使用Python `logging` 库
- 日志分级：INFO、WARNING、ERROR
- 日志文件按日期滚动
- 详细的错误信息和调试信息

## 🎮 支持的功能

- ✅ 自动选怪（Tab键）
- ✅ 起手技能释放
- ✅ 自动卡刀（普通攻击+技能）
- ✅ 移动卡刀（走砍）
- ✅ 仇恨管理
- ✅ 自动使用防御技能
- ✅ 自动拾取
- ✅ 防封机制
- ✅ 状态监控
- ✅ 自动恢复

## 📝 配置说明

### 技能配置

在 `config.yaml` 中配置技能：

```yaml
skills:
  skill_name:
    key: "技能按键"
    name: "技能名称"
    priority: 1  # 优先级，数字越小优先级越高
    cooldown: 0.5  # 冷却时间（秒）
    delay: 0.25  # 技能释放延迟
    target_required: true  # 是否需要目标
    combos_with: ["other_skill"]  # 可连接的技能
```

### 延迟配置

```yaml
delays:
  between_skills: 1.2    # 技能间隔
  after_loot: 0.5        # 拾取后延迟
  find_target: 0.5       # 选怪频率
  loop: 0.5              # 主循环延迟
```

### 防封配置

```yaml
anti_detection:
  randomize_skill_delays: true   # 随机化技能延迟
  human_like_pauses: true        # 模拟人类停顿
  max_pause_duration: 0.5        # 最大停顿时间
  pause_probability: 0.1         # 停顿概率
  randomize_movement: true       # 随机化移动
  max_random_movement: 20        # 最大随机移动像素
  movement_probability: 0.05     # 随机移动概率
```

## 🛠️ 开发说明

### 添加新职业支持

1. 创建新的YAML配置文件（如 `gladiator.yaml`）
2. 配置该职业的技能、按键和参数
3. 修改 `main_new.py` 加载新的配置文件

### 扩展功能

1. 在 `modules/` 目录下创建新的模块
2. 在 `modules/__init__.py` 中导出新模块
3. 在 `main_new.py` 中使用新模块

## 📄 许可证

本项目仅供学习和研究使用，请勿用于任何违反游戏规则的行为。

## 🤝 贡献

欢迎提交Issue和Pull Request，一起完善这个项目。

## 📧 联系方式

如有问题或建议，请通过GitHub Issue联系我。
