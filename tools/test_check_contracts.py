from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).with_name("check_contracts.py")


class ContractRegistryTest(unittest.TestCase):
    def run_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_accepts_empty_canonical_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contracts = root / "docs" / "contracts"
            contracts.mkdir(parents=True)
            (contracts / "index.json").write_text(
                json.dumps(
                    {
                        "generated": True,
                        "plan_refs": {},
                        "schema_version": 1,
                        "subsystems": [],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_missing_owner_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contracts = root / "docs" / "contracts"
            contracts.mkdir(parents=True)
            (contracts / "index.json").write_text("{}", encoding="utf-8")
            (contracts / "api.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "id": "api",
                        "owner_paths": ["apps/api/missing"],
                        "provides": [],
                        "artifacts": [],
                        "state_owned": [],
                        "invariants": [],
                        "depends_on": [],
                        "module_docs": [],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("owner_paths path does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
