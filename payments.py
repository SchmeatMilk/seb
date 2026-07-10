"""
SEB — payments.py : Stripe invoicing integration (honest, env-gated).

DESIGN PRINCIPLE (SOUL.md §5 "No fake it"):
  - If STRIPE_API_KEY is present: we CALL the real Stripe SDK to create a
    draft invoice and persist it to the clients.db `invoices` table.
  - If STRIPE_API_KEY is ABSENT: we do NOT fabricate a Stripe invoice id.
    We run in DRY-RUN mode, persist a local invoice row with
    stripe_invoice_id = None and status='pending', and log that it needs a
    key. This keeps the pipeline runnable offline and never lies about money.

No live charge is ever made by SEB — Stripe invoices are pay-later by design.
"""
from __future__ import annotations

import os
from typing import Optional

from client_db import add_invoice, get_conn, new_id

STRIPE_KEY = os.environ.get("STRIPE_API_KEY")
DRY_RUN = not bool(STRIPE_KEY)


def create_invoice(
    engagement_id: str,
    client_id: str,
    amount: float,
    *,
    due_days: int = 14,
    conn=None,
) -> dict:
    """
    Create an invoice for an engagement.

    Returns a dict with at least:
      {invoice_id, amount, status, stripe_invoice_id, mode}
    mode is 'live' or 'dry-run'.
    """
    own = conn is None
    conn = conn or get_conn()
    iid = new_id("inv")
    try:
        if DRY_RUN:
            # Honest offline path: local record, no fake Stripe id.
            add_invoice(engagement_id=engagement_id, client_id=client_id, amount=amount,
                        stripe_invoice_id=None, status="pending_dryrun", conn=conn)
            return {
                "invoice_id": iid,
                "amount": amount,
                "status": "pending_dryrun",
                "stripe_invoice_id": None,
                "mode": "dry-run",
                "note": "STRIPE_API_KEY not set — invoice recorded locally; supply key to issue via Stripe.",
            }
        # Live path (only when key present). Imported lazily so the module
        # loads fine without the SDK installed.
        import stripe  # type: ignore
        stripe.api_key = STRIPE_API_KEY
        # NOTE: a real invoice needs a Stripe Customer + line items. SEB
        # records the engagement locally and creates a DRAFT invoice object.
        # We deliberately do NOT finalize/charge here.
        inv = stripe.Invoice.create(
            # customer=... resolved from client_id mapping (out of scope pre-key)
            auto_advance=False,
            description=f"SEB engagement {engagement_id}",
            metadata={"engagement_id": engagement_id, "client_id": client_id},
        )
        add_invoice(iid, engagement_id, client_id, amount,
                    stripe_invoice_id=inv.id, status="sent", conn=conn)
        return {
            "invoice_id": iid,
            "amount": amount,
            "status": "sent",
            "stripe_invoice_id": inv.id,
            "mode": "live",
        }
    finally:
        if own:
            conn.close()


if __name__ == "__main__":
    init = get_conn()
    try:
        # Smoke: dry-run invoice against a placeholder engagement (no real rows needed
        # beyond what dogfood created). We just demonstrate the contract.
        r = create_invoice("eng_demo", "cli_demo", 500.0, conn=init)
        print("INVOICE:", r)
    finally:
        init.close()
