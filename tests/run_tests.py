"""Simple test runner for linkedinsearch parsing helper(s).

This script avoids requiring pytest in the environment and provides a quick
sanity check that `parse_ddg_html` correctly extracts LinkedIn profile links
from the sample HTML fixture.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedinsearch.search_linkedin import parse_ddg_html


def main():
    fixture = ROOT / "linkedinsearch" / "fixtures" / "ddg_sample.html"
    html = fixture.read_text(encoding="utf-8")
    results = parse_ddg_html(html, num=10, debug=True)
    print("Parsed results:")
    for r in results:
        print(r)

    assert any("john-doe" in r.get("url", "") for r in results), "john-doe not found"
    assert any("jane-doe" in r.get("url", "") for r in results), "jane-doe not found"
    assert len(results) == 2, f"expected 2 linkedin results, got {len(results)}"
    print("All checks passed.")


if __name__ == "__main__":
    main()
