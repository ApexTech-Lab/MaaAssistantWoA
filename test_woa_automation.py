#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
World of Airports 自动化测试脚本
基于 MaaAssistantWoA 框架
"""

import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional

# 添加 MAA Python 接口路径
sys.path.append(str(Path(__file__).parent / 'src' / 'Python'))

try:
    from asst.asst import Asst
    from asst.utils import Message
except ImportError:
    print("❌ 无法导入 MAA Python 接口")
    print("请确保项目已正确编译并且 Python 接口可用")
    sys.exit(1)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('woa_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WOAAutomation:
    """World of Airports 自动化控制器"""

    def __init__(self, resource_path: str = "resource/woa"):
        self.asst: Optional[Asst] = None
        self.resource_path = Path(resource_path)
        self.task_count = 0
        self.error_count = 0

    def callback(self, msg: int, details: str, arg):
        """MAA 回调函数"""
        try:
            msg_type = Message(msg)
            detail_obj = json.loads(details)

            # 根据消息类型处理
            if msg_type == Message.InternalError:
                logger.error(f"❌ 内部错误: {detail_obj}")
                self.error_count += 1

            elif msg_type == Message.InitFailed:
                logger.error(f"❌ 初始化失败: {detail_obj}")
                self.error_count += 1

            elif msg_type == Message.ConnectionInfo:
                what = detail_obj.get('what', '')
                uuid = detail_obj.get('uuid', 'N/A')
                details_info = detail_obj.get('details', {})

                if what == 'Connected':
                    logger.info(f"✅ 设备连接成功")
                    logger.info(f"   UUID: {uuid}")
                    logger.info(f"   分辨率: {details_info.get('width', '?')}x{details_info.get('height', '?')}")
                elif what == 'UnsupportedResolution':
                    logger.warning(f"⚠️  分辨率不支持: {details_info}")
                elif what == 'ResolutionError':
                    logger.error(f"❌ 分辨率错误: {details_info}")

            elif msg_type == Message.AllTasksCompleted:
                logger.info("✅ 所有任务完成")

            elif msg_type == Message.TaskChainError:
                task_chain = detail_obj.get('taskchain', 'Unknown')
                logger.error(f"❌ 任务链错误: {task_chain}")
                self.error_count += 1

            elif msg_type == Message.TaskChainStart:
                task_chain = detail_obj.get('taskchain', 'Unknown')
                uuid = detail_obj.get('uuid', 'N/A')
                logger.info(f"🚀 开始任务链: {task_chain}")

            elif msg_type == Message.TaskChainCompleted:
                task_chain = detail_obj.get('taskchain', 'Unknown')
                logger.info(f"✅ 任务链完成: {task_chain}")

            elif msg_type == Message.SubTaskStart:
                subtask = detail_obj.get('subtask', 'Unknown')
                logger.debug(f"  → 开始子任务: {subtask}")

            elif msg_type == Message.SubTaskCompleted:
                subtask = detail_obj.get('subtask', 'Unknown')
                self.task_count += 1
                logger.info(f"  ✓ 子任务完成: {subtask}")

            elif msg_type == Message.SubTaskError:
                subtask = detail_obj.get('subtask', 'Unknown')
                why = detail_obj.get('why', 'Unknown')
                logger.warning(f"  ✗ 子任务失败: {subtask} - {why}")

            elif msg_type == Message.SubTaskExtraInfo:
                # 额外信息，如识别结果
                subtask = detail_obj.get('subtask', 'Unknown')
                what = detail_obj.get('what', '')
                details_info = detail_obj.get('details', {})
                logger.debug(f"  ℹ {subtask}: {what} - {details_info}")

        except Exception as e:
            logger.error(f"回调函数错误: {e}")

    def initialize(self) -> bool:
        """初始化 MAA"""
        logger.info("="*60)
        logger.info("World of Airports 自动化脚本")
        logger.info("="*60)

        try:
            # 创建 Asst 实例
            logger.info("📦 创建 Asst 实例...")
            self.asst = Asst(callback=self.callback)

            # 加载资源
            logger.info(f"📂 加载资源: {self.resource_path}")
            if not self.resource_path.exists():
                logger.error(f"❌ 资源路径不存在: {self.resource_path}")
                return False

            if not self.asst.load_resource(str(self.resource_path)):
                logger.error("❌ 资源加载失败")
                return False

            logger.info("✅ 资源加载成功")
            return True

        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            return False

    def connect_device(self, adb_path: str = "adb",
                      address: str = "127.0.0.1:5555",
                      config: str = "General") -> bool:
        """连接设备"""
        try:
            logger.info(f"🔗 连接设备...")
            logger.info(f"   ADB 路径: {adb_path}")
            logger.info(f"   设备地址: {address}")
            logger.info(f"   配置: {config}")

            # 异步连接
            async_id = self.asst.async_connect(adb_path, address, config, block=True)

            if async_id == 0:
                logger.error("❌ 设备连接失败")
                return False

            # 等待连接完成
            time.sleep(2)

            if not self.asst.connected():
                logger.error("❌ 设备未连接")
                return False

            logger.info("✅ 设备连接成功")
            return True

        except Exception as e:
            logger.error(f"❌ 连接设备失败: {e}")
            return False

    def run_task(self, task_name: str, params: Optional[dict] = None) -> bool:
        """运行单个任务"""
        try:
            if params is None:
                params = {}

            # 默认使用 ProcessTask
            task_type = params.pop('task_type', 'ProcessTask')

            # 设置任务名称
            if 'task_names' not in params:
                params['task_names'] = [task_name]

            logger.info(f"📋 添加任务: {task_name}")
            logger.debug(f"   参数: {json.dumps(params, ensure_ascii=False)}")

            # 添加任务
            task_id = self.asst.append_task(task_type, params)

            if task_id == 0:
                logger.error("❌ 任务添加失败")
                return False

            logger.info(f"✅ 任务添加成功 (ID: {task_id})")

            # 开始执行
            logger.info("🚀 开始执行任务...")
            self.asst.start()

            # 等待完成
            while self.asst.running():
                time.sleep(1)

            logger.info("✅ 任务执行完成")
            return True

        except Exception as e:
            logger.error(f"❌ 任务执行失败: {e}")
            return False

    def run_full_automation(self) -> bool:
        """运行完整的自动化流程"""
        try:
            logger.info("="*60)
            logger.info("开始完整自动化流程")
            logger.info("="*60)

            # 运行主任务
            params = {
                'task_names': ['WOA_Start']
            }

            return self.run_task('WOA_Start', params)

        except Exception as e:
            logger.error(f"❌ 自动化流程失败: {e}")
            return False

    def print_summary(self):
        """打印执行摘要"""
        logger.info("="*60)
        logger.info("执行摘要")
        logger.info("="*60)
        logger.info(f"✅ 完成任务数: {self.task_count}")
        logger.info(f"❌ 错误数: {self.error_count}")
        logger.info("="*60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='World of Airports 自动化脚本')
    parser.add_argument('--resource', default='resource/woa',
                       help='资源路径 (默认: resource/woa)')
    parser.add_argument('--adb', default='adb',
                       help='ADB 可执行文件路径 (默认: adb)')
    parser.add_argument('--address', default='127.0.0.1:5555',
                       help='设备地址 (默认: 127.0.0.1:5555)')
    parser.add_argument('--config', default='General',
                       help='连接配置 (默认: General)')
    parser.add_argument('--task', default='WOA_Start',
                       help='要运行的任务名称 (默认: WOA_Start)')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试日志')

    args = parser.parse_args()

    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # 创建自动化控制器
    automation = WOAAutomation(resource_path=args.resource)

    # 初始化
    if not automation.initialize():
        logger.error("初始化失败，退出")
        return 1

    # 连接设备
    if not automation.connect_device(
        adb_path=args.adb,
        address=args.address,
        config=args.config
    ):
        logger.error("设备连接失败，退出")
        return 1

    # 运行任务
    success = automation.run_full_automation()

    # 打印摘要
    automation.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ 未处理的异常: {e}", exc_info=True)
        sys.exit(1)
