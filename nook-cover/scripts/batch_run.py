#!/usr/bin/env python
"""Inject background_image path into briefs and run render-xhs-cover.cjs for all 9."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
OUTPUT = ROOT / "output"
RENDER = ROOT / "scripts" / "render-xhs-cover.cjs"

# name -> (brief dir, image path, asset_strategy)
COVER_MAP = {
    "F1-ai-sidehustle":   ("F1-ai-sidehustle",   "main.jpg",  "qwen_main_visual"),
    "F2-thirty-lessons":  ("F2-thirty-lessons",  "bg.jpg",    "zimage_background"),
    "F3-meal-prep":       ("F3-meal-prep",       "main.jpg",  "image2_main_visual"),
    "M1-ai-tools":        ("M1-ai-tools",        "main.jpg",  "qwen_main_visual"),
    "M2-sidehustle":      ("M2-sidehustle",      "bg.jpg",    "zimage_background"),
    "M3-muscle-gain":     ("M3-muscle-gain",     "main.jpg",  "image2_ref_preserved"),
    "N1-prompt-pack":     ("N1-prompt-pack",     None,        "none"),
    "N2-booklist":        ("N2-booklist",        "bg.jpg",    "zimage_background"),
    "N3-ai-top10":        ("N3-ai-top10",        "main.jpg",  "qwen_main_visual"),
}

results = []
for name, (dir_name, img_name, strategy) in COVER_MAP.items():
    brief_path = EXAMPLES / dir_name / "brief.json"
    out_dir = OUTPUT / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    if img_name:
        brief["background_image"] = str(Path("output") / dir_name / img_name)
    else:
        brief["background_image"] = ""

    # Save patched brief (so user can see what changed)
    with open(brief_path, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)

    # Run renderer
    print(f"\n=== {name} (strategy={strategy}) ===")
    proc = subprocess.run(
        ["node", str(RENDER), str(brief_path), str(out_dir)],
        capture_output=True, text=True, timeout=120,
        cwd=str(ROOT)
    )
    if proc.returncode == 0:
        # Capture output paths
        for line in proc.stdout.splitlines():
            print("  " + line)
        results.append((name, "OK", ""))
    else:
        print("  STDERR:", proc.stderr[-500:] if proc.stderr else "(empty)")
        print("  STDOUT:", proc.stdout[-500:] if proc.stdout else "(empty)")
        results.append((name, "FAIL", proc.stderr[-300:] if proc.stderr else ""))

print("\n\n=========== SUMMARY ===========")
for name, status, err in results:
    marker = "[OK]" if status == "OK" else "[FAIL]"
    print(f"{marker} {name:24s} {status}")
    if err:
        for line in err.splitlines()[:5]:
            print(f"    {line}")
