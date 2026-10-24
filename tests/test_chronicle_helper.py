import os
import sys
import shutil
import unittest
import tempfile
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import scripts.chronicle_helper as chronicle


class TestChronicleHelper(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault = os.path.join(self.test_dir, ".chronicle")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_project(self):
        result = chronicle.init_project("test-project", vault_path=self.vault)
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(os.path.join(self.vault, "state.json")))
        project_dir = os.path.join(self.vault, "projects", "test-project")
        self.assertTrue(os.path.exists(os.path.join(project_dir, "master_evolution.md")))
        self.assertTrue(os.path.exists(os.path.join(project_dir, "graveyard_of_traps.md")))
        self.assertTrue(os.path.exists(os.path.join(project_dir, "versions", "v1.md")))

        with open(os.path.join(self.vault, "state.json"), "r", encoding="utf-8") as f:
            state = json.load(f)
        self.assertEqual(state["active_project"], "test-project")
        self.assertEqual(state["projects"]["test-project"]["active_version"], 1)
        self.assertEqual(state["projects"]["test-project"]["versions"][0]["status"], "in_progress")

    def test_get_status(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        status = chronicle.get_status("test-project", vault_path=self.vault)
        self.assertEqual(status["project_name"], "test-project")
        self.assertEqual(status["active_version"], 1)
        self.assertEqual(status["version_status"], "in_progress")

    def test_complete_version(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        res = chronicle.complete_version(1, "test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        self.assertEqual(res["completed_version"], 1)
        self.assertEqual(res["next_active_version"], 2)

        # Check that v2.md template was created
        v2_path = os.path.join(self.vault, "projects", "test-project", "versions", "v2.md")
        self.assertTrue(os.path.exists(v2_path))

        status = chronicle.get_status("test-project", vault_path=self.vault)
        self.assertEqual(status["active_version"], 2)
        self.assertEqual(status["version_status"], "in_progress")

    def test_reopen_version(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        chronicle.complete_version(1, "test-project", vault_path=self.vault)
        
        # Now active is 2. Let's reopen version 1
        res = chronicle.reopen_version(1, "test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        status = chronicle.get_status("test-project", vault_path=self.vault)
        self.assertEqual(status["active_version"], 1)
        self.assertEqual(status["version_status"], "in_progress")

    def test_validate_schemas(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        val = chronicle.validate_schemas("test-project", vault_path=self.vault)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["errors"]), 0)

    def test_jump_version(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        # Jump from v1 to v4
        res = chronicle.jump_version(4, "test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        self.assertEqual(res["previous_version"], 1)
        self.assertEqual(res["active_version"], 4)
        self.assertEqual(res["skipped_versions"], [2, 3])

        # Verify state.json
        with open(os.path.join(self.vault, "state.json"), "r", encoding="utf-8") as f:
            state = json.load(f)
        pdata = state["projects"]["test-project"]
        self.assertEqual(pdata["active_version"], 4)
        v1 = next(v for v in pdata["versions"] if v["version"] == 1)
        v2 = next(v for v in pdata["versions"] if v["version"] == 2)
        v3 = next(v for v in pdata["versions"] if v["version"] == 3)
        v4 = next(v for v in pdata["versions"] if v["version"] == 4)
        self.assertEqual(v1["status"], "completed")
        self.assertEqual(v2["status"], "skipped")
        self.assertEqual(v3["status"], "skipped")
        self.assertEqual(v4["status"], "in_progress")

        # Verify v4.md exists and v2/v3 do NOT exist
        self.assertTrue(os.path.exists(os.path.join(self.vault, "projects", "test-project", "versions", "v4.md")))
        self.assertFalse(os.path.exists(os.path.join(self.vault, "projects", "test-project", "versions", "v2.md")))
        self.assertFalse(os.path.exists(os.path.join(self.vault, "projects", "test-project", "versions", "v3.md")))

        # Verify master_evolution.md has skipped versions logged
        with open(os.path.join(self.vault, "projects", "test-project", "master_evolution.md"), "r", encoding="utf-8") as f:
            master = f.read()
        self.assertIn("Version 2**: Skipped", master)
        self.assertIn("Version 3**: Skipped", master)
        self.assertIn("Version 4**", master)

        # Verify validation passes cleanly even with skipped versions
        val = chronicle.validate_schemas("test-project", vault_path=self.vault)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["errors"]), 0)

    def test_read_project(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        res = chronicle.read_project("test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        self.assertEqual(res["mode"], "read_only_observer")
        self.assertEqual(res["project_name"], "test-project")
        self.assertEqual(res["active_version"], 1)
        self.assertEqual(res["total_discoveries"], 0)
        self.assertIn("observer_directive", res)
        self.assertIn("Read-Only Observer Mode", res["observer_directive"])
        self.assertIn("## 1. Foundational Intent & Origin Thesis", res["master_evolution_content"])
        self.assertIn("Graveyard of Discarded Ideas", res["graveyard_content"])

    def test_discover_item(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        
        # Add 1st discovery
        res1 = chronicle.discover_item(
            title="Lock-Free Ring Buffer Algorithm",
            asset_path="core/ring_buffer.py",
            summary="Atomic lock-free queue with zero allocation overhead",
            project_name="test-project",
            vault_path=self.vault
        )
        self.assertTrue(res1["success"])
        self.assertEqual(res1["discovery_id"], 1)
        self.assertEqual(res1["file"], "discoveries/001-lock-free-ring-buffer-algorithm.md")
        
        disc_path1 = os.path.join(self.vault, "projects", "test-project", res1["file"])
        self.assertTrue(os.path.exists(disc_path1))
        with open(disc_path1, "r", encoding="utf-8") as f:
            content1 = f.read()
        self.assertIn("# Discovery 001: Lock-Free Ring Buffer Algorithm", content1)
        self.assertIn("core/ring_buffer.py", content1)
        self.assertIn("### 1. Concrete Asset Locations", content1)
        self.assertIn("### 2. Intuition, Philosophy & The \"Why\"", content1)

        # Check state.json
        with open(os.path.join(self.vault, "state.json"), "r", encoding="utf-8") as f:
            state = json.load(f)
        pdata = state["projects"]["test-project"]
        self.assertEqual(len(pdata.get("discoveries", [])), 1)
        self.assertEqual(pdata["discoveries"][0]["id"], 1)
        self.assertEqual(pdata["discoveries"][0]["title"], "Lock-Free Ring Buffer Algorithm")

        # Check master_evolution.md
        with open(os.path.join(self.vault, "projects", "test-project", "master_evolution.md"), "r", encoding="utf-8") as f:
            master = f.read()
        self.assertIn("## 6. Discoveries & Research Catalog", master)
        self.assertIn("Lock-Free Ring Buffer Algorithm", master)
        self.assertIn("core/ring_buffer.py", master)

        # Add 2nd discovery
        res2 = chronicle.discover_item(
            title="Zero-Copy Serialization Engine",
            asset_path="codecs/zerocopy.py",
            summary="Direct memory mapping protocol parser",
            project_name="test-project",
            vault_path=self.vault
        )
        self.assertTrue(res2["success"])
        self.assertEqual(res2["discovery_id"], 2)
        self.assertEqual(res2["file"], "discoveries/002-zero-copy-serialization-engine.md")

        # Validation check
        val = chronicle.validate_schemas("test-project", vault_path=self.vault)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["errors"]), 0)

        # Read mode check with discoveries
        read_res = chronicle.read_project("test-project", vault_path=self.vault)
        self.assertEqual(read_res["total_discoveries"], 2)
        self.assertEqual(len(read_res["discoveries"]), 2)


if __name__ == "__main__":
    unittest.main()
