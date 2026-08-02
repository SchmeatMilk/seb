# SEB — Next Steps (post SEB_V2 execution, 2026-08-01)

Status: all agent-executable plan tasks DONE + committed to origin/main.
27 tests green. Working tree clean. Crons paused. Harness server killed.

## BLOCKERS / DECISIONS (Malik only)
1. **Domain + email** — `seb.security` is dead (NXDOMAIN). Client-facing copy
   still references it. NEEDED before: landing deploy (2.5) and Sam sending
   (3.3/3.5). Malik said: use his own email for now, wire domain next build.
   -> ACTION: pick domain, point inbox, replace `seb.security` refs in copy.
2. **Gate A (autonomous send)** — both Sam gates default CLOSED. Malik opens
   when ready. No external mail until then.
3. **First real engagement** — needs Malik's signed authorization (D-1/D-2).
   CK Catalyst scrapped.

## ENGINEERING (agent can run, not a decision)
4. **2.2 env-repair — DIAGNOSED, BLOCKED (do NOT innovate further without a plan)**.
   Root cause: the plan's engine integration was authored against engine versions
   that have since drifted. Each needs per-engine API research + an isolated venv
   build — genuine engineering, not a "repair pass." Findings (2026-08-01):
   - **Garak 0.15.1** (`.engines-venv`): runs, but `--config` RestGenerator shape
     changed — config needs `uri` + `req_template` (a `$INPUT` template STRING) +
     `response_json_field` as a JSONPath (`$.choices[0].message.content`). My
     current gauntlet.py uses the OLD shape (`req_template_json`, no `$.` prefix),
     so garak reports "nothing to do". FIX KNOWN but NOT applied (would be
     innovation beyond the plan's intent without Malik sign-off on rework scope).
   - **Pyrit 0.14.0** (`.engines-venv`): API is older than assumed — `HTTPTarget`
     has NO `send_prompt` method, and there is NO `pyrit.orchestrator` module. The
     plan's pyrit driver (RedTeamingOrchestrator + PromptRequestPiece) does not
     exist in 0.14.0. Needs a from-scratch 0.14.0-compatible driver.
   - **Giskard 2.19.2**: BROKEN — imports fail because `.engines-venv` (and
     `.venv`) SHARE the Hermes global site-packages, whose scipy is 1.17.1. That
     scipy REMOVED `Ks_2sampResult`, which giskard 2.19.2 still imports. Cannot
     downgrade scipy (would break Hermes). FIX: build a TRULY ISOLATED venv
     (e.g. `uv venv --isolated` or `python -m venv --copies`) with pandas +
     scipy<1.13 + giskard, and point `_engine_python("giskard")` at it.
   - **Harness wiring itself is SOUND**: `gauntlet.py` now stands up
     `local_test_harness` for sim targets and invokes each engine via its correct
     interpreter (no more fake "skipped" strings). The blocker is purely the
     engine-version drift above.
   - RECOMMENDATION: treat 2.2 as a separate, scoped engineering task (pin exact
     engine versions OR adapt drivers to current ones) — not finish it inline.

## READY BUT PARKED (no outbound until 1+2 clear)
5. Phase 3.1/3.3/3.4/3.5 — Sam approval UX, sending infra, copywriting.
6. Phase 4.1/4.2/4.3 — ICP, consent-first discovery, OWASP MCP Top-10
   positioning (messaging assets only; no send).

## DONE (committed)
- Phase 0 (8398d5b), 1.8 OSS PR #1963 mergeable, 2.1/2.3/2.4/2.6/2.7 (3ea5c7d),
  3.2 + 5 safety kernel + eval harness (116e2c5), D-6 org reconcile + CK scrap
  (f03162a), cleanup + nested-repo commits + git gc (a147af2).
