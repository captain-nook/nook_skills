# PPT preflight

Use this reference before generating a formal PPTX, an editable slide deck, or any long deck that needs user-confirmed content and page forms.

## 1. Hard rule

Do not move from raw material directly to the accepted PPTX.

Formal deck generation needs five gates:

1. Content gate.
2. Page-form gate.
3. Asset gate.
4. Template gate.
5. Build gate.

An unconfirmed sample may be produced only as a prototype. Label it as such.

## 2. Content gate

Read the material and propose:

1. Core judgment.
2. Narrative line.
3. Section structure.
4. Suggested page count.
5. Slide-by-slide title.
6. One-sentence message for each slide.
7. Visible on-slide copy.
8. Evidence or asset need for each slide.

Ask the user to approve or revise. Do not treat “continue”, “start”, or “next” as approval if the content gate has not been explicitly passed.

For long decks, confirm by groups instead of asking the user to review 20-30 slides at once.

Recommended groups:

1. Opening group.
2. Framework group.
3. Core case group.
4. Operation/process group.
5. Closing group.

## 3. Page-form gate

For every slide, recommend a presentation form before building it.

Each recommendation must include:

1. Recommended component.
2. Reason.
3. Two alternatives.
4. User decision.

Use concrete component names, not vague layout language. Prefer the maintained component library. If no component fits, pause and propose a new component instead of improvising a one-off layout.

Current high-frequency forms:

1. Giant title.
2. One-sentence judgment.
3. Big number.
4. Process cards.
5. Timeline.
6. Cycle.
7. Hierarchy.
8. Comparison.
9. Image-text layout.
10. Image collage.
11. IP / logo master slot.
12. Generated-asset page.

Heuristics:

1. Strong single claim -> one-sentence judgment or giant title.
2. Metric shock -> big number.
3. Evolution, history, stages -> timeline.
4. Layers or upstream/downstream -> hierarchy; if the point is change over time, use timeline-like progression.
5. Procedure -> process cards.
6. Feedback loop -> cycle.
7. New vs old -> comparison.
8. Real case -> screenshot-led image-text or collage.

The model may recommend, but the user chooses. If the user chooses a pyramid instead of a timeline, follow the user’s decision.

## 3.5 Template gate

For editable PPTX, choose an approved visual-system template before generation.

Rules:

1. The template is the highest visual authority.
2. Do not create a new freeform rendering script when a template exists.
3. If the user requests a new style, update or create the visual-system template first; do not make a one-off deck.
4. After the content and page-form note is confirmed, the template choice is the last visual decision. Generation should then proceed without asking the user to approve component IDs or slot IDs.
5. If no existing template fits the confirmed page form, stop and propose a template/component addition.

## 4. Asset gate

Before generation, list all assets:

1. Logo.
2. IP character.
3. User screenshots.
4. User stickers/photos/interface captures.
5. Charts/data.
6. AI-generated non-text images.

Rules:

1. Logo stays original and small, usually as a master corner mark.
2. IP character must be user-provided. Style-transfer it into the deck’s visual system before use.
3. Product screenshots, chat screenshots, maps, Obsidian screens, and agent logs are factual evidence. Keep them faithful; frame, crop, annotate, or mask private details, but do not invent or redraw factual content unless the user explicitly asks.
4. Missing screenshots may be represented by minimal placeholders inside replaceable image slots. Do not put construction explanations outside the slot.
5. Do not use AI-generated images to replace factual screenshots.

## 5. Core case expansion

If a case is the climax of the deck, do not compress it into one slide.

Turn it into a page group. A five-layer case normally needs at least:

1. Case opener.
2. Layer 1 evidence page.
3. Layer 2 evidence page.
4. Layer 3 evidence page.
5. Layer 4 evidence page.
6. Layer 5 evidence page.
7. Result or reflection page.

Important layers may take 2-3 slides each.

Example for a Xinjiang roadtrip AI-training case:

1. Opener: why this case matters.
2. Layer 1: Doubao/chat screenshot as the first natural-language request.
3. Layer 2: prompt/template/task shell.
4. Layer 3: Obsidian notes, map, weather, route context.
5. Layer 4: agent workflow, file operations, tool calls, iterations.
6. Layer 5: human review, preference changes, system update.
7. Output: itinerary, risks, material package, reusable workflow.

## 6. Page plan schema

Use this structure when planning formal decks:

```yaml
- page_no:
  section:
  role:
  title:
  core_message:
  visible_text:
  recommended_component:
  recommendation_reason:
  alternatives:
  user_choice:
  assets:
    - type:
      name:
      source:
      status:
      treatment:
  notes:
```

This page plan is the source of truth for the deck. Generate PPTX from the confirmed plan, not from implicit memory.

## 7. Build gate

Generate the deck only after content, page forms, and assets have been confirmed or deliberately skipped by the user.

Record skipped gates in the build log. Deliver skipped-gate output as a prototype, not as a fully accepted deck.

## 8. Editable PPTX build rule

For editable PPTX, the build gate uses the skill-owned component registry and one internal artifact: `component_map`.

The page plan decides what each slide says. The component registry decides the reusable layout rules. The component map is generated automatically from those two sources.

Required order:

1. Confirm or consume the content gate.
2. Confirm or consume the page-form gate.
3. Confirm or consume the asset gate.
4. Map every slide to a maintained component ID and variant.
5. Render the visual intermediate from that component map.
6. Export native PPTX from the same component definitions.
7. Validate according to `ppt-native-workflow.md`.

Do not deliver a formal editable PPTX generated by a one-off freeform script. If PowerPoint repair is required, the build failed.

The current duotone zine deck uses 12 top-level components. Add variants before adding new component families.
Do not ask the user to approve the component map. Ask only if the content gate, page-form gate, asset permission, logo, IP, or placeholder decision is missing.
## 9. Visible text lock

Visible slide text is locked after the content and page-form note is confirmed.

During generation, copy exact title, body, caption, and card text from the confirmed note. Do not add construction language, engineering notes, file paths, component IDs, slot IDs, or replacement instructions outside an image placeholder.

The slide is for the audience's eyes and the speaker's mouth. Logs are for construction notes.
