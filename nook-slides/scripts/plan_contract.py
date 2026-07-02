from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


APPROVED_VARIANTS = {
    "zine.hero-title": {"cover-left-type-right-image", "cover-image-right", "case-opener"},
    "zine.statement": {"single-judgement", "fragment-cards"},
    "zine.big-number": {"three-column"},
    "zine.process-cards": {"four-step", "three-deliverables", "system-chain"},
    "zine.timeline": {"four-event", "five-layer", "cpr"},
    "zine.cycle": {"four-node", "action-rhythm"},
    "zine.hierarchy": {"four-layer", "skill-structure", "five-layer-preview"},
    "zine.comparison": {"two-column", "three-case-summary", "template-vs-context", "old-solutions", "shell"},
    "zine.card-group": {"parallel-three"},
    "zine.image-text": {"large-image-left", "illustration-statement", "screenshot-evidence", "project-structure", "project-root"},
    "zine.image-collage": {"three-image", "evidence-triptych"},
    "zine.brand-master": {"logo-ip-rules"},
    "zine.generated-asset": {"asset-spec"},
}


VARIANT_CAPACITY = {
    ("zine.process-cards", "four-step"): {"cards": (4, 4)},
    ("zine.process-cards", "three-deliverables"): {"cards": (3, 3)},
    ("zine.process-cards", "system-chain"): {"cards": (3, 5)},
    ("zine.timeline", "four-event"): {"cards": (4, 4)},
    ("zine.timeline", "five-layer"): {"cards": (5, 5)},
    ("zine.timeline", "cpr"): {"cards": (3, 3)},
    ("zine.cycle", "four-node"): {"cards": (4, 4)},
    ("zine.cycle", "action-rhythm"): {"cards": (4, 4)},
    ("zine.hierarchy", "four-layer"): {"cards": (4, 4)},
    ("zine.hierarchy", "five-layer-preview"): {"cards": (5, 5)},
    ("zine.hierarchy", "skill-structure"): {"cards": (3, 6)},
    ("zine.comparison", "two-column"): {"cards": (2, 2)},
    ("zine.comparison", "three-case-summary"): {"cards": (3, 3)},
    ("zine.comparison", "template-vs-context"): {"cards": (2, 2)},
    ("zine.comparison", "old-solutions"): {"cards": (2, 5)},
    ("zine.comparison", "shell"): {"cards": (2, 2)},
    ("zine.card-group", "parallel-three"): {"cards": (3, 3)},
    ("zine.big-number", "three-column"): {"cards": (3, 3)},
    ("zine.image-text", "large-image-left"): {"image_slots": (1, 1)},
    ("zine.image-text", "illustration-statement"): {"image_slots": (1, 1)},
    ("zine.image-text", "screenshot-evidence"): {"image_slots": (1, 1)},
    ("zine.image-text", "project-structure"): {"image_slots": (1, 1)},
    ("zine.image-text", "project-root"): {"image_slots": (1, 1)},
    ("zine.image-collage", "three-image"): {"image_slots": (3, 3)},
    ("zine.image-collage", "evidence-triptych"): {"image_slots": (3, 3)},
}


PAGE_KEYS = {
    "page_no", "component", "variant", "title", "subtitle", "body", "footer",
    "number", "cards", "chips", "image_slots", "center", "center_body",
    "visual_carrier",
}

PLAN_KEYS = {
    "schema_version", "plan_status", "theme", "title", "logo", "assets",
    "content_lock", "pages",
}

CARD_KEYS = {"title", "body", "label", "year", "accent"}
SLOT_KEYS = {"path", "placeholder", "fit", "accent", "status", "focus_x", "focus_y"}
VISUAL_CARRIERS = {"statement", "image", "screenshot", "chart", "table", "structure"}
THEMES = {"duotone-zine", "oriental-dark-yaji", "bright-street-dance"}
VISIBLE_KEYS = ("page_no", "title", "subtitle", "body", "footer", "number", "center", "center_body", "cards", "chips")

PAGE_TEXT_LIMITS = {
    "title": 24,
    "subtitle": 36,
    "body": 80,
    "footer": 40,
    "center": 18,
    "center_body": 40,
}

CARD_TEXT_LIMITS = {
    "title": 16,
    "body": 60,
    "label": 12,
    "year": 10,
}

CHIP_LIMIT = 12
PLACEHOLDER_LIMIT = 24


class PlanContractError(ValueError):
    pass


def _unexpected_keys(value: Dict[str, Any], allowed: Iterable[str], label: str) -> None:
    extra = sorted(set(value) - set(allowed))
    if extra:
        raise PlanContractError(f"{label} contains unapproved fields: {', '.join(extra)}")


