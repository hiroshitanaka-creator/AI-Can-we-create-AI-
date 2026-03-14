import json
import re
import unittest
from pathlib import Path

from bridge.po_core_bridge import get_tensor_schema


class TestPoCoreApiSpec(unittest.TestCase):
    def test_api_spec_canonical_schema_matches_runtime_schema(self):
        spec_path = Path("docs/api_spec_po_core_v1.md")
        text = spec_path.read_text(encoding="utf-8")

        match = re.search(
            r"<!-- tensor-schema:start -->\s*```json\n(.*?)\n```\s*<!-- tensor-schema:end -->",
            text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "canonical schema block not found in api_spec_po_core_v1.md")

        canonical_schema = json.loads(match.group(1))
        runtime_schema = get_tensor_schema()

        self.assertEqual(canonical_schema, runtime_schema)


if __name__ == "__main__":
    unittest.main()
