from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_CATALOG_PATH = PROJECT_ROOT / "reasoning" / "rules" / "catalog.v1.yaml"


@dataclass
class ReasoningResult:
    inferred_states: list[str] = field(default_factory=list)
    primary_state: str | None = None
    evidence_used: dict[str, list[str]] = field(default_factory=dict)
    rules_fired: list[str] = field(default_factory=list)
    confidence: str = "low"
    needs_clarification: bool = False
    clarification_reason: str | None = None
    rule_version: str = "unknown"


class RuleCatalog:
    def __init__(self, path: Path = RULE_CATALOG_PATH):
        with path.open("r", encoding="utf-8") as handle:
            catalog = yaml.safe_load(handle)
        self.version = str(catalog["version"])
        self.rules: list[dict[str, Any]] = catalog["rules"]
        self.priorities = {
            state: int(config.get("priority", 0))
            for state, config in catalog["states"].items()
        }

    @staticmethod
    def _matches(values: set[str], expected: list[str]) -> bool:
        return bool(values.intersection(expected))

    def evaluate(
        self,
        emotions: list[str],
        symptoms: list[str],
        triggers: list[str],
    ) -> tuple[list[str], list[str]]:
        evidence = {
            "emotions": set(emotions),
            "symptoms": set(symptoms),
            "triggers": set(triggers),
        }
        states: list[str] = []
        fired: list[str] = []
        for rule in self.rules:
            if any(state in states for state in rule.get("unless_states", [])):
                continue
            required_categories = rule.get("require_categories", [])
            if any(not evidence[category] for category in required_categories):
                continue
            all_groups = rule.get("all", {})
            if any(
                not self._matches(evidence[category], expected)
                for category, expected in all_groups.items()
            ):
                continue
            any_groups = rule.get("any", {})
            if any_groups:
                matcher = all if required_categories else any
                matched = matcher(
                    self._matches(evidence[category], expected)
                    for category, expected in any_groups.items()
                )
                if not matched:
                    continue
            state = rule["state"]
            if state not in states:
                states.append(state)
            fired.append(rule["id"])
        return states, fired


class SymbolicReasoningAgent:
    def __init__(self):
        self.catalog = RuleCatalog()

    def reason(
        self,
        emotions: list[str],
        symptoms: list[str],
        triggers: list[str],
        session_id: str = "anonymous",
        persistence: bool = False,
    ) -> ReasoningResult:
        del session_id, persistence
        result = ReasoningResult(
            evidence_used={
                "emotions": emotions,
                "symptoms": symptoms,
                "triggers": triggers,
            },
            rule_version=self.catalog.version,
        )
        states, rules = self.catalog.evaluate(emotions, symptoms, triggers)
        total_evidence = len(emotions) + len(symptoms) + len(triggers)
        if not states:
            if total_evidence == 0:
                result.needs_clarification = True
                result.clarification_reason = "no_evidence"
            else:
                states = ["NeedsMoreContext"]
                rules = ["R_LOW_CONTEXT"]
                result.needs_clarification = True
                result.clarification_reason = "insufficient_evidence"
        result.inferred_states = states
        result.rules_fired = rules
        if states:
            result.primary_state = max(
                states,
                key=lambda state: self.catalog.priorities.get(state, 0),
            )
        categories = sum(bool(items) for items in (emotions, symptoms, triggers))
        if categories >= 2 and states:
            result.confidence = "high"
        elif categories >= 1 and states and states[0] != "NeedsMoreContext":
            result.confidence = "medium"
        return result


_reasoner_instance: SymbolicReasoningAgent | None = None


def get_reasoner() -> SymbolicReasoningAgent:
    global _reasoner_instance
    if _reasoner_instance is None:
        _reasoner_instance = SymbolicReasoningAgent()
    return _reasoner_instance


def get_rule_version() -> str:
    return get_reasoner().catalog.version


def reason_from_signals(
    emotions: list[str],
    symptoms: list[str],
    triggers: list[str],
    session_id: str = "anonymous",
    persistence: bool = False,
) -> dict[str, Any]:
    result = get_reasoner().reason(
        emotions, symptoms, triggers, session_id, persistence
    )
    return {
        "inferred_states": result.inferred_states,
        "primary_state": result.primary_state,
        "evidence_used": result.evidence_used,
        "rules_fired": result.rules_fired,
        "confidence": result.confidence,
        "needs_clarification": result.needs_clarification,
        "clarification_reason": result.clarification_reason,
        "rule_version": result.rule_version,
    }
