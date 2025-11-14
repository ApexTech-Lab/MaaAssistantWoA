// <copyright file="WOAAirportViewModel.cs" company="MaaAssistantArknights">
// Part of the MaaWpfGui project, maintained by the MaaAssistantArknights team (Maa Team)
// Copyright (C) 2021-2025 MaaAssistantArknights Contributors
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License v3.0 only as published by
// the Free Software Foundation, either version 3 of the License, or
// any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY
// </copyright>

#nullable enable
using System.Collections.Generic;
using System.Threading.Tasks;
using JetBrains.Annotations;
using MaaWpfGui.Constants;
using MaaWpfGui.Helper;
using MaaWpfGui.Main;
using MaaWpfGui.Models;
using MaaWpfGui.Models.AsstTasks;
using MaaWpfGui.States;
using MaaWpfGui.Utilities.ValueType;
using Serilog;
using Stylet;

namespace MaaWpfGui.ViewModels.UI
{
    /// <summary>
    /// The view model for World of Airports automation.
    /// </summary>
    public class WOAAirportViewModel : Screen
    {
        private readonly RunningState _runningState;
        private static readonly ILogger _logger = Log.ForContext<WOAAirportViewModel>();

        /// <summary>
        /// Initializes a new instance of the <see cref="WOAAirportViewModel"/> class.
        /// </summary>
        public WOAAirportViewModel()
        {
            DisplayName = "WOA 机场管理";
            _runningState = RunningState.Instance;
            _runningState.StateChanged += (__, e) =>
            {
                Idle = e.Idle;
                Inited = e.Inited;
                Stopping = e.Stopping;
            };
        }

        private bool _idle = true;

        /// <summary>
        /// Gets or sets a value indicating whether it is idle.
        /// </summary>
        public bool Idle
        {
            get => _idle;
            set => SetAndNotify(ref _idle, value);
        }

        private bool _inited;

        /// <summary>
        /// Gets or sets a value indicating whether it is inited.
        /// </summary>
        public bool Inited
        {
            get => _inited;
            set => SetAndNotify(ref _inited, value);
        }

        private bool _stopping;

        /// <summary>
        /// Gets or sets a value indicating whether it is stopping.
        /// </summary>
        public bool Stopping
        {
            get => _stopping;
            set => SetAndNotify(ref _stopping, value);
        }

        /// <summary>
        /// Gets the list of available airports.
        /// </summary>
        public List<CombinedData> AirportList { get; } = new()
        {
            new() { Display = "BRI - 巴里岛", Value = "BRI" },
            new() { Display = "PRG - 布拉格", Value = "PRG" },
            new() { Display = "BKK - 曼谷", Value = "BKK" },
            new() { Display = "MSY - 新奥尔良", Value = "MSY" },
            new() { Display = "IAD - 华盛顿", Value = "IAD" },
        };

        private string _selectedAirport = ConfigurationHelper.GetValue(ConfigurationKeys.WOASelectedAirport, "BRI");

        /// <summary>
        /// Gets or sets the selected airport.
        /// </summary>
        public string SelectedAirport
        {
            get => _selectedAirport;
            set
            {
                SetAndNotify(ref _selectedAirport, value);
                ConfigurationHelper.SetValue(ConfigurationKeys.WOASelectedAirport, value);
                _logger.Information("Selected airport changed to: {Airport}", value);
            }
        }

        private string _statusInfo = "准备就绪。选择机场后点击\"开始\"按钮启动自动化。";

        /// <summary>
        /// Gets or sets the status info.
        /// </summary>
        public string StatusInfo
        {
            get => _statusInfo;
            set => SetAndNotify(ref _statusInfo, value);
        }

        private bool _enableCrewAssignment = true;

        /// <summary>
        /// Gets or sets a value indicating whether crew assignment is enabled.
        /// </summary>
        public bool EnableCrewAssignment
        {
            get => _enableCrewAssignment;
            set
            {
                SetAndNotify(ref _enableCrewAssignment, value);
                ConfigurationHelper.SetValue(ConfigurationKeys.WOAEnableCrewAssignment, value.ToString());
            }
        }

        private bool _enableSpecialOperations = true;

