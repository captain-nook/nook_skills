from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "duotone-zine" / "component-library-source.py"
OUT = ROOT / "global-component-skeleton-v1.json"

COMPONENT_IDS = {
    "C01": "zine.hero-title",
    "C02": "zine.statement",
    "C03": "zine.big-number",
    "C04": "zine.process-cards",
    "C05": "zine.timeline",
    "C06": "zine.cycle",
    "C07": "zine.hierarchy",
    "C08": "zine.comparison",
    "C09": "zine.image-text",
    "C10": "zine.image-collage",
    "C11": "zine.brand-master",
    "C12": "zine.generated-asset",
    "C13": "zine.card-group",
}

COLOR_TOKENS = {
    "F3ECD8": "bg",
    "F8F0DD": "panel",
    "171713": "ink",
    "5E5A51": "muted",
    "3153B8": "a",
    "243D86": "dark",
    "E76186": "b",
    "E8B13F": "c",
    "FFFFFF": "white",
}

FONT_TOKENS = {
    "思源宋体 CN Heavy": "title_font",
    "霞鹜文楷": "body_font",
    "Bodoni 72": "num_font",
    "Consolas": "mono_font",
}


class SlideRecorder:
    def __init__(self):
        self.ops: list[dict] = []
        self.header: dict | None = None
        self.note: str | None = None


class SkeletonExtractor:
    def __init__(self):
        self.current: SlideRecorder | None = None

    def token_color(self, value):
        return COLOR_TOKENS.get(str(value).upper(), value)

    def token_font(self, value):
        return FONT_TOKENS.get(str(value), value)

    def align_name(self, value):
        if value is None:
            return None
        raw = str(value).split(".")[-1].lower()
        return {"center": "center", "right": "right", "left": "left"}.get(raw, raw)

    def op(self, name, **payload):
        cleaned = {"op": name}
        for key, value in payload.items():
            if value is not None:
                cleaned[key] = value
        self.current.ops.append(cleaned)

    def blank_slide(self):
        self.current = SlideRecorder()
        return self.current

    def page_header(self, slide, code, title, subtitle, page):
        ccode = code.split("/", 1)[0].strip()
        slide.header = {
            "code": ccode,
            "label": code,
            "name": title,
            "subtitle": subtitle,
            "folio": page,
            "component": COMPONENT_IDS[ccode],
        }
        self.op("page_header", code=code, title=title, subtitle=subtitle, folio=page)

    def text_box(
        self,
        slide,
        text,
        x,
        y,
        w,
        h,
        font=None,
        size=18,
        color=None,
        bold=False,
        align=None,
        valign=None,
        line_spacing=None,
    ):
        self.op(
            "text_box",
            value=text,
            x=x,
            y=y,
            w=w,
            h=h,
            font=self.token_font(font),
            size=size,
            color=self.token_color(color),
            bold=bool(bold),
            align=self.align_name(align),
            line_spacing=line_spacing,
        )

    def bullet_text(self, slide, lines, x, y, w, h, size=15, color=None):
        self.op("bullet_text", lines=lines, x=x, y=y, w=w, h=h, size=size, color=self.token_color(color))

    def shadow_rect(self, slide, x, y, w, h, color=None, dx=0.06, dy=0.06):
        self.op("shadow_rect", x=x, y=y, w=w, h=h, color=self.token_color(color), dx=dx, dy=dy)

    def rect(self, slide, x, y, w, h, fill_color=None, line_color=None, line_w=2.0, radius=False, dash=None):
        self.op(
            "rect",
            x=x,
            y=y,
            w=w,
            h=h,
            fill=self.token_color(fill_color),
            line=self.token_color(line_color),
            lw=line_w,
            radius=bool(radius),
            dash=bool(dash),
        )

    def line(self, slide, x1, y1, x2, y2, color=None, width=2.0, dash=None):
        self.op("line", x1=x1, y1=y1, x2=x2, y2=y2, color=self.token_color(color), width=width, dash=bool(dash))

    def image_slot(self, slide, x, y, w, h, code, caption="", accent=None, fill_color=None):
        self.op(
            "image_slot",
            x=x,
            y=y,
            w=w,
            h=h,
            code=code,
            caption=caption,
            accent=self.token_color(accent),
            fill=self.token_color(fill_color),
        )

    def big_num(self, slide, txt, x, y, size=66):
        self.op("big_num", value=txt, x=x, y=y, size=size)

    def tiny_rule(self, slide, x, y, w, color=None):
        self.op("tiny_rule", x=x, y=y, w=w, color=self.token_color(color))

    def label(self, slide, txt, x, y, w=1.7):
        self.op("label", value=txt, x=x, y=y, w=w)

    def component_note(self, slide, text):
        slide.note = text
        self.op("component_note", value=text)


def load_duotone_namespace():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8-sig"), filename=str(SOURCE))
    allowed_nodes = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Assign)):
            allowed_nodes.append(node)
    module = ast.Module(body=allowed_nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace: dict = {"__file__": str(SOURCE)}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace


def main():
    namespace = load_duotone_namespace()
    extractor = SkeletonExtractor()
    for name in [
        "blank_slide",
        "page_header",
        "text_box",
        "bullet_text",
        "shadow_rect",
        "rect",
        "line",
        "image_slot",
        "big_num",
        "tiny_rule",
        "label",
        "component_note",
    ]:
        namespace[name] = getattr(extractor, name)

    components = []
    for fn in namespace["slides"]:
        fn()
        rec = extractor.current
        if not rec or not rec.header:
            raise RuntimeError(f"failed to extract header from {fn.__name__}")
        header = rec.header
        components.append(
            {
                "code": header["code"],
                "source_function": fn.__name__,
                "name": header["name"],
                "component": header["component"],
                "note": rec.note or "",
                "ops": rec.ops,
            }
        )

    data = {
        "schema_version": 1,
        "name": "global-component-skeleton-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_mode": "extracted_from_duotone_component_library_source",
        "page_size": {"width_in": 16, "height_in": 9},
        "components": components,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote={OUT}")
    print(f"components={len(components)}")


if __name__ == "__main__":
    main()
