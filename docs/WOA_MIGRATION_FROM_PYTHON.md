# 从 Python 项目迁移到 MAA 框架 - 完整指南

## 📋 目录

1. [迁移概述](#迁移概述)
2. [Python 代码分析](#python-代码分析)
3. [迁移策略](#迁移策略)
4. [JSON 配置映射](#json-配置映射)
5. [WPF UI 修改指南](#wpf-ui-修改指南)
6. [C# 自定义任务类](#c-自定义任务类)
7. [完整实现步骤](#完整实现步骤)

---

## 📖 迁移概述

### 现有架构 vs MAA 架构

```
现有 Python 项目                    MAA 框架
┌──────────────────┐              ┌──────────────────┐
│ CustomTkinter UI │              │  WPF GUI (C#)    │
├──────────────────┤              ├──────────────────┤
│ game.py 逻辑     │    ====>     │  WOATask (C++)   │
│ - 图像识别       │              │  + tasks.json    │
│ - OCR           │              │  + templates/    │
│ - 点击/滑动      │              ├──────────────────┤
├──────────────────┤              │  MaaCore         │
│ ADB + Minitouch  │              │  (已有)          │
└──────────────────┘              └──────────────────┘
```

### 迁移优势

✅ **性能提升**：C++ 核心比 Python 更快
✅ **专业 UI**：WPF 界面更美观、功能更强
✅ **配置化**：JSON 驱动，无需修改代码
✅ **易维护**：模块化设计，清晰的职责分离
✅ **可扩展**：基于成熟框架，便于添加新功能

---

## 🔍 Python 代码分析

### 核心功能拆解

#### 1. 识别的按钮/状态

| Python 模板 | 功能 | MAA 任务名 |
|------------|------|-----------|
| `clear_land.png` | 准许降落 | `WOA_ClearToLand` |
| `confirm.png` | 确认 | `WOA_Confirm` |
| `stand.png` | 分配机位 | `WOA_AssignStand` |
| `crew.png` | 分配地勤 | `WOA_AssignCrew` |
| `taxi.png` | 滑行 | `WOA_Taxi` |
| `pushback.png` | 推出 | `WOA_Pushback` |
| `cross.png` | 穿越跑道 | `WOA_CrossRunway` |
| `lineup.png` | 对齐 | `WOA_Lineup` |
| `takeoff.png` | 起飞 | `WOA_Takeoff` |
| `claim.png` | 领取奖励 | `WOA_ClaimReward` |
| `start.png` | 开始页面 | `WOA_StartPage` |
| `home.png` | 主页 | `WOA_HomePage` |
| `require_action.png` | 需要操作的飞机图标 | `WOA_FindAircraft` |

#### 2. 特殊逻辑

**地勤分配逻辑**：
```python
# 1. OCR 读取可用地勤数量
crew_text = vision.ocr_in_region(screenshot, 1085, 826, 1338, 885)
available_crew = int(match.group(1))

# 2. OCR 读取机型
air_model = vision.ocr_airnum_in_region(screenshot, 224, 444, 321, 489)

# 3. 模糊匹配机型，确定需求
crew_needed = find_crew_need(model)

# 4. 判断是否足够
if available_crew < crew_needed:
    skip()
else:
    perform_sequence_from_auto_sh()  # 滑动条 + 点击
```

**机场切换逻辑**：
```python
def enter_airport(name):
    if name == "BRI":
        swipe(2263,120,2263,1200,2000)  # 向下滑动
        click(2253,306)                  # 点击机场图标
        click(330,1308)                  # 确认进入
```

---

## 🎯 迁移策略

### 方案 A：纯配置方案（推荐新手）

**只修改配置文件，不写 C++ 代码**

```
resource/woa/
├── tasks/tasks.json        # 任务流程（对应 game.py 的逻辑）
├── config.json             # 全局配置
└── template/               # 图像模板（直接复制 images/）
```

**优点**：简单快速，无需编译
**缺点**：复杂逻辑（如模糊匹配机型）需要简化

---

### 方案 B：自定义任务类（推荐你）

**添加 C++ 任务类 + JSON 配置**

```
src/MaaCore/Task/Interface/WOAAirportTask.h/cpp  # 自定义任务类
resource/woa/tasks/tasks.json                     # JSON 配置
src/MaaWpfGui/ViewModels/UI/WOAViewModel.cs      # WPF 界面
src/MaaWpfGui/Views/UI/WOAView.xaml              # WPF 视图
```

**优点**：可以实现复杂逻辑（OCR、模糊匹配、动态决策）
**缺点**：需要学 C++ 和 C#，需要编译

**我推荐方案 B**，因为你的代码有复杂的 OCR 和决策逻辑。

---

## 📝 JSON 配置映射

### 1. 基础飞机处理流程

将 `handle_post_click()` 转换为 JSON：

```json
{
    "WOA_FindAircraft": {
        "Doc": "查找需要操作的飞机",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "require_action.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_HandleAircraft"],
        "on_error_next": ["WOA_CheckStartPage"],
        "maxTimes": 20,
        "postDelay": 500
    },

    "WOA_HandleAircraft": {
        "Doc": "处理飞机（多状态检测）",
        "algorithm": "JustReturn",
        "next": [
            "WOA_ClearToLand",
            "WOA_AssignStand",
            "WOA_AssignCrew",
            "WOA_CrossRunway",
            "WOA_Taxi",
            "WOA_Pushback",
            "WOA_Lineup",
            "WOA_Takeoff",
            "WOA_Confirm",
            "WOA_ClaimReward"
        ]
    },

    "WOA_ClearToLand": {
        "Doc": "准许降落",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "clear_land.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_AssignStand": {
        "Doc": "分配机位",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "stand.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_SelectStand"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_SelectStand": {
        "Doc": "选择第一个机位",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [798, 1220, 100, 100],
        "next": ["WOA_ConfirmStand"],
        "postDelay": 500
    },

    "WOA_ConfirmStand": {
        "Doc": "确认机位",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "stand.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "postDelay": 1000
    },

    "WOA_AssignCrew": {
        "Doc": "分配地勤 - 需要自定义逻辑",
        "algorithm": "CustomTask",
        "taskName": "AssignCrewWithCheck",
        "template": "crew.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"]
    },

    "WOA_Taxi": {
        "Doc": "滑行",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "taxi.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_Pushback": {
        "Doc": "推出",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "pushback.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_CrossRunway": {
        "Doc": "穿越跑道",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "cross.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_Lineup": {
        "Doc": "对齐跑道",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "lineup.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_Takeoff": {
        "Doc": "准许起飞",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "takeoff.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_Confirm": {
        "Doc": "确认",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "confirm.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_FindAircraft"],
        "on_error_next": ["#next"],
        "postDelay": 500
    },

    "WOA_ClaimReward": {
        "Doc": "领取奖励",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "claim.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_ConfirmClaim"],
        "on_error_next": ["#next"],
        "postDelay": 2000
    },

    "WOA_ConfirmClaim": {
        "Doc": "确认领取",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [1236, 909, 100, 100],
        "next": ["WOA_FindAircraft"],
        "postDelay": 5000
    },

    "WOA_CheckStartPage": {
        "Doc": "检查是否在开始页面",
        "algorithm": "MatchTemplate",
        "action": "Click",
        "template": "start.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.8,
        "next": ["WOA_EnterGame"],
        "on_error_next": ["WOA_CheckHomePage"],
        "postDelay": 2000
    },

    "WOA_EnterGame": {
        "Doc": "进入游戏",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [1294, 1347, 100, 100],
        "next": ["WOA_SelectAirport"],
        "postDelay": 2000
    },

    "WOA_CheckHomePage": {
        "Doc": "检查是否在主页",
        "algorithm": "MatchTemplate",
        "template": "home.png",
        "roi": [0, 0, 2560, 1440],
        "threshold": 0.7,
        "next": ["WOA_EnterFromHome"],
        "on_error_next": ["WOA_FindAircraft"],
        "postDelay": 1000
    },

    "WOA_EnterFromHome": {
        "Doc": "从主页进入",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [2300, 400, 100, 100],
        "next": ["WOA_WaitLoading"],
        "postDelay": 60000
    }
}
```

### 2. 机场切换配置

```json
{
    "WOA_SelectAirport_BRI": {
        "Doc": "选择 BRI 机场",
        "algorithm": "JustReturn",
        "action": "DoNothing",
        "next": ["WOA_ScrollDown_BRI_1"]
    },

    "WOA_ScrollDown_BRI_1": {
        "Doc": "向下滑动",
        "algorithm": "JustReturn",
        "action": "Swipe",
        "specificRect": [2263, 120, 50, 50],
        "rectMove": [2263, 1200, 50, 50],
        "specialParams": [2000, 0, 1, 1],
        "next": ["WOA_ScrollDown_BRI_2"],
        "postDelay": 2000
    },

    "WOA_ScrollDown_BRI_2": {
        "Doc": "再次向下滑动",
        "algorithm": "JustReturn",
        "action": "Swipe",
        "specificRect": [2263, 120, 50, 50],
        "rectMove": [2263, 1200, 50, 50],
        "specialParams": [1000, 0, 1, 1],
        "next": ["WOA_ClickAirport_BRI"],
        "postDelay": 2000
    },

    "WOA_ClickAirport_BRI": {
        "Doc": "点击 BRI 机场图标",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [2253, 306, 100, 100],
        "next": ["WOA_ConfirmEnter_BRI"],
        "postDelay": 2000
    },

    "WOA_ConfirmEnter_BRI": {
        "Doc": "确认进入 BRI",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [330, 1308, 100, 100],
        "next": ["WOA_WaitAirportLoad"],
        "postDelay": 10000
    },

    "WOA_WaitAirportLoad": {
        "Doc": "等待机场加载",
        "algorithm": "JustReturn",
        "action": "DoNothing",
        "next": ["WOA_ChangeVision"],
        "postDelay": 5000
    },

    "WOA_ChangeVision": {
        "Doc": "调整视角（4次点击）",
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [2467, 72, 100, 100],
        "next": ["WOA_ChangeVision_2"],
        "postDelay": 2000
    },

    "WOA_ChangeVision_2": {
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [2467, 723, 100, 100],
        "next": ["WOA_ChangeVision_3"],
        "postDelay": 2000
    },

    "WOA_ChangeVision_3": {
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [2467, 72, 100, 100],
        "next": ["WOA_ChangeVision_4"],
        "postDelay": 2000
    },

    "WOA_ChangeVision_4": {
        "algorithm": "JustReturn",
        "action": "Click",
        "specificRect": [1858, 75, 100, 100],
        "next": ["WOA_FindAircraft"],
        "postDelay": 2000
    }
}
```

---

## 🎨 WPF UI 修改指南

### 1. 添加 WOA 界面页面

#### 步骤 1：创建 ViewModel

创建 `src/MaaWpfGui/ViewModels/UI/WOAViewModel.cs`：

```csharp
// Copyright (c) 2025 MaaAssistantWoA team
// Licensed under AGPL-3.0

using System;
using System.Collections.Generic;
using System.Linq;
using Stylet;
using StyletIoC;

namespace MaaWpfGui.ViewModels.UI
{
    public class WOAAirportViewModel : Screen
    {
        private readonly IContainer _container;
        private readonly RunningState _runningState;

        [Inject]
        public WOAAirportViewModel(IContainer container)
        {
            _container = container;
            _runningState = container.Get<RunningState>();
            DisplayName = "World of Airports";
        }

        #region 机场选择

        private static readonly List<string> _airportList = new()
        {
            "BRI",
            "PRG",
            "BKK",
            "MSY",
            "IAD"
        };

        public List<string> AirportList => _airportList;

        private string _selectedAirport = "BRI";

        public string SelectedAirport
        {
            get => _selectedAirport;
            set
            {
                SetAndNotify(ref _selectedAirport, value);
                SaveConfiguration();
            }
        }

        #endregion

        #region 启动/停止

        private bool _isRunning = false;

        public bool IsRunning
        {
            get => _isRunning;
            set => SetAndNotify(ref _isRunning, value);
        }

        public bool IsNotRunning => !IsRunning;

        public void LinkStart()
        {
            if (IsRunning)
            {
                return;
            }

            SaveConfiguration();

            var task = _container.Get<TaskQueueViewModel>();

            // 添加 WOA 任务
            task.AddTask("WOAAirport", new Dictionary<string, object>
            {
                { "airport", SelectedAirport },
                { "enable", true }
            });

            task.LinkStart();
            IsRunning = true;
        }

        public void Stop()
        {
            if (!IsRunning)
            {
                return;
            }

            var task = _container.Get<TaskQueueViewModel>();
            task.Stop();
            IsRunning = false;
        }

        #endregion

        #region 配置保存/加载

        private void SaveConfiguration()
        {
            var settings = _container.Get<SettingsViewModel>();
            settings.WOA_SelectedAirport = SelectedAirport;
        }

        public void LoadConfiguration()
        {
            var settings = _container.Get<SettingsViewModel>();
            SelectedAirport = settings.WOA_SelectedAirport ?? "BRI";
        }

        protected override void OnInitialActivate()
        {
            base.OnInitialActivate();
            LoadConfiguration();
        }

        #endregion

        #region 机场切换

        public void ChangeAirport()
        {
            if (!IsRunning)
            {
                return;
            }

            SaveConfiguration();

            // 触发机场切换任务
            var task = _container.Get<TaskQueueViewModel>();
            task.AddTask("ChangeAirport", new Dictionary<string, object>
            {
                { "airport", SelectedAirport }
            });
        }

        #endregion
    }
}
```

#### 步骤 2：创建 View (XAML)

创建 `src/MaaWpfGui/Views/UI/WOAView.xaml`：

```xml
<UserControl
    x:Class="MaaWpfGui.Views.UI.WOAView"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:hc="https://handyorg.github.io/handycontrol"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    d:DesignHeight="450"
    d:DesignWidth="800"
    mc:Ignorable="d">

    <Grid Margin="20">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="Auto" />
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- 标题 -->
        <TextBlock
            Grid.Row="0"
            FontSize="24"
            FontWeight="Bold"
            Text="World of Airports 自动化" />

        <!-- 机场选择 -->
        <GroupBox Grid.Row="1" Margin="0,20,0,0">
            <GroupBox.Header>
                <TextBlock FontSize="16" Text="机场设置" />
            </GroupBox.Header>

            <StackPanel Margin="10">
                <TextBlock Text="选择机场:" Margin="0,0,0,5" />
                <ComboBox
                    ItemsSource="{Binding AirportList}"
                    SelectedItem="{Binding SelectedAirport}"
                    IsEnabled="{Binding IsNotRunning}"
                    Width="200"
                    HorizontalAlignment="Left" />

                <Button
                    Content="切换机场"
                    Command="{s:Action ChangeAirport}"
                    IsEnabled="{Binding IsRunning}"
                    Margin="0,10,0,0"
                    Width="120"
                    HorizontalAlignment="Left" />
            </StackPanel>
        </GroupBox>

        <!-- 控制按钮 -->
        <StackPanel Grid.Row="2" Margin="0,20,0,0" Orientation="Horizontal">
            <Button
                Content="开始"
                Command="{s:Action LinkStart}"
                IsEnabled="{Binding IsNotRunning}"
                Width="120"
                Height="40"
                Margin="0,0,10,0"
                Style="{StaticResource ButtonPrimary}" />

            <Button
                Content="停止"
                Command="{s:Action Stop}"
                IsEnabled="{Binding IsRunning}"
                Width="120"
                Height="40"
                Style="{StaticResource ButtonDanger}" />
        </StackPanel>

        <!-- 说明文本 -->
        <GroupBox Grid.Row="3" Margin="0,20,0,0">
            <GroupBox.Header>
                <TextBlock FontSize="16" Text="使用说明" />
            </GroupBox.Header>

            <ScrollViewer>
                <TextBlock TextWrapping="Wrap" Margin="10">
                    <Run Text="功能说明:" FontWeight="Bold" />
                    <LineBreak />
                    <Run Text="• 自动处理所有飞机（降落、分配机位、地勤、推出、起飞）" />
                    <LineBreak />
                    <Run Text="• 自动分配最大地勤数量" />
                    <LineBreak />
                    <Run Text="• 处理特殊操作（穿越跑道、除冰等）" />
                    <LineBreak />
                    <Run Text="• 支持切换多个机场" />
                    <LineBreak />
                    <LineBreak />
                    <Run Text="使用步骤:" FontWeight="Bold" />
                    <LineBreak />
                    <Run Text="1. 确保游戏已启动并处于机场界面" />
                    <LineBreak />
                    <Run Text="2. 选择要自动化的机场" />
                    <LineBreak />
                    <Run Text="3. 点击「开始」按钮" />
                    <LineBreak />
                    <Run Text="4. 脚本将自动处理所有飞机" />
                    <LineBreak />
                    <Run Text="5. 需要切换机场时，选择新机场并点击「切换机场」" />
                </TextBlock>
            </ScrollViewer>
        </GroupBox>
    </Grid>
</UserControl>
```

创建对应的 Code-Behind `src/MaaWpfGui/Views/UI/WOAView.xaml.cs`：

```csharp
namespace MaaWpfGui.Views.UI
{
    public partial class WOAView
    {
        public WOAView()
        {
            InitializeComponent();
        }
    }
}
```

#### 步骤 3：注册到主界面

修改 `src/MaaWpfGui/ViewModels/RootViewModel.cs`，添加 WOA 标签页：

```csharp
// 在构造函数中添加
public RootViewModel(IContainer container)
{
    // ... 现有代码 ...

    // 添加 WOA 页面
    SubViewModels.Add(container.Get<WOAAirportViewModel>());
}
```

修改 `src/MaaWpfGui/Views/RootView.xaml`，添加标签页：

```xml
<!-- 在 TabControl 中添加新的 TabItem -->
<TabItem Header="WOA">
    <ContentControl s:View.Model="{Binding WOAAirportViewModel}" />
</TabItem>
```

---

## 💻 C# 自定义任务类

### 创建 WOAAirportTask.h

`src/MaaCore/Task/Interface/WOAAirportTask.h`:

```cpp
#pragma once

#include "InterfaceTask.h"
#include <string>
#include <unordered_map>

namespace asst
{
    class WOAAirportTask final : public InterfaceTask
    {
    public:
        using InterfaceTask::InterfaceTask;
        virtual ~WOAAirportTask() override = default;

        virtual bool _run() override;

    private:
        // 地勤分配逻辑
        bool assign_crew_with_check();

        // OCR 解析可用地勤数量
        int parse_available_crew(const cv::Mat& image);

        // OCR 识别机型
        std::string recognize_aircraft_model(const cv::Mat& image);

        // 根据机型查找所需地勤数
        int get_required_crew(const std::string& model);

        // 模糊匹配机型
        std::string fuzzy_match_model(const std::string& ocr_result);

        // 执行滑动条操作
        bool perform_crew_assignment();

        // 机场切换
        bool change_airport(const std::string& airport_code);

        // 机型-地勤映射表
        static const std::unordered_map<std::string, int> crew_binding;

        // OCR 常见错误修正
        static const std::unordered_map<std::string, std::string> common_fixes;
    };
}
```

### 创建 WOAAirportTask.cpp

`src/MaaCore/Task/Interface/WOAAirportTask.cpp`:

```cpp
#include "WOAAirportTask.h"
#include "Controller/Controller.h"
#include "Vision/OCRer.h"
#include "Vision/Matcher.h"
#include "Utils/Logger.hpp"
#include "ProcessTask.h"

#include <regex>
#include <algorithm>

namespace asst
{
    // 机型-地勤映射表
    const std::unordered_map<std::string, int> WOAAirportTask::crew_binding = {
        {"A225", 21}, {"A124", 21}, {"A388", 14},
        {"B748", 14}, {"B744", 14}, {"B748F", 14}, {"B744F", 14},
        {"B77W", 11}, {"B77L", 11}, {"B77LF", 11},
        {"B789", 9}, {"B78X", 9}, {"B788", 9},
        {"A359", 11}, {"A35K", 11}, {"A346", 11}, {"A343", 9},
        {"A332", 9}, {"A332F", 11}, {"A333", 9},
        {"A321", 7}, {"A21N", 7}, {"A21NX", 7}, {"A21NY", 7},
        {"A320", 7}, {"A20N", 7}, {"A319", 7}, {"A19N", 7}, {"A318", 7},
        {"A306", 8},
        {"B763F", 11}, {"B738", 7}, {"B38M", 7}, {"B734", 7},
        {"E190", 6}, {"E195", 6}, {"E170", 4}, {"E175", 4}, {"E295", 6}, {"E290", 6},
        {"A3ST", 20}, {"C17", 15},
        {"B738F", 7}, {"A321F", 7}, {"B734F", 7},
        {"BCS3", 7}, {"BCS1", 7},
        {"CRJX", 4}, {"CRJ9", 4}, {"CRJ7", 4}, {"CRJ2", 4},
        {"F100", 5}, {"F70", 5}
    };

    // OCR 常见错误修正
    const std::unordered_map<std::string, std::string> WOAAirportTask::common_fixes = {
        {"B7W", "B77W"}, {"A3BB", "A388"}, {"A38B", "A388"}, {"A337", "A332"},
        {"B783", "B789"}, {"AIN", "A21N"}, {"AINX", "A21NX"}, {"A2ON", "A20N"},
        {"ANY", "A21NY"}, {"AN", "A21N"}, {"ANX", "A21NX"},
        {"B7IW", "B77W"}, {"EI5", "E175"}, {"EI0", "E170"}, {"EIO", "E170"},
        {"CRI9", "CRJ9"}, {"CRI7", "CRJ7"}, {"CRI2", "CRJ2"}, {"CRIX", "CRJX"},
        {"FIQO", "F100"}, {"FI0", "F100"}, {"B739", "B789"}
    };

    bool WOAAirportTask::_run()
    {
        LogTraceFunction;

        // 主循环：使用 ProcessTask 执行配置的流程
        ProcessTask process_task(*this, { "WOA_FindAircraft" });
        process_task.set_retry_times(9999);  // 持续运行

        return process_task.run();
    }

    std::string WOAAirportTask::fuzzy_match_model(const std::string& ocr_result)
    {
        // 1. 规范化：去空格、转大写
        std::string normalized = ocr_result;
        normalized.erase(std::remove_if(normalized.begin(), normalized.end(), ::isspace), normalized.end());
        std::transform(normalized.begin(), normalized.end(), normalized.begin(), ::toupper);

        // 2. 先检查常见错误修正表
        auto fix_it = common_fixes.find(normalized);
        if (fix_it != common_fixes.end()) {
            normalized = fix_it->second;
        }

        // 3. 精确匹配
        if (crew_binding.find(normalized) != crew_binding.end()) {
            return normalized;
        }

        // 4. 模糊匹配（简单的编辑距离）
        int min_distance = 999;
        std::string best_match;

        for (const auto& [model, _] : crew_binding) {
            // 计算编辑距离（这里用简化版本）
            int distance = std::abs(static_cast<int>(normalized.size()) - static_cast<int>(model.size()));

            // 计算不同字符数
            for (size_t i = 0; i < std::min(normalized.size(), model.size()); ++i) {
                if (normalized[i] != model[i]) {
                    distance++;
                }
            }

            if (distance < min_distance) {
                min_distance = distance;
                best_match = model;
            }
        }

        // 如果最小距离小于阈值（例如 2），认为是匹配
        if (min_distance <= 2) {
            Log.info(__FUNCTION__, "Fuzzy matched:", ocr_result, "->", best_match);
            return best_match;
        }

        // 默认返回原始值
        Log.warn(__FUNCTION__, "Unknown model:", ocr_result);
        return normalized;
    }

    int WOAAirportTask::get_required_crew(const std::string& model)
    {
        std::string matched_model = fuzzy_match_model(model);

        auto it = crew_binding.find(matched_model);
        if (it != crew_binding.end()) {
            Log.info(__FUNCTION__, "Model:", matched_model, "requires", it->second, "crew");
            return it->second;
        }

        Log.warn(__FUNCTION__, "Unknown model:", model, ", using default 20");
        return 20;  // 默认值
    }

    std::string WOAAirportTask::recognize_aircraft_model(const cv::Mat& image)
    {
        // 使用 OCRer 识别机型
        OCRer ocr(ctrler()->get_image());
        ocr.set_roi(Rect(224, 444, 321 - 224, 489 - 444));  // 机型 OCR 区域

        if (!ocr.analyze()) {
            Log.error(__FUNCTION__, "OCR failed");
            return "";
        }

        const auto& results = ocr.get_result();
        if (results.empty()) {
            return "";
        }

        // 返回第一个结果
        return results[0].text;
    }

    int WOAAirportTask::parse_available_crew(const cv::Mat& image)
    {
        // 使用 OCRer 识别可用地勤数量
        OCRer ocr(image);
        ocr.set_roi(Rect(1085, 826, 1338 - 1085, 885 - 826));

        if (!ocr.analyze()) {
            Log.error(__FUNCTION__, "OCR failed for crew count");
            return 0;
        }

        const auto& results = ocr.get_result();
        if (results.empty()) {
            return 0;
        }

        std::string text = results[0].text;

        // 使用正则表达式提取末尾的数字
        std::regex number_regex(R"((\d+)$)");
        std::smatch match;

        if (std::regex_search(text, match, number_regex)) {
            int count = std::stoi(match[1].str());
            Log.info(__FUNCTION__, "Available crew:", count);
            return count;
        }

        Log.error(__FUNCTION__, "Failed to parse crew count from:", text);
        return 0;
    }

    bool WOAAirportTask::perform_crew_assignment()
    {
        LogTraceFunction;

        // 执行滑动条操作（对应 perform_sequence_from_auto_sh）
        // 1. 滑动
        ctrler()->swipe(Point(793, 919), Point(1222, 919), 500);
        sleep(500);

        // 2. 点击确认
        ctrler()->click(Point(1289, 1040));
        sleep(500);

        // 3. 点击第二个确认
        ctrler()->click(Point(394, 1303));
        sleep(500);

        Log.info(__FUNCTION__, "Crew assigned");
        return true;
    }

    bool WOAAirportTask::assign_crew_with_check()
    {
        LogTraceFunction;

        cv::Mat image = ctrler()->get_image();

        // 1. 识别可用地勤数量
        int available = parse_available_crew(image);

        // 2. 识别机型
        std::string model = recognize_aircraft_model(image);

        // 3. 获取所需地勤
        int required = get_required_crew(model);

        // 4. 判断是否足够
        if (available < required) {
            Log.info(__FUNCTION__, "Insufficient crew. Need:", required, "Available:", available);
            return false;  // 跳过此飞机
        }

        // 5. 执行分配
        return perform_crew_assignment();
    }

    bool WOAAirportTask::change_airport(const std::string& airport_code)
    {
        LogTraceFunction;

        // 根据机场代码执行不同的流程
        std::string task_name = "WOA_SelectAirport_" + airport_code;

        ProcessTask process_task(*this, { task_name });
        return process_task.run();
    }
}
```

### 注册任务类

修改 `src/MaaCore/Task/InterfaceTask.cpp`，注册新任务：

```cpp
// 在 create 函数中添加
if (type == "WOAAirport") {
    return std::make_shared<WOAAirportTask>(callback, inst, task_chain);
}
```

---

## 🔧 完整实现步骤

### 步骤 1：准备资源文件

```bash
# 1. 创建目录
mkdir -p resource/woa/template
mkdir -p resource/woa/tasks

# 2. 复制图像模板
cp /path/to/your/images/*.png resource/woa/template/

# 3. 创建配置文件
# 将上面的 JSON 配置保存为 resource/woa/tasks/tasks.json
# 将机场配置保存为 resource/woa/config.json
```

### 步骤 2：添加 C++ 代码

```bash
# 1. 创建任务类
# 复制上面的 WOAAirportTask.h/cpp 到对应位置

# 2. 修改 CMakeLists.txt，添加新文件
# src/MaaCore/CMakeLists.txt
# 在 INTERFACE_TASK_FILES 部分添加：
#   Task/Interface/WOAAirportTask.h
#   Task/Interface/WOAAirportTask.cpp
```

### 步骤 3：添加 C# WPF 界面

```bash
# 1. 创建 ViewModel 和 View
# 复制上面的 WOAAirportViewModel.cs 和 WOAView.xaml/xaml.cs

# 2. 修改 MaaWpfGui.csproj，添加新文件

# 3. 注册到主界面
# 修改 RootViewModel.cs 和 RootView.xaml
```

### 步骤 4：编译项目

```bash
# Windows (Visual Studio)
mkdir build
cd build
cmake -A x64 ..
cmake --build . --config Release

# 或者直接用 Visual Studio 打开 MaaAssistantWoA.sln
```

### 步骤 5：配置和测试

```bash
# 1. 运行编译好的程序
./build/bin/Release/MaaWpfGui.exe

# 2. 在 WOA 标签页中：
#    - 选择机场
#    - 点击「开始」
#    - 查看日志输出

# 3. 调试：
#    - 查看 debug/maa.log
#    - 检查模板识别效果
#    - 调整 threshold 和 ROI
```

---

## 📊 对比总结

| 功能 | Python 项目 | MAA 迁移后 |
|-----|------------|-----------|
| **性能** | 中等（Python） | 快（C++核心） |
| **UI** | customtkinter | WPF（专业） |
| **配置** | 硬编码 | JSON 配置化 |
| **OCR** | paddleocr | PaddleOCR（集成） |
| **模糊匹配** | rapidfuzz | C++ 实现 |
| **可维护性** | 一般 | 优秀（模块化） |
| **扩展性** | 一般 | 优秀（插件系统） |

---

## ✅ 检查清单

迁移完成前，确保：

- [ ] 所有图像模板已转换并测试
- [ ] JSON 配置文件已完成
- [ ] C++ 任务类已实现并编译
- [ ] WPF 界面已添加并可用
- [ ] 地勤分配逻辑（OCR + 模糊匹配）正常工作
- [ ] 机场切换功能正常
- [ ] 完整流程测试通过

---

## 💡 常见问题

**Q: 必须用 C++ 实现复杂逻辑吗？**
A: 不一定。简单的逻辑可以用 JSON 配置。但 OCR 解析、模糊匹配、动态决策等复杂逻辑，C++ 实现更好。

**Q: WPF UI 必须修改吗？**
A: 如果只是自己用，可以继续用 Python 脚本。但如果想要专业的界面和更好的用户体验，推荐修改 WPF UI。

**Q: 编译很复杂吗？**
A: 第一次编译需要配置环境，但之后只需 `cmake --build .` 即可。详见[开发文档](https://docs.maa.plus/zh-cn/develop/development.html)。

**Q: 能否保留 Python 的灵活性？**
A: 可以！你可以用 Python 接口调用 MAA，获得 C++ 的性能和 Python 的灵活性。

---

**下一步**：开始实现第一个功能，例如飞机处理流程，然后逐步添加其他功能。
