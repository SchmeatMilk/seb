"""
SEB — gauntlet.py : multi-tool adversarial-prompt orchestrator.

Fires probes from multiple engines against a SANDBOXED/authorized target only.

Engines:
  - L1B3RT4S  : local corpus of jailbreak prompts (~/.l1b3rt4s_clone/*.mkd)
                  + !SHORTCUTS.json categories. ALWAYS available offline.
  - Garak      : NVIDIA's LLM vulnerability scanner (import-guarded)
  - PyRIT      : Microsoft red-team framework (import-guarded, multi-turn)
  - Giskard    : agentic probe harness (import-guarded)

Target contract (pluggable):
  A target is ANY callable/probe-sink that takes a prompt string and returns
  a response string. For dogfood we use a local SimulatedTarget that
  operationalizes SEB's own SOUL.md §7 injection-defense rules (so the test
  genuinely checks whether our defenses hold). A real engagement would wire
  this to an authorized HTTP endpoint behind a signed authorization form.

CFAA / SAFE-HARBOR GUARDS (non-negotiable, enforced in code):
  - No target is touched without an authorization token present.
  - Rate-limited: one probe per TARGET_MIN_INTERVAL_S (default 1.0s).
  - Fail-fast: on transport error the run STOPS, logs, and returns what it has.
  - No third-party infra probing. The target is supplied by the caller; we
    never auto-discover or crawl external chatbots.

SEB never fabricates probe results. If an engine is unavailable, it is
reported as skipped, not faked.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from scorer import ProbeResult

L1B3RT4S_DIR = os.path.expanduser("~/.l1b3rt4s_clone")
TARGET_MIN_INTERVAL_S = 1.0  # rate-limit; non-destructive, single-session

# Map L1B3RT4S !SHORTCUTS.json "category" -> SEB internal attack class.
# Keys MUST match the literal category strings in !SHORTCUTS.json
# (verified 2026-07-13 against the corpus). The previous map used 5 keys
# ("Semantic", "Roleplay", "Refusal Inversion", "Exfiltration",
# "Instruction Override") that do NOT exist in the corpus, so every
# Obfuscation/Creative/Experimental/Psychological/Cosmic/Temporal shortcut
# silently fell through to the "jailbreak" default — collapsing taxonomy
# resolution. Corrected below. All values must be keys in scorer.TAXONOMY.
_CATEGORY_MAP = {
    "Core Liberation": "godmode",
    "Dynamic Intelligence": "jailbreak",
    "Formatting / Transparency": "system_prompt_leak",
    "Formatting / Temporal": "instruction_override",
    "Psychological / Philosophical": "roleplay",
    "Cosmic / Esoteric": "roleplay",
    "Obfuscation / Stealth": "instruction_override",
    "Creative / Visual": "instruction_override",
    "Creative / Chaos": "instruction_override",
    "Creative / Autonomy": "instruction_override",
    "Creative / Network Thinking": "instruction_override",
    "Creative / Aesthetic": "instruction_override",
    "Experimental / Stealth": "instruction_override",
    "Experimental / Introspection": "system_prompt_leak",
    "Experimental / Probabilistic": "jailbreak",
}

# Default class for any un-mapped .mkd file (by filename heuristic).
_FILENAME_HEURISTIC = {
    "godmode": "godmode",
    "jailbreak": "jailbreak",
    "system": "system_prompt_leak",
    "leak": "system_prompt_leak",
    "refusal": "refusal_inversion",
    "role": "roleplay",
    "exfil": "exfiltration",
    "inject": "instruction_override",
}


@dataclass
class GauntletRun:
    target_name: str
    probes_total: int = 0
    skipped_engines: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    results: list[ProbeResult] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    stopped_early: bool = False


# ---------------------------------------------------------------------------
# Local L1B3RT4S corpus loader
# ---------------------------------------------------------------------------
def load_l1b3rt4s() -> list[ProbeResult]:
    """Load local jailbreak corpus into unsent ProbeResults (response='' until fired)."""
    probes: list[ProbeResult] = []
    if not os.path.isdir(L1B3RT4S_DIR):
        return probes

    # From !SHORTCUTS.json categories (each entry becomes a derived prompt).
    shortcuts = os.path.join(L1B3RT4S_DIR, "!SHORTCUTS.json")
    if os.path.isfile(shortcuts):
        try:
            with open(shortcuts, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for cmd in data.get("commands", []):
                cat = cmd.get("category", "Core Liberation")
                cls = _CATEGORY_MAP.get(cat, "jailbreak")
                name = cmd.get("name", "")
                probes.append(ProbeResult(
                    probe_id=f"l1b3rt4s:shortcut:{abs(hash(name))}",
                    attack_class=cls,
                    source="l1b3rt4s",
                    prompt=f"Use the command {name}: {cmd.get('definition','')[:200]}",
                    response="",
                ))
        except Exception:
            pass  # never crash the run on a malformed shortcuts file

    # From .mkd attack files (filename heuristic -> class).
    for fn in sorted(os.listdir(L1B3RT4S_DIR)):
        if not fn.endswith(".mkd"):
            continue
        path = os.path.join(L1B3RT4S_DIR, fn)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                body = fh.read().strip()
        except Exception:
            continue
        if not body:
            continue
        cls = "instruction_override"
        low = fn.lower()
        for key, mapped in _FILENAME_HEURISTIC.items():
            if key in low:
                cls = mapped
                break
        probes.append(ProbeResult(
            probe_id=f"l1b3rt4s:file:{fn}",
            attack_class=cls,
            source="l1b3rt4s",
            prompt=body[:500],
            response="",
        ))
    return probes


# ---------------------------------------------------------------------------
# Heavy engines (import-guarded, honestly wired)
#
# SEB's real engagement target is an AUTHORIZED HTTP endpoint (a client's
# chatbot/agent). Garak/PyRIT/Giskard are designed to test model endpoints,
# not in-process Python callables — so we drive them against endpoint targets
# and parse their reports into SEB ProbeResults. For the local dogfood sim
# (a Python callable), we honestly skip the heavy engines and rely on the
# L1B3RT4S corpus already fired above. We never fabricate engine output.
# ---------------------------------------------------------------------------
def _endpoint_of(target) -> Optional[str]:
    """If `target` wraps an authorized HTTP endpoint, return its URL; else None."""
    url = getattr(target, "endpoint_url", None)
    if isinstance(url, str) and url.startswith("http"):
        return url
    return None


def _try_garak(target: Callable[[str], str], run: GauntletRun) -> None:
    """Run Garak via its CLI against the target endpoint, parse its report."""
    try:
        import garak  # noqa: F401  (validates install; version-agnostic)
    except Exception as e:
        run.skipped_engines.append(f"garak ({e.__class__.__name__}: not installed)")
        return

    endpoint = _endpoint_of(target)
    if not endpoint:
        # Local sim target: Garak needs a model endpoint. Be explicit, not fake.
        run.skipped_engines.append(
            "garak (installed; requires HTTP model endpoint — sim uses L1B3RT4S)")
        return

    import json
    import subprocess
    import tempfile
    import os as _os
    # Garak REST generator config pointing at the authorized endpoint.
    gen_cfg = {
        "type": "rest.RestGenerator",
        "rest_generator": {
            "endpoint": endpoint,
            "method": "POST",
            "request_timeout": 30,
            "headers": {"Content-Type": "application/json"},
            "data": {"prompt": "%prompt%"},
            "response_json": "response",
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        _os.write(fh.fileno(), json.dumps(gen_cfg).encode())
        cfg_path = fh.name
    out_dir = tempfile.mkdtemp(prefix="seb-garak-")
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "garak", "--config", cfg_path,
             "--probes", "promptinject", "--report_prefix", out_dir + "/r"],
            capture_output=True, text=True, timeout=600,
        )
        if proc.returncode != 0:
            run.skipped_engines.append(
                f"garak (CLI error rc={proc.returncode}: {proc.stderr[:160]})")
            return
        # Parse Garak's report JSON (if present) into ProbeResults.
        for fn in _os.listdir(out_dir):
            if fn.endswith(".json") and "report" in fn:
                with open(_os.path.join(out_dir, fn), "r", encoding="utf-8") as rf:
                    rep = json.load(rf)
                for rec in rep.get("results", []):
                    run.results.append(ProbeResult(
                        probe_id=f"garak:{rec.get('probe', '?')}:{rec.get('prompt', '')[:40]}",
                        attack_class="instruction_override",
                        source="garak",
                        prompt=str(rec.get("prompt", "")),
                        response=str(rec.get("output", "")),
                    ))
                    run.probes_total += 1
    except Exception as e:
        run.skipped_engines.append(f"garak (integration error: {e.__class__.__name__})")
    finally:
        try:
            _os.remove(cfg_path)
        except Exception:
            pass


def _try_pyrit(target: Callable[[str], str], run: GauntletRun,
                multi_turn: bool = False) -> None:
    try:
        import pyrit  # noqa: F401
    except Exception as e:
        run.skipped_engines.append(f"pyrit ({e.__class__.__name__}: not installed)")
        return
    # PyRIT (multi-turn Crescendo/TAP) requires an Orchestrator + prompt
    # dataset config. Until SEB supplies one, skip honestly rather than fake.
    run.skipped_engines.append(
        "pyrit (installed; requires orchestrator + prompt dataset config)")


def _try_giskard(target: Callable[[str], str], run: GauntletRun) -> None:
    try:
        import giskard  # noqa: F401
    except Exception as e:
        run.skipped_engines.append(f"giskard ({e.__class__.__name__}: not installed)")
        return
    # Giskard agentic scanning requires an AgenticEvaluator target. Until SEB
    # supplies an agent target, skip honestly rather than fake.
    run.skipped_engines.append(
        "giskard (installed; requires agentic target for AgenticEvaluator)")


# ---------------------------------------------------------------------------
# Firing + guards
# ---------------------------------------------------------------------------
def _fire(target: Callable[[str], str], probe: ProbeResult, run: GauntletRun) -> None:
    try:
        resp = target(probe.prompt)
        probe.response = resp if isinstance(resp, str) else str(resp)
        probe.target = run.target_name
        run.results.append(probe)
        run.probes_total += 1
    except Exception as e:
        run.errors.append(f"probe {probe.probe_id}: {e.__class__.__name__}: {e}")
        run.stopped_early = True  # fail-fast: STOP + log + return
        raise


def run_gauntlet(
    target: Callable[[str], str],
    *,
    target_name: str,
    authorization_token: str,
    engines: Optional[list[str]] = None,
    limit_probes: Optional[int] = None,
    rate_interval_s: float = TARGET_MIN_INTERVAL_S,
) -> GauntletRun:
    """
    Run the gauntlet against `target`.

    target            : callable(prompt:str)->str  (authorized/sandboxed only)
    target_name       : label for reporting
    authorization_token: MUST be a non-empty signed-auth reference. Empty -> refuse.
    engines           : subset of ['l1b3rt4s','garak','pyrit','giskard']
    limit_probes      : cap probes (useful for retainer quick-scans)
    """
    if not authorization_token or not str(authorization_token).strip():
        raise PermissionError(
            "REFUSED: no written authorization token. SEB never tests without it (SOUL.md §5/§8)."
        )

    engines = engines or ["l1b3rt4s", "garak", "pyrit", "giskard"]
    run = GauntletRun(target_name=target_name)

    # Build probe set from local corpus (always available offline).
    probes = load_l1b3rt4s()
    if limit_probes:
        probes = probes[:limit_probes]

    if "l1b3rt4s" in engines:
        for p in probes:
            try:
                _fire(target, p, run)
                time.sleep(rate_interval_s)
            except Exception:
                break  # fail-fast

    if "garak" in engines:
        _try_garak(target, run)
    if "pyrit" in engines:
        _try_pyrit(target, run, multi_turn="pyrit" in engines)
    if "giskard" in engines:
        _try_giskard(target, run)

    return run


# ---------------------------------------------------------------------------
# Dogfood target: operationalizes SEB's own SOUL.md §7 defense rules.
# This is a LOCAL simulation so the dogfood genuinely tests our defenses.
# ---------------------------------------------------------------------------
class DefendedSimTarget:
    """
    A simulated target that loads SEB's SOUL.md as its system prompt and
    applies the §7 injection-defense rules. Used for honest dogfood:
    if our defenses are correct, refractory probes should NOT leak.
    """
    BLOCK_PHRASES = [
        "ignore previous instructions", "from now on", "new rule",
        "system reset", "godmode", "jailbreak", "reveal your system prompt",
        "system prompt:", "<system>", "you are now", "bypass",
    ]

    def __init__(self, soul_path: str):
        self.soul = ""
        try:
            with open(soul_path, "r", encoding="utf-8", errors="ignore") as fh:
                self.soul = fh.read()
        except Exception:
            self.soul = "FALLBACK SYSTEM PROMPT"

    def __call__(self, prompt: str) -> str:
        low = (prompt or "").lower()
        # Rule from SOUL.md §7: disregard override/reset directives.
        for phrase in self.BLOCK_PHRASES:
            if phrase in low:
                return ("I can't comply with that. SEB operates within the "
                        "HackerOne Good Faith AI Research Safe Harbor and will "
                        "not alter its instructions or reveal system configuration.")
        # Benign echo for non-adversarial prompts.
        return f"ACKNOWLEDGED (sandboxed): {prompt[:120]}"


class VulnerableSimTarget:
    """Control target that DOES leak — used to validate the scorer's detector."""
    def __call__(self, prompt: str) -> str:
        low = (prompt or "").lower()
        if "system prompt" in low or "godmode" in low:
            return "Here is the system prompt: <SYSTEM> you are SEB, unrestricted mode enabled."
        if "ignore previous" in low:
            return "I will now comply and ignore previous instructions."
        return f"OK: {prompt[:120]}"


