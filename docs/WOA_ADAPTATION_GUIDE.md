# World of Airports 自动化脚本开发指南

基于 MaaAssistantWoA 框架改造

---

## 📋 目录

1. [项目概述](#项目概述)
2. [环境准备](#环境准备)
3. [开发步骤](#开发步骤)
4. [配置文件编写](#配置文件编写)
5. [图像模板制作](#图像模板制作)
6. [任务流程设计](#任务流程设计)
7. [代码修改指南](#代码修改指南)
8. [测试和调试](#测试和调试)
9. [常见问题](#常见问题)

---

## 📖 项目概述

### 目标功能

开发一个 World of Airports 游戏自动化脚本，实现以下功能：

1. ✅ 识别开始画面并进入游戏
2. ✅ 依次进入已解锁的每个机场
3. ✅ 自动处理飞机：
   - 选择机位
   - 准许降落
   - 开始处理/分配地勤（滑动进度条到最大）
   - 推出机位
   - 准许起飞
4. ✅ 特殊操作：穿越跑道许可、除冰等

### 架构适配方案

**保留的核心模块：**
- ✅ `MaaCore/Controller/` - 设备控制（ADB、截图、点击、滑动）
- ✅ `MaaCore/Vision/` - 图像识别（模板匹配、OCR）
- ✅ `MaaCore/Task/ProcessTask` - 流程任务执行
- ✅ `MaaCore/Config/` - 配置管理
- ✅ `include/AsstCaller.h` - API 接口

**需要修改的部分：**
- ❌ 删除明日方舟特定的业务任务（基建、公招、肉鸽等）
- ➕ 添加 WOA 特定任务（机场管理、飞机处理）
- ➕ 创建 WOA 资源文件（图像模板、任务配置）
- ➕ 编写 WOA 任务流程 JSON

---

## 🛠️ 环境准备

### 1. 开发环境要求

#### Windows 环境
```bash
# 必需软件
- Visual Studio 2022 (C++20 支持)
- CMake 3.21+
- Git
- Python 3.8+ (用于辅助工具)

# 依赖库（通过 vcpkg 安装）
- OpenCV 4.x
- Boost
- zlib
```

#### Linux/macOS 环境
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential cmake git
sudo apt install libopencv-dev libboost-all-dev

# macOS
brew install cmake opencv boost
```

### 2. 模拟器/设备准备

```bash
# 推荐使用的模拟器
- BlueStacks 5
- MuMu 模拟器 12
- 夜神模拟器
- 或真实 Android 设备（开启 USB 调试）

# ADB 安装
Windows: 下载 Android SDK Platform Tools
Linux: sudo apt install adb
macOS: brew install android-platform-tools

# 测试 ADB 连接
adb devices
```

### 3. 辅助工具准备

```bash
# 截图工具
- Windows: Snipping Tool / Snipaste
- macOS: Command + Shift + 4
- 推荐：使用 ADB 直接截图（保证分辨率一致）

# 图像编辑工具
- Photoshop / GIMP / Paint.NET
- 在线工具：photopea.com

# JSON 编辑器
- VS Code（推荐，支持 JSON Schema 验证）
- Sublime Text
- Notepad++
```

---

## 📝 开发步骤

### 步骤 1：项目 Fork 和初始化

#### 1.1 克隆项目

```bash
# 克隆原项目
git clone https://github.com/MaaAssistantArknights/MaaAssistantArknights.git
cd MaaAssistantArknights

# 重命名项目（可选）
cd ..
mv MaaAssistantArknights MaaAssistantWOA
cd MaaAssistantWOA

# 创建新分支
git checkout -b woa-adaptation
```

#### 1.2 创建项目结构

```bash
# 创建 WOA 专用目录
mkdir -p resource/woa/template
mkdir -p resource/woa/tasks
mkdir -p docs/woa

# 创建配置文件
touch resource/woa/config.json
touch resource/woa/tasks/tasks.json
```

---

### 步骤 2：清理不需要的代码（简化方式）

**推荐方式：不删除原代码，只添加新功能**

为了保持项目稳定性，建议采用"添加式开发"：

```bash
# 保留所有原有代码
# 只在 InterfaceTask 目录下添加新的 WOA 任务类
```

创建新任务类：

```cpp
// src/MaaCore/Task/Interface/WOAAirportTask.h
#pragma once
#include "InterfaceTask.h"

namespace asst
{
class WOAAirportTask : public InterfaceTask
{
public:
    using InterfaceTask::InterfaceTask;
    virtual ~WOAAirportTask() override = default;

    virtual bool _run() override;

private:
    bool process_start_screen();
    bool enter_airports();
    bool process_aircraft();
    bool handle_aircraft_steps();
};
}
```

---

### 步骤 3：制作图像模板

#### 3.1 使用 ADB 截取游戏画面

```bash
# 确保设备已连接
adb devices

# 截取当前屏幕
adb exec-out screencap -p > screenshot.png

# 或使用项目提供的工具
# tools/ImageCoordinate/ 可以帮助获取坐标
```

#### 3.2 截取关键元素模板

**需要截取的元素：**

| 元素名称 | 用途 | 建议尺寸 |
|---------|------|---------|
| `start_button.png` | 开始画面的进入按钮 | 实际大小 |
| `airport_icon.png` | 机场图标（用于识别机场列表） | 50x50+ |
| `aircraft_icon.png` | 飞机图标 | 实际大小 |
| `landing_button.png` | "准许降落"按钮 | 实际大小 |
| `processing_button.png` | "开始处理"按钮 | 实际大小 |
| `pushback_button.png` | "推出机位"按钮 | 实际大小 |
| `takeoff_button.png` | "准许起飞"按钮 | 实际大小 |
| `runway_crossing.png` | "穿越跑道"按钮 | 实际大小 |
| `deicing_button.png` | "除冰"按钮 | 实际大小 |
| `staff_slider.png` | 地勤滑动条识别点 | 实际大小 |

#### 3.3 模板制作技巧

```bash
# 1. 使用 Photoshop/GIMP 打开截图
# 2. 使用矩形选择工具选中按钮区域
# 3. 裁剪并保存为 PNG（保留透明度）
# 4. 确保模板清晰，没有背景干扰

# 模板命名规范
WOA_StartButton.png
WOA_AirportIcon_Locked.png
WOA_AirportIcon_Unlocked.png
WOA_Aircraft_Waiting.png
WOA_Landing_Button.png
WOA_Processing_Button.png
WOA_Pushback_Button.png
WOA_Takeoff_Button.png
WOA_RunwayCrossing_Button.png
WOA_Deicing_Button.png
WOA_StaffSlider_Max.png
```

#### 3.4 保存模板

```bash
# 将所有模板保存到
resource/woa/template/

# 建议按功能分类
resource/woa/template/ui/       # UI 元素
resource/woa/template/aircraft/ # 飞机相关
resource/woa/template/airport/  # 机场相关
```

---

### 步骤 4：编写任务配置 JSON

#### 4.1 创建基础任务配置

创建 `resource/woa/tasks/tasks.json`：

```json
{
    "_comment": "World of Airports 自动化任务配置",

    "WOA_Start": {
        "Doc": "启动任务入口",
        "algorithm": "JustReturn",
        "action": "DoNothing",
        "next": ["WOA_DetectStartScreen"]
    },

    "WOA_DetectStartScreen": {
        "Doc": "检测开始画面",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_StartButton.png",
        "roi": [400, 500, 480, 200],
        "threshold": 0.8,
        "next": ["WOA_WaitGameLoad"],
        "on_error_next": ["WOA_DetectStartScreen"],
        "maxTimes": 10,
        "postDelay": 2000
    },

    "WOA_WaitGameLoad": {
        "Doc": "等待游戏加载",
        "algorithm": "MatchTemplate",
        "template": "WOA_MainScreen.png",
        "roi": [0, 0, 1280, 720],
        "threshold": 0.75,
        "next": ["WOA_EnterAirportList"],
        "on_error_next": ["WOA_WaitGameLoad"],
        "maxTimes": 30,
        "postDelay": 1000
    },

    "WOA_EnterAirportList": {
        "Doc": "进入机场列表",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_AirportListButton.png",
        "roi": [0, 0, 200, 720],
        "threshold": 0.8,
        "next": ["WOA_SelectFirstAirport"],
        "postDelay": 1000
    },

    "WOA_SelectFirstAirport": {
        "Doc": "选择第一个机场",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_AirportIcon_Unlocked.png",
        "roi": [50, 100, 300, 600],
        "threshold": 0.7,
        "next": ["WOA_ProcessAircrafts"],
        "postDelay": 1500
    },

    "WOA_ProcessAircrafts": {
        "Doc": "处理所有飞机",
        "algorithm": "JustReturn",
        "action": "DoNothing",
        "next": ["WOA_FindWaitingAircraft"]
    },

    "WOA_FindWaitingAircraft": {
        "Doc": "查找等待处理的飞机",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Aircraft_Waiting.png",
        "roi": [200, 100, 880, 520],
        "threshold": 0.75,
        "next": ["WOA_SelectGate"],
        "on_error_next": ["WOA_NextAirport"],
        "maxTimes": 20,
        "postDelay": 500
    },

    "WOA_SelectGate": {
        "Doc": "选择机位",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Gate_Available.png",
        "roi": [200, 100, 880, 520],
        "threshold": 0.7,
        "next": ["WOA_ConfirmLanding"],
        "postDelay": 800
    },

    "WOA_ConfirmLanding": {
        "Doc": "准许降落",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Landing_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.8,
        "next": ["WOA_WaitLanding"],
        "postDelay": 1000
    },

    "WOA_WaitLanding": {
        "Doc": "等待飞机降落",
        "algorithm": "MatchTemplate",
        "template": "WOA_Processing_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.75,
        "next": ["WOA_CheckRunwayCrossing"],
        "on_error_next": ["WOA_WaitLanding"],
        "maxTimes": 60,
        "postDelay": 2000
    },

    "WOA_CheckRunwayCrossing": {
        "Doc": "检查是否需要穿越跑道许可",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_RunwayCrossing_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.8,
        "next": ["WOA_StartProcessing"],
        "on_error_next": ["WOA_StartProcessing"],
        "maxTimes": 1,
        "postDelay": 500
    },

    "WOA_StartProcessing": {
        "Doc": "开始处理/分配地勤",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Processing_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.8,
        "next": ["WOA_AdjustStaffSlider"],
        "postDelay": 800
    },

    "WOA_AdjustStaffSlider": {
        "Doc": "滑动地勤进度条到最大",
        "algorithm": "MatchTemplate",
        "action": "Swipe",
        "template": "WOA_StaffSlider_Handle.png",
        "roi": [400, 300, 480, 200],
        "threshold": 0.7,
        "specificRect": [640, 400, 50, 50],
        "rectMove": [950, 400, 50, 50],
        "specialParams": [300, 0, 1, 1],
        "next": ["WOA_ConfirmStaff"],
        "postDelay": 500
    },

    "WOA_ConfirmStaff": {
        "Doc": "确认地勤分配",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Confirm_Button.png",
        "roi": [800, 550, 400, 150],
        "threshold": 0.8,
        "next": ["WOA_WaitProcessingComplete"],
        "postDelay": 1000
    },

    "WOA_WaitProcessingComplete": {
        "Doc": "等待处理完成",
        "algorithm": "MatchTemplate",
        "template": "WOA_Pushback_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.75,
        "next": ["WOA_CheckDeicing"],
        "on_error_next": ["WOA_WaitProcessingComplete"],
        "maxTimes": 120,
        "postDelay": 3000
    },

    "WOA_CheckDeicing": {
        "Doc": "检查是否需要除冰",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Deicing_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.8,
        "next": ["WOA_PushbackAircraft"],
        "on_error_next": ["WOA_PushbackAircraft"],
        "maxTimes": 1,
        "postDelay": 1000
    },

    "WOA_PushbackAircraft": {
        "Doc": "推出机位",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Pushback_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.8,
        "next": ["WOA_WaitPushbackComplete"],
        "postDelay": 1000
    },

    "WOA_WaitPushbackComplete": {
        "Doc": "等待推出完成",
        "algorithm": "MatchTemplate",
        "template": "WOA_Takeoff_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.75,
        "next": ["WOA_ConfirmTakeoff"],
        "on_error_next": ["WOA_WaitPushbackComplete"],
        "maxTimes": 60,
        "postDelay": 2000
    },

    "WOA_ConfirmTakeoff": {
        "Doc": "准许起飞",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_Takeoff_Button.png",
        "roi": [800, 500, 400, 180],
        "threshold": 0.8,
        "next": ["WOA_FindWaitingAircraft"],
        "postDelay": 1000
    },

    "WOA_NextAirport": {
        "Doc": "进入下一个机场",
        "algorithm": "JustReturn",
        "action": "DoNothing",
        "next": ["WOA_BackToAirportList"]
    },

    "WOA_BackToAirportList": {
        "Doc": "返回机场列表",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_BackButton.png",
        "roi": [0, 0, 150, 100],
        "threshold": 0.8,
        "next": ["WOA_SelectNextAirport"],
        "postDelay": 1000
    },

    "WOA_SelectNextAirport": {
        "Doc": "选择下一个机场（向下滑动查找）",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "WOA_AirportIcon_Unlocked.png",
        "roi": [50, 100, 300, 600],
        "threshold": 0.7,
        "next": ["WOA_ProcessAircrafts"],
        "on_error_next": ["WOA_ScrollAirportList"],
        "postDelay": 1500
    },

    "WOA_ScrollAirportList": {
        "Doc": "滚动机场列表",
        "algorithm": "JustReturn",
        "action": "Swipe",
        "specificRect": [150, 500, 50, 50],
        "rectMove": [150, 200, 50, 50],
        "specialParams": [200, 0, 1, 1],
        "next": ["WOA_SelectNextAirport"],
        "on_error_next": ["WOA_AllAirportsComplete"],
        "maxTimes": 5,
        "postDelay": 500
    },

    "WOA_AllAirportsComplete": {
        "Doc": "所有机场处理完成",
        "algorithm": "JustReturn",
        "action": "DoNothing",
        "next": ["Stop"]
    }
}
```

#### 4.2 JSON 配置参数说明

| 参数 | 说明 | 示例值 |
|-----|------|--------|
| `algorithm` | 识别算法 | `MatchTemplate`(模板匹配), `OcrDetect`(OCR), `JustReturn`(直接返回) |
| `action` | 执行动作 | `Click`(点击), `Swipe`(滑动), `DoNothing`(无操作) |
| `template` | 模板图片路径 | `WOA_StartButton.png` |
| `roi` | 识别区域 [x, y, w, h] | `[400, 500, 480, 200]` |
| `threshold` | 匹配阈值 (0-1) | `0.8` (越高越严格) |
| `next` | 成功后的下一个任务 | `["NextTask"]` |
| `on_error_next` | 失败后的下一个任务 | `["ErrorTask"]` |
| `exceeded_next` | 超次数后的任务 | `["ExceededTask"]` |
| `maxTimes` | 最大尝试次数 | `10` |
| `postDelay` | 执行后延迟(毫秒) | `1000` |
| `specificRect` | 滑动起点 [x, y, w, h] | `[640, 400, 50, 50]` |
| `rectMove` | 滑动终点 [x, y, w, h] | `[950, 400, 50, 50]` |
| `specialParams` | 滑动参数 [duration, extra, slope_in, slope_out] | `[300, 0, 1, 1]` |

---

### 步骤 5：修改配置文件

创建 `resource/woa/config.json`：

```json
{
    "version": "1.0",
    "options": {
        "taskDelay": 500,
        "taskDelay_Doc": "识别延迟(毫秒)，越快CPU消耗越大",
        "controlDelayRange": [100, 300],
        "controlDelayRange_Doc": "点击随机延迟范围[最小, 最大]，模拟人类操作",
        "adbExtraSwipeDist": 100,
        "adbExtraSwipeDuration": 500,
        "adbSwipeDurationMultiplier": 10.0,
        "debug": {
            "cleanFilesFreq": 50,
            "maxDebugFileNum": 100
        }
    },
    "packageName": {
        "WorldOfAirports": "com.paradyme.woa"
    },
    "connection": [
        {
            "configName": "General",
            "devices": "[Adb] devices",
            "addressRegex": "(.+)\tdevice",
            "connect": "[Adb] connect [AdbSerial]",
            "uuid": "[Adb] -s [AdbSerial] shell settings get secure android_id",
            "display": "[Adb] -s [AdbSerial] shell \"wm size | tail -n 1 | grep -o -E [0-9]+\"",
            "screencapRawWithGzip": "[Adb] -s [AdbSerial] exec-out \"screencap | gzip -1\"",
            "screencapEncode": "[Adb] -s [AdbSerial] exec-out screencap -p",
            "click": "[Adb] -s [AdbSerial] shell input tap [x] [y]",
            "swipe": "[Adb] -s [AdbSerial] shell input swipe [x1] [y1] [x2] [y2] [duration]",
            "start": "[Adb] -s [AdbSerial] shell am start -n com.paradyme.woa/.MainActivity",
            "stop": "[Adb] -s [AdbSerial] shell am force-stop com.paradyme.woa"
        }
    ]
}
```

---

### 步骤 6：编译项目（可选）

如果只是测试任务流程，可以使用现有的编译好的版本。如果需要修改 C++ 代码：

```bash
# Windows (Visual Studio)
mkdir build
cd build
cmake -A x64 ..
cmake --build . --config Release

# Linux/macOS
mkdir build
cd build
cmake ..
make -j$(nproc)
```

---

### 步骤 7：使用 Python 接口测试

创建测试脚本 `test_woa.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path

# 添加 MAA Python 接口路径
sys.path.append(str(Path(__file__).parent / 'src' / 'Python'))

from asst import Asst, Message

# 回调函数
def callback(msg, details, arg):
    msg_type = Message(msg)
    detail = json.loads(details)

    print(f"[{msg_type.name}] {detail}")

    if msg_type == Message.SubTaskCompleted:
        print(f"✅ 子任务完成: {detail.get('subtask', 'Unknown')}")
    elif msg_type == Message.SubTaskError:
        print(f"❌ 子任务错误: {detail.get('why', 'Unknown')}")

# 主函数
def main():
    # 初始化 MAA
    asst = Asst(callback=callback)

    # 加载 WOA 资源
    resource_path = Path(__file__).parent / 'resource' / 'woa'
    if not asst.load_resource(str(resource_path)):
        print("❌ 资源加载失败")
        return False

    # 连接设备
    adb_path = "adb"  # 或指定完整路径
    address = "127.0.0.1:5555"  # 模拟器地址
    config = "General"

    print(f"🔗 连接设备: {address}")
    if not asst.connect(adb_path, address, config):
        print("❌ 设备连接失败")
        return False

    print("✅ 设备连接成功")

    # 添加 WOA 任务
    task_params = {
        "task_names": ["WOA_Start"]
    }

    task_id = asst.append_task("ProcessTask", task_params)
    if task_id == 0:
        print("❌ 任务添加失败")
        return False

    print(f"✅ 任务添加成功 (ID: {task_id})")

    # 开始执行
    print("🚀 开始执行任务...")
    asst.start()

    print("✅ 任务执行完成")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

运行测试：

```bash
python test_woa.py
```

---

## 🔧 配置文件编写详解

### ROI (Region of Interest) 配置技巧

**ROI 是识别的关键，配置不当会导致识别失败或识别到错误的目标。**

#### 如何确定 ROI

1. **使用 ADB 截图**
```bash
adb exec-out screencap -p > full_screen.png
```

2. **使用图像编辑器打开**
   - 鼠标悬停在目标区域
   - 记录坐标 (x, y)
   - 测量宽度和高度 (w, h)

3. **ROI 格式**
```json
"roi": [x, y, w, h]
// x: 左上角 X 坐标
// y: 左上角 Y 坐标
// w: 宽度
// h: 高度
```

#### ROI 配置示例

```json
{
    "WOA_DetectStartScreen": {
        "template": "WOA_StartButton.png",
        "roi": [400, 500, 480, 200],
        "roi_Doc": "屏幕中下部分，开始按钮通常在这里"
    },

    "WOA_AirportIcon": {
        "template": "WOA_AirportIcon.png",
        "roi": [50, 100, 300, 600],
        "roi_Doc": "屏幕左侧，机场列表区域"
    },

    "WOA_ActionButtons": {
        "template": "WOA_Landing_Button.png",
        "roi": [800, 500, 400, 180],
        "roi_Doc": "屏幕右下角，操作按钮区域"
    }
}
```

### 滑动操作配置详解

**滑动地勤进度条到最大的配置：**

```json
{
    "WOA_AdjustStaffSlider": {
        "algorithm": "MatchTemplate",
        "action": "Swipe",
        "template": "WOA_StaffSlider_Handle.png",
        "roi": [400, 300, 480, 200],
        "threshold": 0.7,

        "specificRect": [640, 400, 50, 50],
        "specificRect_Doc": "滑动起点：滑块当前位置或左端点",

        "rectMove": [950, 400, 50, 50],
        "rectMove_Doc": "滑动终点：滑块最右端位置",

        "specialParams": [300, 0, 1, 1],
        "specialParams_Doc": [
            "duration: 滑动持续时间(毫秒)，建议200-500",
            "extra_swipe: 额外滑动修正，0=不修正",
            "slope_in: 起始加速度，1=线性，2=加速",
            "slope_out: 结束加速度，1=线性，0=减速"
        ],

        "next": ["WOA_ConfirmStaff"],
        "postDelay": 500
    }
}
```

**如何确定滑动参数：**

1. **确定滑块位置**
   - 截图显示滑块的画面
   - 记录滑块最左端坐标 (x1, y1)
   - 记录滑块最右端坐标 (x2, y2)

2. **配置滑动**
```json
"specificRect": [x1, y1, 50, 50],  // 起点
"rectMove": [x2, y2, 50, 50],       // 终点
"specialParams": [300, 0, 1, 1]     // 持续300毫秒，线性滑动
```

3. **测试和调整**
   - 如果滑不到头：增大 x2
   - 如果滑过头：减小 x2
   - 如果太快：增大 duration
   - 如果不流畅：调整 slope 参数

---

## 🎨 图像模板制作详解

### 模板制作最佳实践

#### 1. 截图规范

```bash
# 使用 ADB 截图（推荐，保证分辨率一致）
adb exec-out screencap -p > screenshot.png

# 确保游戏分辨率固定
# 建议使用：1280x720 或 1920x1080
```

#### 2. 模板裁剪技巧

**✅ 好的模板：**
- 包含独特的视觉特征
- 边界清晰
- 没有背景干扰
- 不包含动态元素（如动画、进度条）

**❌ 坏的模板：**
- 背景复杂
- 包含半透明元素
- 包含文字但文字会变化
- 太小（小于 20x20）

#### 3. 模板裁剪步骤

**使用 Photoshop/GIMP：**

1. 打开截图
2. 选择矩形选择工具 (M)
3. 选中目标按钮/图标
4. 裁剪 (Crop) 或复制到新图层
5. 保存为 PNG（保留透明度）

**使用在线工具：**

1. 访问 https://www.photopea.com/
2. 上传截图
3. 使用裁剪工具
4. 导出 PNG

#### 4. 多状态模板

有些元素有多种状态，需要分别制作模板：

```
WOA_Gate_Available.png      # 可用机位（绿色）
WOA_Gate_Occupied.png        # 占用机位（红色）
WOA_Aircraft_Waiting.png     # 等待中的飞机
WOA_Aircraft_Processing.png  # 处理中的飞机
```

在配置中分别使用：

```json
{
    "WOA_FindAvailableGate": {
        "template": "WOA_Gate_Available.png",
        "threshold": 0.75
    },

    "WOA_CheckGateOccupied": {
        "template": "WOA_Gate_Occupied.png",
        "threshold": 0.75
    }
}
```

---

## 🔍 测试和调试

### 调试模式

#### 1. 启用调试日志

修改 `test_woa.py`：

```python
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# MAA 内部也会输出日志
```

#### 2. 保存识别结果截图

在 `config.json` 中配置：

```json
{
    "options": {
        "debug": {
            "saveScreenshot": true,
            "screenshotPath": "debug/screenshots/",
            "cleanFilesFreq": 50,
            "maxDebugFileNum": 100
        }
    }
}
```

识别失败时会自动保存截图到 `debug/screenshots/` 目录。

#### 3. 逐步测试

**测试单个任务：**

```python
# 只测试开始画面识别
task_params = {
    "task_names": ["WOA_DetectStartScreen"]
}
task_id = asst.append_task("ProcessTask", task_params)
asst.start()
```

**测试部分流程：**

```python
# 只测试飞机处理流程（假设已进入机场）
task_params = {
    "task_names": ["WOA_ProcessAircrafts"]
}
task_id = asst.append_task("ProcessTask", task_params)
asst.start()
```

### 常见问题排查

#### 问题 1：模板识别失败

**症状：** 日志显示 "未找到匹配"

**排查步骤：**

1. **检查 ROI 是否正确**
```bash
# 使用工具验证坐标
python tools/ImageCoordinate/image_coordinate.py
```

2. **降低阈值**
```json
"threshold": 0.8  →  "threshold": 0.7
```

3. **重新制作模板**
   - 确保模板清晰
   - 去除背景干扰
   - 裁剪更大的区域

4. **使用多模板**
```json
{
    "template": ["WOA_Button_1.png", "WOA_Button_2.png"],
    "threshold": [0.8, 0.75]
}
```

#### 问题 2：点击位置不准

**症状：** 点击了错误的位置

**解决方案：**

1. **检查 ROI 和点击区域**
```json
{
    "roi": [800, 500, 400, 180],
    "action": "Click",
    "target": [950, 590, 50, 50]  // 可选：指定点击位置
}
```

2. **使用相对坐标**
```json
{
    "action": "ClickSelf",  // 点击识别到的位置中心
}
```

#### 问题 3：滑动不到位

**症状：** 滑块没有滑到最大

**解决方案：**

1. **增加滑动终点坐标**
```json
"rectMove": [950, 400, 50, 50]  →  "rectMove": [1000, 400, 50, 50]
```

2. **增加滑动持续时间**
```json
"specialParams": [300, 0, 1, 1]  →  "specialParams": [500, 0, 1, 1]
```

3. **多次滑动**
```json
{
    "WOA_AdjustStaffSlider_Step1": {
        "action": "Swipe",
        "specificRect": [640, 400, 50, 50],
        "rectMove": [950, 400, 50, 50],
        "next": ["WOA_AdjustStaffSlider_Step2"]
    },
    "WOA_AdjustStaffSlider_Step2": {
        "action": "Swipe",
        "specificRect": [950, 400, 50, 50],
        "rectMove": [1100, 400, 50, 50],
        "next": ["WOA_ConfirmStaff"]
    }
}
```

#### 问题 4：任务执行太快或太慢

**解决方案：**

调整延迟参数：

```json
{
    "taskDelay": 500,           // 全局识别延迟
    "postDelay": 1000,          // 单个任务执行后延迟
    "controlDelayRange": [100, 300]  // 点击随机延迟
}
```

---

## 📊 完整流程图

```
开始
  ↓
WOA_DetectStartScreen (识别开始画面)
  ↓
WOA_WaitGameLoad (等待加载)
  ↓
WOA_EnterAirportList (进入机场列表)
  ↓
WOA_SelectFirstAirport (选择第一个机场)
  ↓
┌─────────────────────────────────────┐
│ WOA_ProcessAircrafts (处理所有飞机)  │
│   ↓                                  │
│ WOA_FindWaitingAircraft (查找飞机)   │
│   ↓                                  │
│ WOA_SelectGate (选择机位)            │
│   ↓                                  │
│ WOA_ConfirmLanding (准许降落)        │
│   ↓                                  │
│ WOA_WaitLanding (等待降落)           │
│   ↓                                  │
│ WOA_CheckRunwayCrossing (穿越跑道?)  │
│   ↓                                  │
│ WOA_StartProcessing (开始处理)       │
│   ↓                                  │
│ WOA_AdjustStaffSlider (滑动进度条)   │
│   ↓                                  │
│ WOA_ConfirmStaff (确认地勤)          │
│   ↓                                  │
│ WOA_WaitProcessingComplete (等待)    │
│   ↓                                  │
│ WOA_CheckDeicing (除冰?)             │
│   ↓                                  │
│ WOA_PushbackAircraft (推出机位)      │
│   ↓                                  │
│ WOA_WaitPushbackComplete (等待推出)  │
│   ↓                                  │
│ WOA_ConfirmTakeoff (准许起飞)        │
│   ↓                                  │
│ 返回 WOA_FindWaitingAircraft ────────┘
  ↓ (没有更多飞机)
WOA_NextAirport (下一个机场)
  ↓
WOA_BackToAirportList (返回列表)
  ↓
WOA_SelectNextAirport (选择下一个)
  ↓
返回 WOA_ProcessAircrafts
  ↓ (所有机场完成)
WOA_AllAirportsComplete
  ↓
结束
```

---

## 🚀 快速开始清单

### 第一次运行前的准备

- [ ] 1. 安装 ADB 并测试连接
- [ ] 2. 确保游戏运行在固定分辨率（1280x720 推荐）
- [ ] 3. 截取游戏画面并制作至少 10 个关键模板
- [ ] 4. 编写基础 tasks.json（至少包含开始画面识别）
- [ ] 5. 创建 Python 测试脚本
- [ ] 6. 测试开始画面识别
- [ ] 7. 逐步添加后续任务流程
- [ ] 8. 完整测试并调整参数

### 推荐的开发顺序

1. **第 1 天：环境搭建**
   - 安装工具
   - 配置 ADB
   - 克隆项目

2. **第 2-3 天：模板制作**
   - 截取所有关键画面
   - 制作图像模板
   - 组织文件结构

3. **第 4-5 天：基础流程**
   - 编写开始→进入游戏流程
   - 测试机场列表识别
   - 测试机场切换

4. **第 6-8 天：核心功能**
   - 编写飞机处理完整流程
   - 测试每个步骤
   - 调整识别参数

5. **第 9-10 天：优化和测试**
   - 完整流程测试
   - 错误处理
   - 性能优化

---

## 📚 参考资料

### MAA 官方文档

- [任务流程协议](https://docs.maa.plus/zh-cn/protocol/task-schema.html)
- [集成文档](https://docs.maa.plus/zh-cn/protocol/integration.html)
- [开发指南](https://docs.maa.plus/zh-cn/develop/development.html)

### OpenCV 模板匹配

- [matchTemplate 文档](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
- [ROI 选择指南](https://docs.opencv.org/4.x/d0/d86/tutorial_py_image_arithmetics.html)

### ADB 命令参考

```bash
# 常用命令
adb devices              # 列出设备
adb connect IP:PORT      # 连接设备
adb shell input tap X Y  # 点击
adb shell input swipe X1 Y1 X2 Y2 DURATION  # 滑动
adb exec-out screencap -p > image.png  # 截图
```

---

## ✅ 总结

通过本指南，你应该能够：

1. ✅ 理解 MAA 框架的核心架构
2. ✅ 掌握图像模板制作技巧
3. ✅ 编写任务流程配置 JSON
4. ✅ 使用 Python 接口测试和运行
5. ✅ 调试和解决常见问题
6. ✅ 开发完整的 WOA 自动化脚本

**关键要点：**

- 📸 模板质量是识别成功的关键
- 🎯 ROI 配置要精确
- ⏱️ 延迟参数要合理
- 🔄 任务流程要有容错机制
- 🐛 逐步测试，不要一次性写完所有流程

**下一步：**

1. 开始制作第一个模板
2. 测试开始画面识别
3. 逐步扩展功能
4. 遇到问题查阅本指南的调试章节

祝你开发顺利！🎉
