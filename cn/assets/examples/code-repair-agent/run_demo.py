import argparse
import json
from pathlib import Path

from runner import SCENARIOS, run_scenario


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the deterministic code repair fixture")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="success")
    parser.add_argument("--out", type=Path, default=Path("artifacts/demo"))
    args = parser.parse_args()
    print(json.dumps(run_scenario(args.scenario, args.out), ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
