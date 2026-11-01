from dataclasses import dataclass
from enum import StrEnum


class ActionRisk(StrEnum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    CONSEQUENTIAL = "consequential"
    PROHIBITED = "prohibited"


class Decision(StrEnum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True)
class ActionDefinition:
    name: str
    risk: ActionRisk


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str


def evaluate_action(action: ActionDefinition) -> PolicyResult:
    """Deterministic policy gate. Never delegate this decision to the LLM."""
    if action.risk == ActionRisk.PROHIBITED:
        return PolicyResult(Decision.DENY, "This action is prohibited by policy.")
    if action.risk == ActionRisk.CONSEQUENTIAL:
        return PolicyResult(
            Decision.REQUIRE_APPROVAL,
            "Explicit user approval is required before execution.",
        )
    return PolicyResult(Decision.ALLOW, "Action is within the configured low-risk policy.")
