"""
Schema and invariant validator for ShareGuard compiled RuleSet JSON (latest.json).
Verifies structural requirements and invariants to prevent publishing malformed rules.
"""

import datetime
import json
import sys
from pathlib import Path


def validate_ruleset(data: dict) -> list[str]:
    """
    Validate compiled RuleSet dictionary against schema invariants.

    Returns a list of error strings. Empty list indicates valid ruleset.
    """
    errors: list[str] = []

    # 1. Version invariant
    if "version" not in data:
        errors.append("Missing required field 'version'")
    elif not isinstance(data["version"], str) or not data["version"].strip():
        errors.append("'version' must be a non-empty string")

    # 2. Schema version invariant
    if "schema_version" not in data:
        errors.append("Missing required field 'schema_version'")
    elif data["schema_version"] != 1:
        errors.append(f"'schema_version' must be 1, found {data.get('schema_version')}")

    # 3. Expiration invariant (must be ISO-8601 YYYY-MM-DD and strictly in the future)
    if "expires_at" not in data:
        errors.append("Missing required field 'expires_at'")
    elif not isinstance(data["expires_at"], str) or not data["expires_at"].strip():
        errors.append("'expires_at' must be a non-empty string")
    else:
        try:
            exp_date = datetime.date.fromisoformat(data["expires_at"])
            if exp_date <= datetime.date.today():
                errors.append(f"'expires_at' ({data['expires_at']}) must be in the future")
        except ValueError:
            errors.append(f"'expires_at' ('{data['expires_at']}') must be a valid ISO-8601 date (YYYY-MM-DD)")

    # 4. Sacred params invariant (must be list of non-empty strings)
    if "sacred_params" not in data:
        errors.append("Missing required field 'sacred_params'")
    elif not isinstance(data["sacred_params"], list):
        errors.append("'sacred_params' must be a list")
    elif len(data["sacred_params"]) == 0:
        errors.append("'sacred_params' must not be empty")
    elif not all(isinstance(x, str) and x.strip() for x in data["sacred_params"]):
        errors.append("All elements in 'sacred_params' must be non-empty strings")

    # 5. Global analytics invariants (global must be an object with list fields)
    if "global" not in data:
        errors.append("Missing required field 'global'")
    elif not isinstance(data["global"], dict):
        errors.append("'global' must be an object")
    else:
        global_obj = data["global"]
        if "analytics_strip" not in global_obj:
            errors.append("Missing required field 'global.analytics_strip'")
        elif not isinstance(global_obj["analytics_strip"], list):
            errors.append("'global.analytics_strip' must be a list")
        elif len(global_obj["analytics_strip"]) == 0:
            errors.append("'global.analytics_strip' must contain at least 1 parameter")
        elif not all(isinstance(x, str) and x.strip() for x in global_obj["analytics_strip"]):
            errors.append("All elements in 'global.analytics_strip' must be non-empty strings")

        if "analytics_prefix" not in global_obj:
            errors.append("Missing required field 'global.analytics_prefix'")
        elif not isinstance(global_obj["analytics_prefix"], list):
            errors.append("'global.analytics_prefix' must be a list")

    # 6. Invariant: Disjointness between sacred_params and global.analytics_strip
    if (
        isinstance(data.get("sacred_params"), list)
        and isinstance(data.get("global"), dict)
        and isinstance(data["global"].get("analytics_strip"), list)
    ):
        sacred_set = {x for x in data["sacred_params"] if isinstance(x, str)}
        strip_set = {x for x in data["global"]["analytics_strip"] if isinstance(x, str)}
        conflicts = sacred_set & strip_set
        if conflicts:
            errors.append(f"Conflict: parameters appear in both 'sacred_params' and 'global.analytics_strip': {sorted(conflicts)}")

    # 7. Shortener domains invariant (must be list of non-empty strings)
    if "shortener_domains" not in data:
        errors.append("Missing required field 'shortener_domains'")
    elif not isinstance(data["shortener_domains"], list):
        errors.append("'shortener_domains' must be a list")
    elif not all(isinstance(x, str) and x.strip() for x in data["shortener_domains"]):
        errors.append("All elements in 'shortener_domains' must be non-empty strings")

    # 8. Shortener exclusions invariant (must be list of non-empty strings)
    if "shortener_excluded" not in data:
        errors.append("Missing required field 'shortener_excluded'")
    elif not isinstance(data["shortener_excluded"], list):
        errors.append("'shortener_excluded' must be a list")
    elif not all(isinstance(x, str) and x.strip() for x in data["shortener_excluded"]):
        errors.append("All elements in 'shortener_excluded' must be non-empty strings")

    # 9. Domain and redirect chain invariants (must be JSON objects)
    if "domains" not in data:
        errors.append("Missing required field 'domains'")
    elif not isinstance(data["domains"], dict):
        errors.append("'domains' must be an object")

    if "redirect_chains" not in data:
        errors.append("Missing required field 'redirect_chains'")
    elif not isinstance(data["redirect_chains"], dict):
        errors.append("'redirect_chains' must be an object")

    return errors


def validate_file(file_path: str | Path) -> bool:
    """Read a JSON file and validate against RuleSet invariants."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: RuleSet file '{path}' does not exist.", file=sys.stderr)
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON from '{path}': {e}", file=sys.stderr)
        return False

    if not isinstance(data, dict):
        print(f"Error: Root of '{path}' must be a JSON object.", file=sys.stderr)
        return False

    errors = validate_ruleset(data)
    if errors:
        print(f"Validation FAILED for '{path}' with {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print(f"Validation PASSED for '{path}':")
    print(f"  Version: {data['version']}")
    print(f"  Schema version: {data['schema_version']}")
    print(f"  Sacred params: {len(data['sacred_params'])}")
    print(f"  Analytics strip: {len(data['global']['analytics_strip'])}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python schema_validator.py <path-to-latest.json>", file=sys.stderr)
        sys.exit(2)

    target_file = sys.argv[1]
    is_valid = validate_file(target_file)
    sys.exit(0 if is_valid else 1)
