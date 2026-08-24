#!/usr/bin/env python3
"""Validate workslop-detector subagent JSON contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BASELINE_KEYS = {
    "reviewer_id",
    "assignment_interpretation",
    "response_outline",
    "recommendations",
    "specifics_available_from_request",
    "missing_information",
    "assumptions",
}
COLD_READER_KEYS = {
    "reader_profile",
    "point_after_one_read",
    "requested_action",
    "important_points",
    "evidence",
    "confusion_points",
    "verification_burden",
    "claims_needing_support",
    "contradictions",
    "removable_material",
    "compression_estimate_percent",
    "burden_anchor",
    "anchor_reason",
}
ARBITER_KEYS = {
    "target_reader",
    "verdict",
    "workslop",
    "human_delta",
    "reader_burden",
    "review_diligence",
    "trust_check",
    "receipts",
    "funny_diagnosis",
    "serious_diagnosis",
    "recommended_action",
    "limitations",
}

VERDICTS = {
    "NOT_WORKSLOP",
    "NOT_WORKSLOP_NEEDS_EDIT",
    "WORKSLOP_POLISHED_GENERIC",
    "WORKSLOP_RETURN_TO_SENDER",
    "INCONCLUSIVE",
}
ACTIONS = {
    "ACCEPT",
    "REQUEST_COMPRESSION",
    "REQUEST_JUDGMENT",
    "RETURN_FOR_REVISION",
    "REQUEST_CONTEXT",
}
READER_FACING_KEYS = (
    "funny_diagnosis",
    "serious_diagnosis",
)
FORBIDDEN_READER_TERMS = (
    "human delta",
    "reader burden",
    "review diligence",
    "evidence-backed path",
    "decision-ready recommendation",
)


class ContractError(ValueError):
    pass


def require_exact_keys(data: dict[str, Any], expected: set[str]) -> None:
    actual = set(data)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ContractError(f"keys mismatch; missing={missing}, extra={extra}")


def require_string(data: dict[str, Any], key: str) -> None:
    if not isinstance(data.get(key), str):
        raise ContractError(f"{key} must be a string")


def require_string_list(data: dict[str, Any], key: str, minimum: int = 0) -> None:
    value = data.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ContractError(f"{key} must be a list of strings")
    if len(value) < minimum:
        raise ContractError(f"{key} must contain at least {minimum} item(s)")


def validate_trust_items(data: dict[str, Any]) -> None:
    claims = data.get("claims_needing_support")
    if not isinstance(claims, list):
        raise ContractError("claims_needing_support must be a list")
    for index, item in enumerate(claims):
        if not isinstance(item, dict) or set(item) != {"quote", "reason", "materiality"}:
            raise ContractError(f"claims_needing_support[{index}] has invalid shape")
        if not isinstance(item["quote"], str) or not isinstance(item["reason"], str):
            raise ContractError(f"claims_needing_support[{index}] quote and reason must be strings")
        if item["materiality"] not in {"LOW", "MODERATE", "HIGH"}:
            raise ContractError(f"claims_needing_support[{index}].materiality is invalid")

    contradictions = data.get("contradictions")
    if not isinstance(contradictions, list):
        raise ContractError("contradictions must be a list")
    for index, item in enumerate(contradictions):
        expected = {"first_quote", "second_quote", "reason", "materiality"}
        if not isinstance(item, dict) or set(item) != expected:
            raise ContractError(f"contradictions[{index}] has invalid shape")
        if any(not isinstance(item[key], str) for key in expected):
            raise ContractError(f"contradictions[{index}] fields must be strings")
        if item["materiality"] not in {"LOW", "MODERATE", "HIGH"}:
            raise ContractError(f"contradictions[{index}].materiality is invalid")


def validate_baseline(data: dict[str, Any]) -> None:
    require_exact_keys(data, BASELINE_KEYS)
    require_string(data, "reviewer_id")
    require_string(data, "assignment_interpretation")
    for key in (
        "response_outline",
        "recommendations",
        "specifics_available_from_request",
        "missing_information",
        "assumptions",
    ):
        require_string_list(data, key)


def validate_cold_reader(data: dict[str, Any]) -> None:
    require_exact_keys(data, COLD_READER_KEYS)
    for key in ("reader_profile", "point_after_one_read", "requested_action", "anchor_reason"):
        require_string(data, key)
    for key in (
        "important_points",
        "confusion_points",
        "verification_burden",
        "removable_material",
    ):
        require_string_list(data, key)
    validate_trust_items(data)
    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        raise ContractError("evidence must be a list")
    for index, item in enumerate(evidence):
        if not isinstance(item, dict) or set(item) != {"dimension", "quote", "observation"}:
            raise ContractError(f"evidence[{index}] has invalid shape")
        if item["dimension"] not in {"NAVIGATION", "ACTION", "VERIFICATION", "COMPRESSION"}:
            raise ContractError(f"evidence[{index}].dimension is invalid")
        if not isinstance(item["quote"], str) or not isinstance(item["observation"], str):
            raise ContractError(f"evidence[{index}] quote and observation must be strings")
    estimate = data.get("compression_estimate_percent")
    if not isinstance(estimate, int) or isinstance(estimate, bool) or not 0 <= estimate <= 90:
        raise ContractError("compression_estimate_percent must be an integer from 0 to 90")
    if data.get("burden_anchor") not in {"LOW", "MODERATE", "HIGH"}:
        raise ContractError("burden_anchor is invalid")


def validate_rating_object(
    data: dict[str, Any], key: str, ratings: set[str], expected_keys: set[str]
) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise ContractError(f"{key} has invalid shape")
    if value.get("rating") not in ratings:
        raise ContractError(f"{key}.rating is invalid")
    require_string_list(value, "evidence", minimum=1)
    return value


def validate_arbiter(data: dict[str, Any]) -> None:
    require_exact_keys(data, ARBITER_KEYS)
    for key in ("target_reader", "funny_diagnosis", "serious_diagnosis"):
        require_string(data, key)
    for key in READER_FACING_KEYS:
        lowered = data[key].casefold()
        for term in FORBIDDEN_READER_TERMS:
            if term in lowered:
                raise ContractError(f"{key} contains internal jargon: {term}")
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        raise ContractError("verdict is invalid")
    if data.get("recommended_action") not in ACTIONS:
        raise ContractError("recommended_action is invalid")

    human_delta = validate_rating_object(
        data,
        "human_delta",
        {"LOW", "PARTIAL", "HIGH"},
        {"rating", "evidence", "baseline_convergence"},
    )
    require_string_list(human_delta, "baseline_convergence", minimum=1)
    reader_burden = validate_rating_object(
        data,
        "reader_burden",
        {"LOW", "MODERATE", "HIGH"},
        {"rating", "evidence"},
    )
    diligence = validate_rating_object(
        data,
        "review_diligence",
        {"CLEAN", "CONCERNING", "UNREVIEWED"},
        {"rating", "evidence", "confirmed_residue"},
    )
    trust_check = data.get("trust_check")
    if not isinstance(trust_check, dict) or set(trust_check) != {
        "claims_needing_support",
        "contradictions",
        "effect_on_reader_burden",
    }:
        raise ContractError("trust_check has invalid shape")
    validate_trust_items(trust_check)
    require_string(trust_check, "effect_on_reader_burden")
    residue = diligence.get("confirmed_residue")
    if not isinstance(residue, list):
        raise ContractError("review_diligence.confirmed_residue must be a list")
    for index, item in enumerate(residue):
        if not isinstance(item, dict) or set(item) != {"line", "quote", "reason"}:
            raise ContractError(f"confirmed_residue[{index}] has invalid shape")
        if not isinstance(item["line"], int) or item["line"] < 1:
            raise ContractError(f"confirmed_residue[{index}].line must be a positive integer")
        if not isinstance(item["quote"], str) or not isinstance(item["reason"], str):
            raise ContractError(f"confirmed_residue[{index}] quote and reason must be strings")

    require_string_list(data, "receipts", minimum=2)
    if len(data["receipts"]) > 5:
        raise ContractError("receipts must contain no more than 5 items")
    require_string_list(data, "limitations")

    expected_workslop = {
        "NOT_WORKSLOP": False,
        "NOT_WORKSLOP_NEEDS_EDIT": False,
        "WORKSLOP_POLISHED_GENERIC": True,
        "WORKSLOP_RETURN_TO_SENDER": True,
        "INCONCLUSIVE": None,
    }[verdict]
    if data.get("workslop") is not expected_workslop:
        raise ContractError(f"workslop must be {expected_workslop!r} for {verdict}")

    rating = human_delta["rating"]
    burden = reader_burden["rating"]
    matrix_verdict = {
        ("HIGH", "LOW"): "NOT_WORKSLOP",
        ("HIGH", "MODERATE"): "NOT_WORKSLOP_NEEDS_EDIT",
        ("HIGH", "HIGH"): "NOT_WORKSLOP_NEEDS_EDIT",
        ("PARTIAL", "LOW"): "NOT_WORKSLOP_NEEDS_EDIT",
        ("PARTIAL", "MODERATE"): "WORKSLOP_RETURN_TO_SENDER",
        ("PARTIAL", "HIGH"): "WORKSLOP_RETURN_TO_SENDER",
        ("LOW", "LOW"): "WORKSLOP_POLISHED_GENERIC",
        ("LOW", "MODERATE"): "WORKSLOP_POLISHED_GENERIC",
        ("LOW", "HIGH"): "WORKSLOP_RETURN_TO_SENDER",
    }[(rating, burden)]
    if verdict != "INCONCLUSIVE" and verdict != matrix_verdict:
        raise ContractError(
            f"verdict {verdict} conflicts with matrix result {matrix_verdict} for {rating}/{burden}"
        )

    expected_action = {
        "NOT_WORKSLOP": "ACCEPT",
        "NOT_WORKSLOP_NEEDS_EDIT": (
            "REQUEST_COMPRESSION" if rating == "HIGH" else "REQUEST_JUDGMENT"
        ),
        "WORKSLOP_POLISHED_GENERIC": "REQUEST_JUDGMENT",
        "WORKSLOP_RETURN_TO_SENDER": "RETURN_FOR_REVISION",
        "INCONCLUSIVE": "REQUEST_CONTEXT",
    }[verdict]
    if data.get("recommended_action") != expected_action:
        raise ContractError(
            f"recommended_action must be {expected_action} for {verdict} with {rating}/{burden}"
        )



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("baseline", "cold-reader", "arbiter"))
    parser.add_argument("json_file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ContractError("top-level JSON value must be an object")
        validators = {
            "baseline": validate_baseline,
            "cold-reader": validate_cold_reader,
            "arbiter": validate_arbiter,
        }
        validators[args.role](data)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"contract_violation: {exc}", file=sys.stderr)
        return 3
    print(f"valid: {args.role} {args.json_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
