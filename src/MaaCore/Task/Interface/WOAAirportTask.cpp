#include "WOAAirportTask.h"

#include "Controller/Controller.h"
#include "Task/ProcessTask.h"
#include "Utils/Logger.hpp"
#include "Vision/OCRer.h"
#include "Vision/Matcher.h"

#include <regex>
#include <algorithm>
#include <cctype>

namespace asst
{
    // 机型-地勤映射表（对应 Python 的 CREW_BIND）
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

    // OCR 常见错误修正表（对应 Python 的 COMMON_FIXES）
    const std::unordered_map<std::string, std::string> WOAAirportTask::ocr_fixes = {
        {"B7W", "B77W"}, {"A3BB", "A388"}, {"A38B", "A388"}, {"A337", "A332"},
        {"B783", "B789"}, {"AIN", "A21N"}, {"AINX", "A21NX"}, {"A2ON", "A20N"},
        {"ANY", "A21NY"}, {"AN", "A21N"}, {"ANX", "A21NX"},
        {"B7IW", "B77W"}, {"EI5", "E175"}, {"EI0", "E170"}, {"EIO", "E170"},
        {"CRI9", "CRJ9"}, {"CRI7", "CRJ7"}, {"CRI2", "CRJ2"}, {"CRIX", "CRJX"},
        {"FIQO", "F100"}, {"FI0", "F100"}, {"B739", "B789"}
    };

    WOAAirportTask::WOAAirportTask(const AsstCallback& callback, Assistant* inst)
        : InterfaceTask(callback, inst, TaskType)
    {
        LogTraceFunction;
    }

    bool WOAAirportTask::set_params(const json::value& params)
    {
        LogTraceFunction;

        auto airport_opt = params.find<std::string>("airport");
        if (airport_opt) {
            m_selected_airport = *airport_opt;
            Log.info("Selected airport:", m_selected_airport);
        }

        return true;
    }

    bool WOAAirportTask::_run()
    {
        LogTraceFunction;

        // 使用 ProcessTask 执行主流程
        ProcessTask process_task(*this, { "WOA_Start" });
        process_task.set_retry_times(9999);  // 持续运行

        return process_task.run();
    }

    void WOAAirportTask::set_selected_airport(const std::string& airport)
    {
        m_selected_airport = airport;
        Log.info(__FUNCTION__, "Selected airport set to:", airport);
    }

    std::string WOAAirportTask::fuzzy_match_model(const std::string& ocr_result)
    {
        LogTraceFunction;

        // 1. 规范化：去空格、转大写
        std::string normalized = ocr_result;
        normalized.erase(
            std::remove_if(normalized.begin(), normalized.end(),
                [](unsigned char c) { return std::isspace(c); }),
            normalized.end()
        );
        std::transform(normalized.begin(), normalized.end(),
                      normalized.begin(), ::toupper);

        Log.trace(__FUNCTION__, "OCR result:", ocr_result, "-> Normalized:", normalized);

        // 2. 先检查常见错误修正表
        auto fix_it = ocr_fixes.find(normalized);
        if (fix_it != ocr_fixes.end()) {
            normalized = fix_it->second;
            Log.info(__FUNCTION__, "Applied OCR fix:", ocr_result, "->", normalized);
        }

        // 3. 精确匹配
        if (crew_binding.find(normalized) != crew_binding.end()) {
            Log.info(__FUNCTION__, "Exact match found:", normalized);
            return normalized;
        }

        // 4. 模糊匹配（简单的编辑距离算法）
        int min_distance = 999;
        std::string best_match;

        for (const auto& [model, _] : crew_binding) {
            // 计算编辑距离
            int distance = std::abs(static_cast<int>(normalized.size()) - static_cast<int>(model.size()));

            // 计算不同字符数
            size_t min_len = std::min(normalized.size(), model.size());
            for (size_t i = 0; i < min_len; ++i) {
                if (normalized[i] != model[i]) {
                    distance++;
                }
            }

            if (distance < min_distance) {
                min_distance = distance;
                best_match = model;
            }
        }

        // 如果最小距离小于阈值（2），认为是匹配成功
        if (min_distance <= 2) {
            Log.info(__FUNCTION__, "Fuzzy matched:", ocr_result, "->", best_match,
                    "(distance:", min_distance, ")");
            return best_match;
        }

        // 默认返回原始规范化值
        Log.warn(__FUNCTION__, "No match found for:", ocr_result, ", using normalized:", normalized);
        return normalized;
    }

    int WOAAirportTask::get_required_crew(const std::string& model)
    {
        LogTraceFunction;

        std::string matched_model = fuzzy_match_model(model);

        auto it = crew_binding.find(matched_model);
        if (it != crew_binding.end()) {
            Log.info(__FUNCTION__, "Model:", matched_model, "requires", it->second, "crew");
            return it->second;
        }

        Log.warn(__FUNCTION__, "Unknown model:", model, ", using default 20 crew");
        return 20;  // 默认值（对应 Python 代码）
    }

    std::string WOAAirportTask::recognize_aircraft_model(const cv::Mat& image)
    {
        LogTraceFunction;

        // OCR 区域：(224, 444, 321, 489) - 对应 Python 代码
        OCRer ocr(image);
        ocr.set_roi(Rect(224, 444, 321 - 224, 489 - 444));

        if (!ocr.analyze()) {
            Log.error(__FUNCTION__, "OCR failed for aircraft model");
            return "";
        }

        const auto& results = ocr.get_result();
        if (results.empty()) {
            Log.warn(__FUNCTION__, "No OCR results for aircraft model");
            return "";
        }

        std::string model = results[0].text;
        Log.info(__FUNCTION__, "Recognized aircraft model:", model);
        return model;
    }

