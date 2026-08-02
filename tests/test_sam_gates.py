"""Tests for Sam's machine-enforced outreach gates (Task 3.2).

Required by the plan: gates default closed; a missing file fails closed; a
malformed file fails closed; Gate B true + Gate A false still blocks sending;
no test ever sends real mail.
"""
import json
import os

import pytest

import sam_gates
from sam_gates import GateClosed, assert_may_send_without_review, signature_block


def _write_gates(tmp_path, payload):
    p = tmp_path / "sam_gates.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return str(p)


def test_gate_a_closed_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr(sam_gates, "GATE_FILE", _write_gates(tmp_path, {}))
    with pytest.raises(GateClosed):
        assert_may_send_without_review()


def test_missing_gate_file_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(sam_gates, "GATE_FILE", str(tmp_path / "does_not_exist.json"))
    with pytest.raises(GateClosed):
        assert_may_send_without_review()


def test_malformed_gate_file_fails_closed(tmp_path, monkeypatch):
    bad = tmp_path / "sam_gates.json"
    bad.write_text("{ this is not valid json", encoding="utf-8")
    monkeypatch.setattr(sam_gates, "GATE_FILE", str(bad))
    with pytest.raises(GateClosed):
        assert_may_send_without_review()


def test_gate_a_open_allows_send(tmp_path, monkeypatch):
    monkeypatch.setattr(sam_gates, "GATE_FILE",
                        _write_gates(tmp_path, {"gate_a_autonomous_send": True}))
    assert_may_send_without_review()  # does not raise


def test_gate_b_true_gate_a_false_still_blocks(tmp_path, monkeypatch):
    monkeypatch.setattr(sam_gates, "GATE_FILE",
                        _write_gates(tmp_path, {
                            "gate_a_autonomous_send": False,
                            "gate_b_sam_signs_own_name": True,
                        }))
    with pytest.raises(GateClosed):
        assert_may_send_without_review()
    # Gate B being open only changes the signature block, never the send gate.
    assert signature_block() == "Sam\nSEB — Security Inquisitor Balance"


def test_signature_block_defaults_to_malik(tmp_path, monkeypatch):
    monkeypatch.setattr(sam_gates, "GATE_FILE", _write_gates(tmp_path, {}))
    assert signature_block() == "Malik\nSEB — Security Inquisitor Balance"
