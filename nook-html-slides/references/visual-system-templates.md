# Visual system templates

Use this reference whenever an editable PPTX deck needs a maintained visual system.

## 1. Hard rule

A visual system is a template package, not a prompt description.

If there are 3 visual systems, keep 3 template packages. If there are 8, keep 8. If there are many, each still needs its own template file/package. The selected template package is the highest presentation authority for layout, spacing, image slots, component proportions, typography, color rhythm, and decorative vocabulary.

Do not treat a screenshot, SVG preview, or mood board as a loose style hint during final PPTX generation. If the visual system has already been approved, use its maintained template package and component registry.

## 2. Current maintained template packages

### 2.1 双色独立刊物风

Status: first maintained visual system.

Template/sample package:

- Component library HTML: `D:\nook_vault\82_Skills\nook-skills\skills\nook-html-slides\项目搭建\style-samples\260627-双色独立刊物风-组件库\index.html`
- Editable component PPTX: `D:\nook_vault\82_Skills\nook-skills\skills\nook-html-slides\项目搭建\style-samples\260627-双色独立刊物风-组件库\260627-双色独立刊物风-组件库-v0.3.1-12类组件.pptx`
- Component builder reference: `D:\nook_vault\82_Skills\nook-skills\skills\nook-html-slides\项目搭建\style-samples\260627-双色独立刊物风-组件库\build_12_component_pptx.py`
- Visual dissection note: `D:\nook_vault\82_Skills\nook-skills\skills\nook-html-slides\项目搭建\260627双色独立刊物风视觉拆解.md`
- Component registry: `references/duotone-zine-component-registry.md`

Use this package for decks approved as 双色独立刊物风, independent-zine, duotone zine, old-paper/risograph-like, or any deck explicitly based on the 260627/260628 small samples.

## 3. Generation contract

After the user confirms content and page forms:

1. Do not create a new visual style.
2. Do not ask the user to approve component IDs or slot IDs.
3. Map every page internally to the maintained component registry.
4. Fill template/component slots with locked text.
5. Insert illustrations and screenshots into named image slots with aspect ratio preserved.
6. Keep logo original and small in the master/corner slot.
7. Put IP characters through style transfer before inserting them, unless the user asks to keep them original.
8. Keep construction notes in logs, not on slide canvas.

## 4. Component completeness principle

The template package must enumerate the common slide elements before formal generation:

- giant title / cover
- one-sentence judgment
- big-number page
- text card
- process cards
- timeline
- cycle
- hierarchy / layer diagram
- comparison
- image-text page
- image collage / screenshot evidence page
- logo master slot
- IP / character slot
- generated-asset page

If a confirmed page cannot be expressed with the maintained package, stop and update the template package first. Do not solve it by one-off layout improvisation in the user project.

## 5. Anti-drift rules

A deck is drifting away from the template if any of these appear:

1. Large black bars or labels that are not in the approved template sample.
2. Huge empty containers holding only one or two short lines.
3. Random connector mazes.
4. Text-heavy pages that ignore the “big words, few words, many images” rule.
5. Captions or badges that explain construction status.
6. AI-generated factual screenshots.
7. A PPTX that passes XML checks but looks unlike the approved sample when rendered.

When drift is detected, fix by returning to the template package, not by adding more ad-hoc CSS or DrawingML.
