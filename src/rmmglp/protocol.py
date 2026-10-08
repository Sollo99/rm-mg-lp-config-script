from __future__ import annotations

VID = 0x04D9

PID = 0xA09F

IFACE = 2

EP_OUT = 0x03

POLLING_PACKETS = {
    500: bytes.fromhex("27 2b dd ff 00 1d 96 76"),
    1000: bytes.fromhex("27 2b dd ff e8 25 96 76"),
}

CTRL = [
    bytes.fromhex("27 27 dd ff f4 2d 96 76"),
    bytes.fromhex("25 2d a5 ff f0 32 06 ee"),
    bytes.fromhex("27 2b dd ff e8 25 96 76"),
    None,
    bytes.fromhex("27 2b 65 ff e8 ed 96 76"),
    None,
    None,
    bytes.fromhex("27 2a 85 ff f0 95 96 36"),
    bytes.fromhex("27 2a 8d ff e8 95 96 36"),
    bytes.fromhex("27 2b fd ff e0 9d 96 b6"),
    bytes.fromhex("27 2d 5d ff e8 a5 98 76"),
    bytes.fromhex("27 2d 25 ff 00 a5 98 76"),
    bytes.fromhex("27 2b fd ff f8 95 96 d6"),
    bytes.fromhex("27 2c 65 02 40 da ac d6"),
]

