#!/usr/bin/env python3
"""Replace unfinished contact placeholders in the Kuwait CSV.

The live Kuwait site currently publishes the regional +971 desk number until a
dedicated +965 line exists. Override with env vars when that number is issued:

  PHONE_RUKN_KUWAIT=+965XXXXXXXX
  WHATSAPP_RUKN_KUWAIT=965XXXXXXXX
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "rukn-eltatawer-kuwait-FULL.csv"
DST = ROOT / "rukn-eltatawer-kuwait-READY.csv"

PHONE = os.environ.get("PHONE_RUKN_KUWAIT", "+971586634710")
WHATSAPP = os.environ.get("WHATSAPP_RUKN_KUWAIT", "971586634710")


def main() -> int:
    if not SRC.exists():
        print(f"missing {SRC}", file=sys.stderr)
        return 1

    replacements = 0
    rows_out = 0
    with SRC.open(newline="", encoding="utf-8") as inf, DST.open(
        "w", newline="", encoding="utf-8"
    ) as outf:
        reader = csv.DictReader(inf)
        if not reader.fieldnames:
            print("CSV has no header", file=sys.stderr)
            return 1
        writer = csv.DictWriter(outf, fieldnames=reader.fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in reader:
            for key, val in list(row.items()):
                if not val:
                    continue
                if "{PHONE_RUKN_KUWAIT}" in val:
                    replacements += val.count("{PHONE_RUKN_KUWAIT}")
                    val = val.replace("{PHONE_RUKN_KUWAIT}", PHONE)
                if "{WHATSAPP_RUKN_KUWAIT}" in val:
                    replacements += val.count("{WHATSAPP_RUKN_KUWAIT}")
                    val = val.replace("{WHATSAPP_RUKN_KUWAIT}", WHATSAPP)
                row[key] = val
            writer.writerow(row)
            rows_out += 1

    print(f"wrote {DST}")
    print(f"rows={rows_out} replacements={replacements}")
    print(f"PHONE_RUKN_KUWAIT={PHONE}")
    print(f"WHATSAPP_RUKN_KUWAIT={WHATSAPP}")
    print("Do not re-import if these slugs are already published on /kw.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
