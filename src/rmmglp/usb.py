from __future__ import annotations

import time

import usb.core
import usb.util

from .protocol import EP_OUT, EVENTS, IFACE, PID, POLLING_PACKETS, VID, build_full_packets, format_transaction
from .state import validate_state


def find_device():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        raise RuntimeError("RM-MG-LP (04d9:a09f) not found.")
    return dev


def open_vendor_interface():
    dev = find_device()
    detached = False
    try:
        if dev.is_kernel_driver_active(IFACE):
            dev.detach_kernel_driver(IFACE)
            detached = True
        usb.util.claim_interface(dev, IFACE)
    except Exception:
        close_vendor_interface(dev, detached)
        raise
    return dev, detached


def close_vendor_interface(dev, detached):
    try:
        usb.util.release_interface(dev, IFACE)
    except Exception:
        pass
    try:
        usb.util.dispose_resources(dev)
    finally:
        if detached:
            try:
                dev.attach_kernel_driver(IFACE)
            except Exception:
                pass


def apply_full_state(state: dict, dry_run: bool = False, emit=print):
    validate_state(state)
    ctrl5 = bytes.fromhex(state["rgb_ctrl5"])
    ctrl6 = bytes.fromhex(state["rgb_ctrl6"])
    ctrls, reports = build_full_packets(
        int(state["dpi"]), int(state["polling"]), ctrl5, ctrl6
    )

    emit(f"DPI: {state['dpi']}")
    emit(f"Polling: {state['polling']} Hz")
    emit(f"RGB CTRL5: {state['rgb_ctrl5']}")
    emit(f"RGB CTRL6: {state['rgb_ctrl6']}")

    if dry_run:
        emit(format_transaction(ctrls, reports))
        emit("Dry run: no USB access or state saving performed.")
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
                emit("GET_FEATURE: " + feature.hex(" "))

        emit("Configuration sent successfully.")
    finally:
        close_vendor_interface(dev, detached)


def set_polling_direct(rate: int, dry_run: bool = False, emit=print):
    if rate not in POLLING_PACKETS:
        raise ValueError("Verified polling rates are 500 and 1000 Hz.")
    packet = POLLING_PACKETS[rate]
    emit(f"Polling: {rate} Hz")
    emit(f"0.000000s CTRL3        {packet.hex(' ')}")
    if dry_run:
        emit("Dry run: no USB access or state saving performed.")
        return
    dev, detached = open_vendor_interface()
    try:
        result = dev.ctrl_transfer(
            0x21, 0x09, 0x0300, IFACE, packet, timeout=1000
        )
        if result != 8:
            raise RuntimeError(f"CTRL3: expected 8 bytes, got {result}")
        emit("Polling configuration sent successfully.")
    finally:
        close_vendor_interface(dev, detached)
