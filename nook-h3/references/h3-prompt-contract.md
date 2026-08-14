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
- When the storyboard calls for atmospheric motion, describe moving mist, cloud, fog, dust, rain, light, or other layers with depth. State what the motion must not obscure, such as faces, hands, props, or foot placement.
