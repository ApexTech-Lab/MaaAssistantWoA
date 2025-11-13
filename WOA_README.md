# World of Airports 自动化脚本开发包

基于 MaaAssistantWoA 框架的完整开发指南

---

## 📚 文档索引

本开发包包含以下文档和工具：

### 1. 📖 主要文档

| 文档 | 说明 | 适合人群 |
|-----|------|---------|
| **[WOA_QUICKSTART.md](WOA_QUICKSTART.md)** | 5分钟快速上手指南 | 🔰 新手入门 |
| **[docs/WOA_ADAPTATION_GUIDE.md](docs/WOA_ADAPTATION_GUIDE.md)** | 详细开发指南（60+页） | 👨‍💻 开发者 |
| **本文件 (WOA_README.md)** | 文档导航和项目概述 | 📋 所有人 |

### 2. 🛠️ 工具脚本

| 工具 | 用途 | 使用方法 |
|-----|------|---------|
| **test_woa_automation.py** | 运行自动化脚本 | `python test_woa_automation.py` |
| **tools/template_validator.py** | 验证模板识别效果 | `python tools/template_validator.py screenshot.png template.png` |

### 3. 📦 资源文件

```
resource/woa/
├── config.json          # 全局配置
├── tasks/
│   └── tasks.json      # 任务流程定义
└── template/           # 图像模板
    ├── WOA_StartButton.png
    ├── WOA_Landing_Button.png
    └── ...
```

---

## 🎯 功能目标

开发一个能够自动处理 World of Airports 游戏的脚本，实现：

### ✅ 核心功能

1. **启动游戏**
   - 识别开始画面
   - 自动进入游戏

2. **机场管理**
   - 依次进入已解锁的机场
   - 自动切换机场

3. **飞机处理**（完整流程）
   - 🛬 选择机位
   - ✈️ 准许降落
   - 👷 开始处理/分配地勤
   - 📊 滑动进度条到最大地勤数量
   - 🚪 推出机位
   - 🛫 准许起飞

4. **特殊操作**
   - 🛣️ 穿越跑道许可
   - ❄️ 除冰操作

---

## 🚀 快速开始

### 前置要求

```bash
✓ Python 3.8+
✓ ADB (Android Debug Bridge)
✓ Android 设备或模拟器
✓ World of Airports 游戏已安装
```

### 3 步启动

```bash
# 1. 检查连接
adb devices

# 2. 准备资源（参考快速开始指南）
mkdir -p resource/woa/template
# 放置模板图片和配置文件

# 3. 运行
python test_woa_automation.py
```

---

## 📖 推荐阅读顺序

### 第 1 天：入门

1. ✅ 阅读 **[WOA_QUICKSTART.md](WOA_QUICKSTART.md)**
   - 了解基本概念
   - 完成环境搭建
   - 运行第一个测试

2. ✅ 使用 **template_validator.py**
   - 学习制作模板
   - 测试模板识别
   - 理解 ROI 和阈值

### 第 2-3 天：基础开发

3. ✅ 阅读 **[WOA_ADAPTATION_GUIDE.md](docs/WOA_ADAPTATION_GUIDE.md)** 的前半部分
   - 项目架构理解
   - 配置文件编写
   - 图像模板制作

4. ✅ 开发第一个功能
   - 识别开始画面
   - 点击进入游戏
   - 测试和调试

### 第 4-7 天：核心功能

5. ✅ 阅读详细指南的任务流程章节
   - 理解任务流程图
   - 编写复杂流程配置
   - 实现飞机处理流程

6. ✅ 学习高级功能
   - 滑动操作
   - 异常处理
   - 多状态识别

### 第 8-10 天：优化和完善

7. ✅ 阅读调试和优化章节
   - 提高识别准确性
   - 优化执行速度
   - 添加错误处理

---

## 🏗️ 项目结构

```
MaaAssistantWoA/
│
├── 📚 文档
│   ├── WOA_README.md              # 本文件（导航）
│   ├── WOA_QUICKSTART.md          # 快速开始
│   └── docs/
│       └── WOA_ADAPTATION_GUIDE.md # 详细指南
│
├── 🛠️ 工具
│   ├── test_woa_automation.py     # 主测试脚本
│   └── tools/
│       └── template_validator.py  # 模板验证工具
│
├── 📦 资源（需要自己创建）
│   └── resource/woa/
│       ├── config.json            # 配置文件
│       ├── tasks/
│       │   └── tasks.json        # 任务定义
│       └── template/             # 图像模板
│
└── 💻 MAA 核心代码
    ├── src/MaaCore/              # C++ 核心库
    ├── include/                  # API 头文件
    └── src/Python/               # Python 接口
```

---

## 🎓 学习路径

### 路径 1：快速体验（1-2 小时）

适合想快速了解项目的用户

```
1. 阅读 WOA_QUICKSTART.md (15分钟)
2. 安装环境和依赖 (30分钟)
3. 运行最小示例 (15分钟)
4. 测试模板识别 (30分钟)
```

