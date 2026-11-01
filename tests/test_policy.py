from jarvis_api.policy import (
    ActionDefinition,
    ActionRisk,
    Decision,
    evaluate_action,
)


def test_read_only_action_is_allowed():
    result = evaluate_action(ActionDefinition("search_notes", ActionRisk.READ_ONLY))
    assert result.decision == Decision.ALLOW


def test_reversible_action_is_allowed_by_base_policy():
    result = evaluate_action(ActionDefinition("create_draft", ActionRisk.REVERSIBLE))
    assert result.decision == Decision.ALLOW


def test_consequential_action_requires_approval():
    result = evaluate_action(ActionDefinition("send_email", ActionRisk.CONSEQUENTIAL))
    assert result.decision == Decision.REQUIRE_APPROVAL


def test_prohibited_action_is_denied():
    result = evaluate_action(ActionDefinition("exfiltrate_secrets", ActionRisk.PROHIBITED))
    assert result.decision == Decision.DENY
