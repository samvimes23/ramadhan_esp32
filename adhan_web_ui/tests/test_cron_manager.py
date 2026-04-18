import tempfile
import textwrap
import unittest
from pathlib import Path

from projects.ramadhan_esp32.adhan_web_ui.cron_manager import (
    AdhanCronManager,
    FileCrontabBackend,
)


class CronManagerTests(unittest.TestCase):
    def make_manager(self, content: str):
        tempdir = tempfile.TemporaryDirectory()
        path = Path(tempdir.name) / "crontab.txt"
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
        manager = AdhanCronManager(FileCrontabBackend(path))
        return manager, path, tempdir

    def test_list_jobs_infers_missing_labels(self):
        manager, path, tempdir = self.make_manager(
            """
            MAILTO=""
            0 5 * * * cd /home/hammadkhan/.openclaw/workspace && python3 projects/ramadhan_esp32/trigger_ha.py http://192.168.1.100:8002/adhan_final.mp3 1.0 >> adhan.log 2>&1
            30 13 * * * cd /home/hammadkhan/.openclaw/workspace && python3 projects/ramadhan_esp32/trigger_ha.py http://192.168.1.100:8002/adhan_final.mp3 1.0 >> adhan.log 2>&1
            # [Adhan: Asr]
            # 0 16 * * * cd /home/hammadkhan/.openclaw/workspace && python3 projects/ramadhan_esp32/trigger_ha.py http://192.168.1.100:8002/adhan_final.mp3 1.0 >> adhan.log 2>&1
            """
        )
        try:
            jobs = manager.list_jobs()
            self.assertEqual([job.label for job in jobs], ["Fajr", "Dhuhr", "Asr"])
            saved = path.read_text(encoding="utf-8")
            self.assertIn("# [Adhan: Fajr]", saved)
            self.assertIn("# [Adhan: Dhuhr]", saved)
            self.assertIn("# [Adhan: Asr]", saved)
        finally:
            tempdir.cleanup()

    def test_update_jobs_changes_time_and_toggle(self):
        manager, path, tempdir = self.make_manager(
            """
            # [Adhan: Maghrib]
            30 18 * * * cd /home/hammadkhan/.openclaw/workspace && python3 projects/ramadhan_esp32/trigger_ha.py http://192.168.1.100:8002/adhan_final.mp3 1.0 >> adhan.log 2>&1
            """
        )
        try:
            job = manager.list_jobs()[0]
            manager.update_jobs(
                [
                    {
                        "id": job.job_id,
                        "enabled": False,
                        "time": "18:45",
                    }
                ]
            )
            saved = path.read_text(encoding="utf-8")
            self.assertIn("# [Adhan: Maghrib]", saved)
            self.assertIn("# 45 18 * * * cd /home/hammadkhan/.openclaw/workspace", saved)
        finally:
            tempdir.cleanup()


if __name__ == "__main__":
    unittest.main()
