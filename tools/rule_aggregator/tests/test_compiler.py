"""Tests for rule_compiler.py — verifies merge, dedup, filter, and JSON output."""

import json
import os
from pathlib import Path

from rule_compiler import compile_rules, load_ignore_list


def test_load_ignore_list(tmp_path):
    """Ignore list loads correctly, skipping blank lines and comments."""
    ignore_file = tmp_path / "ignore.txt"
    ignore_file.write_text("v\nid\n# comment\n\nq\n")

    result = load_ignore_list(ignore_file)

    assert result == {"v", "id", "q"}


def test_load_ignore_list_missing_file(tmp_path):
    """Missing ignore list returns empty set instead of crashing."""
    result = load_ignore_list(tmp_path / "nonexistent.txt")
    assert result == set()


def test_compile_merges_and_deduplicates(mocker, tmp_path):
    """Params from both extractors are merged and deduplicated."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": ["utm_source", "fbclid", "shared_param"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": ["fbclid", "gclid", "shared_param"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value=set(),
    )

    output_file = str(tmp_path / "output.json")
    result = compile_rules(output_path=output_file)

    analytics = result["global"]["analytics_strip"]
    assert "utm_source" in analytics
    assert "fbclid" in analytics
    assert "gclid" in analytics
    assert "shared_param" in analytics
    # No duplicates
    assert len(analytics) == len(set(analytics))


def test_compile_filters_ignore_list(mocker, tmp_path):
    """Functional params from ignore list are excluded from output."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": ["utm_source", "v", "id", "fbclid"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": ["q", "gclid"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value={"v", "id", "q"},
    )

    output_file = str(tmp_path / "output.json")
    result = compile_rules(output_path=output_file)

    analytics = result["global"]["analytics_strip"]
    assert "v" not in analytics
    assert "id" not in analytics
    assert "q" not in analytics
    assert "utm_source" in analytics
    assert "fbclid" in analytics
    assert "gclid" in analytics


def test_compile_output_sorted(mocker, tmp_path):
    """Output analytics_strip list is sorted alphabetically."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": ["zzz", "aaa", "mmm"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": ["bbb"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value=set(),
    )

    output_file = str(tmp_path / "output.json")
    result = compile_rules(output_path=output_file)

    analytics = result["global"]["analytics_strip"]
    assert analytics == sorted(analytics)


def test_compile_json_schema(mocker, tmp_path):
    """Output JSON matches the ShareGuard RuleSet schema."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": ["utm_source"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": ["fbclid"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value={"v", "id"},
    )

    output_file = str(tmp_path / "output.json")
    compile_rules(output_path=output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Required top-level keys
    assert "version" in data
    assert "schema_version" in data
    assert data["schema_version"] == 1
    assert "expires_at" in data
    assert "global" in data
    assert "domains" in data
    assert "redirect_chains" in data
    assert "sacred_params" in data
    assert "shortener_domains" in data
    assert "shortener_excluded" in data

    # Global structure
    assert "analytics_strip" in data["global"]
    assert "analytics_prefix" in data["global"]
    assert isinstance(data["global"]["analytics_strip"], list)
    assert isinstance(data["global"]["analytics_prefix"], list)

    # Sacred params should contain the ignore list entries
    assert "v" in data["sacred_params"]
    assert "id" in data["sacred_params"]


def test_compile_writes_valid_json_file(mocker, tmp_path):
    """Output file is valid JSON and can be parsed back."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": ["param_a"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": ["param_b"], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value=set(),
    )

    output_file = str(tmp_path / "output.json")
    result = compile_rules(output_path=output_file)

    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    assert parsed == result


def test_compile_sacred_params_sorted(mocker, tmp_path):
    """Sacred params (ignore list) in output are also sorted."""
    mocker.patch(
        "rule_compiler.extract_clearurls_data",
        return_value={"sacred_params": [], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.extract_adguard_data",
        return_value={"sacred_params": [], "shortener_domains": []},
    )
    mocker.patch(
        "rule_compiler.load_ignore_list",
        return_value={"z_param", "a_param", "m_param"},
    )

    output_file = str(tmp_path / "output.json")
    result = compile_rules(output_path=output_file)

    assert result["sacred_params"] == sorted(result["sacred_params"])
