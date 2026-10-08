from __future__ import annotations

import json
import os
from pathlib import Path

from .protocol import RGB_NAMED

STATE_FILE = Path.home() / ".config" / "rm-mg-lp" / "config.json"


def default_state() -> dict:
    return {
        "dpi": 1200,
        "polling": 1000,
        "rgb_ctrl5": RGB_NAMED["green"][0].hex(),
        "rgb_ctrl6": RGB_NAMED["green"][1].hex(),
    }


def load_state() -> dict:
    if not STATE_FILE.exists():
        return default_state()
    try:
        with STATE_FILE.open() as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read {STATE_FILE}: {exc}") from exc
    return {**default_state(), **state}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.replace(tmp, STATE_FILE)