EP3 = [
    bytes.fromhex("ff 00 00 00 ff 00 00 00 ff ff ff 00 ff 00 ff 00 ff ff ff 80 00 ff ff ff 00 00 00 00 00 00 00 00"),
    bytes.fromhex("ff 00 00 00 ff 00 00 00 ff ff ff 00 00 ff ff ff 00 ff ff ff ff ff 55 00 00 00 00 00 00 00 00 00"),
    bytes.fromhex("0c 10 05 3d 4f d0 50 f8 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    bytes.fromhex("01 00 f0 00 01 00 f1 00 01 00 f2 00 01 00 f4 00 01 00 f3 00 07 00 04 02 07 00 03 00 0b 00 00 00"),
    bytes.fromhex("05 00 03 00 0a f0 32 02 0b 00 00 00 0b 00 00 00 0b 00 00 00 0b 00 00 00 04 00 01 00 04 00 02 00"),
    bytes(32),
    bytes(32),
    bytes.fromhex("ff 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
]

RGB_NAMED = {
    "green": (
        bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"),
        bytes.fromhex("27 2b 6d ff e8 fd 9d 6e"),
    ),
    "red": (
        bytes.fromhex("27 2b 9d 04 98 f5 96 76"),
        bytes.fromhex("27 2b 6d ff e8 fd 9d 6e"),
    ),
    "blue": (
        bytes.fromhex("27 2b 9d ff f0 fa 2e 76"),
        bytes.fromhex("27 2b 6d ff e8 fd 9d 6e"),
    ),
}

RGB_CAPTURED = {
    1: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 6d ff f0 fd 96 76")),
    2: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 6d ff e8 fd 9d 6e")),
    3: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 6d ff e8 fd 9d 6e")),
    4: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 6d ff e8 fd 9d 6e")),
    5: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 7d ff e8 fd 8d 6e")),
    6: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 5d ff 00 fd 96 96")),
    7: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 5d ff 00 fd 96 96")),
    8: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 5d ff 00 fd 96 96")),
    9: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 2d ff 00 fd 86 96")),
    10: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 5d ff f8 02 2e 96")),
    11: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 4d ff f8 02 2e 86")),
    12: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 7d ff f8 02 2e 76")),
    13: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 45 ff f8 fd 96 76")),
    14: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 4d ff f8 02 2e 86")),
    15: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 25 ff d0 02 2e 96")),
    16: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 55 ff d0 02 2e 86")),
    17: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 45 ff d0 02 2e 76")),
    18: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 4d ff c8 fd 9d 6e")),
    19: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 4d ff c8 fd 9d 6e")),
    20: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 4d ff c8 fd 9d 6e")),
    21: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 5d ff c8 fd 8d 6e")),
    22: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 0d ff e0 fd 86 96")),
    23: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 3d ff e0 fd 86 86")),
    24: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 2d ff e0 fd 86 76")),
    25: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 5d ff e0 fd 96 76")),
    26: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 5d ff e0 fd 96 76")),
    27: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 5d ff e0 fd 96 76")),
    28: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 25 ff d8 fd 96 76")),
    29: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 25 ff d8 fd 96 76")),
    30: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 25 ff d8 fd 96 76")),
    31: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 35 ff d8 fd 86 76")),
    32: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 2d ff 30 fd a5 6e")),
    33: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 25 ff 30 fd 9d 6e")),
    34: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 25 ff 30 fd 9d 6e")),
    35: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 25 ff 30 fd 9d 6e")),
    36: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2d 2d ff 28 ff 9d 6e")),
    37: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2a 2d ff 28 fc 9d 6e")),
    38: (bytes.fromhex("27 2b 9d 04 98 f5 96 76"), bytes.fromhex("27 2b 2d ff 28 fd 9d 6e")),
    39: (bytes.fromhex("27 2b 9d ff f0 f5 9d 6e"), bytes.fromhex("27 2b 2d ff 28 fd 9d 6e")),
    40: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 2d ff 28 fd 9d 6e")),
    41: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 3d ff 28 fd 8d 6e")),
    42: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 2d ff 40 fd 9d 66")),
    43: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 3d ff 40 fd 8d 66")),
    44: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 0d ff 40 fd 7d 66")),
    45: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 05 ff 38 fd 8d 66")),
    46: (bytes.fromhex("27 2b 9d ff f0 fa 2e 76"), bytes.fromhex("27 2b 05 ff 38 fd 8d 66")),
}

EVENTS = [
    ("ctrl", 0, 0.000000),
    ("get", 0, 0.000667),
    ("ctrl", 1, 0.001109),
    ("ctrl", 2, 0.029335),
    ("ctrl", 3, 0.052092),
    ("ctrl", 4, 0.083352),
    ("ctrl", 5, 0.114583),
    ("ctrl", 6, 0.152160),
    ("ctrl", 7, 0.183398),
    ("ep3", 0, 0.214646),
    ("ctrl", 8, 0.252206),
    ("ep3", 1, 0.283433),
    ("ctrl", 9, 0.314669),
    ("ep3", 2, 0.352206),
    ("ctrl", 10, 0.367865),
    ("ep3", 3, 0.383488),
    ("ep3", 4, 0.399124),
    ("ctrl", 11, 0.414678),
    ("ep3", 5, 0.430375),
    ("ep3", 6, 0.452200),
    ("ctrl", 12, 0.467930),
    ("ep3", 7, 0.483576),
    ("ctrl", 13, 0.530519),
]

BUTTON_ACTIONS = {
    "left": bytes.fromhex("01 00 F0 00"),
    "right": bytes.fromhex("01 00 F1 00"),
    "middle": bytes.fromhex("01 00 F2 00"),
    "forward": bytes.fromhex("01 00 F4 00"),
    "backward": bytes.fromhex("01 00 F3 00"),
    "dpi+": bytes.fromhex("07 00 01 00"),
    "dpi-": bytes.fromhex("07 00 02 00"),
    "dpi-cycle": bytes.fromhex("07 00 03 00"),
    "poll+": bytes.fromhex("05 00 01 00"),
    "poll-": bytes.fromhex("05 00 02 00"),
    "poll-cycle": bytes.fromhex("05 00 03 00"),
    "double-click": bytes.fromhex("0A F0 32 02"),
    "triple-click": bytes.fromhex("0A F0 32 03"),
}

MULTIMEDIA_ACTIONS = {
    "media-player": bytes.fromhex("03 00 83 01"),
    "play-pause": bytes.fromhex("03 00 CD 00"),
    "stop": bytes.fromhex("03 00 B7 00"),
    "previous": bytes.fromhex("03 00 B6 00"),
    "next": bytes.fromhex("03 00 B5 00"),
    "volume+": bytes.fromhex("03 00 E9 00"),
    "volume-": bytes.fromhex("03 00 EA 00"),
    "mute": bytes.fromhex("03 00 E2 00"),
}

WINDOWS_ACTIONS = {
    "browser-home": bytes.fromhex("03 00 23 02"),
    "browser-favorites": bytes.fromhex("03 00 2A 02"),
    "browser-forward": bytes.fromhex("03 00 25 02"),
    "browser-back": bytes.fromhex("03 00 24 02"),
    "browser-stop": bytes.fromhex("03 00 26 02"),
    "browser-refresh": bytes.fromhex("03 00 27 02"),
    "browser-search": bytes.fromhex("03 00 21 02"),
    "email": bytes.fromhex("03 00 8A 01"),
    "calculator": bytes.fromhex("03 00 92 01"),
    "computer": bytes.fromhex("03 00 94 01"),
}

OFFICE_ACTIONS = {
    "cut": bytes.fromhex("00 01 1B 00"),
    "copy": bytes.fromhex("00 01 06 00"),
    "paste": bytes.fromhex("00 01 19 00"),
    "open": bytes.fromhex("00 01 12 00"),
    "save": bytes.fromhex("00 01 16 00"),
    "find": bytes.fromhex("00 01 09 00"),
    "redo": bytes.fromhex("00 01 1C 00"),
    "select-all": bytes.fromhex("00 01 04 00"),
    "new": bytes.fromhex("00 01 11 00"),
    "print": bytes.fromhex("00 01 13 00"),
}

SYSTEM_ACTIONS = {
    "switch-windows": bytes.fromhex("00 04 2B 00"),
    "close-window": bytes.fromhex("00 04 3D 00"),
    "show-desktop": bytes.fromhex("00 08 07 00"),
    "lock-pc": bytes.fromhex("00 08 0F 00"),
    "run-command": bytes.fromhex("00 08 15 00"),
}

def validate_dpi(dpi: int) -> None:
    if dpi < 200 or dpi > 16000 or dpi % 100:
        raise ValueError("DPI must be 200-16000 in 100-DPI steps.")


def validate_rgb(ctrl5: bytes, ctrl6: bytes) -> None:
    if len(ctrl5) != 8 or len(ctrl6) != 8:
        raise ValueError("RGB control packets must be 8 bytes.")


def build_full_packets(dpi: int, polling: int, ctrl5: bytes, ctrl6: bytes):
    validate_dpi(dpi)
    if polling not in POLLING_PACKETS:
        raise ValueError("Verified polling rates are 500 and 1000 Hz.")
    validate_rgb(ctrl5, ctrl6)

    ctrls = list(CTRL)
    ctrls[3] = POLLING_PACKETS[polling]
    ctrls[5] = ctrl5
    ctrls[6] = ctrl6

    reports = list(EP3)
    reports[2] = bytes([dpi // 100]) + reports[2][1:]

    if any(x is None or len(x) != 8 for x in ctrls):
        raise RuntimeError("Internal CTRL packet error.")
    if any(len(x) != 32 for x in reports):
        raise RuntimeError("Internal EP3 packet error.")
    return ctrls, reports


def all_actions() -> dict[str, bytes]:
    actions = {}
    actions.update(BUTTON_ACTIONS)
    actions.update(MULTIMEDIA_ACTIONS)
    actions.update(WINDOWS_ACTIONS)
    actions.update(OFFICE_ACTIONS)
    actions.update(SYSTEM_ACTIONS)
    return actions


def button_report(action_names: list[str]) -> bytes:
    if len(action_names) != 8:
        raise ValueError("Exactly 8 button slots are required.")
    actions = all_actions()
    try:
        return b"".join(actions[name] for name in action_names)
    except KeyError as exc:
        raise ValueError(f"Unknown action: {exc.args[0]}") from exc
