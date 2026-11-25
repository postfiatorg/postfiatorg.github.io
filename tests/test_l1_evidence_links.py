import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "l1-docs-theme"))
from evidence_links import EvidenceLinks, source_heading_lines


class EvidenceFragmentTests(unittest.TestCase):
    extensions = ["toc", "attr_list", "fenced_code"]

    def test_line_numbers_follow_rendered_headings(self):
        source = """# Report

```markdown
## G2.1 — PASS: `candidate`
```

## G2.1 — PASS: `candidate`

## Different wording { #release-id }

## G2.1 — PASS: `candidate`

Qualification check — 2026-09-02
--------------------------------
"""
        self.assertEqual(source_heading_lines(source, self.extensions, {}), {
            "report": 1, "g21-pass-candidate": 7, "release-id": 9,
            "g21-pass-candidate_1": 11, "qualification-check-2026-09-02": 13,
        })

    def test_links_use_committed_lines_and_keep_query_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", repo], check=True)
            doc = repo / "docs" / "audit.md"
            doc.parent.mkdir()
            doc.write_text("# Report\n\n## Signed evidence { #explicit-id }\n", encoding="utf-8")
            subprocess.run(["git", "-C", repo, "add", "docs"], check=True)
            subprocess.run(["git", "-C", repo, "-c", "user.name=test", "-c", "user.email=test@example.com",
                            "commit", "-qm", "fixture"], check=True)
            links = EvidenceLinks(repo, self.extensions, {})
            links.page = SimpleNamespace(file=SimpleNamespace(src_uri="status/page.md"))
            links.files = Mock()
            links.files.get_file_from_path.return_value = None
            doc.write_text("# An uncommitted edit\n", encoding="utf-8")

            base = f"https://github.com/postfiatorg/postfiatl1v2/blob/{links.revision}/docs/audit.md"
            self.assertEqual(links.destination("../audit.md?view=1&plain=0#explicit%2Did"),
                             base + "?view=1&plain=1#L3")
            self.assertEqual(links.destination("../audit.md"), base)
            with self.assertRaisesRegex(ValueError, "unknown source heading"):
                links.destination("../audit.md#misspelled")
            links.files.get_file_from_path.return_value = Mock()
            links.files.get_file_from_path.return_value.inclusion.is_included.return_value = True
            self.assertEqual(links.destination("../audit.md#explicit-id"), "../audit.md#explicit-id")
