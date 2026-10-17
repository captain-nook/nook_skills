"""去 AI 味的表面表达检查：扫方案里所有文字字段，命中就报错，处理办法一律是直接删掉或改成直接陈述（删除测试：删了主句仍成立就删）。
规则来源：nook-alive 的形态算子和高危套话清单（本库内的去 AI 味子 skill）、nook 自己的禁用表达。
只能查到表面表达；"没有锚点""节奏太顺"这类问题查不到，要靠 SKILL 里的人工自检清单。"""
import re

# (规则名, 正则, 说明)
RULES = [
    ("对举结构", r"不是[^。；]{1,16}而是", "删掉“不是……”半句，只留具体事实"),
    ("虚假递进", r"不仅[^。；]{1,16}(而且|更是|还)|与其说[^。；]{1,16}不如说", "删掉凑数的递进，直接说事"),
    ("虚假过渡", r"值得注意的是|值得一提的是|不可否认|此外|不仅如此|换句话说|这意味着|综上所述|总而言之|总的来说", "直接删掉这个词"),
    ("空心起首", r"说白了|坦率地讲|不难看出|不难发现|本质上|某种意义上", "直接删掉"),
    ("宏大开场", r"随着[^，。]{0,10}的发展|在当今时代|当今社会|信息爆炸", "删掉，开门见山"),
    ("黑话大词", r"赋能|闭环|深度融合|全方位|颗粒度|底层逻辑|抓手|打通", "翻译成大白话，翻译后什么都不剩就整句删"),
    ("程度副词", r"非常|极其|极大地|进一步|深入地|十分", "删掉，信息量不减"),
    ("两头讨好", r"一方面[^。]{0,20}另一方面|双刃剑", "删掉伪中立，保留立场"),
    ("口号式标题", r"一图看懂|一文读懂|一张图读懂|干货满满|超全|必看|建议收藏|记住它|只需三步", "删掉口号，直接写内容"),
    ("号召式结尾", r"让我们|一起携手|拥抱[^，。]{0,6}(未来|时代|变化)|未来可期|拭目以待", "删掉"),
    ("助手腔", r"希望这对你有帮助|如果你需要|当然可以|欢迎随时", "删掉"),
    ("带走拿走", r"带走|拿走", "按本库规矩换成“获得”“得到”，或直接删"),
    ("序数小标题", r"第[一二三四五六七八九十][，、：:点步个]", "去掉序数词，靠页序和结构表达先后"),
    ("提示性冒号", r"(在于|是|有)[：:]", "冒号改逗号，或直接说事"),
    ("破折号", r"——|—", "改成逗号或拆成短句"),
]
COMPILED = [(n, re.compile(p), h) for n, p, h in RULES]
SKIP_KEYS = {"screenshot", "images", "sticker", "stickers", "pose", "face", "step_no", "number", "highlight", "value", "red_box", "arrow", "type"}


def _walk(obj, where, out, any_text=False):
    if isinstance(obj, str):
        if any_text or re.search(r"[一-鿿]", obj):
            out.append((where, obj))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk(v, f"{where}[{i + 1}]", out, any_text)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS:
                continue
            _walk(v, f"{where}.{k}" if where else k, out, any_text)


def lint_plan(plan):
    """返回错误列表。"""
    errs = []
    for i, pg in enumerate(plan.get("pages", []), 1):
        texts = []
        _walk(pg.get("fields", {}), "", texts)
        for where, s in texts:
            for name, rx, hint in COMPILED:
                m = rx.search(s)
                if m:
                    errs.append(f"第 {i} 页（{pg.get('type')}），字段 {where}：命中「{m.group(0)}」（{name}），{hint}")
    return errs


def lint_text(text):
    """检查一段文字（标题、正文）。返回 [(行号, 命中词, 规则名, 办法)]。"""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for name, rx, hint in COMPILED:
            for m in rx.finditer(line):
                out.append((n, m.group(0), name, hint))
    return out


# 提醒级规则：不拦截，但要让人看一眼，确认真的有依据
WARN_RULES = [
    ("夸大承诺", r"一键|秒出|秒懂|秒会|零门槛|零基础|100%|百分百|绝对|史上|最强|最全|保证|必火|必爆|全自动|躺赚|无脑", "这类词暗示结果没有门槛或没有例外，确认素材里有依据；没有就换成具体做法"),
    ("绝对化", r"所有人|每个人|永远|从不|一定会|肯定会", "绝对化的说法容易被反驳，改成有范围的表述"),
]
WARN_COMPILED = [(n, re.compile(p), h) for n, p, h in WARN_RULES]


def warn_plan(plan):
    out = []
    for i, pg in enumerate(plan.get("pages", []), 1):
        texts = []
        _walk(pg.get("fields", {}), "", texts)
        for where, t in texts:
            for name, rx, hint in WARN_COMPILED:
                m = rx.search(t)
                if m:
                    out.append(f"第 {i} 页（{pg.get('type')}），字段 {where}：「{m.group(0)}」（{name}），{hint}")
    return out


def warn_text(text):
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for name, rx, hint in WARN_COMPILED:
            for m in rx.finditer(line):
                out.append(f"第 {n} 行：「{m.group(0)}」（{name}），{hint}")
    return out
