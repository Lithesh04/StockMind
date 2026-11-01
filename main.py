"""StockMind command-line entry point.

Quick start:
  python main.py setup
  python main.py demo
  python main.py api
  python main.py test
"""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stockmind.demo import (run_all_demos, run_reflex_demo, run_monitor_demo, run_negotiation_demo,
                            run_utility_demo, run_bdi_demo, run_security_demo, run_api_demo)
from stockmind.security import ensure_demo_keys


def write_text(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def setup() -> None:
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "data").mkdir(exist_ok=True)
    ensure_demo_keys(ROOT / "data" / "keys")
    print("[SETUP] StockMind folders checked")
    print("[SETUP] Demo Ed25519 keys generated/verified in data/keys")
    print("[SECURITY] Keep *_private.pem files private; they are excluded by .gitignore")


def demo(include_live_api: bool = False) -> None:
    setup()
    output = run_all_demos(include_live_api=include_live_api)
    write_text("logs/assignment_1_2_reflex_execution.txt", run_reflex_demo())
    write_text("logs/assignment_2_1_concurrency_latency.txt", run_monitor_demo())
    write_text("logs/assignment_3_1_negotiation_timeline.txt", run_negotiation_demo())
    utility_text, utility_result = run_utility_demo()
    write_text("logs/assignment_3_2_utility_results.txt", utility_text)
    with (ROOT / "logs" / "assignment_3_2_utility_results.csv").open("w", newline="", encoding="utf-8") as handle:
        rows = utility_result["evaluated"]
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    write_text("logs/assignment_4_1_bdi_replanning.txt", run_bdi_demo())
    write_text("logs/assignment_5_1_security_verification.txt", run_security_demo())
    write_text("logs/full_demo_execution.txt", output["text"])
    print(output["text"])
    print("\n[FILES] Assignment logs written to the logs/ folder")


def live_api() -> None:
    try:
        result = run_api_demo()
        text = "ASSIGNMENT 4.2 - LIVE OPEN-METEO API RESULT\n" + json.dumps(result, indent=2)
        write_text("logs/assignment_4_2_live_api.txt", text)
        print(text)
    except Exception as exc:
        text = f"LIVE API REQUEST FAILED: {exc}\nCheck internet access and run python main.py api again."
        write_text("logs/assignment_4_2_live_api_error.txt", text)
        print(text)
        raise SystemExit(1)


def run_tests() -> None:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
    raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="StockMind autonomous inventory agent")
    parser.add_argument("command", choices=["setup", "demo", "api", "test"], nargs="?", default="demo")
    parser.add_argument("--live-api", action="store_true", help="Include a real Open-Meteo API request in the demo")
    args = parser.parse_args()
    if args.command == "setup": setup()
    elif args.command == "demo": demo(include_live_api=args.live_api)
    elif args.command == "api": live_api()
    elif args.command == "test": run_tests()

if __name__ == "__main__":
    main()
