#!/usr/bin/env python3
"""
Nginx JSON Log Analyzer

Parses JSON-format Nginx access logs and outputs:
  - QPS (overall / per-minute peak)
  - HTTP status code distribution
  - P50 / P99 latency
  - Top N request URIs
  - Error request details (4xx / 5xx)

Usage:
  python nginx-log-analyzer.py access.log
  python nginx-log-analyzer.py access.log --top 10
  docker logs knowledge-base | python nginx-log-analyzer.py --stdin
"""

import argparse
import json
import sys
from collections import Counter, defaultdict


def parse_log_line(line):
    try:
        return json.loads(line.strip())
    except json.JSONDecodeError:
        return None


def analyze(records, top_n=5):
    if not records:
        print("No valid log records found.")
        return

    total = len(records)
    status_counter = Counter()
    request_times = []
    uri_counter = Counter()
    minute_qps = Counter()
    error_records = []

    for r in records:
        status = r.get("status", 0)
        status_counter[status] += 1

        rt = r.get("request_time", 0)
        if isinstance(rt, (int, float)):
            request_times.append(rt)

        uri = r.get("uri", "")
        uri_counter[uri] += 1

        ts = r.get("timestamp", "")
        if ts:
            minute_key = ts[:16]
            minute_qps[minute_key] += 1

        if status >= 400:
            error_records.append(r)

    request_times.sort()

    print("=" * 60)
    print("[Nginx Log Analysis Report]")
    print(f"   Total Requests: {total}")
    if records:
        print(f"   Time Range: {records[0].get('timestamp','?')} ~ {records[-1].get('timestamp','?')}")
    print()

    if minute_qps:
        minutes = len(minute_qps)
        avg_qps = total / (minutes * 60) if minutes > 0 else 0
        peak_minute, peak_count = minute_qps.most_common(1)[0]
        print("[QPS]")
        print(f"   Avg QPS: {avg_qps:.2f}")
        print(f"   Peak Minute: {peak_minute} ({peak_count} requests)")
        print()

    print("[HTTP Status Codes]")
    for code in sorted(status_counter.keys()):
        count = status_counter[code]
        bar = "#" * (count * 40 // total)
        print(f"   {code}: {count:>6} ({count/total*100:5.1f}%) {bar}")
    print()

    if request_times:
        p50 = request_times[int(len(request_times) * 0.5)]
        p99 = request_times[int(len(request_times) * 0.99)]
        avg = sum(request_times) / len(request_times)
        print("[Latency]")
        print(f"   P50: {p50:.4f}s")
        print(f"   P99: {p99:.4f}s")
        print(f"   AVG: {avg:.4f}s")
        print()

    print(f"[Top {top_n} URIs]")
    for uri, count in uri_counter.most_common(top_n):
        print(f"   {count:>6}  {uri}")
    print()

    if error_records:
        print(f"[Errors] ({len(error_records)} requests)")
        for r in error_records[:top_n]:
            print(f"   [{r.get('status')}] {r.get('request_method','')} {r.get('uri','')} "
                  f"rt={r.get('request_time','?')}s  addr={r.get('remote_addr','')}")
        if len(error_records) > top_n:
            print(f"   ... and {len(error_records) - top_n} more")
        print()

    error_rate = len(error_records) / total * 100 if total else 0
    print(f"[Summary] Total={total}  ErrorRate={error_rate:.2f}%  P99_Latency={p99:.4f}s")


def main():
    parser = argparse.ArgumentParser(description="Nginx JSON Log Analyzer")
    parser.add_argument("file", nargs="?", help="Log file path")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--top", type=int, default=5, help="Top N URIs (default: 5)")
    args = parser.parse_args()

    records = []
    if args.stdin:
        for line in sys.stdin:
            rec = parse_log_line(line)
            if rec:
                records.append(rec)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                rec = parse_log_line(line)
                if rec:
                    records.append(rec)
    else:
        print("Usage: python nginx-log-analyzer.py <logfile> [--stdin] [--top N]")
        sys.exit(1)

    analyze(records, top_n=args.top)


if __name__ == "__main__":
    main()
