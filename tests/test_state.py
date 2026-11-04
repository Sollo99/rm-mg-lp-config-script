"""Exercise real OS locks and atomic saving without accessing USB hardware."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from rmmglp import state


class StateTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "settings" / "config.json"
        patcher = patch.object(state, "STATE_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def child(self, crash=False):
        # A fresh interpreter exercises the OS lock, not the in-process guard.
        code = """
import os
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from rmmglp import state
state.STATE_FILE = Path(sys.argv[2])
try:
    with state.configuration_lock():
        if sys.argv[3] == 'crash':
            os._exit(0)
except RuntimeError as exc:
    print(exc)
    raise SystemExit(2)
"""
        return subprocess.run(
            [sys.executable, "-B", "-c", code,
             str(Path(state.__file__).resolve().parents[1]), str(self.path),
             "crash" if crash else "normal"],
            capture_output=True, text=True, timeout=10,
        )

    def test_competing_process_is_rejected_until_lock_released(self):
        with state.configuration_lock():
            result = self.child()
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Another configuration operation", result.stdout)
        result = self.child()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_competing_thread_is_rejected(self):
        errors = []

        def competing_operation():
            try:
                with state.configuration_lock():
                    self.fail("A competing thread acquired the lock")
            except RuntimeError as exc:
                errors.append(str(exc))

        with state.configuration_lock():
            worker = threading.Thread(target=competing_operation)
            worker.start()
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive())
        self.assertEqual(len(errors), 1)
        self.assertIn("Another configuration operation", errors[0])

    def test_process_exit_releases_lock_without_cleanup(self):
        result = self.child(crash=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.path.with_suffix(".lock").exists())
        with state.configuration_lock():
            pass

    def test_open_failure_releases_thread_guard(self):
        with patch.object(state.os, "open", side_effect=PermissionError("read only")):
            with self.assertRaisesRegex(PermissionError, "read only"):
                with state.configuration_lock():
                    pass
        with state.configuration_lock():
            pass

    def test_successful_saves_use_distinct_temporary_files(self):
        real_replace = state.os.replace
        paths = []

        def replace(source, destination):
            paths.append(Path(source))
            self.assertEqual(Path(source).parent, self.path.parent)
            # The temporary file is complete before the atomic replacement.
            self.assertEqual(json.loads(Path(source).read_text()), state.default_state())
            real_replace(source, destination)

        with patch.object(state.os, "replace", side_effect=replace):
            state.save_state(state.default_state())
            state.save_state(state.default_state())
        self.assertNotEqual(paths[0], paths[1])
        self.assertFalse(any(path.exists() for path in paths))
        self.assertEqual(state.load_state(), state.default_state())

    def test_failed_saves_preserve_existing_state_and_remove_temporary_files(self):
        state.save_state(state.default_state())
        before = self.path.read_bytes()
        changed = {**state.default_state(), "dpi": 1600}
        for module, name in ((state.json, "dump"), (state.os, "replace")):
            with self.subTest(failing_operation=name):
                with patch.object(module, name, side_effect=OSError("disk failure")):
                    with self.assertRaisesRegex(OSError, "disk failure"):
                        state.save_state(changed)
                self.assertEqual(self.path.read_bytes(), before)
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])


if __name__ == "__main__":
    unittest.main()
