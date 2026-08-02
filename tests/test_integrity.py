import json
import sqlite3
import pytest
from integrity import (
    IntegrityViolation,
    load_verified_authorization,
    assert_target_in_scope,
    assert_engagement_completable,
    assert_no_unsubstantiated_capability_claim,
)


def _auth(tmp_path, **over):
    rec = {
        "company": "X",
        "authorized_url": "https://x.example",
        "scope": "s",
        "written_authorization_granted": True,
        "provenance": {"method": "countersigned_email", "received": "2026-08-02"},
    }
    rec.update(over)
    p = tmp_path / "a.json"
    p.write_text(json.dumps(rec), encoding="utf-8")
    return str(p)


def test_missing_file_refused():
    with pytest.raises(IntegrityViolation):
        load_verified_authorization("nope.json")


def test_quarantine_refused(tmp_path):
    d = tmp_path / "QUARANTINE"
    d.mkdir()
    p = d / "a.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(IntegrityViolation):
        load_verified_authorization(str(p))


def test_freetext_scope_without_url_refused(tmp_path):
    with pytest.raises(IntegrityViolation):
        load_verified_authorization(_auth(tmp_path, authorized_url=""))


def test_missing_provenance_refused(tmp_path):
    with pytest.raises(IntegrityViolation):
        load_verified_authorization(_auth(tmp_path, provenance=None))


def test_scope_mismatch_refused(tmp_path):
    a = load_verified_authorization(_auth(tmp_path))
    assert_target_in_scope("https://x.example/api", a)  # ok
    with pytest.raises(IntegrityViolation):
        assert_target_in_scope("https://evil.example/api", a)  # different host


def test_zero_findings_blocks_completion(tmp_path):
    db = tmp_path / "c.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE findings(engagement_id TEXT)")
    con.execute("CREATE TABLE engagements(id TEXT, report_path TEXT)")
    con.execute("INSERT INTO engagements VALUES('e1','/nope.pdf')")
    con.commit()
    with pytest.raises(IntegrityViolation):
        assert_engagement_completable(str(db), "e1")  # the 2026-08-01 bug


@pytest.mark.parametrize("bad", [
    "We run 100+ probes across 4 tools",
    "Authorization status: Signed authorization on file",
])
def test_false_capability_claims_blocked(bad):
    with pytest.raises(IntegrityViolation):
        assert_no_unsubstantiated_capability_claim(bad)
