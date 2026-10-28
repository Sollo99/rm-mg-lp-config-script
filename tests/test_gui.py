"""Exercise GUI dispatch and worker lifecycle without opening a desktop window."""
import queue
import threading
import unittest
from unittest.mock import Mock, patch

try:
    from rmmglp import gui, service
except ModuleNotFoundError as exc:
    if exc.name == "tkinter":
        raise unittest.SkipTest("Optional Tkinter is not installed") from exc
    raise


class GuiTests(unittest.TestCase):
    def application(self):
        app = gui.Application.__new__(gui.Application)
        app.root = Mock()
        app.busy = False
        app.messages = queue.Queue()
        app.buttons = [Mock(), Mock()]
        app.status = Mock()
        app.log = Mock()
        app.refresh = Mock()
        return app

    def run_worker(self, app, operation, value, dry_run):
        workers = []
        real_thread = threading.Thread

        def thread(*args, **kwargs):
            worker = real_thread(*args, **kwargs)
            workers.append(worker)
            return worker

        with patch.object(gui.threading, "Thread", side_effect=thread):
            app.run(operation, value, dry_run)
        for worker in workers:
            worker.join(timeout=2)
            self.assertFalse(worker.is_alive())

    def test_preview_uses_worker_and_main_thread_updates(self):
        app = self.application()
        main_thread = threading.get_ident()
        worker_threads = []

        def operation(value, dry_run, emit):
            self.assertEqual(value, 1600)
            self.assertTrue(dry_run)
            worker_threads.append(threading.get_ident())
            emit("packet preview")

        self.run_worker(app, operation, "1600", True)
        self.assertNotEqual(worker_threads, [main_thread])
        app.log.assert_not_called()
        app.root.after.assert_not_called()
        self.assertTrue(app.busy)
        app.poll()
        self.assertFalse(app.busy)
        app.log.assert_any_call("packet preview")
        for button in app.buttons:
            self.assertEqual(button.configure.call_args.kwargs, {"state": "normal"})

    def test_error_reenables_buttons(self):
        app = self.application()
        operation = Mock(side_effect=RuntimeError("USB unavailable"))
        self.run_worker(app, operation, "500", False)
        app.poll()
        app.status.set.assert_called_with("Error: USB unavailable")
        self.assertFalse(app.busy)
        app.refresh.assert_not_called()

    def test_busy_blocks_new_operation_and_close(self):
        app = self.application()
        app.busy = True
        operation = Mock()
        app.run(operation, "500", False)
        operation.assert_not_called()
        app.close()
        app.root.destroy.assert_not_called()
        app.busy = False
        app.close()
        app.root.destroy.assert_called_once()

    def test_rgb_routes_all_captures_and_names(self):
        app = self.application()
        with patch.object(service, "set_rgb_named") as named, patch.object(service, "set_rgb_capture") as captured:
            app.rgb_operation("red", True, print)
            named.assert_called_once_with("red", True, print)
            app.rgb_operation("capture-46", False, print)
            captured.assert_called_once_with(46, False, print)

    def test_rgb_dispatch_preserves_string_argument(self):
        app = self.application()
        with patch.object(service, "set_rgb_capture") as captured:
            self.run_worker(app, app.rgb_operation, "capture-2", True)
        self.assertEqual(captured.call_args.args[:2], (2, True))
        app.poll()
        self.assertFalse(app.busy)


if __name__ == "__main__":
    unittest.main()
