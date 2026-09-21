"""Tests for schema_validator.py — verifies invariant enforcement."""

import json
from pathlib import Path

from schema_validator import validate_ruleset, validate_file
from rule_compiler import compile_rules


def test_valid_ruleset():
    valid_data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {
            "analytics_strip": ["utm_source", "fbclid"],
            "analytics_prefix": [],
        },
        "domains": {},
        "redirect_chains": {},
        "sacred_params": ["v", "id"],
        "shortener_domains": ["bit.ly"],
        "shortener_excluded": [],
    }
    errors = validate_ruleset(valid_data)
    assert errors == []


def test_missing_version():
    data = {
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": ["utm_source"]},
        "sacred_params": ["v"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("version" in err for err in errors)


def test_invalid_schema_version():
    data = {
        "version": "2026.09.12",
        "schema_version": 2,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": ["utm_source"]},
        "sacred_params": ["v"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("schema_version" in err for err in errors)


def test_empty_sacred_params():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": ["utm_source"]},
        "sacred_params": [],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("sacred_params" in err for err in errors)


def test_empty_analytics_strip():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": []},
        "sacred_params": ["v"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("analytics_strip" in err for err in errors)


def test_expired_expires_at():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2020-01-01",
        "global": {"analytics_strip": ["utm_source"]},
        "sacred_params": ["v"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("must be in the future" in err for err in errors)


def test_invalid_expires_at_format():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "invalid-date",
        "global": {"analytics_strip": ["utm_source"]},
        "sacred_params": ["v"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("valid ISO-8601 date" in err for err in errors)


def test_non_string_sacred_params():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": ["utm_source"]},
        "sacred_params": ["v", 123],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("All elements in 'sacred_params' must be non-empty strings" in err for err in errors)


def test_non_string_analytics_strip():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": ["utm_source", {}]},
        "sacred_params": ["v"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("All elements in 'global.analytics_strip' must be non-empty strings" in err for err in errors)


def test_disjoint_sacred_and_analytics_strip():
    data = {
        "version": "2026.09.12",
        "schema_version": 1,
        "expires_at": "2026-12-11",
        "global": {"analytics_strip": ["utm_source", "conflict_param"]},
        "sacred_params": ["v", "conflict_param"],
        "shortener_domains": [],
    }
    errors = validate_ruleset(data)
    assert any("Conflict: parameters appear in both" in err for err in errors)


def test_validate_file_not_found(tmp_path):
    assert validate_file(tmp_path / "nonexistent.json") is False


def test_validate_file_invalid_json(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not valid json}")
    assert validate_file(bad_json) is False


def test_validate_compiled_output(mocker, tmp_path):
    """End-to-end integration test: compiler output passes validator."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": ["utm_source", "fbclid"], "shortener_domains": ["bit.ly"]},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": ["gclid"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value={"v", "id"},
    )

    out_file = tmp_path / "latest.json"
    compile_rules(output_path=str(out_file))

    assert validate_file(out_file) is True