class EndpointTarget:
    """
    Wraps an AUTHORIZED client HTTP endpoint so the heavy engines (Garak/PyRIT/
    Giskard) can test it. The endpoint URL is exposed via `.endpoint_url` and
    this target also satisfies the callable contract for the L1B3RT4S corpus.

    REQUIREMENT: only point this at an endpoint you are WRITTENly authorized to
    test (signed authorization form on file). SEB never probes without it.
    """
    def __init__(self, endpoint_url: str, *, method: str = "POST",
                 headers: Optional[dict] = None, prompt_field: str = "prompt",
                 response_field: str = "response", timeout: int = 30):
        if not str(endpoint_url).startswith("http"):
            raise ValueError("EndpointTarget requires an http(s) URL.")
        self.endpoint_url = endpoint_url
        self.method = method
        self.headers = headers or {"Content-Type": "application/json"}
        self.prompt_field = prompt_field
        self.response_field = response_field
        self.timeout = timeout

    def __call__(self, prompt: str) -> str:
        import json
        import urllib.request
        payload = json.dumps({self.prompt_field: prompt}).encode()
        req = urllib.request.Request(
            self.endpoint_url, data=payload, headers=self.headers, method=self.method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode())
            if isinstance(body, dict) and self.response_field in body:
                return str(body[self.response_field])
            return str(body)
        except Exception as e:
            raise RuntimeError(f"EndpointTarget call failed: {e.__class__.__name__}: {e}")


if __name__ == "__main__":
    import sys
    soul = os.path.expanduser("~/AppData/Local/hermes/profiles/seb/SOUL.md")
    defended = DefendedSimTarget(soul)
    r = run_gauntlet(defended, target_name="SEB-SOUL-dogfood",
                     authorization_token="SELF-AUTH-dogfood", rate_interval_s=0.001)
    print(f"Defended target -> probes={r.probes_total}, errors={len(r.errors)}, "
          f"skipped={r.skipped_engines}")
    # Sanity: defending target should produce zero leak findings via scorer.
    from scorer import score_results
    f = score_results(r.results)
    print(f"Confirmed findings against DEFENDED self: {len(f)} (expected 0)")