    int WOAAirportTask::parse_available_crew(const cv::Mat& image)
    {
        LogTraceFunction;

        // OCR 区域：(1085, 826, 1338, 885) - 对应 Python 代码
        OCRer ocr(image);
        ocr.set_roi(Rect(1085, 826, 1338 - 1085, 885 - 826));

        if (!ocr.analyze()) {
            Log.error(__FUNCTION__, "OCR failed for crew count");
            return 0;
        }

        const auto& results = ocr.get_result();
        if (results.empty()) {
            Log.warn(__FUNCTION__, "No OCR results for crew count");
            return 0;
        }

        std::string text = results[0].text;
        Log.trace(__FUNCTION__, "OCR text for crew:", text);

        // 使用正则表达式提取末尾的数字（对应 Python: re.search(r'(\d+)$', crew_text)）
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

        /*
         * 对应 Python 的 perform_sequence_from_auto_sh 函数：
         * def perform_sequence_from_auto_sh(x1=793, y1=919, x2=1222, y2=919,
         *                                  p3x=1289, p3y=1040, p4x=394, p4y=1303,
         *                                  drag_ms=500, gap1=0.5, gap2=0.5):
         *     swipe(x1, y1, x2, y2, drag_ms)
         *     time.sleep(gap1)
         *     click(p3x, p3y)
         *     time.sleep(gap2)
         *     click(p4x, p4y)
         */

        // 1. 滑动地勤进度条到最大
        Point start(793, 919);
        Point end(1222, 919);
        int duration = 500;

        Log.info(__FUNCTION__, "Sliding crew assignment bar from", start, "to", end);
        ctrler()->swipe(start, end, duration);
        sleep(500);  // gap1 = 0.5s

        // 2. 点击第一个确认按钮
        Point confirm1(1289, 1040);
        Log.info(__FUNCTION__, "Clicking first confirm button at", confirm1);
        ctrler()->click(confirm1);
        sleep(500);  // gap2 = 0.5s

        // 3. 点击第二个确认按钮
        Point confirm2(394, 1303);
        Log.info(__FUNCTION__, "Clicking second confirm button at", confirm2);
        ctrler()->click(confirm2);

        Log.info(__FUNCTION__, "Crew assigned successfully");
        return true;
    }

    bool WOAAirportTask::check_and_assign_crew()
    {
        LogTraceFunction;

        cv::Mat image = ctrler()->get_image();

        // 1. 识别可用地勤数量
        int available = parse_available_crew(image);
        if (available == 0) {
            Log.error(__FUNCTION__, "Failed to parse available crew, skipping");
            return false;
        }

        // 2. 识别机型
        std::string model = recognize_aircraft_model(image);
        if (model.empty()) {
            Log.error(__FUNCTION__, "Failed to recognize aircraft model, skipping");
            return false;
        }

        // 3. 获取所需地勤数
        int required = get_required_crew(model);

        // 4. 判断是否足够（对应 Python 的条件判断）
        if (available < required) {
            Log.info(__FUNCTION__, "Insufficient crew. Need:", required,
                    "Available:", available, "- Skipping this aircraft");
            return false;  // 跳过此飞机，返回 false 让流程继续
        }

        // 5. 地勤足够，执行分配
        Log.info(__FUNCTION__, "Sufficient crew. Need:", required,
                "Available:", available, "- Assigning crew");
        return perform_crew_assignment();
    }

    bool WOAAirportTask::enter_selected_airport(const std::string& airport_code)
    {
        LogTraceFunction;

        Log.info(__FUNCTION__, "Entering airport:", airport_code);

        // 先打开机场列表
        ProcessTask open_list(*this, { "WOA_EnterAirportList" });
        if (!open_list.run()) {
            Log.error(__FUNCTION__, "Failed to open airport list");
            return false;
        }

        // 根据机场代码执行相应的选择流程
        std::string task_name = "WOA_SelectAirport_" + airport_code;
        ProcessTask select_airport(*this, { task_name });

        return select_airport.run();
    }

    bool WOAAirportTask::change_to_airport(const std::string& airport_code)
    {
        LogTraceFunction;

        Log.info(__FUNCTION__, "Changing to airport:", airport_code);

        // 对应 Python 的 change_airport 函数：
        // click(100, 85)  # 返回
        // time.sleep(1)
        // click(1622, 594)  # 确认
        // time.sleep(5)
        // click(95, 104)   # 返回主界面
        // time.sleep(5)

        ctrler()->click(Point(100, 85));
        sleep(1000);

        ctrler()->click(Point(1622, 594));
        sleep(5000);

        ctrler()->click(Point(95, 104));
        sleep(5000);

        // 然后进入新机场
        return enter_selected_airport(airport_code);
    }

    bool WOAAirportTask::change_vision()
    {
        LogTraceFunction;

        /*
         * 对应 Python 的 change_vision 函数：
         * def change_vision():
         *     time.sleep(10)
         *     click(2467,72)
         *     time.sleep(2)
         *     click(2467,723)
         *     time.sleep(2)
         *     click(2467,72)
         *     time.sleep(2)
         *     click(1858,75)
         *     time.sleep(2)
         */

        sleep(10000);

        ctrler()->click(Point(2467, 72));
        sleep(2000);

        ctrler()->click(Point(2467, 723));
        sleep(2000);

        ctrler()->click(Point(2467, 72));
        sleep(2000);

        ctrler()->click(Point(1858, 75));
        sleep(2000);

        Log.info(__FUNCTION__, "Vision changed successfully");
        return true;
    }

} // namespace asst
