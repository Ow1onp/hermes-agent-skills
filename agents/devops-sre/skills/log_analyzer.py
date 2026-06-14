"""
Log Analyzer Skill — Production log pattern analysis for debugging and incident response.

Analyzes structured and unstructured logs, identifies error patterns, groups related
errors, detects anomalies, and generates incident summaries. Supports JSON, plaintext,
and common log formats (Apache, Nginx, syslog).

Part of the DevOps SRE agent in the HermesHub marketplace.
"""
import json
import re
from collections import Counter
from typing import Any


SCHEMA = {
    "name": "devops_log_analyzer",
    "description": (
        "Analyze production logs to identify error patterns, group related issues, "
        "detect anomalies, and generate incident summaries. Supports structured JSON logs, "
        "plaintext, and common formats (Apache, Nginx, syslog). Returns categorized findings "
        "with severity, frequency, and root cause hypotheses. "
        "Use when: debugging production issues, analyzing error logs, identifying recurring "
        "failures, or generating post-incident reports."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "logs": {
                "type": "string",
                "description": "Log content to analyze. Can be multi-line, multiple log entries."
            },
            "format": {
                "type": "string",
                "enum": ["auto", "json", "plaintext", "apache", "nginx", "syslog"],
                "description": "Log format. 'auto' attempts to detect the format automatically.",
                "default": "auto"
            },
            "analysis_type": {
                "type": "string",
                "enum": ["error_summary", "pattern_analysis", "timeline", "comprehensive"],
                "description": "Type of analysis to perform.",
                "default": "comprehensive"
            },
            "time_window_minutes": {
                "type": "integer",
                "description": "If logs span a time range, the window in minutes to focus on. 0 = all.",
                "default": 0
            }
        },
        "required": ["logs"]
    }
}


def handler(args: dict[str, Any]) -> str:
    """Analyze logs and return structured findings."""
    try:
        logs = args.get("logs", "")
        fmt = args.get("format", "auto")
        analysis_type = args.get("analysis_type", "comprehensive")
        time_window = args.get("time_window_minutes", 0)

        if not logs or not logs.strip():
            return json.dumps({"error": "No logs provided for analysis."})

        if len(logs) > 100000:
            return json.dumps({
                "error": "Log content too large. Limit to 100,000 characters.",
                "log_length": len(logs),
                "max_allowed": 100000
            })

        # Parse log entries
        entries = _parse_logs(logs, fmt)
        if not entries:
            return json.dumps({
                "success": True,
                "summary": {"total_entries": 0, "message": "No parseable log entries found. Check the log format."}
            })

        result: dict = {"success": True, "summary": {"total_entries": len(entries)}}

        # Error summary
        if analysis_type in ("error_summary", "comprehensive"):
            error_entries = [e for e in entries if e.get("level") in ("ERROR", "CRITICAL", "FATAL", "error", "critical", "fatal")]
            if error_entries:
                result["error_summary"] = _error_summary(error_entries, entries)

        # Pattern analysis
        if analysis_type in ("pattern_analysis", "comprehensive"):
            result["pattern_analysis"] = _pattern_analysis(entries)

        # Timeline
        if analysis_type in ("timeline", "comprehensive"):
            result["timeline"] = _build_timeline(entries, time_window)

        # Recommendations
        result["recommendations"] = _generate_log_recommendations(entries, result)

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Log analysis failed: {str(e)}", "type": type(e).__name__})


def _parse_logs(logs: str, fmt: str) -> list[dict]:
    """Parse log text into structured entries."""
    if fmt == "auto":
        # Try JSON first
        if logs.strip().startswith("{"):
            fmt = "json"
        elif re.search(r'\d+\.\d+\.\d+\.\d+', logs[:200]):
            fmt = "apache"
        elif "nginx" in logs[:200].lower():
            fmt = "nginx"
        else:
            fmt = "plaintext"

    parsers = {
        "json": _parse_json_logs,
        "apache": _parse_apache_logs,
        "nginx": _parse_nginx_logs,
        "syslog": _parse_syslog_logs,
        "plaintext": _parse_plaintext_logs,
    }

    parser = parsers.get(fmt, _parse_plaintext_logs)
    return parser(logs)


