from __future__ import annotations

import argparse
import json
from pathlib import Path

from plan_contract import PlanContractError, validate_plan_contract


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a locked nook slide deck plan without rendering PPTX.")
    parser.add_argument("plan", help="Path to deck_plan.json")
    args = parser.parse_args()
    path = Path(args.plan)
    try:
        plan = json.loads(path.read_text(encoding="utf-8-sig"))
        validate_plan_contract(plan, path)
    except (OSError, json.JSONDecodeError, PlanContractError) as exc:
        print(f"FAILED: {exc}")
        return 1
    print(f"OK pages={len(plan['pages'])} status={plan.get('plan_status', 'prototype')} theme={plan['theme']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