def _require_text(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise PlanContractError(f"{label} must be a non-empty string")


def _check_text_limit(value: Any, limit: int, label: str) -> None:
    if value is None:
        return
    if not isinstance(value, (str, int, float)):
        raise PlanContractError(f"{label} must be text-like")
    text = str(value)
    if len(text) > limit:
        raise PlanContractError(f"{label} is too long: {len(text)} chars; max {limit}. Split the page or choose another variant.")


def _check_collection(page: Dict[str, Any], key: str, low: int, high: int) -> None:
    items = page.get(key, [])
    if not isinstance(items, list):
        raise PlanContractError(f"page {page['page_no']}: {key} must be an array")
    if not low <= len(items) <= high:
        raise PlanContractError(
            f"page {page['page_no']}: {page['component']} / {page['variant']} requires "
            f"{low}-{high} {key}; got {len(items)}. Split the page or approve a new variant."
        )


def _forbid_fields(page: Dict[str, Any], fields: Iterable[str]) -> None:
    present = [field for field in fields if field in page and page.get(field) not in (None, "", [], {})]
    if present:
        raise PlanContractError(
            f"page {page['page_no']}: {page['component']} / {page['variant']} forbids fields: {', '.join(present)}"
        )


def _validate_component_contract(page: Dict[str, Any]) -> None:
    component = page["component"]
    variant = page["variant"]

    if component == "zine.hero-title":
        _forbid_fields(page, {"cards", "number", "center", "center_body"})
        if "image_slots" in page:
            _check_collection(page, "image_slots", 0, 1)
        return

    if component == "zine.statement":
        _forbid_fields(page, {"image_slots", "number", "center", "center_body"})
        if variant == "fragment-cards":
            _check_collection(page, "cards", 2, 4)
        else:
            _forbid_fields(page, {"cards"})
        if "chips" in page:
            _check_collection(page, "chips", 0, 3)
        return

    if component == "zine.big-number":
        _forbid_fields(page, {"image_slots", "chips", "center", "center_body"})
        _check_collection(page, "cards", 3, 3)
        return

    if component == "zine.process-cards":
        _forbid_fields(page, {"image_slots", "number", "center", "center_body"})
        return

    if component == "zine.timeline":
        _forbid_fields(page, {"image_slots", "chips", "number", "center", "center_body"})
        return

    if component == "zine.cycle":
        _forbid_fields(page, {"image_slots", "number"})
        _check_collection(page, "cards", 4, 4)
        return

    if component == "zine.hierarchy":
        _forbid_fields(page, {"image_slots", "chips", "number", "center", "center_body"})
        return

    if component == "zine.comparison":
        _forbid_fields(page, {"image_slots", "number", "center", "center_body"})
        return

    if component == "zine.card-group":
        _forbid_fields(page, {"image_slots", "number", "center", "center_body"})
        _check_collection(page, "cards", 3, 3)
        return

    if component == "zine.image-text":
        _forbid_fields(page, {"cards", "number", "center", "center_body"})
        _check_collection(page, "image_slots", 1, 1)
        return

    if component == "zine.image-collage":
        _forbid_fields(page, {"cards", "number", "center", "center_body"})
        _check_collection(page, "image_slots", 3, 3)
        return

    if component == "zine.brand-master":
        if "cards" in page:
            _check_collection(page, "cards", 2, 4)
        if "image_slots" in page:
            _check_collection(page, "image_slots", 1, 4)
        return

    if component == "zine.generated-asset":
        if "cards" in page:
            _check_collection(page, "cards", 3, 4)
        if "image_slots" in page:
            _check_collection(page, "image_slots", 0, 1)
        return


def _sha256(path: Path) -> str:
    if path.suffix.lower() in {".md", ".markdown", ".json"}:
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_link(path_text: str, plan_path: Optional[Path]) -> Path:
    path = Path(path_text)
    if not path.is_absolute() and plan_path:
        path = (plan_path.parent / path).resolve()
    return path


def _visible_projection(page: Dict[str, Any]) -> Dict[str, Any]:
    projected = {key: page[key] for key in VISIBLE_KEYS if key in page}
    if "cards" in projected:
        projected["cards"] = [
            {key: card[key] for key in ("title", "body", "label", "year") if key in card}
            for card in projected["cards"]
        ]
    placeholders = [slot.get("placeholder") for slot in page.get("image_slots", []) if slot.get("placeholder")]
    if placeholders:
        projected["image_placeholders"] = placeholders
    return projected


def validate_plan_contract(plan: Dict[str, Any], plan_path: Optional[Path] = None) -> None:
    if not isinstance(plan, dict):
        raise PlanContractError("deck plan must be a JSON object")
    _unexpected_keys(plan, PLAN_KEYS, "deck plan")

    if plan.get("schema_version", 1) != 1:
        raise PlanContractError("schema_version must be 1")
    if plan.get("theme") not in THEMES:
        raise PlanContractError(f"theme must be one of {', '.join(sorted(THEMES))}")
    status = plan.get("plan_status", "prototype")
    if status not in {"prototype", "accepted"}:
        raise PlanContractError("plan_status must be prototype or accepted")

    if status == "accepted":
        lock = plan.get("content_lock")
        if not isinstance(lock, dict):
            raise PlanContractError("accepted plans require content_lock")
        _unexpected_keys(lock, {"source_path", "sha256", "copy_path", "copy_sha256", "approved_at"}, "content_lock")
        _require_text(lock.get("source_path"), "content_lock.source_path")
        _require_text(lock.get("sha256"), "content_lock.sha256")
        _require_text(lock.get("copy_path"), "content_lock.copy_path")
        _require_text(lock.get("copy_sha256"), "content_lock.copy_sha256")
        _require_text(lock.get("approved_at"), "content_lock.approved_at")
        source = _resolve_link(lock["source_path"], plan_path)
        if not source.exists():
            raise PlanContractError(f"locked content source does not exist: {source}")
        actual = _sha256(source)
        if actual.lower() != lock["sha256"].lower():
            raise PlanContractError("content lock hash mismatch; reopen the content gate before building")
        copy_path = _resolve_link(lock["copy_path"], plan_path)
        if not copy_path.exists():
            raise PlanContractError(f"locked visible-copy manifest does not exist: {copy_path}")
        if _sha256(copy_path).lower() != lock["copy_sha256"].lower():
            raise PlanContractError("visible-copy manifest hash mismatch; reopen the content gate before building")
        try:
            locked_copy = json.loads(copy_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            raise PlanContractError(f"cannot read visible-copy manifest: {exc}") from exc
        expected_copy = locked_copy.get("pages") if isinstance(locked_copy, dict) else None
        actual_copy = [_visible_projection(page) for page in plan.get("pages", [])]
        if expected_copy != actual_copy:
            raise PlanContractError("visible copy differs from the approved manifest; reopen the content gate")

    pages = plan.get("pages")
    if not isinstance(pages, list) or not pages:
        raise PlanContractError("pages must be a non-empty array")

    seen = set()
    for index, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            raise PlanContractError(f"page entry {index} must be an object")
        _unexpected_keys(page, PAGE_KEYS, f"page entry {index}")
        number = page.get("page_no")
        if not isinstance(number, int) or number < 1:
            raise PlanContractError(f"page entry {index}: page_no must be a positive integer")
        if number in seen:
            raise PlanContractError(f"duplicate page_no: {number}")
        seen.add(number)

        component = page.get("component")
        variant = page.get("variant")
        if component not in APPROVED_VARIANTS:
            raise PlanContractError(f"page {number}: unsupported component {component!r}")
        if not variant:
            raise PlanContractError(f"page {number}: variant is required; empty variants are forbidden")
        if variant not in APPROVED_VARIANTS[component]:
            approved = ", ".join(sorted(APPROVED_VARIANTS[component]))
            raise PlanContractError(f"page {number}: unapproved variant {variant!r}; allowed: {approved}")
        _require_text(page.get("title"), f"page {number}.title")
        for key, limit in PAGE_TEXT_LIMITS.items():
            _check_text_limit(page.get(key), limit, f"page {number}.{key}")
        carrier = page.get("visual_carrier")
        if carrier not in VISUAL_CARRIERS:
            raise PlanContractError(
                f"page {number}: visual_carrier is required and must be one of {', '.join(sorted(VISUAL_CARRIERS))}"
            )

        for card_index, card in enumerate(page.get("cards", []), start=1):
            if not isinstance(card, dict):
                raise PlanContractError(f"page {number}: card {card_index} must be an object")
            _unexpected_keys(card, CARD_KEYS, f"page {number} card {card_index}")
            _require_text(card.get("title"), f"page {number} card {card_index}.title")
            for key, limit in CARD_TEXT_LIMITS.items():
                _check_text_limit(card.get(key), limit, f"page {number} card {card_index}.{key}")
        for chip_index, chip in enumerate(page.get("chips", []), start=1):
            _check_text_limit(chip, CHIP_LIMIT, f"page {number} chip {chip_index}")
        for slot_index, slot in enumerate(page.get("image_slots", []), start=1):
            if not isinstance(slot, dict):
                raise PlanContractError(f"page {number}: image slot {slot_index} must be an object")
            _unexpected_keys(slot, SLOT_KEYS, f"page {number} image slot {slot_index}")
            if not slot.get("path") and not slot.get("placeholder"):
                raise PlanContractError(f"page {number}: image slot {slot_index} needs path or placeholder")
            _check_text_limit(slot.get("placeholder"), PLACEHOLDER_LIMIT, f"page {number} image slot {slot_index}.placeholder")

        for key, bounds in VARIANT_CAPACITY.get((component, variant), {}).items():
            _check_collection(page, key, bounds[0], bounds[1])
        _validate_component_contract(page)

    expected = list(range(1, len(pages) + 1))
    if sorted(seen) != expected:
        raise PlanContractError(f"page numbers must be continuous 1-{len(pages)}")
