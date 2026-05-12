#!/usr/bin/env python3
"""
HTTP Endpoint Health Checker

Reads target list from a YAML config file, concurrently checks all endpoints,
and reports results. Supports Prometheus textfile collector format for
integration with Node Exporter.

Usage:
  python health-checker.py targets.yaml
  python health-checker.py targets.yaml --prometheus /var/lib/node_exporter/health.prom
  python health-checker.py targets.yaml --json
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed


def check_endpoint(name, url, method="GET", expected_status=200, timeout=5):
    """Check a single HTTP endpoint, return result dict"""
    start = time.time()
    result = {
        "name": name,
        "url": url,
        "method": method,
    }

    try:
        req = urllib.request.Request(url, method=method)
        resp = urllib.request.urlopen(req, timeout=timeout)
        elapsed = time.time() - start
        result["status"] = resp.status
        result["latency"] = round(elapsed, 4)
        result["healthy"] = resp.status == expected_status
        result["error"] = None
    except urllib.error.HTTPError as e:
        result["status"] = e.code
        result["latency"] = round(time.time() - start, 4)
        result["healthy"] = False
        result["error"] = f"HTTP {e.code}"
    except Exception as e:
        result["status"] = 0
        result["latency"] = round(time.time() - start, 4)
        result["healthy"] = False
        result["error"] = str(e)

    return result


def load_targets(path):
    """Load targets from YAML config file"""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("targets", [])


def output_text(results):
    """Plain-text table output"""
    print(f"{'Status':<8} {'Name':<30} {'Code':<6} {'Latency':<10} URL")
    print("-" * 90)
    ok = 0
    fail = 0
    for r in results:
        icon = "[OK]" if r["healthy"] else "[FAIL]"
        status = str(r["status"]) if r["status"] else "ERR"
        error = f" ({r['error']})" if r.get("error") else ""
        print(f"{icon:<8} {r['name']:<30} {status:<6} {r['latency']}s   {r['url']}{error}")
        if r["healthy"]:
            ok += 1
        else:
            fail += 1
    print("-" * 90)
    print(f"Total: {ok} OK / {fail} FAIL / {ok+fail} Total")


def output_json(results):
    """JSON output"""
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(results),
        "healthy": sum(1 for r in results if r["healthy"]),
        "unhealthy": sum(1 for r in results if not r["healthy"]),
        "results": results,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def output_prometheus(results, output_path=None):
    """Prometheus textfile collector format"""
    lines = []
    lines.append("# HELP http_health_check_up Endpoint health (1=up, 0=down)")
    lines.append("# TYPE http_health_check_up gauge")

    for r in results:
        name_safe = r["name"].replace(" ", "_").replace("-", "_")
        value = 1 if r["healthy"] else 0
        lines.append(f'http_health_check_up{{name="{name_safe}",url="{r["url"]}"}} {value}')

    lines.append("# HELP http_health_check_latency_seconds Response latency in seconds")
    lines.append("# TYPE http_health_check_latency_seconds gauge")
    for r in results:
        name_safe = r["name"].replace(" ", "_").replace("-", "_")
        lines.append(f'http_health_check_latency_seconds{{name="{name_safe}",url="{r["url"]}"}} {r["latency"]}')

    output = "\n".join(lines) + "\n"

    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
        print(f"Prometheus metrics written to {output_path}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="HTTP Endpoint Health Checker")
    parser.add_argument("targets", help="YAML targets config file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--prometheus", nargs="?", const="-", metavar="PATH",
                        help="Output in Prometheus textfile format (optional: output file path)")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrency level (default: 5)")
    args = parser.parse_args()

    targets = load_targets(args.targets)

    if not targets:
        print("Error: No targets found. Check config file format.")
        sys.exit(1)

    # Concurrent health checks
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {}
        for t in targets:
            future = executor.submit(
                check_endpoint,
                t.get("name", t.get("url")),
                t.get("url"),
                t.get("method", "GET"),
                t.get("expected_status", 200),
                t.get("timeout", 5),
            )
            futures[future] = t

        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda r: r["name"])

    if args.prometheus:
        path = None if args.prometheus == "-" else args.prometheus
        output_prometheus(results, path)
    elif args.json:
        output_json(results)
    else:
        output_text(results)

    # Non-zero exit if any endpoint is unhealthy
    if any(not r["healthy"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
