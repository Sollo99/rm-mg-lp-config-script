from __future__ import annotations

import argparse
import json

from .protocol import (
    RGB_CAPTURED,
    RGB_NAMED,
    EP3,
    replace_button,
    all_actions,
    button_report,
)
from .state import load_state
from . import service
from usb.core import USBError
from .usb import find_device


def fmt(data: bytes) -> str:
    return data.hex(" ")


def die(message: str):
    raise SystemExit(message)


def cmd_show():
    print(json.dumps(load_state(), indent=2))


def cmd_info():
    dev = find_device()
    print(f"VID:PID      {dev.idVendor:04x}:{dev.idProduct:04x}")
    print(f"Manufacturer {dev.manufacturer}")
    print(f"Product      {dev.product}")
    print("Interface    2")
    print("EP OUT       0x03")


def cmd_dpi(value: str, dry_run: bool):
    service.set_dpi(int(value), dry_run)


def cmd_polling(value: str, dry_run: bool):
    service.set_polling(int(value), dry_run)


def cmd_rgb_named(name: str, dry_run: bool):
    service.set_rgb_named(name, dry_run)


def cmd_rgb_capture(number: str, dry_run: bool):
    service.set_rgb_capture(int(number), dry_run)


def cmd_list_rgb():
    print("Named RGB states:")
    for name, (ctrl5, ctrl6) in RGB_NAMED.items():
        print(f"  {name}")
        print(f"    CTRL5: {fmt(ctrl5)}")
        print(f"    CTRL6: {fmt(ctrl6)}")
    print()
    print("Captured RGB states:")
    for n, (ctrl5, ctrl6) in RGB_CAPTURED.items():
        print(f"  capture-{n:02}  CTRL5={fmt(ctrl5)}  CTRL6={fmt(ctrl6)}")


def build_parser():
    parser = argparse.ArgumentParser(prog="rm-mg-lpctl")
    parser.add_argument("--dry-run", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, fn in (("show", lambda a: cmd_show()), ("info", lambda a: cmd_info()), ("list-rgb", lambda a: cmd_list_rgb())):
        subp = sub.add_parser(name)
        subp.set_defaults(func=fn)

    dpi = sub.add_parser("dpi")
    dpi.add_argument("value")
    dpi.set_defaults(func=lambda a: cmd_dpi(a.value, a.dry_run))

    poll = sub.add_parser("polling")
    poll.add_argument("value")
    poll.set_defaults(func=lambda a: cmd_polling(a.value, a.dry_run))

    rgb = sub.add_parser("rgb")
    rgb_sub = rgb.add_subparsers(dest="rgb_command", required=True)
    named = rgb_sub.add_parser("named")
    named.add_argument("name", choices=sorted(RGB_NAMED))
    named.set_defaults(func=lambda a: cmd_rgb_named(a.name, a.dry_run))
    captured = rgb_sub.add_parser("capture")
    captured.add_argument("number")
    captured.set_defaults(func=lambda a: cmd_rgb_capture(a.number, a.dry_run))

    packet = sub.add_parser("packet")
    packet_sub = packet.add_subparsers(dest="packet_command", required=True)
    pbutton = packet_sub.add_parser("button")
    pbutton.add_argument("actions", nargs=8, choices=sorted(all_actions()))
    pbutton.set_defaults(func=lambda a: print(fmt(button_report(a.actions))))
    edit = packet_sub.add_parser("button-edit", help="Preview one slot; never sends USB writes")
    edit.add_argument("slot", type=int, choices=range(1, 9))
    edit.add_argument("action", choices=sorted(all_actions()))
    edit.add_argument("--report", help="32-byte base report in hex; defaults to captured EP3 #3")
    edit.set_defaults(func=lambda a: print(fmt(replace_button(
        bytes.fromhex(a.report) if a.report else EP3[3], a.slot, a.action))))
    prgb = packet_sub.add_parser("rgb")
    prgb.add_argument("preset", choices=sorted(RGB_NAMED))
    prgb.set_defaults(func=lambda a: (print("CTRL5", fmt(RGB_NAMED[a.preset][0])), print("CTRL6", fmt(RGB_NAMED[a.preset][1]))))

    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (ValueError, RuntimeError, OSError, USBError) as exc:
        die(f"Error: {exc}")


if __name__ == "__main__":
    main()
