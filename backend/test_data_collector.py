#!/usr/bin/env python3
"""
MCU-Copilot 测试数据收集器
分离数据收集与HTML渲染，便于调整渲染逻辑
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os

# 测试用例定义
TEST_CASES = [
    # 简单级别 (5个)
    {
        "id": "T01",
        "level": "简单",
        "requirement": "控制LED P03引脚闪烁：500ms开，500ms关",
        "expected_features": ["LED控制", "定时延时", "引脚切换", "循环控制"]
    },
    {
        "id": "T02",
        "level": "简单",
        "requirement": "控制P05引脚输出高电平，点亮LED",
        "expected_features": ["IO配置", "引脚输出", "LED控制", "基础初始化"]
    },
    {
        "id": "T03",
        "level": "简单",
        "requirement": "读取P01引脚按键状态，按下时P02引脚输出高电平",
        "expected_features": ["按键输入", "IO配置", "条件控制", "引脚读取"]
    },
    {
        "id": "T04",
        "level": "简单",
        "requirement": "实现0-99循环计数器，每次计数间隔100ms",
        "expected_features": ["计数器", "循环控制", "延时控制", "变量操作"]
    },
    {
        "id": "T05",
        "level": "简单",
        "requirement": "初始化所有IO端口为输出模式，输出0x1234",
        "expected_features": ["IO初始化", "多位输出", "十六进制常数", "端口配置"]
    },

    # 中级级别 (4个)
    {
        "id": "T06",
        "level": "中级",
        "requirement": "实现4个LED(P00-P03)跑马灯效果，每个LED亮100ms后切换到下一个",
        "expected_features": ["多LED控制", "状态切换", "精确定时", "循环状态机"]
    },
    {
        "id": "T07",
        "level": "中级",
        "requirement": "按键P12防抖处理：长按1秒后每100ms计数+1，松开清零计数器",
        "expected_features": ["按键防抖", "长按检测", "定时器管理", "状态记录"]
    },
    {
        "id": "T08",
        "level": "中级",
        "requirement": "读取ADC通道0模拟量，当值大于512时点亮P10 LED，小于等于512时熄灭",
        "expected_features": ["ADC配置", "模拟量读取", "阈值比较", "条件控制"]
    },
    {
        "id": "T09",
        "level": "中级",
        "requirement": "实现交通灯状态机：红灯5秒->绿灯3秒->黄灯2秒循环，使用P00(红)P01(绿)P02(黄)",
        "expected_features": ["状态机设计", "多状态定时", "LED控制", "时序控制"]
    },

    # 困难级别 (1个)
    {
        "id": "T10",
        "level": "困难",
        "requirement": "数码管显示系统：按键P12增加计数(0-99)，按键P13减少计数，数码管实时显示当前值，支持按键防抖和数码管查表显示",
        "expected_features": ["数码管驱动", "双按键处理", "防抖算法", "查表显示", "完整交互系统"]
    }
]

class TestDataCollector:
    def __init__(self, base_url="http://localhost:8000", data_dir="test_data"):
        self.base_url = base_url
        self.data_dir = data_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = f"test_session_{self.timestamp}"

        # 创建数据目录
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例并保存原始数据"""
        print(f"🧪 运行测试 {test_case['id']}: {test_case['requirement'][:50]}...")

        start_time = time.time()
        test_result = {
            "test_case": test_case,
            "timestamp": datetime.now().isoformat(),
            "session_name": self.session_name,
            "success": False,
            "duration": 0,
            "request": {},
            "response": {},
            "raw_response": "",
            "error": None
        }

        try:
            # 准备请求数据
            request_data = {"requirement": test_case["requirement"]}
            test_result["request"] = {
                "url": f"{self.base_url}/compile?use_gemini=true",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": request_data
            }

            # 调用API
            response = requests.post(
                f"{self.base_url}/compile?use_gemini=true",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=120
            )

            test_result["duration"] = time.time() - start_time
            test_result["raw_response"] = response.text

            if response.status_code == 200:
                result = response.json()
                test_result["response"] = result
                test_result["success"] = True

                # 分析和评分
                test_result["analysis"] = self._analyze_result(test_case, result)

                status = "✅ 成功" if result.get("machine_code") else "❌ 编译失败"
                print(f"   {status} - 耗时: {test_result['duration']:.1f}s - 评分: {test_result['analysis']['score']}/100")

            else:
                test_result["error"] = f"HTTP {response.status_code}: {response.text}"
                test_result["analysis"] = {"score": 0, "details": "API调用失败"}
                print(f"   ❌ API调用失败: {response.status_code}")

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            test_result["analysis"] = {"score": 0, "details": f"异常: {e}"}
            print(f"   ❌ 测试异常: {e}")

        # 保存单个测试结果
        self._save_single_test_result(test_result)
        return test_result

    def _analyze_result(self, test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试结果"""
        analysis = {
            "score": 0,
            "details": {},
            "quality_check": {}
        }

        # 基础分：有汇编代码输出 (30分)
        if result.get("assembly"):
            analysis["score"] += 30
            analysis["details"]["has_assembly"] = True
        else:
            analysis["details"]["has_assembly"] = False

        # 编译成功 (40分)
        if result.get("machine_code") and not result.get("compile_error"):
            analysis["score"] += 40
            analysis["details"]["compile_success"] = True
            analysis["details"]["machine_code_count"] = len(result.get("machine_code", []))
        else:
            analysis["details"]["compile_success"] = False
            analysis["details"]["compile_error"] = result.get("compile_error")

        # 思考过程完整性 (15分)
        thought = result.get("thought", "")
        thought_length = len(thought)
        if thought_length > 200:
            analysis["score"] += 15
        elif thought_length > 100:
            analysis["score"] += 10
        elif thought_length > 50:
            analysis["score"] += 5

        analysis["details"]["thought_length"] = thought_length

        # 代码质量检查 (15分)
        assembly = result.get("assembly", "")
        quality_checks = {
            "has_data_section": "DATA" in assembly and "ENDDATA" in assembly,
            "has_code_section": "CODE" in assembly and "ENDCODE" in assembly,
            "uses_ldins": "LDINS" in assembly,
            "has_comments": ";" in assembly,
            "uppercase_style": assembly.isupper() or any(word.isupper() for word in assembly.split()),
        }

        analysis["quality_check"] = quality_checks
        quality_score = sum(quality_checks.values()) * 3
        analysis["score"] += quality_score

        analysis["score"] = min(analysis["score"], 100)
        return analysis

    def _save_single_test_result(self, test_result: Dict[str, Any]):
        """保存单个测试结果"""
        filename = f"{self.data_dir}/{self.session_name}_{test_result['test_case']['id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, indent=2, ensure_ascii=False)

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """运行所有测试用例"""
        print(f"🚀 开始收集测试数据...")
        print(f"📊 会话名称: {self.session_name}")
        print(f"💾 数据保存目录: {self.data_dir}/")
        print("=" * 60)

        all_results = []

        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"[{i}/{len(TEST_CASES)}]", end=" ")
            result = self.run_single_test(test_case)
            all_results.append(result)

            # 测试间隔
            if i < len(TEST_CASES):
                time.sleep(1)

        # 保存汇总数据
        summary_data = {
            "session_name": self.session_name,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(TEST_CASES),
            "results_summary": [
                {
                    "id": r["test_case"]["id"],
                    "level": r["test_case"]["level"],
                    "success": r["success"],
                    "score": r["analysis"]["score"],
                    "duration": r["duration"]
                }
                for r in all_results
            ]
        }

        summary_file = f"{self.data_dir}/{self.session_name}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        print("=" * 60)
        print(f"✅ 数据收集完成！")
        print(f"📁 数据文件数: {len(TEST_CASES) + 1}")
        print(f"📋 汇总文件: {summary_file}")

        return all_results

    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算统计信息"""
        total_tests = len(results)
        successful_tests = len([r for r in results if r["success"] and r.get("response", {}).get("machine_code")])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_score = sum(r["analysis"]["score"] for r in results) / total_tests if total_tests > 0 else 0
        avg_duration = sum(r["duration"] for r in results) / total_tests if total_tests > 0 else 0

        # 按难度分组统计
        level_stats = {}
        for result in results:
            level = result["test_case"]["level"]
            if level not in level_stats:
                level_stats[level] = {"total": 0, "success": 0, "scores": []}

            level_stats[level]["total"] += 1
            if result["success"] and result.get("response", {}).get("machine_code"):
                level_stats[level]["success"] += 1
            level_stats[level]["scores"].append(result["analysis"]["score"])

        for level in level_stats:
            stats = level_stats[level]
            stats["success_rate"] = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "avg_score": avg_score,
            "avg_duration": avg_duration,
            "level_stats": level_stats
        }

def main():
    """主函数"""
    print("🤖 MCU-Copilot 测试数据收集器")
    print("=" * 60)

    # 创建数据收集器
    collector = TestDataCollector()

    # 运行所有测试
    results = collector.run_all_tests()

    # 计算和显示统计信息
    stats = collector.get_statistics(results)

    print(f"")
    print(f"📊 数据收集统计:")
    print(f"   总测试用例: {stats['total_tests']}")
    print(f"   编译成功: {stats['successful_tests']}")
    print(f"   成功率: {stats['success_rate']:.1f}%")
    print(f"   平均评分: {stats['avg_score']:.1f}/100")
    print(f"   平均耗时: {stats['avg_duration']:.1f}秒")

    print(f"")
    print(f"📁 数据文件位置:")
    print(f"   数据目录: test_data/")
    print(f"   会话前缀: {collector.session_name}")
    print(f"")
    print(f"🔧 下一步: 使用 html_renderer.py 生成HTML报告")

    return collector.session_name

if __name__ == "__main__":
    main()