def _parse_json_logs(logs: str) -> list[dict]:
    """Parse JSON (structured) log entries, one per line or array."""
    entries: list[dict] = []
    for line in logs.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            entries.append({
                "raw": line,
                "timestamp": entry.get("timestamp") or entry.get("time") or entry.get("@timestamp", ""),
                "level": entry.get("level") or entry.get("severity") or entry.get("log_level", "INFO"),
                "message": entry.get("message") or entry.get("msg") or entry.get("error", ""),
                "service": entry.get("service") or entry.get("app") or entry.get("logger", ""),
                "error": entry.get("error") or entry.get("exception") or entry.get("stack_trace", ""),
            })
        except json.JSONDecodeError:
            entries.append({"raw": line, "level": "UNKNOWN", "message": line[:200]})
    return entries


def _parse_plaintext_logs(logs: str) -> list[dict]:
    """Parse plaintext log lines."""
    entries: list[dict] = []
    level_pattern = re.compile(
        r'\b(CRITICAL|FATAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b', re.IGNORECASE
    )
    ts_pattern = re.compile(
        r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})'
    )

    for line in logs.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        level_match = level_pattern.search(line)
        ts_match = ts_pattern.search(line)
        entries.append({
            "raw": line,
            "timestamp": ts_match.group(1) if ts_match else "",
            "level": level_match.group(1).upper() if level_match else "INFO",
            "message": line[:300],
            "service": "",
            "error": "",
        })
    return entries


def _parse_apache_logs(logs: str) -> list[dict]:
    """Parse Apache combined log format."""
    entries: list[dict] = []
    pattern = re.compile(
        r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+)'
    )
    for line in logs.strip().split("\n"):
        match = pattern.search(line)
        if match:
            status = int(match.group(5))
            level = "ERROR" if status >= 500 else "WARNING" if status >= 400 else "INFO"
            entries.append({
                "raw": line,
                "timestamp": match.group(2),
                "level": level,
                "message": f"{match.group(3)} {match.group(4)} -> {status}",
                "status_code": status,
                "service": "apache",
                "error": "",
            })
    return entries


def _parse_nginx_logs(logs: str) -> list[dict]:
    """Parse Nginx access log format."""
    return _parse_apache_logs(logs)  # Similar format


def _parse_syslog_logs(logs: str) -> list[dict]:
    """Parse syslog format."""
    entries: list[dict] = []
    pattern = re.compile(
        r'(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)(?:\[(\d+)\])?:\s+(.*)'
    )
    for line in logs.strip().split("\n"):
        match = pattern.search(line)
        if match:
            msg = match.group(5)
            level = "ERROR" if "error" in msg.lower() else "WARNING" if "warn" in msg.lower() else "INFO"
            entries.append({
                "raw": line,
                "timestamp": match.group(1),
                "level": level,
                "message": msg[:300],
                "service": match.group(3),
                "error": msg if "error" in msg.lower() else "",
            })
    return entries


def _error_summary(error_entries: list[dict], all_entries: list[dict]) -> dict:
    """Generate error summary with groupings and frequency."""
    error_rate = round(len(error_entries) / len(all_entries) * 100, 1) if all_entries else 0

    # Group errors by message pattern
    groups: dict[str, list[dict]] = {}
    for e in error_entries:
        msg = e.get("message", "")
        # Normalize message (remove IDs, timestamps in message)
        normalized = re.sub(r'\b[0-9a-f]{8,}\b', '<ID>', msg)
        normalized = re.sub(r'\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\b', '<TIME>', normalized)
        normalized = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', normalized)
        key = normalized[:120]
        groups.setdefault(key, []).append(e)

    # Build grouped errors with counts
    grouped = []
    for normalized, entries in groups.items():
        grouped.append({
            "pattern": normalized,
            "count": len(entries),
            "sample": entries[0].get("message", "")[:200],
            "services": list(set(e.get("service", "") for e in entries)),
            "first_seen": min((e.get("timestamp", "") for e in entries), default=""),
            "last_seen": max((e.get("timestamp", "") for e in entries), default=""),
        })

    grouped.sort(key=lambda g: g["count"], reverse=True)

    return {
        "error_count": len(error_entries),
        "error_rate_percent": error_rate,
        "unique_error_patterns": len(groups),
        "top_errors": grouped[:10]
    }


