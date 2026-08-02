"""
SEB — corpus_inventory.py
Daily threat-intel inventory: enumerates the L1B3RT4S + CL4R1T4S local corpora,
classifies attack classes, and writes a manifest to intel/corpus_manifest.json.

On each run it diffs against the previous manifest (if any) to compute:
  - corpus size delta (file count, total bytes, derived attack-class count)
  - new / removed files
  - new SHORTCUTS categories detected
It NEVER contacts a live target and performs NO testing (SOUL.md §5 guards).
Output is a JSON summary on stdout and an updated manifest file.
"""
from __future__ import annotations
import hashlib
import json
import os
import time
from datetime import datetime, timezone

L1B3RT4S_DIR = os.path.expanduser("~/.l1b3rt4s_clone")
CL4R1T4S_DIR = os.path.expanduser("~/.cl4r1tas")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "corpus_manifest.json")

# Filename heuristic -> SEB internal attack class (mirrors gauntlet.py).
_FILENAME_HEURISTIC = {
    "godmode": "godmode",
    "1337": "godmode",
    "jailbreak": "jailbreak",
    "system": "system_prompt_leak",
    "leak": "system_prompt_leak",
    "refusal": "refusal_inversion",
    "role": "roleplay",
    "exfil": "exfiltration",
    "inject": "instruction_override",
    "token": "token_smuggling",
    "shortcut": "instruction_override",
}


def classify(fn: str) -> str:
    low = fn.lower()
    for key, mapped in _FILENAME_HEURISTIC.items():
        if key in low:
            return mapped
    return "instruction_override"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return "ERR"


def inventory_l1b3rt4s() -> dict:
    files = {}
    total_bytes = 0
    classes = set()
    if os.path.isdir(L1B3RT4S_DIR):
        for fn in sorted(os.listdir(L1B3RT4S_DIR)):
            if not fn.endswith(".mkd"):
                continue
            p = os.path.join(L1B3RT4S_DIR, fn)
            try:
                sz = os.path.getsize(p)
            except OSError:
                sz = 0
            files[fn] = {"bytes": sz, "sha": sha256(p), "class": classify(fn)}
            total_bytes += sz
            classes.add(files[fn]["class"])
    # SHORTCUTS categories
    shortcut_cats = set()
    sc = os.path.join(L1B3RT4S_DIR, "!SHORTCUTS.json")
    if os.path.isfile(sc):
        try:
            with open(sc, "r", encoding="utf-8", errors="ignore") as fh:
                data = json.load(fh)
            for cmd in data.get("commands", []):
                shortcut_cats.add(cmd.get("category", "Core Liberation"))
        except Exception:
            pass
    return {
        "file_count": len(files),
        "total_bytes": total_bytes,
        "attack_classes": sorted(classes),
        "attack_class_count": len(classes),
        "shortcut_categories": sorted(shortcut_cats),
        "files": files,
    }


def inventory_cl4r1tas() -> dict:
    platforms = []
    if os.path.isdir(CL4R1T4S_DIR):
        for name in sorted(os.listdir(CL4R1T4S_DIR)):
            full = os.path.join(CL4R1T4S_DIR, name)
            if os.path.isdir(full) and not name.startswith("."):
                platforms.append(name)
    return {"platform_count": len(platforms), "platforms": platforms}


def load_prev() -> dict | None:
    if os.path.isfile(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None
    return None


def main() -> dict:
    l1 = inventory_l1b3rt4s()
    cl = inventory_cl4r1tas()
    now = datetime.now(timezone.utc)
    manifest = {
        "generated_at": now.isoformat(),
        "l1b3rt4s": l1,
        "cl4r1tas": cl,
        "git_commit": _git_commit(),
    }
    prev = load_prev()
    delta = _diff(prev, manifest) if prev else None

    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    summary = {
        "generated_at": manifest["generated_at"],
        "git_commit": manifest["git_commit"],
        "l1b3rt4s": {
            "file_count": l1["file_count"],
            "total_bytes": l1["total_bytes"],
            "attack_class_count": l1["attack_class_count"],
            "attack_classes": l1["attack_classes"],
            "shortcut_categories": l1["shortcut_categories"],
        },
        "cl4r1tas": {
            "platform_count": cl["platform_count"],
        },
        "delta_vs_prev": delta,
    }
    return summary


def _git_commit() -> str | None:
    try:
        import subprocess
        out = subprocess.run(
            ["git", "-C", L1B3RT4S_DIR, "log", "-1", "--format=%H"],
            capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or None
    except Exception:
        return None


def _diff(prev: dict, cur: dict) -> dict:
    pf = prev.get("l1b3rt4s", {}).get("files", {})
    cf = cur.get("l1b3rt4s", {}).get("files", {})
    new_files = sorted(set(cf) - set(pf))
    removed = sorted(set(pf) - set(cf))
    changed = sorted([f for f in set(pf) & set(cf) if pf[f].get("sha") != cf[f].get("sha")])
    prev_classes = set(prev.get("l1b3rt4s", {}).get("attack_classes", []))
    cur_classes = set(cur.get("l1b3rt4s", {}).get("attack_classes", []))
    new_classes = sorted(cur_classes - prev_classes)
    prev_bytes = prev.get("l1b3rt4s", {}).get("total_bytes", 0)
    cur_bytes = cur.get("l1b3rt4s", {}).get("total_bytes", 0)
    prev_pc = prev.get("l1b3rt4s", {}).get("file_count", 0)
    cur_pc = cur.get("l1b3rt4s", {}).get("file_count", 0)
    return {
        "new_files": new_files,
        "removed_files": removed,
        "changed_files": changed,
        "new_attack_classes": new_classes,
        "file_count_delta": cur_pc - prev_pc,
        "byte_delta": cur_bytes - prev_bytes,
        "attack_class_count_delta": len(cur_classes) - len(prev_classes),
        "cl4r1tas_new_platforms": sorted(
            set(cur.get("cl4r1tas", {}).get("platforms", []))
            - set(prev.get("cl4r1tas", {}).get("platforms", []))
        ),
    }


if __name__ == "__main__":
    import sys
    s = main()
    print(json.dumps(s, indent=2))
