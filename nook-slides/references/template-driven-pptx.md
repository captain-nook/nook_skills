# Template-driven PPTX workflow

Use this reference before generating any formal editable PPTX from an approved visual system.

## 1. Highest rule

The selected template package is the highest visual authority.

A template package is not a loose reference, mood board, or style hint. It contains one maintained machine geometry source plus generated PPTX/screenshots used as human-reviewed visual golden artifacts. Together they define layout, spacing, text scale, image slots, component proportions, decorative vocabulary, and visual hierarchy.

If there are 3 visual systems, maintain 3 template files. If there are 8 visual systems, maintain 8 template files. If there are many systems, each system still needs its own template file or template package.

Do not create a new freeform rendering script when an approved template package exists. Do not maintain unrelated geometry in both the component source and renderer.

## 2. Required source files

Before generation, there must be two locked sources:

1. **Confirmed content/page-form note**: decides slide count, every visible word, punctuation, title/body/card text, page role, and presentation form.
2. **Selected template file/package**: decides final visual presentation.

Generation is only template filling.

## 3. Text lock

Visible slide text must come from the confirmed note.

Do not rewrite, summarize, embellish, translate, add transitions, add engineering explanations, or add placeholder warnings into visible slide text.

Allowed visible text sources:

1. Confirmed slide title.
2. Confirmed main sentence.
3. Confirmed body/caption/card text.
4. Minimal placeholder text inside a replaceable image slot, such as `待替换真实截图`.

Forbidden visible text:

1. “真实截图后补”.
2. “这里保留证据槽”.
3. “不伪造界面”.
4. “后续替换”.
5. “REAL SCREENSHOT ONLY”.
6. Component IDs, slot IDs, file paths, build notes, debug labels, internal validation labels.
7. Any sentence invented during PPTX generation.

Engineering notes may go into build logs, speaker notes, comments, or process notes, not on the slide canvas.

## 4. Template filling rules

1. Choose the selected visual system template.
2. Copy the matching template slide/component.
3. Replace text in named text slots using the locked note.
4. Insert images into named image slots while preserving aspect ratio.
5. Keep logo original and small in the template-defined master slot.
6. Keep screenshot placeholders inside the image slot only.
7. Do not add extra captions, badges, labels, or black bars unless they are part of the selected template and required by the confirmed page form.
8. Do not resize text boxes into large empty containers when the content is short. Select the correct template variant instead.

## 5. Design principles for this project

For the duotone independent-zine system:

1. Big words.
2. Few words.
3. Many images.
4. Strong image hierarchy.
5. Text boxes sized to their content.
6. Black blocks used sparingly for emphasis, not as default containers.
7. Color blocks used for rhythm and accents, not random large panels.
8. No construction labels on final slides.

## 6. Image planning

At the asset gate, plan illustration needs early.

1. Generate 3-5 atmosphere/illustration images when the deck needs visual energy.
2. Distinguish illustrations from factual screenshots.
3. Use illustrations as visual support for speaking, not as factual proof.
4. Missing factual screenshots stay as image-slot placeholders.
5. During generation, the agent may create additional illustrations if a confirmed page would otherwise be visually empty, but it must keep the selected template and the locked visible text.

## 7. Correct generation sequence

1. User provides draft MD.
2. Skill asks guided questions.
3. Confirm visual system/template choice.
4. Confirm content/page-form note: slide count, exact visible text, presentation form, assets.
5. Plan or generate illustrations if needed.
6. Fill the selected template with locked text and assets.
7. Export editable PPTX.
8. Render or inspect actual PPTX thumbnails/screenshots.
9. Fix only template filling errors, not content or design direction, unless the user reopens those decisions.

## 8. Failure criteria

Stop and report failure if:

1. The generator needs to invent visible slide text.
2. The generator cannot map a page to a template slide/component.
3. The output contains construction notes on the slide canvas.
4. A page visually looks like a component manual rather than a presentation slide.
5. Images are missing from pages that should be image-led.
6. A PPTX opens only after repair.
## 9. Process-note lock

The confirmed content/page-form note is a process file, but it is binding.

It usually contains two parts:

1. **Structure and text**: slide count, exact title, exact body, exact card text, and punctuation.
2. **Presentation form**: the recommended and user-confirmed page form for each slide.

Once confirmed, generation must follow both parts exactly. The agent may use planning skill to recommend page forms before confirmation, but it must not revise visible text, add page explanations, or choose a different form during final generation.

If the user later asks for a new form, update the template/component package first when the requested form is not already in the maintained component registry.
## 10. Reusable component generator

A maintained template system must eventually have an executable component generator.

For the current duotone zine system, use:

- `scripts/build_deck.py`: read `deck_plan.json`, render maintained components, print visible progress, write PPTX, component map, and build log.
- `scripts/validate_deck.py`: validate PPTX package, slide count, construction-text pollution, and text density.
- `scripts/diagnose_deck.py`: diagnose component quality, including black block overuse, too many text boxes, dense/sparse pages, and shape overload.

Do not treat a successful hand-built sample as production-ready until it has been converted into a reusable generator. A 30-page one-off build script is a failure mode because it hides progress, wastes time, and cannot be trusted by future agents.