        /// <summary>
        /// Gets or sets a value indicating whether special operations (crossing, deicing) are enabled.
        /// </summary>
        public bool EnableSpecialOperations
        {
            get => _enableSpecialOperations;
            set
            {
                SetAndNotify(ref _enableSpecialOperations, value);
                ConfigurationHelper.SetValue(ConfigurationKeys.WOAEnableSpecialOperations, value.ToString());
            }
        }

        /// <summary>
        /// Starts the WOA automation task.
        /// UI 绑定的方法
        /// </summary>
        /// <returns>Task</returns>
        [UsedImplicitly]
        public async Task LinkStart()
        {
            if (!Idle)
            {
                await Stop();
                return;
            }

            _runningState.SetIdle(false);
            StatusInfo = "正在连接模拟器...";

            string errMsg = string.Empty;
            bool connected = await Task.Run(() => Instances.AsstProxy.AsstConnect(ref errMsg));

            if (!connected)
            {
                StatusInfo = $"连接失败: {errMsg}";
                _runningState.SetIdle(true);
                return;
            }

            StatusInfo = $"已连接。开始处理机场: {SelectedAirport}";

            // Create and append WOA task
            var taskParams = new Newtonsoft.Json.Linq.JObject
            {
                ["airport"] = SelectedAirport,
                ["enable_crew"] = EnableCrewAssignment,
                ["enable_special"] = EnableSpecialOperations,
            };

            bool ret = Instances.AsstProxy.AsstAppendTaskWithEncoding(
                AsstProxy.TaskType.WOAAirport,
                Services.AsstTaskType.WOAAirport,
                taskParams);

            if (!ret)
            {
                StatusInfo = "添加任务失败";
                _runningState.SetIdle(true);
                return;
            }

            ret = Instances.AsstProxy.AsstStart();

            if (!ret)
            {
                StatusInfo = "启动任务失败";
                _runningState.SetIdle(true);
                return;
            }

            _logger.Information("WOA automation started for airport: {Airport}", SelectedAirport);
        }

        /// <summary>
        /// Stops the current task.
        /// </summary>
        /// <returns>Task</returns>
        public async Task Stop()
        {
            _runningState.SetStopping(true);
            StatusInfo = "正在停止...";

            await Task.Run(() => Instances.AsstProxy.AsstStop());

            await Task.Delay(100);
            _runningState.SetIdle(true);
            StatusInfo = "已停止";
            _logger.Information("WOA automation stopped");
        }

        /// <summary>
        /// Processes WOA-specific messages from the callback.
        /// </summary>
        /// <param name="details">The message details</param>
        public void ProcWOAMsg(Newtonsoft.Json.Linq.JObject details)
        {
            string? what = details["what"]?.ToString();
            var subTaskDetails = details["details"];

            switch (what)
            {
                case "WOAAirportEntered":
                    {
                        string? airport = subTaskDetails?["airport"]?.ToString();
                        StatusInfo = $"已进入机场: {airport}";
                    }
                    break;

                case "WOAAircraftFound":
                    {
                        int count = (int)(subTaskDetails?["count"] ?? 0);
                        StatusInfo = $"发现 {count} 架需要处理的飞机";
                    }
                    break;

                case "WOACrewAssigned":
                    {
                        string? model = subTaskDetails?["model"]?.ToString();
                        int crew = (int)(subTaskDetails?["crew"] ?? 0);
                        StatusInfo = $"已为 {model} 分配 {crew} 名地勤";
                    }
                    break;

                case "WOACrewInsufficient":
                    {
                        string? model = subTaskDetails?["model"]?.ToString();
                        int required = (int)(subTaskDetails?["required"] ?? 0);
                        int available = (int)(subTaskDetails?["available"] ?? 0);
                        StatusInfo = $"地勤不足: {model} 需要 {required} 人，可用 {available} 人";
                    }
                    break;

                case "WOATaskCompleted":
                    {
                        StatusInfo = "所有任务已完成";
                    }
                    break;

                case "WOAError":
                    {
                        string? error = subTaskDetails?["message"]?.ToString();
                        StatusInfo = $"错误: {error}";
                    }
                    break;
            }
        }
    }
}
