# World of Airports 自动化使用指南

## 快速开始

### 1. 编译项目

在完成所有代码修改后，使用 Visual Studio 2022 编译项目：

1. 打开 `MAA.sln`
2. 选择 `Release` 配置
3. 生成解决方案（Ctrl+Shift+B）

### 2. 准备游戏环境

1. 在 Android 设备上安装 World of Airports
2. 启用 USB 调试模式
3. 连接设备到电脑
4. 确认 ADB 连接：`adb devices`

### 3. 启动自动化

1. 运行编译后的 `MaaWpfGui.exe`
2. 在左侧菜单选择 "WOA 机场管理"
3. 选择要操作的机场（BRI/PRG/BKK/MSY/IAD）
4. 点击"开始"按钮

## 功能说明

### 自动化流程

程序会按以下顺序执行：

1. **识别游戏状态**
   - 检测是否在主界面
   - 自动进入游戏

2. **进入选定机场**
   - 根据选择的机场代码进入对应机场
   - BRI/PRG/IAD: 向下滚动 2 次
   - BKK/MSY: 向上滚动 3 次

3. **调整视角**
   - 自动调整游戏视角以便识别飞机
   - 执行 4 次点击调整视角位置

4. **飞机处理循环**

   对每架需要处理的飞机：

   a. **选择停机位（Stand）**
      - 识别飞机图标上的操作提示
      - 点击选择合适的停机位

   b. **准许降落（Clear to Land）**
      - 点击准许降落按钮
      - 等待飞机降落

   c. **分配地勤（Assign Crew）** ⭐核心功能
      - OCR 识别可用地勤数量
      - OCR 识别飞机型号
      - 查询该型号所需地勤数量
      - 如果地勤充足：
        - 滑动进度条到最大值
        - 点击确认按钮（2 次）
      - 如果地勤不足：跳过该飞机

   d. **处理特殊情况**
      - 穿越跑道许可（Runway Crossing）
      - 除冰作业（De-icing）

   e. **推出机位（Pushback）**
      - 地勤作业完成后推出

   f. **滑行（Taxi）**
      - 引导飞机滑行至跑道

   g. **对齐跑道（Line up）**
      - 飞机对齐跑道准备起飞

   h. **准许起飞（Clear for Takeoff）**
      - 点击起飞许可完成整个流程

5. **循环处理**
   - 自动寻找下一架需要处理的飞机
   - 重复步骤 4
   - 直到没有飞机需要处理

## 地勤分配逻辑

### 飞机型号识别

程序使用 OCR 识别飞机型号，支持 52 种机型：

**超大型机**：
- A225 (21 人), A3BB/A388 (19 人), B77W (11 人)

**大型机**：
- B77L/B772 (10 人), A359 (10 人), B789 (9 人), B788 (8 人)

**中型机**：
- A332/A333/A339 (9 人), A21N/A321 (7 人), B38M/B39M (7 人)

**小型机**：
- E190/E195 (6 人), E170/E175 (4 人), CRJX/CRJ7/CRJ9 (4 人)

**支线机**：
- AT75/AT76 (3 人), DH8D (3 人)

完整列表见 `resource/woa/config.json`

### OCR 纠错

程序内置 20+ 常见 OCR 错误修正：

```
B7W → B77W
A3BB → A388
AIN → A21N
EI5 → E175
FIQO → F100
B739 → B789
```

### 模糊匹配

如果 OCR 结果不在已知型号中，程序会使用编辑距离算法进行模糊匹配，容许 2 个字符差异。

## 配置文件说明

### resource/woa/tasks/tasks.json

定义所有任务流程和图像识别参数：

```json
{
    "任务名称": {
        "algorithm": "匹配算法",
        "template": "模板图片",
        "roi": [识别区域],
        "threshold": 0.8,
        "next": ["成功后执行"],
        "on_error_next": ["失败后执行"]
    }
}
```

### resource/woa/config.json

包含地勤数据和参数配置：

```json
{
    "woa": {
        "crewRequirements": {
            "机型代码": 所需人数
        },
        "ocrFixes": {
            "错误识别": "正确型号"
        },
        "crewAssignment": {
            "swipe": "滑动参数",
            "confirmButton1": "确认按钮1坐标",
            "confirmButton2": "确认按钮2坐标"
        }
    }
}
```

