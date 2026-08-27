#!/usr/bin/env python3
"""Validate deterministic invariants for source-scan.json using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SOURCE_ROLES = {
    "platform",
    "component",
    "integration_adapter",
    "controller",
    "operator",
    "sdk",
    "deployment",
    "service_contract",
    "policy_contract",
    "storage_contract",
    "generated_artifact",
}
PATH_CLASSES = {
    "north_south",
    "workload_east_west",
    "node_local",
    "kubernetes_control",
    "non_network",
    "storage",
    "controller_or_sdk",
    "managed_service",
}
TARGET_PREFIX = {
    "component_interface": "CIFACE-",
    "gpu_asset": "GASSET-",
    "platform_service_operation": "PSOP-",
}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
CONFIDENCE_ORDER = {"High": 0, "Medium": 1}
FINAL_STATUSES = {"source_supported_candidate", "deployment_dependent_candidate"}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def unique_ids(self, records: list[dict[str, Any]], field: str) -> set[str]:
        values: list[str] = []
        for index, record in enumerate(records):
            value = record.get(field)
            self.require(isinstance(value, str) and bool(value), f"{field}[{index}] is missing")
            if isinstance(value, str):
                values.append(value)
        duplicates = sorted({value for value in values if values.count(value) > 1})
        self.require(not duplicates, f"duplicate {field}: {', '.join(duplicates)}")
        return set(values)

    def references(self, values: list[str], known: set[str], context: str) -> None:
        missing = sorted(set(values) - known)
        self.require(not missing, f"{context} references missing IDs: {', '.join(missing)}")


def load_document(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("document root must be an object")
    return data


def records(data: dict[str, Any], key: str, validation: Validation) -> list[dict[str, Any]]:
    value = data.get(key)
    validation.require(isinstance(value, list), f"{key} must be an array")
    if not isinstance(value, list):
        return []
    validation.require(all(isinstance(item, dict) for item in value), f"{key} must contain objects")
    return [item for item in value if isinstance(item, dict)]


def validate_target(target: Any, known_targets: set[str], context: str, validation: Validation) -> None:
    validation.require(isinstance(target, dict), f"{context}.target must be an object")
    if not isinstance(target, dict):
        return
    kind = target.get("kind")
    target_id = target.get("target_id")
    validation.require(kind in TARGET_PREFIX, f"{context}.target.kind is invalid: {kind}")
    if kind in TARGET_PREFIX:
        validation.require(
            isinstance(target_id, str) and target_id.startswith(TARGET_PREFIX[kind]),
            f"{context}.target_id {target_id!r} does not match kind {kind}",
        )
    validation.require(target_id in known_targets, f"{context} references unknown target {target_id!r}")


def validate(path: Path) -> list[str]:
    validation = Validation()
    data = load_document(path)

    validation.require(data.get("schema_version") == "1.0", "schema_version must be 1.0")
    validation.require(data.get("scan_mode") == "source_discovery", "scan_mode must be source_discovery")
    validation.require(bool(re.fullmatch(r"SSCAN-[A-Z0-9-]+", str(data.get("scan_id", "")))), "scan_id is invalid")

    inputs = data.get("inputs", {})
    validation.require(isinstance(inputs, dict), "inputs must be an object")
    if not isinstance(inputs, dict):
        inputs = {}

    integration_sources = inputs.get("integration_sources", [])
    validation.require(isinstance(integration_sources, list), "inputs.integration_sources must be an array")
    integration_sources = [item for item in integration_sources if isinstance(item, dict)]
    source_ids = validation.unique_ids(integration_sources, "source_id")

    evidence = records(data, "evidence", validation)
    evidence_ids = validation.unique_ids(evidence, "evidence_id")
    for item in evidence:
        validation.require(item.get("source_id") in source_ids, f"{item.get('evidence_id')} references unknown source_id")

    actors = records(data, "threat_model", validation)
    actor_ids = validation.unique_ids(actors, "actor_id")

    targets = records(data, "targets", validation)
    local_target_ids = validation.unique_ids(targets, "target_id")
    stage_a_ids = set(inputs.get("stage_a_interface_ids", [])) if isinstance(inputs.get("stage_a_interface_ids"), list) else set()
    known_targets = local_target_ids | stage_a_ids
    for item in targets:
        validation.require(
            item.get("kind") in {"gpu_asset", "platform_service_operation"},
            f"{item.get('target_id', 'target')} must be a Stage B GASSET or PSOP target",
        )
        validate_target(item, known_targets, item.get("target_id", "target"), validation)
        validation.references(item.get("evidence_ids", []), evidence_ids, item.get("target_id", "target"))

    gaps = records(data, "gaps", validation)
    gap_ids = validation.unique_ids(gaps, "gap_id")

    guards = records(data, "guards", validation)
    guard_ids = validation.unique_ids(guards, "guard_id")
    guards_by_id = {item.get("guard_id"): item for item in guards}
    for item in guards:
        validation.references(item.get("evidence_ids", []), evidence_ids, item.get("guard_id", "guard"))
        validation.references(item.get("gap_ids", []), gap_ids, item.get("guard_id", "guard"))

    chains = records(data, "chains", validation)
    chain_ids = validation.unique_ids(chains, "chain_id")
    chains_by_id = {item.get("chain_id"): item for item in chains}
    for item in chains:
        context = item.get("chain_id", "chain")
        validation.require(item.get("actor_id") in actor_ids, f"{context} references unknown actor_id")
        validate_target(item.get("target"), known_targets, context, validation)
        validation.references(item.get("guard_ids", []), guard_ids, context)
        validation.references(item.get("evidence_ids", []), evidence_ids, context)
        hops = item.get("hops", [])
        orders = [hop.get("order") for hop in hops if isinstance(hop, dict)]
        validation.require(orders == list(range(1, len(orders) + 1)), f"{context} hop order must be contiguous from 1")
        for hop in hops:
            if isinstance(hop, dict):
                validation.references(hop.get("evidence_ids", []), evidence_ids, context)

    deltas = records(data, "deltas", validation)
    delta_ids = validation.unique_ids(deltas, "delta_id")
    deltas_by_id = {item.get("delta_id"): item for item in deltas}
    for item in deltas:
        context = item.get("delta_id", "delta")
        validate_target(item.get("target"), known_targets, context, validation)
        validation.references(item.get("chain_ids", []), chain_ids, context)
        validation.references(item.get("evidence_ids", []), evidence_ids, context)
        validation.references(item.get("gap_ids", []), gap_ids, context)

    candidates = records(data, "candidates", validation)
    candidate_ids = validation.unique_ids(candidates, "candidate_id")
    for item in candidates:
        context = item.get("candidate_id", "candidate")
        validation.require(item.get("status") in FINAL_STATUSES, f"{context} has invalid final status")
        validation.require(item.get("source_confidence") in CONFIDENCE_ORDER, f"{context} must have High or Medium confidence")
        validation.require(item.get("actor_id") in actor_ids, f"{context} references unknown actor_id")
        for field in ("chain_ids", "guard_ids", "delta_ids", "possible_impact", "evidence_ids"):
            validation.require(bool(item.get(field)), f"{context}.{field} must not be empty")
        validate_target(item.get("target"), known_targets, context, validation)
        validation.references(item.get("chain_ids", []), chain_ids, context)
        validation.references(item.get("guard_ids", []), guard_ids, context)
        validation.references(item.get("delta_ids", []), delta_ids, context)
        validation.references(item.get("evidence_ids", []), evidence_ids, context)
        manual = item.get("manual_verification", {})
        validation.require(isinstance(manual, dict), f"{context}.manual_verification must be an object")
        if isinstance(manual, dict):
            for field in ("steps", "positive_signals", "negative_signals", "evidence_to_collect", "prohibited_actions"):
                validation.require(bool(manual.get(field)), f"{context}.manual_verification.{field} must not be empty")
            steps = manual.get("steps", [])
            orders = [step.get("order") for step in steps if isinstance(step, dict)]
            validation.require(orders == list(range(1, len(orders) + 1)), f"{context} verification step order must be contiguous from 1")
        if item.get("status") == "deployment_dependent_candidate":
            validation.require(bool(item.get("deployment_conditions")), f"{context} requires deployment_conditions")
        if item.get("status") == "source_supported_candidate":
            for chain_id in item.get("chain_ids", []):
                chain = chains_by_id.get(chain_id, {})
                validation.require(chain.get("status") == "resolved", f"{context} requires resolved chain {chain_id}")
                validation.require(
                    chain.get("reachability") == "statically_proven",
                    f"{context} requires statically_proven reachability for {chain_id}",
                )
            for guard_id in item.get("guard_ids", []):
                guard = guards_by_id.get(guard_id, {})
                validation.require(
                    guard.get("result") not in {"deployment_dependent", "unknown"},
                    f"{context} cannot rely on unresolved guard {guard_id}",
                )
        for delta_id in item.get("delta_ids", []):
            delta = deltas_by_id.get(delta_id, {})
            validation.require(delta.get("changed") is True, f"{context} requires changed=true for {delta_id}")

    for gap in gaps:
        validation.references(gap.get("blocks_candidate_ids", []), candidate_ids, gap.get("gap_id", "gap"))

    leads = records(data, "research_leads", validation)
    validation.unique_ids(leads, "lead_id")
    for item in leads:
        validation.references(item.get("unresolved_gap_ids", []), gap_ids, item.get("lead_id", "lead"))

    source_coverage = records(data, "source_coverage", validation)
    source_roles = [item.get("role") for item in source_coverage]
    validation.require(set(source_roles) == SOURCE_ROLES, "source_coverage must contain every required source role exactly once")
    validation.require(len(source_roles) == len(set(source_roles)), "source_coverage contains duplicate roles")

    path_coverage = records(data, "path_coverage", validation)
    path_classes = [item.get("path_class") for item in path_coverage]
    validation.require(set(path_classes) == PATH_CLASSES, "path_coverage must contain every required path class exactly once")
    validation.require(len(path_classes) == len(set(path_classes)), "path_coverage contains duplicate path classes")

    for collection, name in ((source_coverage, "source_coverage"), (path_coverage, "path_coverage")):
        for item in collection:
            context = f"{name}.{item.get('role', item.get('path_class'))}"
            status = item.get("status")
            applicable = item.get("applicable")
            validation.require(
                not (applicable is False and status != "not_applicable"),
                f"{context} with applicable=false must be not_applicable",
            )
            validation.require(
                not (applicable is True and status == "not_applicable"),
                f"{context} with applicable=true cannot be not_applicable",
            )
            if status == "not_applicable":
                validation.require(bool(item.get("evidence_ids")), f"{context} not_applicable requires evidence")
            if status == "unresolved":
                validation.require(bool(item.get("gap_ids")), f"{context} unresolved requires gap_ids")
            validation.references(item.get("evidence_ids", []), evidence_ids, context)
            validation.references(item.get("gap_ids", []), gap_ids, context)
            if name == "path_coverage":
                validation.references(item.get("chain_ids", []), chain_ids, context)

    expected_order = sorted(
        candidates,
        key=lambda item: (
            PRIORITY_ORDER.get(item.get("verification_priority"), 99),
            SEVERITY_ORDER.get(item.get("preliminary_severity"), 99),
            CONFIDENCE_ORDER.get(item.get("source_confidence"), 99),
            item.get("candidate_id", ""),
        ),
    )
    validation.require(candidates == expected_order, "candidates are not in deterministic priority/severity/confidence/ID order")

    return validation.errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_scan", type=Path, help="Path to source-scan.json")
    args = parser.parse_args()

    try:
        errors = validate(args.source_scan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.source_scan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
