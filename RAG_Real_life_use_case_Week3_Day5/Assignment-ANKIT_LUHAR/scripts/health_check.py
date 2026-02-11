#!/usr/bin/env python3
"""
DP World RAG Chatbot — Health Check Script.

Checks the health of all services.

Usage:
    python scripts/health_check.py [--api-url http://localhost:8000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> None:
    parser = argparse.ArgumentParser(description="Check service health")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    print("=" * 60)
    print("🏥 DP World Chatbot — Health Check")
    print("=" * 60)

    all_healthy = True

    # Check API
    print("\n[1] FastAPI Backend")
    try:
        resp = requests.get(f"{args.api_url}/api/v1/health/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✅ Status: {data.get('status', 'unknown')}")
            print(f"  ⏱  Uptime: {data.get('uptime_seconds', 0):.0f}s")
        else:
            print(f"  ❌ HTTP {resp.status_code}")
            all_healthy = False
    except requests.RequestException as e:
        print(f"  ❌ Unreachable: {e}")
        all_healthy = False

    # Check detailed health
    print("\n[2] Service Dependencies")
    try:
        resp = requests.get(f"{args.api_url}/api/v1/health/detailed", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            for service, status in data.get("services", {}).items():
                icon = "✅" if status in ("healthy", "configured") else "❌"
                print(f"  {icon} {service}: {status}")
                if status not in ("healthy", "configured"):
                    all_healthy = False
    except requests.RequestException:
        print("  ⚠️ Could not check detailed health")

    # Check Streamlit
    print("\n[3] Streamlit Frontend")
    try:
        resp = requests.get("http://localhost:8501/", timeout=5)
        if resp.status_code == 200:
            print("  ✅ Running")
        else:
            print(f"  ❌ HTTP {resp.status_code}")
            all_healthy = False
    except requests.RequestException:
        print("  ❌ Not running")
        all_healthy = False

    # Summary
    print(f"\n{'=' * 60}")
    if all_healthy:
        print("✅ All services are healthy!")
    else:
        print("⚠️ Some services have issues. Check the details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