## 模板图片

所有模板图片位于 `resource/woa/template/`：

| 文件名 | 用途 |
|--------|------|
| require_action.png | 识别需要操作的飞机 |
| stand.png | 停机位选择按钮 |
| land.png | 准许降落按钮 |
| crew.png | 地勤分配按钮 |
| push.png | 推出按钮 |
| taxi.png | 滑行按钮 |
| lineup.png | 对齐跑道按钮 |
| takeoff.png | 起飞按钮 |
| cross.png | 穿越跑道按钮 |
| confirm.png | 确认按钮 |
| cancel.png | 取消按钮 |
| start.png | 游戏开始界面 |
| home.png | 主界面图标 |
| home_bright.png | 高亮主界面图标 |
| claim.png | 奖励领取 |

## 常见问题

### Q: 程序无法识别飞机

**A**: 检查以下几点：
1. 确保模板图片与游戏画面分辨率匹配（2560x1440）
2. 调整 `tasks.json` 中的 `threshold` 值（降低到 0.7-0.75）
3. 检查 ROI 区域是否正确

### Q: OCR 识别不准确

**A**:
1. 在 `config.json` 的 `ocrFixes` 中添加错误映射
2. 检查 OCR 识别区域坐标是否正确
3. 确保游戏界面清晰，没有被其他窗口遮挡

### Q: 地勤数量判断错误

**A**:
1. 检查 `crewRequirements` 中的机型数据是否完整
2. 验证 OCR 识别的可用地勤数量是否正确
3. 查看日志中的识别结果

### Q: 需要添加新的飞机型号

**A**: 在 `config.json` 中添加：

```json
{
    "woa": {
        "crewRequirements": {
            "新机型代码": 所需人数
        }
    }
}
```

### Q: 坐标点击不准确

**A**:
1. 确认设备分辨率为 2560x1440
2. 如果分辨率不同，需要按比例调整所有坐标
3. 在 `tasks.json` 中修改 `action_rect` 坐标

## 调试技巧

### 查看日志

日志文件位于：`debug/asst.log`

关键日志信息：
```
[Info] Available crew: 15
[Info] Aircraft model: B77W
[Info] Required crew: 11
[Info] Crew assignment success
```

### 截图调试

修改 `tasks.json` 添加截图功能：

```json
{
    "任务名称": {
        "screenshot": true,
        "screenshotDir": "debug/screenshots/"
    }
}
```

### 单步测试

在 WPF UI 中可以选择执行特定任务：
- 只测试进入机场
- 只测试地勤分配
- 只测试完整流程

## 性能优化

### 提高识别速度

1. 减少 `roi` 区域大小，缩小搜索范围
2. 降低 `postDelay` 值，减少等待时间
3. 使用更精确的模板图片，提高首次匹配成功率

### 减少误操作

1. 提高 `threshold` 值到 0.85-0.90
2. 增加 `preDelay`，等待界面完全加载
3. 添加更多的状态检测任务

## 扩展功能

### 添加新机场

1. 在 `WOAView.xaml` 的机场列表中添加新机场代码
2. 在 `tasks.json` 中添加对应的进入任务
3. 测试并调整滚动参数

### 添加新操作流程

1. 截取新操作的模板图片
2. 在 `tasks.json` 中定义新任务
3. 在任务流程中插入新任务
4. 在 C++ 代码中添加特殊逻辑（如需要）

## 技术支持

- 项目仓库：https://github.com/MaaAssistantArknights/MaaAssistantArknights
- 文档：`docs/` 目录下的相关文档
- 原 Python 代码参考：用户提供的 `game.py` 和 `app.py`

## 从 Python 迁移的改进

相比原 Python 实现，MAA 版本的优势：

1. **更快的响应速度**：C++ 实现 + minitouch 协议
2. **更好的稳定性**：完善的错误处理和状态恢复
3. **更强的扩展性**：配置化设计，易于添加新功能
4. **更友好的 UI**：WPF 现代化界面
5. **更详细的日志**：完整的执行记录便于调试
6. **更低的资源占用**：C++ 原生性能

## 下一步

完成基础功能后，可以考虑：

1. 添加多机场轮询功能
2. 实现自动切换机场策略
3. 添加收益统计和报表
4. 实现远程控制功能
5. 添加推送通知（地勤不足、异常情况等）
