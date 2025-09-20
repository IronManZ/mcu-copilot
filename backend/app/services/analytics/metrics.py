"""
Performance metrics collection and analysis
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    session_id: str
    provider: str
    model: str
    success: bool
    total_attempts: int
    total_duration_ms: float
    first_success_attempt: Optional[int] = None
    compilation_success_rate: float = 0.0
    average_response_time_ms: float = 0.0
    total_tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    final_code_length: int = 0
    error_patterns: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class MetricsCollector:
    """Collects and analyzes performance metrics"""

    def __init__(self):
        self._session_metrics: Dict[str, Dict[str, Any]] = {}
        self._timing_data: Dict[str, List[float]] = defaultdict(list)
        self._global_stats = {
            'total_sessions': 0,
            'successful_sessions': 0,
            'total_attempts': 0,
            'successful_attempts': 0,
            'provider_stats': defaultdict(lambda: {'success': 0, 'total': 0, 'avg_attempts': 0}),
            'model_stats': defaultdict(lambda: {'success': 0, 'total': 0, 'avg_time': 0}),
            'error_frequency': defaultdict(int)
        }

    def start_session(self, session_id: str, provider: str, model: str, requirement: str):
        """Initialize metrics collection for a new session"""
        self._session_metrics[session_id] = {
            'provider': provider,
            'model': model,
            'requirement': requirement,
            'start_time': time.time(),
            'attempts': [],
            'llm_calls': [],
            'compilation_results': [],
            'total_tokens': 0,
            'success': False,
            'final_attempt': 0
        }

    def record_llm_call(
        self,
        session_id: str,
        attempt: int,
        duration_ms: float,
        success: bool,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        error: Optional[str] = None
    ):
        """Record an LLM API call"""
        if session_id not in self._session_metrics:
            return

        call_data = {
            'attempt': attempt,
            'duration_ms': duration_ms,
            'success': success,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'error': error,
            'timestamp': time.time()
        }

        metrics = self._session_metrics[session_id]
        metrics['llm_calls'].append(call_data)
        metrics['total_tokens'] += call_data['total_tokens']

        # Update timing data for provider analysis
        provider_model_key = f"{metrics['provider']}_{metrics['model']}"
        self._timing_data[provider_model_key].append(duration_ms)

    def record_compilation_result(
        self,
        session_id: str,
        attempt: int,
        success: bool,
        code_length: int,
        errors: List[str] = None,
        warnings: List[str] = None
    ):
        """Record compilation attempt result"""
        if session_id not in self._session_metrics:
            return

        result_data = {
            'attempt': attempt,
            'success': success,
            'code_length': code_length,
            'errors': errors or [],
            'warnings': warnings or [],
            'error_count': len(errors) if errors else 0,
            'warning_count': len(warnings) if warnings else 0,
            'timestamp': time.time()
        }

        metrics = self._session_metrics[session_id]
        metrics['compilation_results'].append(result_data)

        # Track error patterns for analysis
        if errors:
            for error in errors:
                self._global_stats['error_frequency'][self._categorize_error(error)] += 1

    def end_session(self, session_id: str, final_success: bool, final_code_length: int = 0) -> PerformanceMetrics:
        """End session and calculate final metrics"""
        if session_id not in self._session_metrics:
            raise ValueError(f"Session {session_id} not found")

        metrics = self._session_metrics[session_id]
        end_time = time.time()
        total_duration_ms = (end_time - metrics['start_time']) * 1000

        # Calculate success metrics
        compilation_results = metrics['compilation_results']
        successful_compilations = sum(1 for r in compilation_results if r['success'])
        first_success_attempt = None

        for result in compilation_results:
            if result['success']:
                first_success_attempt = result['attempt']
                break

        # Calculate averages
        llm_calls = metrics['llm_calls']
        avg_response_time = sum(call['duration_ms'] for call in llm_calls) / len(llm_calls) if llm_calls else 0

        # Collect error patterns
        all_errors = []
        for result in compilation_results:
            all_errors.extend(result['errors'])
        error_patterns = [self._categorize_error(error) for error in all_errors]

        # Create performance metrics object
        performance_metrics = PerformanceMetrics(
            session_id=session_id,
            provider=metrics['provider'],
            model=metrics['model'],
            success=final_success,
            total_attempts=len(compilation_results),
            total_duration_ms=total_duration_ms,
            first_success_attempt=first_success_attempt,
            compilation_success_rate=successful_compilations / len(compilation_results) if compilation_results else 0,
            average_response_time_ms=avg_response_time,
            total_tokens_used=metrics['total_tokens'],
            prompt_tokens=sum(call['prompt_tokens'] for call in llm_calls),
            completion_tokens=sum(call['completion_tokens'] for call in llm_calls),
            final_code_length=final_code_length,
            error_patterns=list(set(error_patterns))
        )

        # Update global statistics
        self._update_global_stats(performance_metrics)

        # Clean up session data
        del self._session_metrics[session_id]

        return performance_metrics

    def _update_global_stats(self, metrics: PerformanceMetrics):
        """Update global statistics with session results"""
        stats = self._global_stats
        stats['total_sessions'] += 1

        if metrics.success:
            stats['successful_sessions'] += 1

        stats['total_attempts'] += metrics.total_attempts

        # Update provider stats
        provider_key = metrics.provider
        provider_stats = stats['provider_stats'][provider_key]
        provider_stats['total'] += 1
        if metrics.success:
            provider_stats['success'] += 1
        provider_stats['avg_attempts'] = (provider_stats.get('avg_attempts', 0) * (provider_stats['total'] - 1) + metrics.total_attempts) / provider_stats['total']

        # Update model stats
        model_key = f"{metrics.provider}_{metrics.model}"
        model_stats = stats['model_stats'][model_key]
        model_stats['total'] += 1
        if metrics.success:
            model_stats['success'] += 1
        model_stats['avg_time'] = (model_stats.get('avg_time', 0) * (model_stats['total'] - 1) + metrics.average_response_time_ms) / model_stats['total']

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error messages for pattern analysis"""
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
        elif 'address' in error_lower or '地址' in error_lower:
            return 'address_error'
        else:
            return 'other'

    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global performance statistics"""
        stats = dict(self._global_stats)

        # Calculate success rates
        if stats['total_sessions'] > 0:
            stats['session_success_rate'] = stats['successful_sessions'] / stats['total_sessions']
        else:
            stats['session_success_rate'] = 0.0

        # Calculate provider performance
        provider_performance = {}
        for provider, data in stats['provider_stats'].items():
            if data['total'] > 0:
                provider_performance[provider] = {
                    'success_rate': data['success'] / data['total'],
                    'average_attempts': data['avg_attempts'],
                    'total_sessions': data['total']
                }

        stats['provider_performance'] = provider_performance

        # Calculate model performance
        model_performance = {}
        for model, data in stats['model_stats'].items():
            if data['total'] > 0:
                model_performance[model] = {
                    'success_rate': data['success'] / data['total'],
                    'average_response_time': data['avg_time'],
                    'total_sessions': data['total']
                }

        stats['model_performance'] = model_performance

        return stats

    def get_recommendations(self) -> Dict[str, Any]:
        """Generate recommendations based on collected metrics"""
        stats = self.get_global_statistics()
        recommendations = {
            'preferred_providers': [],
            'optimal_models': [],
            'common_issues': [],
            'suggested_improvements': []
        }

        # Recommend best performing providers
        provider_perf = stats.get('provider_performance', {})
        if provider_perf:
            sorted_providers = sorted(
                provider_perf.items(),
                key=lambda x: (x[1]['success_rate'], -x[1]['average_attempts']),
                reverse=True
            )
            recommendations['preferred_providers'] = [p[0] for p in sorted_providers[:2]]

        # Recommend best performing models
        model_perf = stats.get('model_performance', {})
        if model_perf:
            sorted_models = sorted(
                model_perf.items(),
                key=lambda x: (x[1]['success_rate'], -x[1]['average_response_time']),
                reverse=True
            )
            recommendations['optimal_models'] = [m[0] for m in sorted_models[:3]]

        # Identify common issues
        error_freq = stats.get('error_frequency', {})
        if error_freq:
            most_common_errors = sorted(
                error_freq.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            recommendations['common_issues'] = [error[0] for error in most_common_errors]

        # Generate improvement suggestions
        if stats.get('session_success_rate', 0) < 0.7:
            recommendations['suggested_improvements'].append(
                "Success rate below 70% - consider prompt optimization"
            )

        if 'undefined_variable' in recommendations['common_issues']:
            recommendations['suggested_improvements'].append(
                "High undefined variable errors - enhance variable definition guidance"
            )

        return recommendations