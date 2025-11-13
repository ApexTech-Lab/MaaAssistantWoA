#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模板验证工具
用于测试模板图片是否能在截图中正确识别
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional


class TemplateValidator:
    """模板验证器"""

    def __init__(self):
        self.screenshot = None
        self.template = None
        self.result = None

    def load_screenshot(self, screenshot_path: str) -> bool:
        """加载截图"""
        try:
            self.screenshot = cv2.imread(screenshot_path)
            if self.screenshot is None:
                print(f"❌ 无法加载截图: {screenshot_path}")
                return False

            h, w = self.screenshot.shape[:2]
            print(f"✅ 截图加载成功: {w}x{h}")
            return True

        except Exception as e:
            print(f"❌ 加载截图失败: {e}")
            return False

    def load_template(self, template_path: str) -> bool:
        """加载模板"""
        try:
            self.template = cv2.imread(template_path)
            if self.template is None:
                print(f"❌ 无法加载模板: {template_path}")
                return False

            h, w = self.template.shape[:2]
            print(f"✅ 模板加载成功: {w}x{h}")
            return True

        except Exception as e:
            print(f"❌ 加载模板失败: {e}")
            return False

    def match_template(self,
                      roi: Optional[Tuple[int, int, int, int]] = None,
                      threshold: float = 0.8,
                      method: int = cv2.TM_CCOEFF_NORMED) -> List[dict]:
        """
        执行模板匹配

        Args:
            roi: 感兴趣区域 (x, y, w, h)
            threshold: 匹配阈值
            method: OpenCV 匹配方法

        Returns:
            匹配结果列表
        """
        if self.screenshot is None or self.template is None:
            print("❌ 请先加载截图和模板")
            return []

        try:
            # 裁剪 ROI
            if roi:
                x, y, w, h = roi
                search_area = self.screenshot[y:y+h, x:x+w]
                offset_x, offset_y = x, y
            else:
                search_area = self.screenshot
                offset_x, offset_y = 0, 0

            # 模板匹配
            self.result = cv2.matchTemplate(search_area, self.template, method)

            # 查找所有匹配位置
            locations = np.where(self.result >= threshold)
            matches = []

            template_h, template_w = self.template.shape[:2]

            for pt in zip(*locations[::-1]):
                match = {
                    'x': pt[0] + offset_x,
                    'y': pt[1] + offset_y,
                    'w': template_w,
                    'h': template_h,
                    'score': self.result[pt[1], pt[0]]
                }
                matches.append(match)

            # 按分数排序
            matches.sort(key=lambda m: m['score'], reverse=True)

            # 非极大值抑制（NMS）- 去除重叠的检测
            matches = self._non_max_suppression(matches, 0.5)

            return matches

        except Exception as e:
            print(f"❌ 模板匹配失败: {e}")
            return []

    def _non_max_suppression(self, matches: List[dict], overlap_threshold: float = 0.5) -> List[dict]:
        """非极大值抑制"""
        if not matches:
            return []

        # 转换为 numpy 数组
        boxes = np.array([[m['x'], m['y'], m['x'] + m['w'], m['y'] + m['h']] for m in matches])
        scores = np.array([m['score'] for m in matches])

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h

            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= overlap_threshold)[0]
            order = order[inds + 1]

        return [matches[i] for i in keep]

    def visualize_matches(self,
                         matches: List[dict],
                         roi: Optional[Tuple[int, int, int, int]] = None,
                         output_path: str = "match_result.png") -> bool:
        """可视化匹配结果"""
        if self.screenshot is None:
            print("❌ 没有截图可以可视化")
            return False

        try:
            # 复制截图用于绘制
            result_img = self.screenshot.copy()

            # 绘制 ROI
            if roi:
                x, y, w, h = roi
                cv2.rectangle(result_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(result_img, "ROI", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # 绘制匹配结果
            for i, match in enumerate(matches):
                x, y, w, h = match['x'], match['y'], match['w'], match['h']
                score = match['score']

                # 绘制矩形
                cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # 绘制分数
                label = f"#{i+1}: {score:.3f}"
                cv2.putText(result_img, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 保存结果
            cv2.imwrite(output_path, result_img)
            print(f"✅ 结果已保存到: {output_path}")
            return True

        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            return False

    def validate(self,
                screenshot_path: str,
                template_path: str,
                roi: Optional[Tuple[int, int, int, int]] = None,
                threshold: float = 0.8,
                output_path: str = "match_result.png") -> bool:
        """
        完整的验证流程

        Args:
            screenshot_path: 截图路径
            template_path: 模板路径
            roi: ROI 区域 (x, y, w, h)
            threshold: 匹配阈值
            output_path: 输出图片路径

        Returns:
            是否找到匹配
        """
        print("="*60)
        print("模板验证工具")
        print("="*60)

        # 加载图片
        if not self.load_screenshot(screenshot_path):
            return False

        if not self.load_template(template_path):
            return False

        # 执行匹配
        print(f"\n🔍 开始匹配...")
        print(f"   ROI: {roi if roi else '全屏'}")
        print(f"   阈值: {threshold}")

        matches = self.match_template(roi=roi, threshold=threshold)

        # 显示结果
        print(f"\n📊 匹配结果:")
        if matches:
            print(f"   ✅ 找到 {len(matches)} 个匹配")
            for i, match in enumerate(matches):
                print(f"   #{i+1}: 位置=({match['x']}, {match['y']}), "
                      f"大小={match['w']}x{match['h']}, "
                      f"分数={match['score']:.3f}")
        else:
            print(f"   ❌ 未找到匹配")
            print(f"\n💡 建议:")
            print(f"   1. 降低阈值（当前: {threshold}）")
            print(f"   2. 检查模板是否清晰")
            print(f"   3. 确认 ROI 区域是否正确")
            print(f"   4. 尝试重新截取模板")

        # 可视化
        self.visualize_matches(matches, roi, output_path)

        print("\n" + "="*60)
        return len(matches) > 0


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='模板验证工具')
    parser.add_argument('screenshot', help='截图路径')
    parser.add_argument('template', help='模板路径')
    parser.add_argument('--roi', nargs=4, type=int, metavar=('X', 'Y', 'W', 'H'),
                       help='ROI 区域 (x y w h)')
    parser.add_argument('--threshold', type=float, default=0.8,
                       help='匹配阈值 (默认: 0.8)')
    parser.add_argument('--output', default='match_result.png',
                       help='输出图片路径 (默认: match_result.png)')

    args = parser.parse_args()

    # 验证文件存在
    if not Path(args.screenshot).exists():
        print(f"❌ 截图文件不存在: {args.screenshot}")
        return 1

    if not Path(args.template).exists():
        print(f"❌ 模板文件不存在: {args.template}")
        return 1

    # ROI 处理
    roi = tuple(args.roi) if args.roi else None

    # 执行验证
    validator = TemplateValidator()
    success = validator.validate(
        screenshot_path=args.screenshot,
        template_path=args.template,
        roi=roi,
        threshold=args.threshold,
        output_path=args.output
    )

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
