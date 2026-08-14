# H3 prompt contract

Read the installed official skill first. This file is a compact project reminder, not a replacement for the official reference files.

## Core field order

Base modes use exactly:

```text
integrated_multimodal_description: ...

overall_soundscape: ...

non_diegetic_music: ...
```

Ref2VA uses exactly six sections, in this order:

```text
subject_definitions: ...

summary: ...

retention_analysis: ...

detailed_description: ...

overall_soundscape: ...

non_diegetic_music: ...
```

Write the structural text in English. Preserve dialogue exactly in its original language inside `<d>[Chinese] ...</d>`. Use stable speaker IDs, e.g. the heroine `(S1)`. Put dialogue in the timeline, not in `overall_soundscape`.

At every actual vocal event, attach the speaker ID directly to the speaking subject: `<Subject 1> (S1) ... says: <d>[Chinese] ...</d>`. Do not rely on an `(S1)` marker that appeared only in an earlier composition sentence. Describe exact pronunciation and syllable-synchronized mouth articulation at the same event.

## Exact frame-alignment lines

I2VA must begin with:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

FL2VA must begin with the official base-guide form, with real shot indices and the actual duration:

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 4.00-second mark of the target video.
```

For I2VA, establish the supplied first frame before describing forward motion. For FL2VA, describe one continuous path from first frame to last frame without inventing cuts or sudden landmarks.

## Sound and atmosphere

- Keep high-altitude wind, local ambience, and action Foley audible.
- Walking shots explicitly include clear but natural footsteps.
- Keep non-diegetic music `N/A`; BGM is edited separately.
- When the storyboard calls for atmospheric motion, describe the layer, depth, direction, speed, and amplitude precisely.
- For a calm celestial cloud sea, keep its height and outer silhouette stable. Describe fine internal wisps or texture drifting laterally along the horizon at low speed and low amplitude. Keep palace visibility nearly constant. Do not use `surge`, `roll`, `wave motion`, `broad coherent waves/layers`, `billow toward camera`, or other high-energy wave language unless the storyboard explicitly calls for a disaster-scale event.
- Keep moving cloud layers in the middle and far distance when the storyboard calls for distant clouds; do not let them advance toward the lens or expand into a foreground obstruction.
- For I2VA and FL2VA, the supplied first frame must already contain every subject required at the opening composition. Do not ask a required subject to enter from outside the frame unless that entrance is the explicit narrative action.
- For Ref2VA, specify the subject's opening position, framing, and visible proportion. When the subject is required at the opening, state that the subject is already fully composed in the first frame. Do not use off-screen or side-entry language unless that entrance is the shot's explicit narrative action.
