#pragma once

#include "InterfaceTask.h"
#include <string>
#include <unordered_map>

namespace asst
{
    /**
     * @brief World of Airports 自动化任务类
     *
     * 实现了复杂的地勤分配逻辑和机场切换功能
     * 基于原 Python 代码（game.py 和 app.py）
     */
    class WOAAirportTask final : public InterfaceTask
    {
    public:
        inline static constexpr std::string_view TaskType = "WOAAirport";

        using InterfaceTask::InterfaceTask;
        virtual ~WOAAirportTask() override = default;

        virtual bool _run() override;

        // 设置选中的机场
        void set_selected_airport(const std::string& airport);

    private:
        // ===== 地勤分配相关 =====

        /**
         * @brief 检查并分配地勤（对应 Python 的 assign_crew_with_check）
         * @return true 如果成功分配，false 如果地勤不足跳过
         */
        bool check_and_assign_crew();

        /**
         * @brief OCR 解析可用地勤数量
         * @param image 当前截图
         * @return 可用地勤数量，失败返回 0
         */
        int parse_available_crew(const cv::Mat& image);

        /**
         * @brief OCR 识别飞机机型
         * @param image 当前截图
         * @return 机型字符串
         */
        std::string recognize_aircraft_model(const cv::Mat& image);

        /**
         * @brief 根据机型获取所需地勤数（对应 Python 的 find_crew_need）
         * @param model 机型字符串（可能包含 OCR 错误）
         * @return 所需地勤数量
         */
        int get_required_crew(const std::string& model);

        /**
         * @brief 模糊匹配机型（对应 Python 的 fuzzy_match_model 和 rapidfuzz）
         * @param ocr_result OCR 识别结果
         * @return 匹配后的标准机型名称
         */
        std::string fuzzy_match_model(const std::string& ocr_result);

        /**
         * @brief 执行地勤分配操作（对应 Python 的 perform_sequence_from_auto_sh）
         * @return true 成功，false 失败
         */
        bool perform_crew_assignment();

        // ===== 机场切换相关 =====

        /**
         * @brief 进入选中的机场（对应 Python 的 enter_airport）
         * @param airport_code 机场代码（BRI, PRG, BKK, MSY, IAD）
         * @return true 成功，false 失败
         */
        bool enter_selected_airport(const std::string& airport_code);

        /**
         * @brief 切换到指定机场
         * @param airport_code 机场代码
         * @return true 成功，false 失败
         */
        bool change_to_airport(const std::string& airport_code);

        // ===== 视角调整 =====

        /**
         * @brief 调整游戏视角（对应 Python 的 change_vision）
         * @return true 成功，false 失败
         */
        bool change_vision();

        // ===== 数据表 =====

        // 机型-地勤映射表（对应 Python 的 CREW_BIND）
        static const std::unordered_map<std::string, int> crew_binding;

        // OCR 常见错误修正表（对应 Python 的 COMMON_FIXES）
        static const std::unordered_map<std::string, std::string> ocr_fixes;

        // 当前选中的机场
        std::string m_selected_airport = "BRI";
    };
}
