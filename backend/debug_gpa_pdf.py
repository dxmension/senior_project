"""
Diagnostic script — run from the backend directory:
    uv run python debug_gpa_pdf.py path/to/your_gpa_report.pdf

Prints what pdfplumber extracts so we can see why grade columns are missing.
"""

import re
import sys

import pdfplumber

GRADE_LETTERS = {"A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "W", "I", "AU", "P", "NP"}


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def check_pdf(path: str):
    print(f"\n=== Checking: {path} ===\n")

    with pdfplumber.open(path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")

        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables() or []
            text = page.extract_text() or ""

            print(f"--- Page {page_num} ---")
            print(f"  Tables found: {len(tables)}")

            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                print(f"\n  Table {t_idx}: {len(table)} rows × {len(table[0]) if table else 0} cols")

                # Show first 3 rows (likely header + 2 data rows)
                for row_i, row in enumerate(table[:4]):
                    print(f"    Row {row_i}: {row}")

                # Check for grade columns
                header = table[0]
                grade_hits = []
                for col in header:
                    upper = str(col or "").strip().upper().lstrip("%")
                    if upper in GRADE_LETTERS:
                        grade_hits.append(col)
                print(f"    Grade cols detected in row 0: {grade_hits}")

                # Also check row 1 as a potential header
                if len(table) > 1:
                    header2 = table[1]
                    grade_hits2 = []
                    for col in header2:
                        upper = str(col or "").strip().upper().lstrip("%")
                        if upper in GRADE_LETTERS:
                            grade_hits2.append(col)
                    print(f"    Grade cols detected in row 1: {grade_hits2}")

            # Show first 5 text lines
            lines = text.splitlines()
            print(f"\n  Text lines (first 10):")
            for line in lines[:10]:
                print(f"    {repr(line)}")

            # Check if any text line looks like a data row
            has_data_line = False
            for line in lines:
                tokens = line.split()
                if len(tokens) >= 6:
                    nums = [t for t in tokens if _is_num(t)]
                    if len(nums) >= 5:
                        print(f"\n  Likely data line: {repr(line[:120])}")
                        has_data_line = True
                        break
            if not has_data_line:
                print("\n  No data lines with 5+ numeric tokens found on this page.")

            # Only show first 3 pages in detail
            if page_num >= 3:
                print(f"\n  (stopping after page {page_num} for brevity)")
                break


def _is_num(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python debug_gpa_pdf.py <path_to_pdf>")
        sys.exit(1)
    check_pdf(sys.argv[1])
