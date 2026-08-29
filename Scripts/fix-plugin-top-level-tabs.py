#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

for relative in [
    "Sources/CodexBar/StatusItemController+Menu.swift",
    "Sources/CodexBar/StatusItemController+MenuSwitcherWarmup.swift",
]:
    path = ROOT / relative
    text = path.read_text()
    old = "        let selectedProvider = if isOverviewSelected {\n"
    new = "        let selectedProvider: UsageProvider? = if isOverviewSelected {\n"
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{relative}: expected one selectedProvider match, found {count}")
    path.write_text(text.replace(old, new, 1))

print("Fixed optional provider type inference")
