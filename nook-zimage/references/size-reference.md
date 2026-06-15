# Size Reference

Recommended sizes:

| Size | Ratio | Use |
|---|---:|---|
| `1024x1024` | 1:1 | quick draft, square asset |
| `1080x1440` | 3:4 | Xiaohongshu / poster background |
| `720x1280` | 9:16 | vertical draft |
| `1440x1080` | 4:3 | horizontal card material |
| `1280x720` | 16:9 | web / video background |

Keep prompts explicit:

```text
no text, no logo, no watermark, background material only
```

For `nook-poster`, prefer `1080x1440` when generating full-card background material.

Implementation note:

ModelScope Z-Image currently expects `size` as a `WxH` string such as `1280x720`. Sending only `width` and `height` may fall back to the model default size.