def _pattern_analysis(entries: list[dict]) -> dict:
    """Analyze log patterns: frequency, burst detection, common keywords."""
    levels = Counter(e.get("level", "UNKNOWN") for e in entries)
    services = Counter(e.get("service", "app") for e in entries if e.get("service"))

    # Keyword frequency
    all_text = " ".join(e.get("message", "") for e in entries).lower()
    keywords = ["timeout", "connection refused", "out of memory", "permission denied",
                "not found", "unauthorized", "rate limit", "panic", "segfault",
                "deadlock", "corrupted", "overflow", "null pointer"]
    keyword_hits = {kw: all_text.count(kw) for kw in keywords if kw in all_text}

    # Burst detection: check for time clustering
    bursts: list[dict] = []
    if len(entries) > 10:
        error_times = [
            e.get("timestamp", "") for e in entries
            if e.get("level") in ("ERROR", "CRITICAL", "FATAL")
        ]
        # Simple burst check: >3 errors within 5 entries
        for i in range(len(error_times) - 3):
            window = error_times[i:i+5]
            if len([t for t in window if t]) >= 3:
                bursts.append({
                    "position": i,
                    "count": len([t for t in window if t]),
                    "window": f"entries {i}-{i+5}"
                })
                break  # Report first burst

    return {
        "level_distribution": dict(levels.most_common()),
        "service_distribution": dict(services.most_common()),
        "keyword_hits": keyword_hits,
        "bursts_detected": len(bursts),
        "burst_details": bursts[:3]
    }


def _build_timeline(entries: list[dict], window_minutes: int) -> dict:
    """Build a timeline of notable events."""
    events: list[dict] = []
    first_error_idx = None
    last_error_idx = None

    for i, e in enumerate(entries):
        level = (e.get("level") or "").upper()
        if level in ("ERROR", "CRITICAL", "FATAL"):
            events.append({
                "index": i,
                "timestamp": e.get("timestamp", ""),
                "type": "error",
                "message": e.get("message", "")[:200],
                "service": e.get("service", "")
            })
            if first_error_idx is None:
                first_error_idx = i
            last_error_idx = i
        elif level == "WARNING":
            # Only include first and last warning for brevity
            if not any(ev.get("type") == "warning" for ev in events[-3:]):
                events.append({
                    "index": i,
                    "timestamp": e.get("timestamp", ""),
                    "type": "warning",
                    "message": e.get("message", "")[:200]
                })

    return {
        "total_events": len(events),
        "first_error_at": first_error_idx,
        "last_error_at": last_error_idx,
        "events": events[:20]  # Cap at 20 for readability
    }


def _generate_log_recommendations(entries: list[dict], result: dict) -> list[dict]:
    """Generate actionable recommendations based on analysis."""
    recs: list[dict] = []

    error_rate = result.get("error_summary", {}).get("error_rate_percent", 0)
    if error_rate > 10:
        recs.append({
            "priority": "critical",
            "action": "High error rate detected",
            "detail": f"Error rate is {error_rate}%. Investigate immediately.",
            "next_steps": [
                "1. Check recent deployments for regressions",
                "2. Review error patterns in the top_errors list",
                "3. Rollback if error rate spike correlates with a deployment"
            ]
        })
    elif error_rate > 5:
        recs.append({
            "priority": "high",
            "action": "Elevated error rate",
            "detail": f"Error rate is {error_rate}%. Monitor and investigate.",
            "next_steps": ["1. Set up alert for error rate threshold", "2. Review top error patterns"]
        })

    # Timeout-related
    keyword_hits = result.get("pattern_analysis", {}).get("keyword_hits", {})
    if keyword_hits.get("timeout", 0) > 0:
        recs.append({
            "priority": "high",
            "action": "Timeout errors detected",
            "detail": f"Found {keyword_hits['timeout']} timeout occurrences.",
            "next_steps": [
                "1. Check downstream service latency",
                "2. Review timeout configuration (connection/read timeouts)",
                "3. Consider circuit breaker pattern"
            ]
        })

    # Memory-related
    if keyword_hits.get("out of memory", 0) > 0:
        recs.append({
            "priority": "critical",
            "action": "Out of Memory errors detected",
            "detail": f"Found {keyword_hits['out of memory']} OOM occurrences.",
            "next_steps": [
                "1. Check memory limits in deployment config",
                "2. Profile memory usage (memory_profiler, py-spy)",
                "3. Increase memory limits or fix memory leak"
            ]
        })

    # General
    if not recs:
        recs.append({
            "priority": "info",
            "action": "No critical issues detected",
            "detail": "Log analysis shows normal operation patterns.",
            "next_steps": ["Continue monitoring", "Review log levels (consider reducing DEBUG in production)"]
        })

    return recs
