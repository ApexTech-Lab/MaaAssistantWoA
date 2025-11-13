# World of Airports 自动化 - 快速开始

## 🚀 5 分钟快速上手

### 步骤 1：环境检查

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 检查 ADB 是否可用
adb version

# 检查设备连接
adb devices
```

### 步骤 2：创建资源目录

```bash
# 在项目根目录执行
mkdir -p resource/woa/template
mkdir -p resource/woa/tasks
```

### 步骤 3：准备配置文件

创建 `resource/woa/config.json`（复制下面的内容）：

```json
{
    "version": "1.0",
    "options": {
        "taskDelay": 500,
        "controlDelayRange": [100, 300]
    },
    "connection": [
        {
            "configName": "General",
            "screencapEncode": "[Adb] -s [AdbSerial] exec-out screencap -p",
            "click": "[Adb] -s [AdbSerial] shell input tap [x] [y]",
            "swipe": "[Adb] -s [AdbSerial] shell input swipe [x1] [y1] [x2] [y2] [duration]"
        }
    ]
}
```

### 步骤 4：截取第一个模板

```bash
# 启动游戏到开始画面
# 使用 ADB 截图
adb exec-out screencap -p > start_screen.png

# 使用图像编辑器裁剪出"开始"按钮
# 保存为 resource/woa/template/WOA_StartButton.png
```

### 步骤 5：创建最简任务配置

创建 `resource/woa/tasks/tasks.json`：

```json
{
    "WOA_Start": {
        "algorithm": "JustReturn",
        "next": ["WOA_DetectStartScreen"]
    },

    "WOA_DetectStartScreen": {
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_StartButton.png",
        "roi": [400, 500, 480, 200],
        "threshold": 0.8,
        "next": ["Stop"],
        "maxTimes": 10,
        "postDelay": 2000
    }
}
```

### 步骤 6：运行测试

```bash
# 确保游戏在开始画面
python test_woa_automation.py --address 127.0.0.1:5555
```

---

## 📋 开发检查清单

### 第一次运行前

- [ ] Python 3.8+ 已安装
- [ ] ADB 已安装并可用
- [ ] 设备/模拟器已连接（adb devices 能看到）
- [ ] 游戏已安装并能正常运行
- [ ] 创建了 resource/woa 目录结构
- [ ] 创建了 config.json
- [ ] 至少有一个模板图片
- [ ] 创建了基础的 tasks.json

### 开发过程中

- [ ] 每添加一个新功能就测试一次
- [ ] 保存识别失败的截图用于调试
- [ ] 记录每个 ROI 的坐标
- [ ] 为复杂操作添加注释
- [ ] 定期备份配置文件

---

## 🎯 最小可行示例

以下是一个最简单但完整的示例，只实现"点击开始按钮"功能：

### 1. 目录结构

```
MaaAssistantWoA/
├── resource/
│   └── woa/
│       ├── config.json
│       ├── tasks/
│       │   └── tasks.json
│       └── template/
│           └── WOA_StartButton.png
├── test_woa_automation.py
└── WOA_QUICKSTART.md (本文件)
```

### 2. config.json（最小配置）

```json
{
    "version": "1.0",
    "options": {
        "taskDelay": 500
    },
    "connection": [
        {
            "configName": "General",
            "click": "[Adb] -s [AdbSerial] shell input tap [x] [y]",
            "screencapEncode": "[Adb] -s [AdbSerial] exec-out screencap -p"
        }
    ]
}
```

### 3. tasks.json（最小任务）

```json
{
    "WOA_Start": {
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_StartButton.png",
        "roi": [0, 0, 1280, 720],
        "threshold": 0.75,
        "next": ["Stop"]
    }
}
```

### 4. 运行

```bash
python test_woa_automation.py
```

如果能成功点击开始按钮，说明基础框架已经工作！

---

## 🔧 常见问题快速解决

### 问题：找不到设备

```bash
# 检查设备连接
adb devices

# 如果没有设备，尝试重启 ADB
adb kill-server
adb start-server
adb devices

# 如果是模拟器，确保已启动并等待几秒
```

### 问题：模板识别不到

```bash
# 1. 检查模板文件是否存在
ls resource/woa/template/WOA_StartButton.png

# 2. 降低阈值
# 在 tasks.json 中将 threshold 从 0.8 改为 0.7 或 0.6

# 3. 扩大 ROI 范围
# 将 roi 改为全屏 [0, 0, 1280, 720]

# 4. 重新截图制作模板
adb exec-out screencap -p > new_screenshot.png
```

### 问题：Python 找不到 asst 模块

```bash
# 确保路径正确
# 检查 src/Python 目录是否存在
ls src/Python/asst/

# 如果不存在，可能需要使用已编译的版本
# 或者手动设置 PYTHONPATH
export PYTHONPATH=/path/to/MaaAssistantWoA/src/Python:$PYTHONPATH
```

### 问题：任务执行太快/太慢

```bash
# 修改 config.json 中的延迟
{
    "taskDelay": 500,  # 增加这个值会变慢
    "controlDelayRange": [200, 500]  # 增加点击延迟
}

# 修改 tasks.json 中的 postDelay
{
    "postDelay": 2000  # 每个任务后等待 2 秒
}
```

---

## 📚 下一步

完成快速开始后，查看完整文档：

1. **详细指南**：`docs/WOA_ADAPTATION_GUIDE.md`
   - 完整的开发流程
   - 高级配置选项
   - 调试技巧

2. **任务配置**：逐步添加更多功能
   - 进入游戏
   - 切换机场
   - 处理飞机

3. **优化**：提高识别准确性和执行速度
   - 优化 ROI
   - 调整阈值
   - 添加容错机制

---

## 💡 提示

- **从简单开始**：先让一个按钮识别成功，再添加复杂流程
- **小步快跑**：每添加一个任务就测试一次
- **保存截图**：遇到问题时截图很有用
- **查看日志**：运行后会生成 `woa_automation.log`，包含详细信息
- **耐心调试**：图像识别需要反复调整参数才能达到最佳效果

---

## 🎓 学习路径

### 第 1 天：基础识别
- [ ] 完成环境搭建
- [ ] 成功识别并点击一个按钮
- [ ] 理解 ROI 和 threshold 的作用

### 第 2-3 天：简单流程
- [ ] 实现开始→进入游戏流程
- [ ] 学会使用 next 和 on_error_next
- [ ] 添加延迟和重试机制

### 第 4-7 天：核心功能
- [ ] 实现机场选择
- [ ] 实现飞机处理基本流程
- [ ] 学会使用 Swipe 动作

### 第 8-10 天：完善和优化
- [ ] 添加异常处理
- [ ] 优化识别准确性
- [ ] 提高执行速度

---

## ✅ 成功标志

当你能做到以下几点时，说明你已经掌握了基础：

- ✅ 能够截图并制作模板
- ✅ 理解 tasks.json 的配置方式
- ✅ 能够调试识别失败的问题
- ✅ 实现了至少一个完整的功能流程

祝你开发顺利！如果遇到问题，查看详细指南或检查日志文件。🚀
