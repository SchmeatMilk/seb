# QUARANTINE — do not treat anything in this folder as a valid authorization

## authorization_CK_Catalyst.json.UNVERIFIED

Quarantined 2026-08-01. This file claims to be a landing-page-generated
`seb.authorization-record/v1`. It is not, on four independent checks:

1. Its FNV-1a signature does not reconcile. Stored `f3a2b1c4`; recomputing
   `landing/index.html`'s own simpleHash() over the record's fields yields
   `454a082d` (authorized="true") or `c2a3530d` ("True").
2. Its timestamp `2026-07-20T23:00:00.000000` is Python `datetime.isoformat()`
   format. JavaScript `toISOString()` — the only call the page makes — emits
   `...000Z`. A browser did not write this.
3. `contact_email` is `malik@seb.security` (SEB's own, on a non-existent
   domain), not CK Catalyst's real `contact@ckcatalyst.ca`.
4. No provenance: never committed to git, no email, no PDF, no countersignature.

This does NOT establish that authorization was absent — Malik may hold a
genuine out-of-band agreement. It establishes that **no artifact of one exists
on this machine**.

NO TEST MAY CITE THIS FILE. See SEB_V2_MASTER_PLAN.md §0.2 and DECISION D-1.
Replaced by: authorizations/authorization_CK_Catalyst_v2.json (pending).