### 路径 2：完整开发（1-2 周）

适合想开发完整功能的开发者

```
第 1-2 天: 环境搭建和基础学习
第 3-4 天: 模板制作和基础识别
第 5-7 天: 核心功能开发
第 8-10 天: 测试优化和完善
```

### 路径 3：深度定制（2-4 周）

适合想深度定制和扩展功能的高级开发者

```
第 1 周: 完成路径 2 的所有内容
第 2 周: 学习 MAA 框架源码
第 3 周: 自定义 C++ 任务类
第 4 周: 性能优化和功能扩展
```

---

## 📊 开发进度追踪

使用以下清单追踪开发进度：

### 阶段 1：环境准备 (0-20%)

- [ ] Python 环境配置
- [ ] ADB 安装和测试
- [ ] 设备连接成功
- [ ] 项目代码下载
- [ ] 目录结构创建

### 阶段 2：基础功能 (20-40%)

- [ ] 第一个模板制作成功
- [ ] 开始画面识别成功
- [ ] 基础配置文件完成
- [ ] 能够点击进入游戏

### 阶段 3：核心开发 (40-80%)

- [ ] 机场列表识别
- [ ] 机场切换功能
- [ ] 飞机识别和选择
- [ ] 完整处理流程（降落→处理→起飞）
- [ ] 滑动进度条功能

### 阶段 4：完善优化 (80-100%)

- [ ] 特殊操作处理（穿越跑道、除冰）
- [ ] 异常处理机制
- [ ] 多机场循环处理
- [ ] 识别准确性优化
- [ ] 执行速度优化
- [ ] 完整测试通过

---

## 🔧 工具使用示例

### 1. 测试自动化脚本

```bash
# 基础运行
python test_woa_automation.py

# 指定设备地址
python test_woa_automation.py --address 127.0.0.1:5555

# 启用调试日志
python test_woa_automation.py --debug

# 指定资源路径
python test_woa_automation.py --resource /path/to/resource/woa

# 运行特定任务
python test_woa_automation.py --task WOA_ProcessAircrafts
```

### 2. 验证模板识别

```bash
# 基础验证
python tools/template_validator.py screenshot.png template.png

# 指定 ROI
python tools/template_validator.py screenshot.png template.png \
    --roi 400 500 480 200

# 指定阈值
python tools/template_validator.py screenshot.png template.png \
    --threshold 0.75

# 指定输出文件
python tools/template_validator.py screenshot.png template.png \
    --output result_image.png
```

---

## 💡 最佳实践

### 开发建议

1. **小步快跑**
   - 每次只添加一个功能
   - 立即测试，确保工作正常
   - 再添加下一个功能

2. **详细记录**
   - 记录每个 ROI 的坐标
   - 保存识别失败的截图
   - 写注释说明复杂逻辑

3. **版本控制**
   - 使用 Git 管理代码
   - 功能完成后及时提交
   - 添加有意义的提交信息

4. **测试驱动**
   - 先用模板验证工具测试
   - 确保识别准确再写配置
   - 每个功能都要完整测试

### 调试技巧

1. **识别失败时**
   - 降低阈值
   - 扩大 ROI 范围
   - 重新制作模板
   - 使用模板验证工具

2. **流程卡住时**
   - 检查日志文件
   - 查看 next 配置
   - 增加 maxTimes
   - 添加 on_error_next

3. **性能优化**
   - 缩小 ROI 范围
   - 提高阈值
   - 减少不必要的延迟
   - 使用更快的识别算法

---

## 📞 获取帮助

### 问题排查顺序

1. **查看日志文件** `woa_automation.log`
2. **阅读错误信息**
3. **查阅文档相关章节**
4. **使用模板验证工具测试**
5. **检查配置文件语法**

### 常见问题快速链接

- [找不到设备](WOA_QUICKSTART.md#问题找不到设备)
- [模板识别不到](WOA_QUICKSTART.md#问题模板识别不到)
- [任务执行太快/太慢](WOA_QUICKSTART.md#问题任务执行太快太慢)
- [完整调试指南](docs/WOA_ADAPTATION_GUIDE.md#测试和调试)

---

## 🎉 成功案例

完成开发后，你将能够：

✅ 让脚本 24/7 自动运行
✅ 自动处理所有机场的所有飞机
✅ 自动处理特殊情况（跑道穿越、除冰等）
✅ 获得完整的执行日志
✅ 根据需要随时暂停/继续

---

## 📄 许可证

本项目基于 MaaAssistantWoA，遵循 AGPL-3.0 许可证。

---

## 🙏 致谢

感谢 MaaAssistantWoA 项目提供的优秀框架！

---

## 📮 反馈

如有问题或建议，欢迎：

- 📝 查看文档
- 🐛 提交 Issue
- 💬 参与讨论

---

**现在就开始吧！** 👉 [WOA_QUICKSTART.md](WOA_QUICKSTART.md)
