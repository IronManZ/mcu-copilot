"""
Structured logging for LLM interactions and compilation attempts
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    """Log levels for structured logging"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: LogLevel
    session_id: str
    event_type: str
    message: str
    data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    provider: Optional[str] = None
    model: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['level'] = self.level.value
        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(',', ':'))

class StructuredLogger:
    """Structured logger for LLM and compilation events"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._ensure_log_directory()
        self._setup_file_handlers()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _setup_file_handlers(self):
        """Setup file handlers for different log types"""
        self._session_log_file = os.path.join(
            self.log_dir,
            f"sessions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        self._performance_log_file = os.path.join(
            self.log_dir,
            f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        self._error_log_file = os.path.join(
            self.log_dir,
            f"errors_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )

    def _write_to_file(self, entry: LogEntry, log_file: str):
        """Write log entry to specified file"""
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry.to_json() + '\n')
        except Exception as e:
            # Fallback to console logging
            print(f"Failed to write to log file {log_file}: {e}")
            print(f"Log entry: {entry.to_json()}")

    def log_session_start(self, session_id: str, requirement: str, provider: str, model: str):
        """Log the start of a new session"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.INFO,
            session_id=session_id,
            event_type="session_start",
            message="New session started",
            data={
                "requirement": requirement,
                "requirement_length": len(requirement),
                "provider": provider,
                "model": model
            },
            provider=provider,
            model=model
        )
        self._write_to_file(entry, self._session_log_file)

    def log_llm_request(self, session_id: str, provider: str, model: str, prompt_length: int, attempt: int):
        """Log LLM API request"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.INFO,
            session_id=session_id,
            event_type="llm_request",
            message=f"LLM request attempt {attempt}",
            data={
                "provider": provider,
                "model": model,
                "prompt_length": prompt_length,
                "attempt": attempt
            },
            provider=provider,
            model=model
        )
        self._write_to_file(entry, self._session_log_file)

    def log_llm_response(
        self,
        session_id: str,
        provider: str,
        model: str,
        success: bool,
        response_length: Optional[int] = None,
        duration_ms: Optional[float] = None,
        token_usage: Optional[Dict[str, int]] = None,
        error_message: Optional[str] = None
    ):
        """Log LLM API response"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            session_id=session_id,
            event_type="llm_response",
            message="LLM response received" if success else f"LLM request failed: {error_message}",
            data={
                "success": success,
                "response_length": response_length,
                "token_usage": token_usage,
                "error_message": error_message
            },
            duration_ms=duration_ms,
            provider=provider,
            model=model
        )

        log_file = self._session_log_file if success else self._error_log_file
        self._write_to_file(entry, log_file)

    def log_compilation_attempt(
        self,
        session_id: str,
        attempt: int,
        code_length: int,
        success: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ):
        """Log compilation attempt"""
        level = LogLevel.INFO if success else LogLevel.WARNING
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            session_id=session_id,
            event_type="compilation_attempt",
            message=f"Compilation attempt {attempt} {'succeeded' if success else 'failed'}",
            data={
                "attempt": attempt,
                "success": success,
                "code_length": code_length,
                "error_count": len(errors) if errors else 0,
                "warning_count": len(warnings) if warnings else 0,
                "errors": errors[:5] if errors else None,  # Limit to first 5 errors
                "warnings": warnings[:5] if warnings else None
            }
        )
        self._write_to_file(entry, self._session_log_file)

    def log_session_end(
        self,
        session_id: str,
        success: bool,
        total_attempts: int,
        final_code_length: Optional[int] = None,
        total_duration_ms: Optional[float] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Log session completion"""
        level = LogLevel.INFO if success else LogLevel.WARNING
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            session_id=session_id,
            event_type="session_end",
            message=f"Session {'completed successfully' if success else 'failed after all attempts'}",
            data={
                "success": success,
                "total_attempts": total_attempts,
                "final_code_length": final_code_length,
                "provider": provider,
                "model": model
            },
            duration_ms=total_duration_ms,
            provider=provider,
            model=model
        )
        self._write_to_file(entry, self._session_log_file)

    def log_performance_metrics(
        self,
        session_id: str,
        metrics: Dict[str, Any]
    ):
        """Log performance metrics"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.INFO,
            session_id=session_id,
            event_type="performance_metrics",
            message="Performance metrics recorded",
            data=metrics
        )
        self._write_to_file(entry, self._performance_log_file)

    def log_error(
        self,
        session_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None
    ):
        """Log errors with context"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.ERROR,
            session_id=session_id,
            event_type="error",
            message=f"{error_type}: {error_message}",
            data={
                "error_type": error_type,
                "context": context
            },
            provider=provider
        )
        self._write_to_file(entry, self._error_log_file)

    def get_logs_for_session(self, session_id: str) -> List[LogEntry]:
        """Retrieve all logs for a specific session"""
        logs = []
        log_files = [self._session_log_file, self._performance_log_file, self._error_log_file]

        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            data = json.loads(line.strip())
                            if data.get('session_id') == session_id:
                                entry = LogEntry(
                                    timestamp=data['timestamp'],
                                    level=LogLevel(data['level']),
                                    session_id=data['session_id'],
                                    event_type=data['event_type'],
                                    message=data['message'],
                                    data=data.get('data'),
                                    duration_ms=data.get('duration_ms'),
                                    provider=data.get('provider'),
                                    model=data.get('model')
                                )
                                logs.append(entry)
                except Exception as e:
                    print(f"Error reading log file {log_file}: {e}")

        # Sort by timestamp
        logs.sort(key=lambda x: x.timestamp)
        return logs