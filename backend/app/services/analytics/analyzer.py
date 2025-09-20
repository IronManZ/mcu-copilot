"""
Session analysis and compilation analytics
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from .logger import LogEntry, LogLevel
from .metrics import PerformanceMetrics

@dataclass
class CompilationAnalytics:
    """Analytics for compilation attempts and success patterns"""
    total_sessions: int
    successful_sessions: int
    success_rate: float
    average_attempts_per_session: float
    most_common_errors: List[Tuple[str, int]]
    provider_performance: Dict[str, Dict[str, Any]]
    model_performance: Dict[str, Dict[str, Any]]
    time_to_success_stats: Dict[str, float]
    error_resolution_patterns: Dict[str, List[str]]

class SessionAnalyzer:
    """Analyzes session logs and performance data"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir

    def analyze_session(self, session_id: str, logs: List[LogEntry]) -> Dict[str, Any]:
        """Analyze a single session's performance"""
        if not logs:
            return {"error": "No logs found for session"}

        # Group logs by type
        logs_by_type = defaultdict(list)
        for log in logs:
            logs_by_type[log.event_type].append(log)

        analysis = {
            "session_id": session_id,
            "start_time": logs[0].timestamp if logs else None,
            "end_time": logs[-1].timestamp if logs else None,
            "total_duration_seconds": self._calculate_duration(logs),
            "provider": logs[0].provider if logs else None,
            "model": logs[0].model if logs else None,
            "events": {
                "total": len(logs),
                "by_type": {event_type: len(event_logs) for event_type, event_logs in logs_by_type.items()}
            }
        }

        # Analyze LLM interactions
        llm_requests = logs_by_type.get("llm_request", [])
        llm_responses = logs_by_type.get("llm_response", [])
        analysis["llm_analysis"] = self._analyze_llm_interactions(llm_requests, llm_responses)

        # Analyze compilation attempts
        compilation_logs = logs_by_type.get("compilation_attempt", [])
        analysis["compilation_analysis"] = self._analyze_compilation_attempts(compilation_logs)

        # Analyze overall success
        session_end_logs = logs_by_type.get("session_end", [])
        if session_end_logs:
            end_log = session_end_logs[-1]
            analysis["final_success"] = end_log.data.get("success", False)
            analysis["total_attempts"] = end_log.data.get("total_attempts", 0)

        # Identify patterns and issues
        analysis["patterns"] = self._identify_patterns(logs)

        return analysis

    def analyze_time_period(
        self,
        start_date: datetime,
        end_date: datetime,
        provider_filter: Optional[str] = None,
        model_filter: Optional[str] = None
    ) -> CompilationAnalytics:
        """Analyze performance over a time period"""
        logs = self._load_logs_for_period(start_date, end_date)

        # Group logs by session
        sessions_logs = defaultdict(list)
        for log in logs:
            sessions_logs[log.session_id].append(log)

        # Filter by provider/model if specified
        if provider_filter or model_filter:
            filtered_sessions = {}
            for session_id, session_logs in sessions_logs.items():
                if session_logs:
                    first_log = session_logs[0]
                    if ((not provider_filter or first_log.provider == provider_filter) and
                        (not model_filter or first_log.model == model_filter)):
                        filtered_sessions[session_id] = session_logs
            sessions_logs = filtered_sessions

        # Analyze each session
        session_analyses = {}
        for session_id, session_logs in sessions_logs.items():
            session_analyses[session_id] = self.analyze_session(session_id, session_logs)

        # Aggregate statistics
        total_sessions = len(session_analyses)
        successful_sessions = sum(1 for analysis in session_analyses.values()
                                if analysis.get("final_success", False))

        success_rate = successful_sessions / total_sessions if total_sessions > 0 else 0.0

        # Calculate average attempts
        total_attempts = sum(analysis.get("total_attempts", 0) for analysis in session_analyses.values())
        avg_attempts = total_attempts / total_sessions if total_sessions > 0 else 0.0

        # Analyze errors
        error_counter = Counter()
        for analysis in session_analyses.values():
            compilation_analysis = analysis.get("compilation_analysis", {})
            errors = compilation_analysis.get("all_errors", [])
            for error in errors:
                error_counter[self._categorize_error(error)] += 1

        most_common_errors = error_counter.most_common(10)

        # Analyze provider performance
        provider_stats = defaultdict(lambda: {"total": 0, "successful": 0, "attempts": []})
        model_stats = defaultdict(lambda: {"total": 0, "successful": 0, "response_times": []})

        for analysis in session_analyses.values():
            provider = analysis.get("provider")
            model = analysis.get("model")
            success = analysis.get("final_success", False)
            attempts = analysis.get("total_attempts", 0)

            if provider:
                provider_stats[provider]["total"] += 1
                if success:
                    provider_stats[provider]["successful"] += 1
                provider_stats[provider]["attempts"].append(attempts)

            if model:
                model_key = f"{provider}_{model}" if provider else model
                model_stats[model_key]["total"] += 1
                if success:
                    model_stats[model_key]["successful"] += 1

                llm_analysis = analysis.get("llm_analysis", {})
                avg_response_time = llm_analysis.get("average_response_time_ms", 0)
                if avg_response_time > 0:
                    model_stats[model_key]["response_times"].append(avg_response_time)

        # Calculate provider performance metrics
        provider_performance = {}
        for provider, stats in provider_stats.items():
            provider_performance[provider] = {
                "success_rate": stats["successful"] / stats["total"] if stats["total"] > 0 else 0,
                "average_attempts": sum(stats["attempts"]) / len(stats["attempts"]) if stats["attempts"] else 0,
                "total_sessions": stats["total"]
            }

        # Calculate model performance metrics
        model_performance = {}
        for model, stats in model_stats.items():
            model_performance[model] = {
                "success_rate": stats["successful"] / stats["total"] if stats["total"] > 0 else 0,
                "average_response_time": sum(stats["response_times"]) / len(stats["response_times"]) if stats["response_times"] else 0,
                "total_sessions": stats["total"]
            }

        # Analyze time to success
        time_to_success_stats = self._calculate_time_to_success_stats(session_analyses)

        # Analyze error resolution patterns
        error_resolution_patterns = self._analyze_error_resolution_patterns(session_analyses)

        return CompilationAnalytics(
            total_sessions=total_sessions,
            successful_sessions=successful_sessions,
            success_rate=success_rate,
            average_attempts_per_session=avg_attempts,
            most_common_errors=most_common_errors,
            provider_performance=provider_performance,
            model_performance=model_performance,
            time_to_success_stats=time_to_success_stats,
            error_resolution_patterns=error_resolution_patterns
        )

    def generate_recommendations(self, analytics: CompilationAnalytics) -> Dict[str, Any]:
        """Generate recommendations based on analytics"""
        recommendations = {
            "model_recommendations": [],
            "prompt_improvements": [],
            "error_prevention": [],
            "performance_optimization": []
        }

        # Model recommendations
        best_models = sorted(
            analytics.model_performance.items(),
            key=lambda x: (x[1]["success_rate"], -x[1]["average_response_time"]),
            reverse=True
        )[:3]

        for model, stats in best_models:
            recommendations["model_recommendations"].append({
                "model": model,
                "success_rate": f"{stats['success_rate']:.1%}",
                "avg_response_time": f"{stats['average_response_time']:.0f}ms",
                "reason": "High success rate and good performance"
            })

        # Prompt improvements based on common errors
        common_errors = dict(analytics.most_common_errors[:5])

        if "undefined_variable" in common_errors:
            recommendations["prompt_improvements"].append(
                "Add stronger emphasis on variable definition requirements in DATA section"
            )

        if "invalid_instruction" in common_errors:
            recommendations["prompt_improvements"].append(
                "Include instruction set reference in prompt for better accuracy"
            )

        if "jump_distance" in common_errors:
            recommendations["prompt_improvements"].append(
                "Add guidance on jump distance limitations and JUMP vs JZ usage"
            )

        # Error prevention strategies
        for error_type, count in analytics.most_common_errors[:3]:
            recommendations["error_prevention"].append({
                "error_type": error_type,
                "frequency": count,
                "prevention": self._get_error_prevention_strategy(error_type)
            })

        # Performance optimization
        if analytics.average_attempts_per_session > 3:
            recommendations["performance_optimization"].append(
                "High average attempts - consider prompt optimization or model switching"
            )

        if analytics.success_rate < 0.7:
            recommendations["performance_optimization"].append(
                "Low success rate - review prompt effectiveness and error handling"
            )

        return recommendations

    def _analyze_llm_interactions(self, requests: List[LogEntry], responses: List[LogEntry]) -> Dict[str, Any]:
        """Analyze LLM API interactions"""
        if not responses:
            return {"error": "No LLM responses found"}

        successful_responses = [r for r in responses if r.data.get("success", False)]
        failed_responses = [r for r in responses if not r.data.get("success", False)]

        analysis = {
            "total_requests": len(requests),
            "total_responses": len(responses),
            "successful_responses": len(successful_responses),
            "failed_responses": len(failed_responses),
            "success_rate": len(successful_responses) / len(responses) if responses else 0
        }

        # Analyze response times
        response_times = [r.duration_ms for r in responses if r.duration_ms]
        if response_times:
            analysis["response_time_stats"] = {
                "average_ms": sum(response_times) / len(response_times),
                "min_ms": min(response_times),
                "max_ms": max(response_times)
            }

        # Analyze token usage
        total_tokens = sum(r.data.get("token_usage", {}).get("total_tokens", 0) for r in responses if r.data)
        analysis["total_tokens_used"] = total_tokens

        return analysis

    def _analyze_compilation_attempts(self, compilation_logs: List[LogEntry]) -> Dict[str, Any]:
        """Analyze compilation attempts"""
        if not compilation_logs:
            return {"error": "No compilation attempts found"}

        successful_attempts = [log for log in compilation_logs if log.data.get("success", False)]
        failed_attempts = [log for log in compilation_logs if not log.data.get("success", False)]

        analysis = {
            "total_attempts": len(compilation_logs),
            "successful_attempts": len(successful_attempts),
            "failed_attempts": len(failed_attempts),
            "success_rate": len(successful_attempts) / len(compilation_logs) if compilation_logs else 0
        }

        # Collect all errors
        all_errors = []
        for log in failed_attempts:
            errors = log.data.get("errors", [])
            all_errors.extend(errors)

        analysis["all_errors"] = all_errors
        analysis["unique_error_types"] = len(set(self._categorize_error(e) for e in all_errors))

        # Find first successful attempt
        for i, log in enumerate(compilation_logs, 1):
            if log.data.get("success", False):
                analysis["first_success_attempt"] = i
                break

        return analysis

    def _identify_patterns(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Identify patterns in session logs"""
        patterns = {
            "retry_patterns": [],
            "error_evolution": [],
            "performance_trends": []
        }

        # Analyze retry patterns
        compilation_logs = [log for log in logs if log.event_type == "compilation_attempt"]
        if len(compilation_logs) > 1:
            retry_pattern = []
            for log in compilation_logs:
                retry_pattern.append({
                    "attempt": log.data.get("attempt"),
                    "success": log.data.get("success"),
                    "error_count": log.data.get("error_count", 0)
                })
            patterns["retry_patterns"] = retry_pattern

        # Analyze error evolution
        error_evolution = []
        for log in compilation_logs:
            if not log.data.get("success", False):
                errors = log.data.get("errors", [])
                error_types = [self._categorize_error(e) for e in errors]
                error_evolution.append({
                    "attempt": log.data.get("attempt"),
                    "error_types": error_types
                })
        patterns["error_evolution"] = error_evolution

        return patterns

    def _calculate_duration(self, logs: List[LogEntry]) -> float:
        """Calculate duration between first and last log"""
        if len(logs) < 2:
            return 0.0

        try:
            start_time = datetime.fromisoformat(logs[0].timestamp)
            end_time = datetime.fromisoformat(logs[-1].timestamp)
            return (end_time - start_time).total_seconds()
        except Exception:
            return 0.0

    def _load_logs_for_period(self, start_date: datetime, end_date: datetime) -> List[LogEntry]:
        """Load logs for a specific time period"""
        # This is a simplified implementation
        # In practice, you'd implement efficient log file reading
        logs = []
        # Implementation would load from log files based on date range
        return logs

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message"""
        error_lower = error_message.lower()

        if 'undefined' in error_lower or '未定义' in error_lower:
            return 'undefined_variable'
        elif 'instruction' in error_lower or '指令' in error_lower:
            return 'invalid_instruction'
        elif 'jump' in error_lower or '跳转' in error_lower:
            return 'jump_distance'
        elif 'immediate' in error_lower or '立即数' in error_lower:
            return 'immediate_value'
        elif 'syntax' in error_lower:
            return 'syntax_error'
        else:
            return 'other'

    def _calculate_time_to_success_stats(self, session_analyses: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate statistics for time to success"""
        successful_times = []
        for analysis in session_analyses.values():
            if analysis.get("final_success", False):
                duration = analysis.get("total_duration_seconds", 0)
                if duration > 0:
                    successful_times.append(duration)

        if not successful_times:
            return {"average": 0, "min": 0, "max": 0}

        return {
            "average": sum(successful_times) / len(successful_times),
            "min": min(successful_times),
            "max": max(successful_times)
        }

    def _analyze_error_resolution_patterns(self, session_analyses: Dict[str, Dict]) -> Dict[str, List[str]]:
        """Analyze how different errors are typically resolved"""
        resolution_patterns = defaultdict(list)

        for analysis in session_analyses.values():
            patterns = analysis.get("patterns", {})
            error_evolution = patterns.get("error_evolution", [])

            if len(error_evolution) > 1:
                for i in range(len(error_evolution) - 1):
                    current_errors = set(error_evolution[i]["error_types"])
                    next_errors = set(error_evolution[i + 1]["error_types"])

                    resolved_errors = current_errors - next_errors
                    for error in resolved_errors:
                        if next_errors:
                            resolution_patterns[error].append(f"resolved_with_{list(next_errors)[0]}")
                        else:
                            resolution_patterns[error].append("resolved_completely")

        return dict(resolution_patterns)

    def _get_error_prevention_strategy(self, error_type: str) -> str:
        """Get prevention strategy for specific error type"""
        strategies = {
            "undefined_variable": "Add comprehensive variable checklist to prompt",
            "invalid_instruction": "Include instruction validation in prompt",
            "jump_distance": "Add jump distance calculation guidance",
            "immediate_value": "Emphasize LDINS-only rule for immediates",
            "syntax_error": "Add syntax validation examples",
            "other": "Review and categorize for specific guidance"
        }
        return strategies.get(error_type, "Implement targeted error checking")