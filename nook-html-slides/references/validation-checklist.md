# Validation Checklist

Run this before delivery and after substantial revisions.

## Stage

- [ ] Slides use a fixed 16:9 stage.
- [ ] Stage scales as a whole to viewport.
- [ ] No slide content reflows differently on phone or small viewport unless explicitly designed.
- [ ] No slide has scrolling content.

## Text

- [ ] Every visible title is one line.
- [ ] Long titles were rewritten instead of wrapped.
- [ ] Body text is short and readable.
- [ ] No main slide is a pasted article or full-page text.
- [ ] Explanations that do not fit are in notes, comments, appendix, or outline.

## Layout

- [ ] No text overflow.
- [ ] No incoherent overlap.
- [ ] No element is clipped unintentionally.
- [ ] Buttons, labels, chips, and small components have stable dimensions.
- [ ] Visual hierarchy is clear: title, visual, support, source.

## Visual

- [ ] Each slide has one main message.
- [ ] Each theme is expressed by layout and components, not only color.
- [ ] The deck uses consistent fonts, colors, spacing, and shape language.
- [ ] Accent color is controlled and not overused.
- [ ] No generic AI purple-blue gradients, decorative blobs, or meaningless glass cards.

## Assets

- [ ] Logos and product screenshots come from official or user-provided sources where possible.
- [ ] AI images are not used as factual evidence.
- [ ] Screenshots are large enough to read.
- [ ] Asset paths load correctly.
- [ ] Important assets are recorded in `assets/assets_manifest.yml`.

## Facts And Data

- [ ] Time-sensitive claims are checked.
- [ ] Charts have source or data scope.
- [ ] Numbers are not invented for decoration.
- [ ] Uncertain claims are marked or removed.

## Browser Check

When possible:

- [ ] Open `output/deck.html` in a browser.
- [ ] Screenshot desktop viewport.
- [ ] Screenshot one smaller viewport.
- [ ] Check slide navigation.
- [ ] Check local images and fonts load.

If browser automation is unavailable, state that limitation clearly.
