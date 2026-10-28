"""Shared application operations for CLI and GUI. No hardware readback implied."""
from __future__ import annotations

from .protocol import RGB_CAPTURED, RGB_NAMED
from .state import load_state, save_state, validate_state
from .usb import apply_full_state, set_polling_direct


def _apply(changes: dict, dry_run: bool, emit, polling_only=False):
    state = load_state()
    state.update(changes)
    validate_state(state)
    if polling_only:
        set_polling_direct(state["polling"], dry_run, emit=emit)
    else:
        apply_full_state(state, dry_run, emit=emit)
    if not dry_run:
        try:
            save_state(state)
        except OSError as exc:
            raise RuntimeError(
                "USB write succeeded, but saving the local configuration failed: " + str(exc)
            ) from exc
    return state


def set_dpi(value: int, dry_run=False, emit=print):
    return _apply({"dpi": value}, dry_run, emit)


def set_polling(value: int, dry_run=False, emit=print):
    return _apply({"polling": value}, dry_run, emit, polling_only=True)


def _set_rgb(pair, dry_run, emit):
    return _apply(dict(zip(("rgb_ctrl5", "rgb_ctrl6"), (p.hex() for p in pair))), dry_run, emit)


def set_rgb_named(name: str, dry_run=False, emit=print):
    if name not in RGB_NAMED:
        raise ValueError("Unknown named RGB capture.")
    return _set_rgb(RGB_NAMED[name], dry_run, emit)


def set_rgb_capture(number: int, dry_run=False, emit=print):
    if type(number) is not int or number not in RGB_CAPTURED:
        raise ValueError("Capture ID must be between 1 and 46.")
    return _set_rgb(RGB_CAPTURED[number], dry_run, emit)
