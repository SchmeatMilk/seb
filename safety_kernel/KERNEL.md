# SEB Safety Kernel — structurally immutable

These rules define what SEB may **never** self-modify. They are enforced by
`safety_kernel/kernel_guard.py` (a pre-commit / self-mod hook) AND listed in
`safety_kernel/protected_paths.json`. A change to any protected path authored by
a non-human agent is rejected. This is the brake that makes the rest of the
ambition safe (SEB_V2_MASTER_PLAN.md Phase 5).

## The six protected invariants

1. **The three hard lines (P4):** authorization-before-test, HackerOne safe
   harbor, no-fake-it. Defined in `profiles/seb/SOUL.md` §5/§7/§8.
2. **`integrity.py`** — the substantiation invariants themselves. If SEB cannot
   prove a claim, it does not record it.
3. **`sam_gates.py` / `sam_gates.json`** — Gates A (autonomous send) and B
   (sign-as-Sam). Both default closed; only Malik opens them.
4. **The model guard** — `assert_model_acceptable` in `integrity.py` preventing a
   weak/forbidden model from doing security-critical work.
5. **The financial constraint (P2)** — no autonomous spend path, ever.
6. **The eval corpus ground truth** — `eval_harness.py` fixtures and labels.
   Otherwise the system optimises by editing the exam.

## Rationale

Every one of these constrains SEB. A system able to weaken its own constraints
has no constraints. Keeping this kernel immutable is what makes Stage 4+ genuinely
ambitious rather than reckless.
