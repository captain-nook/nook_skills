from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from plan_contract import APPROVED_VARIANTS, THEMES, VISUAL_CARRIERS


GATE_ORDER = [
    "intake",
    "gate1_content",
    "gate2_page_forms",
    "gate3_visual_system",
    "gate4_assets",
    "final_lock",
    "plan_built",
    "rendered",
    "delivered",
]

CURRENT_GATES = set(GATE_ORDER) | {"blocked"}
GATE_STATUSES = {"pending", "in_progress", "confirmed", "blocked", "skipped"}
DELIVERY_TARGETS = {"schema-only", "prototype", "sample-review", "editable-pptx"}
LENGTHS = {"short", "medium", "long"}
DENSITIES = {"speaker-led", "reading-first"}
QUESTION_TYPES = {"source_material", "intake_choice", "decision_card", "confirmation"}
FACTUAL_ASSET_TYPES = {
    "screenshot",
    "product_ui",
    "chart",
    "logo",
    "map",
    "dashboard",
    "document",
    "evidence_photo",
    "real_photo",
}


class InteractionStateError(ValueError):
    pass


def _fail(message: str) -> None:
    raise InteractionStateError(message)


def _require_object(value: Any, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> List[Any]:
    if not isinstance(value, list):
        _fail(f"{label} must be an array")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a non-empty string")
    return value


def _require_int(value: Any, label: str) -> int:
    if not isinstance(value, int):
        _fail(f"{label} must be an integer")
    return value


def _reject_extra_keys(value: Dict[str, Any], allowed: Iterable[str], label: str) -> None:
    extra = sorted(set(value) - set(allowed))
    if extra:
        _fail(f"{label} contains unapproved fields: {', '.join(extra)}")


def _state_root(state_path: Optional[Path], project: Dict[str, Any]) -> Optional[Path]:
    if state_path is None:
        return None
    if state_path.parent.name == "notes":
        return state_path.parent.parent.resolve()
    folder = project.get("folder")
    if not isinstance(folder, str) or not folder:
        return state_path.parent.resolve()
    candidate = Path(folder)
    if candidate.is_absolute():
        return candidate
    return (state_path.parent / candidate).resolve()


def _resolve_project_path(path_text: str, state_path: Optional[Path], project: Dict[str, Any]) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    root = _state_root(state_path, project)
    return (root / path).resolve() if root else path


def _validate_top_level(state: Dict[str, Any]) -> None:
    _reject_extra_keys(
        state,
        {
            "schema_version",
            "project",
            "interaction_policy",
            "current_gate",
            "delivery_target",
            "gates",
            "intake",
            "active_questions",
            "pages",
            "pending_decision_cards",
            "visual_system",
            "assets",
            "locks",
            "history",
        },
        "interaction state",
    )
    if state.get("schema_version") != 1:
        _fail("schema_version must be 1")
    current_gate = state.get("current_gate")
    if current_gate not in CURRENT_GATES:
        _fail(f"current_gate must be one of {', '.join(sorted(CURRENT_GATES))}")
    if state.get("delivery_target") not in DELIVERY_TARGETS:
        _fail(f"delivery_target must be one of {', '.join(sorted(DELIVERY_TARGETS))}")
    project = _require_object(state.get("project"), "project")
    _reject_extra_keys(project, {"slug", "folder", "title", "created"}, "project")
    _require_text(project.get("slug"), "project.slug")
    _require_text(project.get("folder"), "project.folder")


def _validate_interaction_policy(state: Dict[str, Any]) -> Dict[str, Any]:
    policy = _require_object(state.get("interaction_policy"), "interaction_policy")
    _reject_extra_keys(
        policy,
        {
            "default_to_choices",
            "max_intake_questions_per_round",
            "max_decision_cards_per_round",
            "source_material_open_allowed",
            "text_lock_after_gate",
        },
        "interaction_policy",
    )
    if policy.get("default_to_choices") is not True:
        _fail("interaction_policy.default_to_choices must be true")
    max_intake = policy.get("max_intake_questions_per_round")
    if not isinstance(max_intake, int) or not 1 <= max_intake <= 3:
        _fail("interaction_policy.max_intake_questions_per_round must be 1-3")
    max_cards = policy.get("max_decision_cards_per_round")
    if not isinstance(max_cards, int) or not 1 <= max_cards <= 4:
        _fail("interaction_policy.max_decision_cards_per_round must be 1-4")
    if policy.get("text_lock_after_gate") != "gate2_page_forms":
        _fail("interaction_policy.text_lock_after_gate must be gate2_page_forms")
    return policy


def _validate_gates(state: Dict[str, Any]) -> None:
    gates = _require_object(state.get("gates"), "gates")
    _reject_extra_keys(gates, set(GATE_ORDER), "gates")
    for gate in GATE_ORDER:
        gate_state = _require_object(gates.get(gate), f"gates.{gate}")
        _reject_extra_keys(gate_state, {"status", "confirmed_at", "confirmed_by", "note"}, f"gates.{gate}")
        if gate_state.get("status") not in GATE_STATUSES:
            _fail(f"gates.{gate}.status must be one of {', '.join(sorted(GATE_STATUSES))}")

    current_gate = state["current_gate"]
    if current_gate == "blocked":
        if not any(gates[gate]["status"] == "blocked" for gate in GATE_ORDER):
            _fail("current_gate is blocked but no gate status is blocked")
        return

    current_index = GATE_ORDER.index(current_gate)
    for gate in GATE_ORDER[:current_index]:
        if gates[gate]["status"] != "confirmed":
            _fail(f"cannot enter {current_gate}; previous gate {gate} is not confirmed")

    for gate in GATE_ORDER[current_index + 1 :]:
        if gates[gate]["status"] == "confirmed":
            _fail(f"future gate {gate} is confirmed before current_gate {current_gate}")


def _validate_active_questions(state: Dict[str, Any], policy: Dict[str, Any]) -> None:
    questions = _require_list(state.get("active_questions", []), "active_questions")
    if not questions:
        return
    max_allowed = policy["max_decision_cards_per_round"]
    if state["current_gate"] == "intake":
        max_allowed = policy["max_intake_questions_per_round"]
    if len(questions) > max_allowed:
        _fail(f"active_questions contains {len(questions)} questions; max for current gate is {max_allowed}")
    for index, raw_question in enumerate(questions, start=1):
        question = _require_object(raw_question, f"active_questions[{index}]")
        _reject_extra_keys(question, {"id", "question_type", "prompt", "options", "recommended"}, f"active_questions[{index}]")
        question_type = question.get("question_type")
        if question_type not in QUESTION_TYPES:
            _fail(f"active_questions[{index}].question_type must be one of {', '.join(sorted(QUESTION_TYPES))}")
        _require_text(question.get("prompt"), f"active_questions[{index}].prompt")
        options = question.get("options")
        if question_type == "source_material":
            if options is not None:
                _require_list(options, f"active_questions[{index}].options")
            continue
        options = _require_list(options, f"active_questions[{index}].options")
        if not 2 <= len(options) <= 4:
            _fail(f"active_questions[{index}] must have 2-4 options unless it asks for source material")
        keys = set()
        for opt_index, raw_option in enumerate(options, start=1):
            option = _require_object(raw_option, f"active_questions[{index}].options[{opt_index}]")
            _reject_extra_keys(option, {"key", "label", "description"}, f"active_questions[{index}].options[{opt_index}]")
            key = _require_text(option.get("key"), f"active_questions[{index}].options[{opt_index}].key")
            if key in keys:
                _fail(f"active_questions[{index}] has duplicate option key {key}")
            keys.add(key)
            _require_text(option.get("label"), f"active_questions[{index}].options[{opt_index}].label")
        recommended = question.get("recommended")
        if recommended is not None and recommended not in keys:
            _fail(f"active_questions[{index}].recommended must match an option key")


def _validate_intake(state: Dict[str, Any]) -> None:
    if state["gates"]["intake"]["status"] != "confirmed":
        return
    intake = _require_object(state.get("intake"), "intake")
    required = ["source_material", "purpose", "audience", "outcome", "length", "density", "delivery_target"]
    for key in required:
        _require_text(intake.get(key), f"intake.{key}")
    if intake["length"] not in LENGTHS:
        _fail("intake.length must be short, medium, or long")
    if intake["density"] not in DENSITIES:
        _fail("intake.density must be speaker-led or reading-first")
    if intake["delivery_target"] != state["delivery_target"]:
        _fail("intake.delivery_target must match top-level delivery_target")


def _validate_pages_for_content(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    pages = _require_list(state.get("pages"), "pages")
    if not pages:
        _fail("gate1_content confirmed requires at least one page")
    seen = set()
    for index, raw_page in enumerate(pages, start=1):
        page = _require_object(raw_page, f"pages[{index}]")
        number = _require_int(page.get("page_no"), f"pages[{index}].page_no")
        if number < 1:
            _fail(f"pages[{index}].page_no must be positive")
        if number in seen:
            _fail(f"duplicate page_no: {number}")
        seen.add(number)
        _require_text(page.get("title"), f"page {number}.title")
        if page.get("visual_carrier") not in VISUAL_CARRIERS:
            _fail(f"page {number}.visual_carrier must be one of {', '.join(sorted(VISUAL_CARRIERS))}")
        if page.get("content_status") != "confirmed":
            _fail(f"page {number}.content_status must be confirmed")
        visible_copy = _require_object(page.get("visible_copy"), f"page {number}.visible_copy")
        if not visible_copy:
            _fail(f"page {number}.visible_copy cannot be empty")
    if sorted(seen) != list(range(1, len(pages) + 1)):
        _fail(f"page numbers must be continuous 1-{len(pages)}")
    return [page for page in pages if isinstance(page, dict)]


def _validate_page_forms(state: Dict[str, Any], pages: List[Dict[str, Any]]) -> None:
    if state["gates"]["gate2_page_forms"]["status"] != "confirmed":
        return
    for page in pages:
        number = page["page_no"]
        page_form = _require_object(page.get("page_form"), f"page {number}.page_form")
        if page_form.get("status") != "confirmed":
            _fail(f"page {number}.page_form.status must be confirmed")
        _require_text(page_form.get("natural_form"), f"page {number}.page_form.natural_form")
        component = page_form.get("component")
        variant = page_form.get("variant")
        if component not in APPROVED_VARIANTS:
            _fail(f"page {number}.page_form.component is not approved: {component!r}")
        if variant not in APPROVED_VARIANTS[component]:
            approved = ", ".join(sorted(APPROVED_VARIANTS[component]))
            _fail(f"page {number}.page_form.variant is not approved: {variant!r}; allowed: {approved}")


def _validate_post_gate2_text_lock(state: Dict[str, Any], state_path: Optional[Path]) -> None:
    if state["gates"]["gate2_page_forms"]["status"] != "confirmed":
        return
    locks = _require_object(state.get("locks"), "locks")
    if locks.get("text_locked") is not True:
        _fail("Gate 2 confirmed requires locks.text_locked=true")
    if locks.get("locked_after_gate") != "gate2_page_forms":
        _fail("Gate 2 confirmed requires locks.locked_after_gate=gate2_page_forms")
    accepted = _require_text(locks.get("accepted_copy_path"), "locks.accepted_copy_path")
    visible = _require_text(locks.get("visible_copy_path"), "locks.visible_copy_path")
    _require_text(locks.get("approved_at"), "locks.approved_at")
    if state_path is None or state_path.parent.name != "notes":
        return
    project = _require_object(state.get("project"), "project")
    for label, path_text in (("accepted_copy_path", accepted), ("visible_copy_path", visible)):
        resolved = _resolve_project_path(path_text, state_path, project)
        if not resolved.exists():
            _fail(f"locks.{label} does not exist: {resolved}")


def _validate_pending_decision_cards(state: Dict[str, Any]) -> None:
    cards = _require_list(state.get("pending_decision_cards", []), "pending_decision_cards")
    policy = _require_object(state.get("interaction_policy"), "interaction_policy")
    max_cards = policy.get("max_decision_cards_per_round", 4)
    if len(cards) > max_cards:
        _fail(f"pending_decision_cards may contain at most {max_cards} cards")
    seen_ids = set()
    for index, raw_card in enumerate(cards, start=1):
        card = _require_object(raw_card, f"pending_decision_cards[{index}]")
        card_id = _require_text(str(card.get("id", "")), f"pending_decision_cards[{index}].id")
        if card_id in seen_ids:
            _fail(f"duplicate decision card id: {card_id}")
        seen_ids.add(card_id)
        options = _require_list(card.get("options"), f"decision card {card_id}.options")
        if not 3 <= len(options) <= 4:
            _fail(f"decision card {card_id} must have 3-4 options")
        allowed_keys = set()
        for opt_index, raw_option in enumerate(options, start=1):
            option = _require_object(raw_option, f"decision card {card_id}.options[{opt_index}]")
            key = _require_text(option.get("key"), f"decision card {card_id}.option.key")
            if key not in {"A", "B", "C", "D"}:
                _fail(f"decision card {card_id} option key must be A-D")
            if key in allowed_keys:
                _fail(f"decision card {card_id} has duplicate option key {key}")
            allowed_keys.add(key)
            _require_text(option.get("label"), f"decision card {card_id}.option.label")
            component = option.get("component")
            variant = option.get("variant")
            if component is not None or variant is not None:
                if component not in APPROVED_VARIANTS:
                    _fail(f"decision card {card_id} option {key} has unapproved component {component!r}")
                if variant not in APPROVED_VARIANTS[component]:
                    _fail(f"decision card {card_id} option {key} has unapproved variant {variant!r}")
        recommended = card.get("recommended")
        if recommended is not None and recommended not in allowed_keys:
            _fail(f"decision card {card_id}.recommended must match an option key")


def _validate_visual_system(state: Dict[str, Any]) -> None:
    if state["gates"]["gate3_visual_system"]["status"] != "confirmed":
        return
    visual_system = _require_object(state.get("visual_system"), "visual_system")
    if visual_system.get("status") != "confirmed":
        _fail("visual_system.status must be confirmed")
    theme = visual_system.get("theme")
    if theme not in THEMES:
        _fail(f"visual_system.theme must be one of {', '.join(sorted(THEMES))}")
    renderer_status = visual_system.get("renderer_status")
    if state["delivery_target"] == "editable-pptx":
        if theme != "duotone-zine":
            _fail(f"{theme} cannot be used for editable-pptx until its deterministic renderer is approved")
        if renderer_status not in {"available", "approved"}:
            _fail("duotone-zine editable-pptx requires renderer_status available or approved")


def _validate_assets(state: Dict[str, Any]) -> None:
    if state["gates"]["gate4_assets"]["status"] != "confirmed":
        return
    assets = _require_object(state.get("assets"), "assets")
    if assets.get("status") != "confirmed":
        _fail("assets.status must be confirmed")
    items = _require_list(assets.get("items"), "assets.items")
    for index, raw_item in enumerate(items, start=1):
        item = _require_object(raw_item, f"assets.items[{index}]")
        asset_type = item.get("asset_type")
        source = item.get("source")
        if asset_type in FACTUAL_ASSET_TYPES and source == "ai_generated":
            _fail(f"asset {index} is factual ({asset_type}) and cannot use ai_generated source")


def _validate_locks(state: Dict[str, Any], state_path: Optional[Path]) -> None:
    if state["gates"]["final_lock"]["status"] != "confirmed":
        return
    locks = _require_object(state.get("locks"), "locks")
    accepted = _require_text(locks.get("accepted_copy_path"), "locks.accepted_copy_path")
    visible = _require_text(locks.get("visible_copy_path"), "locks.visible_copy_path")
    _require_text(locks.get("approved_at"), "locks.approved_at")
    if locks.get("text_locked") is not True:
        _fail("final_lock requires locks.text_locked=true")
    if locks.get("locked_after_gate") != "gate2_page_forms":
        _fail("final_lock requires locks.locked_after_gate=gate2_page_forms")
    project = _require_object(state.get("project"), "project")
    for label, path_text in (("accepted_copy_path", accepted), ("visible_copy_path", visible)):
        resolved = _resolve_project_path(path_text, state_path, project)
        if state_path is not None and state_path.parent.name == "notes" and not resolved.exists():
            _fail(f"locks.{label} does not exist: {resolved}")


def validate_interaction_state(state: Dict[str, Any], state_path: Optional[Path] = None) -> None:
    if not isinstance(state, dict):
        _fail("interaction state must be a JSON object")
    _validate_top_level(state)
    policy = _validate_interaction_policy(state)
    _validate_gates(state)
    _validate_active_questions(state, policy)
    _validate_intake(state)
    pages: List[Dict[str, Any]] = []
    if state["gates"]["gate1_content"]["status"] == "confirmed":
        pages = _validate_pages_for_content(state)
    _validate_page_forms(state, pages)
    _validate_post_gate2_text_lock(state, state_path)
    _validate_pending_decision_cards(state)
    _validate_visual_system(state)
    _validate_assets(state)
    _validate_locks(state, state_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate nook slide workflow interaction state before gate transitions.")
    parser.add_argument("state", help="Path to notes/interaction-state.json")
    args = parser.parse_args()
    path = Path(args.state)
    try:
        state = json.loads(path.read_text(encoding="utf-8-sig"))
        validate_interaction_state(state, path)
    except (OSError, json.JSONDecodeError, InteractionStateError) as exc:
        print(f"FAILED: {exc}")
        return 1
    gates = state["gates"]
    confirmed = sum(1 for gate in GATE_ORDER if gates[gate]["status"] == "confirmed")
    print(f"OK current_gate={state['current_gate']} confirmed_gates={confirmed} delivery_target={state['delivery_target']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
