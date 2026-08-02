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
4. **2.2 env-repair pass** — garak/pyrit/giskard venvs are broken:
   - giskard: `scipy` version mismatch (`Ks_2sampResult` removed in new scipy)
     -> pin compatible scipy in the giskard venv.
   - pyrit 0.14.0: module paths drifted (`pyrit.orchestrator`,
     `pyrit.models.prompt_request_piece` don't exist) -> find real 0.14.0 paths
     or upgrade pyrit; fix HTTPTarget/RedTeamingOrchestrator invocation.
   - garak: runs but report-parse glob needs adjustment (reports written, not
     parsed into ProbeResults).
   - Then re-run dogfood (vulnerable) to confirm >200 probes, 0 skipped,
     findings from all 3 engines; defended=0 findings.

## READY BUT PARKED (no outbound until 1+2 clear)
5. Phase 3.1/3.3/3.4/3.5 — Sam approval UX, sending infra, copywriting.
6. Phase 4.1/4.2/4.3 — ICP, consent-first discovery, OWASP MCP Top-10
   positioning (messaging assets only; no send).

## DONE (committed)
- Phase 0 (8398d5b), 1.8 OSS PR #1963 mergeable, 2.1/2.3/2.4/2.6/2.7 (3ea5c7d),
  3.2 + 5 safety kernel + eval harness (116e2c5), D-6 org reconcile + CK scrap
  (f03162a), cleanup + nested-repo commits + git gc (a147af2).
