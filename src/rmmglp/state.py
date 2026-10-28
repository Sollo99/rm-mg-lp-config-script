from __future__ import annotations

import json
import os
from pathlib import Path

from .protocol import RGB_NAMED, POLLING_PACKETS, validate_dpi, validate_rgb

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
    validate_state(state, partial=True)
    return {**default_state(), **state}


def validate_state(state: dict, partial: bool = False) -> None:
    if not isinstance(state, dict):
        raise ValueError("Configuration must be a JSON object.")
    candidate = {**default_state(), **state} if partial else state
    try:
        validate_dpi(candidate["dpi"])
        if type(candidate["polling"]) is not int or candidate["polling"] not in POLLING_PACKETS:
            raise ValueError("Verified polling rates are 500 and 1000 Hz.")
        colors = []
        for key in ("rgb_ctrl5", "rgb_ctrl6"):
            if not isinstance(candidate[key], str):
                raise ValueError(f"{key} must be a hexadecimal string.")
            colors.append(bytes.fromhex(candidate[key]))
        validate_rgb(*colors)
    except KeyError as exc:
        raise ValueError(f"Missing configuration field: {exc.args[0]}") from exc


def save_state(state: dict) -> None:
    validate_state(state)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.replace(tmp, STATE_FILE)
