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
        self.assertIn("workspace_root", state["projects"]["test-project"])

    def test_get_status(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        status = chronicle.get_status("test-project", vault_path=self.vault)
        self.assertEqual(status["project_name"], "test-project")
        self.assertEqual(status["active_version"], 1)
        self.assertEqual(status["version_status"], "in_progress")

    def test_complete_version_default_and_regex(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        
        # Test completing without explicit version argument (defaults to active_version)
        res = chronicle.complete_version(version=None, project_name="test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        self.assertEqual(res["completed_version"], 1)
        self.assertEqual(res["next_active_version"], 2)

        # Verify header in v1.md changed to completed
        v1_path = os.path.join(self.vault, "projects", "test-project", "versions", "v1.md")
        with open(v1_path, "r", encoding="utf-8") as f:
            v1_content = f.read()
        self.assertIn("**Status:** completed", v1_content)
        self.assertNotIn("**Status:** in_progress", v1_content)

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

        v1_path = os.path.join(self.vault, "projects", "test-project", "versions", "v1.md")
        with open(v1_path, "r", encoding="utf-8") as f:
            v1_content = f.read()
        self.assertIn("**Status:** in_progress", v1_content)
        self.assertIn("## Retroactive Reopening & Amendments", v1_content)

    def test_validate_vault_handles_missing_state(self):
        # Empty directory with no state.json must return valid: False
        empty_dir = os.path.join(self.test_dir, "empty_vault")
        os.makedirs(empty_dir, exist_ok=True)
        val = chronicle.validate_vault(vault_path=empty_dir)
        self.assertFalse(val["valid"])
        self.assertIn("Missing state file", val["errors"][0])

    def test_validate_vault_clean_project(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        val = chronicle.validate_schemas("test-project", vault_path=self.vault)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["errors"]), 0)

    def test_jump_version_preserves_chapter_6(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        
        # Add a discovery first so Chapter 6 has content
        chronicle.discover_item(
            title="Initial Test Discovery",
            asset_path="core/sample.py",
            summary="A discovery before jumping",
            project_name="test-project",
            vault_path=self.vault
        )

        # Jump from v1 to v4
        res = chronicle.jump_version(4, "test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        self.assertEqual(res["previous_version"], 1)
        self.assertEqual(res["active_version"], 4)
        self.assertEqual(res["skipped_versions"], [2, 3])

        # Verify master_evolution.md
        with open(os.path.join(self.vault, "projects", "test-project", "master_evolution.md"), "r", encoding="utf-8") as f:
            master = f.read()

        # Chapter 5 must contain skipped logs
        self.assertIn("Version 2**: Skipped", master)
        self.assertIn("Version 3**: Skipped", master)
        self.assertIn("Version 4**", master)

        # Crucial check: Chapter 5 entries must appear BEFORE Chapter 6!
        ch5_idx = master.find("## 5. Comprehensive Version Progression Log")
        ch6_idx = master.find("## 6. Discoveries & Research Catalog")
        v2_idx = master.find("Version 2**: Skipped")
        
        self.assertTrue(ch5_idx < v2_idx < ch6_idx, "Skipped version entries must be inside Chapter 5, before Chapter 6!")
        self.assertIn("Initial Test Discovery", master[ch6_idx:])

    def test_read_project(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        res = chronicle.read_project("test-project", vault_path=self.vault, include_content=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["mode"], "read_only_observer")
        self.assertEqual(res["project_name"], "test-project")
        self.assertEqual(res["active_version"], 1)
        self.assertEqual(res["total_discoveries"], 0)
        self.assertIn("observer_directive", res)
        self.assertIn("Read-Only Observer Mode", res["observer_directive"])
        self.assertIn("## 1. Foundational Intent & Origin Thesis", res["master_evolution_content"])
        self.assertIn("Graveyard of Discarded Ideas", res["graveyard_content"])

        # CLI read with include_content=False
        cli_res = chronicle.read_project("test-project", vault_path=self.vault, include_content=False)
        self.assertNotIn("master_evolution_content", cli_res)
        self.assertNotIn("graveyard_content", cli_res)

    def test_discover_item_handles_crlf(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        master_path = os.path.join(self.vault, "projects", "test-project", "master_evolution.md")
        
        # Simulate Windows CRLF line endings in master_evolution.md
        with open(master_path, "r", encoding="utf-8") as f:
            content = f.read()
        crlf_content = content.replace("\n", "\r\n")
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(crlf_content)

        # Add discovery
        res = chronicle.discover_item(
            title="Lock-Free Ring Buffer Algorithm",
            asset_path="core/ring_buffer.py",
            summary="Atomic lock-free queue with zero allocation overhead",
            project_name="test-project",
            vault_path=self.vault
        )
        self.assertTrue(res["success"])

        # Verify placeholder row was cleanly removed despite CRLF
        with open(master_path, "r", encoding="utf-8") as f:
            updated_master = f.read()
        self.assertNotIn("No discoveries logged yet", updated_master)
        self.assertIn("Lock-Free Ring Buffer Algorithm", updated_master)

    def test_atomic_save_and_error_handling(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        state_file = os.path.join(self.vault, "state.json")
        
        # Corrupt state.json with invalid JSON
        with open(state_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json")

        # Loading must raise RuntimeError, NOT silently return empty dict
        with self.assertRaises(RuntimeError):
            chronicle._load_state(self.vault)

    def test_reopen_skipped_version_scaffolds_file_and_validates(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        chronicle.jump_version(4, "test-project", vault_path=self.vault)
        
        # v2 was skipped and had no dossier file
        v2_path = os.path.join(self.vault, "projects", "test-project", "versions", "v2.md")
        self.assertFalse(os.path.exists(v2_path))

        # Reopen v2
        res = chronicle.reopen_version(2, "test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        self.assertEqual(res["active_version"], 2)
        
        # Dossier file must now exist
        self.assertTrue(os.path.exists(v2_path))
        with open(v2_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("**Status:** in_progress", content)

        # Validation must pass cleanly without missing dossier errors
        val = chronicle.validate_vault("test-project", vault_path=self.vault)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["errors"]), 0)

    def test_complete_historical_version_preserves_future_milestones(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        chronicle.jump_version(4, "test-project", vault_path=self.vault)
        
        # Active is now 4. Let's reopen 1 to make an amendment
        chronicle.reopen_version(1, "test-project", vault_path=self.vault)
        status_reopen = chronicle.get_status("test-project", vault_path=self.vault)
        self.assertEqual(status_reopen["active_version"], 1)

        # Complete version 1
        res = chronicle.complete_version(1, "test-project", vault_path=self.vault)
        self.assertTrue(res["success"])
        
        # Active version should restore to 4 (the latest in_progress milestone), NOT corrupt v2/v3
        self.assertEqual(res["next_active_version"], 4)
        
        with open(os.path.join(self.vault, "state.json"), "r", encoding="utf-8") as f:
            state = json.load(f)
        pdata = state["projects"]["test-project"]
        self.assertEqual(pdata["active_version"], 4)
        
        # v2 and v3 must remain skipped
        v2 = next(v for v in pdata["versions"] if v["version"] == 2)
        v3 = next(v for v in pdata["versions"] if v["version"] == 3)
        self.assertEqual(v2["status"], "skipped")
        self.assertEqual(v3["status"], "skipped")

    def test_sync_project_validates_version_existence(self):
        chronicle.init_project("test-project", vault_path=self.vault)
        
        # Syncing to a non-existent version must return an error
        err_res = chronicle.sync_project("test-project", version=99, vault_path=self.vault)
        self.assertFalse(err_res["success"])
        self.assertIn("Version 99 does not exist", err_res["error"])

        # Syncing to existing version 1 succeeds
        ok_res = chronicle.sync_project("test-project", version=1, vault_path=self.vault)
        self.assertTrue(ok_res["success"])
        self.assertEqual(ok_res["active_version"], 1)

    def test_resolve_project_name_and_workspace_isolation(self):
        state = {
            "active_project": "default-proj",
            "projects": {
                "proj-alpha": {"workspace_root": os.path.join(self.test_dir, "alpha")},
                "proj-beta": {"workspace_root": os.path.join(self.test_dir, "beta", "sub")}
            }
        }
        
        # Explicit name takes priority
        self.assertEqual(chronicle._resolve_project_name("custom-name", state), "custom-name")

        # Fallback when no match
        self.assertEqual(chronicle._resolve_project_name(None, state), "default-proj")

    def test_cli_complete_with_omitted_version(self):
        import subprocess
        chronicle.init_project("test-project", vault_path=self.vault)
        helper_path = os.path.abspath(chronicle.__file__)

        # Run complete CLI without --version flag
        cmd = [
            sys.executable,
            helper_path,
            "complete",
            "--vault", self.vault,
            "--project", "test-project"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"CLI stderr: {proc.stderr}")
        
        data = json.loads(proc.stdout)
        self.assertTrue(data["success"])
        self.assertEqual(data["completed_version"], 1)
        self.assertEqual(data["next_active_version"], 2)


if __name__ == "__main__":
    unittest.main()
