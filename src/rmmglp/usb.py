from __future__ import annotations

import time

import usb.core
import usb.util

from .protocol import EP3, EP_OUT, EVENTS, IFACE, PID, POLLING_PACKETS, VID, build_full_packets


def find_device():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        raise RuntimeError("RM-MG-LP (04d9:a09f) not found.")
    return dev


def open_vendor_interface():
    dev = find_device()
    detached = False
    if dev.is_kernel_driver_active(IFACE):
        dev.detach_kernel_driver(IFACE)
        detached = True
    usb.util.claim_interface(dev, IFACE)
    return dev, detached


def close_vendor_interface(dev, detached):
    try:
        usb.util.release_interface(dev, IFACE)
    except Exception:
        pass
    usb.util.dispose_resources(dev)
    if detached:
        try:
            dev.attach_kernel_driver(IFACE)
        except Exception:
            pass


def apply_full_state(state: dict, dry_run: bool = False):
    ctrl5 = bytes.fromhex(state["rgb_ctrl5"])
    ctrl6 = bytes.fromhex(state["rgb_ctrl6"])
    ctrls, reports = build_full_packets(
        int(state["dpi"]), int(state["polling"]), ctrl5, ctrl6
    )

    print(f"DPI: {state['dpi']}")
    print(f"Polling: {state['polling']} Hz")
    print(f"RGB CTRL5: {state['rgb_ctrl5']}")
    print(f"RGB CTRL6: {state['rgb_ctrl6']}")

    if dry_run:
        print("Dry run: no USB writes performed.")
        return

    dev, detached = open_vendor_interface()
    try:
        start = time.monotonic()

        def wait_until(offset: float):
            remaining = offset - (time.monotonic() - start)
            if remaining > 0:
                time.sleep(remaining)

        for kind, index, offset in EVENTS:
            wait_until(offset)
            if kind == "ctrl":
                result = dev.ctrl_transfer(
                    0x21, 0x09, 0x0300, IFACE, ctrls[index], timeout=1000
                )
                if result != 8:
                    raise RuntimeError(
                        f"CTRL {index}: expected 8 bytes, got {result}"
                    )
            elif kind == "ep3":
                result = dev.write(EP_OUT, reports[index], timeout=1000)
                if result != 32:
                    raise RuntimeError(
                        f"EP3 {index}: expected 32 bytes, got {result}"
                    )
            else:
                feature = bytes(dev.ctrl_transfer(
                    0xA1, 0x01, 0x0300, IFACE, 8, timeout=1000
                ))
                print("GET_FEATURE:", feature.hex(" "))

        print("Configuration sent successfully.")
    finally:
        close_vendor_interface(dev, detached)


def set_polling_direct(rate: int, dry_run: bool = False):
    if rate not in POLLING_PACKETS:
        raise ValueError("Verified polling rates are 500 and 1000 Hz.")
    packet = POLLING_PACKETS[rate]
    print(f"Polling: {rate} Hz")
    print(f"CTRL3: {packet.hex(' ')}")
    if dry_run:
        print("Dry run: no USB writes performed.")
        return
    dev, detached = open_vendor_interface()
    try:
        result = dev.ctrl_transfer(
            0x21, 0x09, 0x0300, IFACE, packet, timeout=1000
        )
        if result != 8:
            raise RuntimeError(f"CTRL3: expected 8 bytes, got {result}")
        print("Polling configuration sent successfully.")
    finally:
        close_vendor_interface(dev, detached)
