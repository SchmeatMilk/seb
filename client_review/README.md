# SEB — Client-Facing Sign-Off Folder

Per SOUL.md §4b, nothing a prospect/client will see or read ships without sign-off
from **Brok (Marketing Manager)** or **Malik (owner)**.

## How it works
1. SEB drafts client-facing material here as `<asset>_DRAFT.md`.
2. SEB appends an entry to `signoff_queue.jsonl` with `status: "pending"`.
3. Brok (or Malik) reviews. On approval they write `<asset>_APPROVED.md` and set the
   queue entry to `status: "approved"` (with a `reviewer` + optional `note`).
   On rejection, set `status: "rejected"` with a note and SEB revises.
4. Only `approved` assets may be published / posted / sent.

## Current pending assets
(SEB updates the queue; see signoff_queue.jsonl)
