import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from rmmglp import cli, service, state, usb
from rmmglp.protocol import EP3, RGB_CAPTURED, RGB_NAMED, build_full_packets, replace_button


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "config.json"
        self.patcher = patch.object(state, "STATE_FILE", self.path)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_invalid_state_is_rejected(self):
        for invalid in ([], None, 42, {"dpi": True}, {"dpi": "1600"},
                        {"dpi": 100}, {"dpi": 16100}, {"dpi": 1250},
                        {"polling": 250}, {"polling": 1000.0},
                        {"rgb_ctrl5": "zz"}, {"rgb_ctrl6": "00"}, {"rgb_ctrl5": 8}):
            with self.subTest(invalid=invalid):
                self.path.write_text(json.dumps(invalid))
                with self.assertRaises(ValueError):
                    state.load_state()

    def test_corrupted_json(self):
        self.path.write_text("{")
        with self.assertRaisesRegex(RuntimeError, "Could not read"):
            state.load_state()

    def test_partial_and_atomic_save(self):
        self.path.write_text('{"dpi": 1600}')
        loaded = state.load_state()
        self.assertEqual(loaded["polling"], 1000)
        with patch.object(state.os, "replace", wraps=state.os.replace) as replace:
            state.save_state(loaded)
        replace.assert_called_once()
        self.assertEqual(state.load_state(), loaded)

    def test_all_dry_runs_skip_usb_and_save(self):
        with patch.object(usb, "open_vendor_interface") as opened, patch.object(service, "save_state") as saved:
            for operation, argument in ((service.set_dpi, 1600), (service.set_polling, 500),
                                        (service.set_rgb_named, "red"), (service.set_rgb_capture, 46)):
                lines = []
                operation(argument, dry_run=True, emit=lines.append)
                self.assertTrue(any("0.000000s" in line for line in lines))
            opened.assert_not_called()
            saved.assert_not_called()
        self.assertFalse(self.path.exists())

    def test_existing_state_unchanged_by_preview(self):
        state.save_state(state.default_state())
        before = self.path.read_bytes()
        service.set_dpi(1600, dry_run=True, emit=lambda _: None)
        self.assertEqual(self.path.read_bytes(), before)

    def test_failed_usb_does_not_save(self):
        with patch.object(service, "apply_full_state", side_effect=RuntimeError("USB failure")), patch.object(service, "save_state") as saved:
            with self.assertRaisesRegex(RuntimeError, "USB failure"):
                service.set_dpi(1600)
            saved.assert_not_called()

    def test_direct_polling_and_save_order(self):
        calls = []
        with patch.object(service, "set_polling_direct", side_effect=lambda *a, **kw: calls.append("usb")), patch.object(service, "apply_full_state") as full, patch.object(service, "save_state", side_effect=lambda s: calls.append("save")):
            result = service.set_polling(500)
        self.assertEqual(calls, ["usb", "save"])
        self.assertEqual(result["polling"], 500)
        full.assert_not_called()

    def test_successful_full_write_saves_new_state(self):
        with patch.object(service, "apply_full_state") as apply:
            service.set_dpi(1600)
        self.assertEqual(state.load_state()["dpi"], 1600)
        self.assertEqual(apply.call_args.args[0]["dpi"], 1600)

    def test_cli_preview_button_preserves_slots(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            args = cli.build_parser().parse_args(["packet", "button-edit", "5", "right"])
            args.func(args)
        report = bytes.fromhex(output.getvalue())
        self.assertEqual(report[:16], EP3[3][:16])
        self.assertEqual(report[16:20], bytes.fromhex("01 00 f1 00"))
        self.assertEqual(report[20:], EP3[3][20:])

    def test_button_edit_rejects_invalid_inputs(self):
        for report, slot, action in ((bytes(33), 5, "right"), (EP3[3], 0, "right"),
                                     (EP3[3], 9, "right"), (EP3[3], True, "right"),
                                     (EP3[3], 5, "unknown")):
            with self.assertRaises(ValueError):
                replace_button(report, slot, action)

    def test_all_slots_preserve_other_bytes(self):
        original = bytes(range(32))
        for slot in range(1, 9):
            offset = (slot - 1) * 4
            modified = replace_button(original, slot, "right")
            self.assertEqual(len(modified), 32)
            self.assertEqual(modified[:offset], original[:offset])
            self.assertEqual(modified[offset + 4:], original[offset + 4:])
        self.assertEqual(original, bytes(range(32)))

    def test_rgb_captures_preserved_in_build(self):
        for pair in RGB_CAPTURED.values():
            ctrls, _ = build_full_packets(1200, 1000, *pair)
            self.assertEqual((ctrls[5], ctrls[6]), pair)
        self.assertEqual(RGB_NAMED["red"][0], bytes.fromhex("27 2b 9d 04 98 f5 96 76"))
        self.assertEqual(RGB_NAMED["blue"][0], bytes.fromhex("27 2b 9d ff f0 fa 2e 76"))


class TransportTests(unittest.TestCase):
    def test_claim_failure_restores_driver(self):
        dev = Mock()
        dev.is_kernel_driver_active.return_value = True
        with patch.object(usb, "find_device", return_value=dev), patch.object(usb.usb.util, "claim_interface", side_effect=RuntimeError("claim failed")), patch.object(usb.usb.util, "release_interface"), patch.object(usb.usb.util, "dispose_resources"):
            with self.assertRaisesRegex(RuntimeError, "claim failed"):
                usb.open_vendor_interface()
        dev.detach_kernel_driver.assert_called_once_with(2)
        dev.attach_kernel_driver.assert_called_once_with(2)

    def test_short_write_cleans_up(self):
        dev = Mock()
        dev.ctrl_transfer.return_value = 7
        with patch.object(usb, "open_vendor_interface", return_value=(dev, False)), patch.object(usb, "close_vendor_interface") as close:
            with self.assertRaisesRegex(RuntimeError, "expected 8 bytes"):
                usb.set_polling_direct(500, emit=lambda _: None)
        close.assert_called_once_with(dev, False)

    def test_transaction_sequence_and_deadlines(self):
        # Independent fixture from the known-good capture, including GET_FEATURE.
        expected = [
            ("ctrl", 0, 0.000000), ("get", 0, 0.000667),
            ("ctrl", 1, 0.001109), ("ctrl", 2, 0.029335),
            ("ctrl", 3, 0.052092), ("ctrl", 4, 0.083352),
            ("ctrl", 5, 0.114583), ("ctrl", 6, 0.152160),
            ("ctrl", 7, 0.183398), ("ep3", 0, 0.214646),
            ("ctrl", 8, 0.252206), ("ep3", 1, 0.283433),
            ("ctrl", 9, 0.314669), ("ep3", 2, 0.352206),
            ("ctrl", 10, 0.367865), ("ep3", 3, 0.383488),
            ("ep3", 4, 0.399124), ("ctrl", 11, 0.414678),
            ("ep3", 5, 0.430375), ("ep3", 6, 0.452200),
            ("ctrl", 12, 0.467930), ("ep3", 7, 0.483576),
            ("ctrl", 13, 0.530519),
        ]
        ctrls, reports = build_full_packets(1200, 1000, *RGB_NAMED["green"])
        sent = []
        sleeps = []
        dev = Mock()

        def ctrl(request_type, request, value, interface, data, timeout):
            self.assertEqual((value, interface, timeout), (0x0300, 2, 1000))
            if request_type == 0xA1:
                self.assertEqual((request, data), (0x01, 8))
                sent.append(("get", None))
                return bytes.fromhex("25 28 fd ff f4 32 06 ee")
            self.assertEqual((request_type, request), (0x21, 0x09))
            self.assertEqual(len(data), 8)
            sent.append(("ctrl", data))
            return 8

        def write(endpoint, data, timeout):
            self.assertEqual((endpoint, len(data), timeout), (3, 32, 1000))
            sent.append(("ep3", data))
            return 32

        dev.ctrl_transfer.side_effect = ctrl
        dev.write.side_effect = write
        with patch.object(usb, "open_vendor_interface", return_value=(dev, False)), patch.object(usb, "close_vendor_interface") as close, patch.object(usb.time, "monotonic", return_value=0), patch.object(usb.time, "sleep", side_effect=sleeps.append):
            usb.apply_full_state(state.default_state(), emit=lambda _: None)
        self.assertEqual(sent, [(kind, None if kind == "get" else (ctrls if kind == "ctrl" else reports)[index]) for kind, index, _ in expected])
        self.assertEqual(sleeps, [offset for _, _, offset in expected if offset > 0])
        close.assert_called_once_with(dev, False)


if __name__ == "__main__":
    unittest.main()
