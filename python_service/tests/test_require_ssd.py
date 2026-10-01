"""--require-ssd: the service does nothing without the archive drive and stops when it is removed."""
import logging
import unittest
from types import SimpleNamespace

import main


def service(mounted: bool, require_ssd: bool = True, configured: bool = True):
    s = main.MP3Service.__new__(main.MP3Service)
    s.require_ssd = require_ssd
    s.watch = True
    s.dry_run = False
    s.running = False
    s.watcher = None
    s.logger = logging.getLogger("test_require_ssd")
    s.scans = []
    s.processor = SimpleNamespace(
        ssd_archiver=SimpleNamespace(mounted=mounted, configured=configured),
        process_all=lambda: s.scans.append(1) or {},
    )
    return s


class RequireSSDTests(unittest.TestCase):
    def test_start_does_nothing_when_the_drive_is_not_mounted(self):
        s = service(mounted=False)
        with self.assertLogs("test_require_ssd", level="INFO") as logs:
            s.start()
        self.assertFalse(s.running)
        self.assertEqual(s.scans, [])
        self.assertIn("not connected", " ".join(logs.output))

    def test_start_does_nothing_when_no_drive_is_configured(self):
        s = service(mounted=False, configured=False)
        with self.assertLogs("test_require_ssd", level="WARNING") as logs:
            s.start()
        self.assertEqual(s.scans, [])
        self.assertIn("ssd_archive_path", " ".join(logs.output))

    def test_a_running_service_stops_when_the_drive_is_removed(self):
        s = service(mounted=True)
        s.running = True
        self.assertFalse(s._stop_if_ssd_removed())
        self.assertTrue(s.running)
        s.processor.ssd_archiver.mounted = False
        with self.assertLogs("test_require_ssd", level="INFO"):
            self.assertTrue(s._stop_if_ssd_removed())
        self.assertFalse(s.running)

    def test_without_the_flag_the_drive_is_never_a_reason_to_stop(self):
        s = service(mounted=False, require_ssd=False)
        s.running = True
        self.assertFalse(s._ssd_required_but_absent())
        self.assertFalse(s._stop_if_ssd_removed())
        self.assertTrue(s.running)


if __name__ == "__main__":
    unittest.main()
