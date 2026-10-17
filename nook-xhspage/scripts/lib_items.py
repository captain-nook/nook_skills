"""素材库条目：id, 中文名, 标签, 提示词。运行 python lib_items.py 写出 jobs 到 assets/library/_jobs/<分类>.json"""
import json
import pathlib

STYLE = ("A flat marker-doodle sticker icon with a thick white die-cut border around the shape, clean deep navy blue outline, "
         "solid fills in warm orange, sunny yellow and cream with small light-blue accents, simple friendly cartoon shapes, "
         "no letters or words anywhere, centered with generous empty margin around it. ")
CHAR = ("A simple round-headed doodle character with dot eyes, cream skin tone, small body, black ink outline, thick white die-cut sticker border, "
        "warm orange and light-blue accents, no letters or words anywhere, centered with generous empty margin. ")

OBJ = [
    ("monitor", "显示器", ["电脑", "屏幕", "工作"], "A desktop computer monitor on a small stand, screen showing three short orange lines and a small yellow sun shape."),
    ("keyboard", "键盘", ["电脑", "打字", "输入"], "A cream computer keyboard seen from a slight angle with rounded keys, a few orange keys."),
    ("mouse", "鼠标", ["电脑", "点击"], "A small cream computer mouse with an orange scroll wheel and a short cable."),
    ("phone", "手机", ["手机", "移动", "小红书"], "A smartphone with a navy frame and a screen showing a small grid of colored squares."),
    ("tablet", "平板", ["平板", "阅读", "屏幕"], "A tablet with a navy frame and a screen showing two orange text lines and a yellow image block."),
    ("headphones", "耳机", ["音频", "听", "播客"], "A pair of over-ear headphones, navy band, orange ear cups."),
    ("notebook", "本子", ["笔记", "记录", "学习"], "A closed spiral notebook with an orange cover, a navy elastic band, and a small bookmark ribbon."),
    ("open_notebook", "翻开的本子", ["笔记", "记录", "计划"], "An open spiral notebook with ruled lines and a few doodle bullet points drawn as small dots and short lines."),
    ("pen", "钢笔", ["写作", "笔", "签名"], "A fountain pen with a navy body and an orange nib, slightly tilted."),
    ("pencil", "铅笔", ["写作", "笔", "画"], "A yellow pencil with a pink eraser and a sharpened tip, tilted."),
    ("marker_pen", "马克笔", ["标注", "强调", "笔"], "An orange marker pen with the cap beside it."),
    ("paper_clip", "回形针", ["文件", "附件", "整理"], "A single orange metal paper clip shaped as a double loop wire."),
    ("document", "文档", ["文件", "文章", "资料"], "A sheet of paper with a folded corner and four short text lines drawn as thin bars, with a small orange check mark."),
    ("file_stack", "文件堆", ["资料", "整理", "项目"], "A neat stack of three papers with a clip on top."),
    ("calendar", "日历", ["日期", "计划", "时间"], "A wall calendar page with two navy rings on top and a grid of small squares, one square circled in orange."),
    ("clock", "时钟", ["时间", "效率", "省时"], "A round wall clock with simple hands and small tick marks, orange rim."),
    ("alarm_clock", "闹钟", ["时间", "提醒", "截止"], "A classic alarm clock with two bells on top and little legs, orange body."),
    ("hourglass", "沙漏", ["时间", "等待", "耐心"], "An hourglass with yellow sand and a navy frame."),
    ("book", "书", ["学习", "知识", "阅读"], "A closed hardcover book standing slightly tilted, orange cover, cream page edges."),
    ("open_book", "翻开的书", ["学习", "阅读", "知识"], "An open book with two pages showing short doodle lines and a small light bulb shape."),
    ("books_stack", "书堆", ["学习", "资料", "知识"], "A stack of three books in orange, navy and yellow."),
    ("bookmark", "书签", ["收藏", "标记", "保存"], "A tall orange bookmark ribbon with a small star on it."),
    ("scissors", "剪刀", ["剪辑", "删减", "裁"], "A pair of scissors with orange handles and navy blades."),
    ("tape", "胶带", ["贴", "整理", "手账"], "A roll of translucent yellow washi tape with a torn end."),
    ("stapler", "订书机", ["办公", "文件"], "A small stapler with a navy base and an orange top."),
    ("ruler", "尺子", ["测量", "标准", "设计"], "A yellow ruler with navy tick marks along one edge."),
    ("calculator", "计算器", ["数字", "成本", "计算"], "A small calculator with an orange display and a grid of round buttons."),
    ("coffee", "咖啡", ["休息", "日常", "加班"], "A cream coffee cup with a saucer and three small curly steam lines."),
    ("battery", "电池", ["能量", "精力", "充电"], "A battery icon with three orange charge bars and a small lightning bolt."),
    ("plug", "插头", ["连接", "接入", "电"], "A two-prong electrical plug with a curly orange cable."),
    ("cloud_upload", "云端", ["云", "存储", "同步"], "A fluffy cloud with an upward arrow shape inside it, light-blue and cream."),
    ("database", "数据库", ["数据", "存储", "后台"], "A database cylinder drawn as three stacked discs, navy and light blue with orange edge."),
    ("server", "服务器", ["服务器", "后台", "部署"], "A small server rack with three stacked units and tiny round indicator lights."),
    ("chip", "芯片", ["算力", "硬件", "模型"], "A square computer chip with pins on all four sides and a small orange square in the center."),
    ("robot", "机器人", ["AI", "助手", "智能体"], "A cute friendly robot head with a square face, two round eyes, a small antenna with an orange ball and rounded ears."),
    ("magic_wand", "魔法棒", ["魔法", "自动", "一键"], "A magic wand with a navy stick and a yellow star on the tip, small sparkles."),
    ("key", "钥匙", ["权限", "关键", "解锁"], "A golden key with a round head and an orange ribbon."),
    ("lock", "锁", ["安全", "隐私", "保密"], "A closed padlock with a navy shackle and an orange body."),
    ("shield", "盾牌", ["安全", "保护", "防护"], "A shield with a check mark in the center, navy and light blue."),
    ("trophy", "奖杯", ["成果", "冠军", "成就"], "A golden trophy cup with two handles and a small star."),
    ("medal", "奖牌", ["成果", "第一", "认可"], "A round medal with an orange ribbon and a star in the center."),
    ("gift", "礼物", ["福利", "赠送", "惊喜"], "A gift box with an orange ribbon and bow, yellow box."),
    ("flag", "旗子", ["目标", "里程碑", "起点"], "A small orange flag on a navy pole planted on a tiny mound."),
    ("pushpin", "图钉", ["标记", "重点", "固定"], "A round orange push pin."),
    ("target", "靶心", ["目标", "精准", "定位"], "A bullseye target with concentric orange and cream rings and a navy arrow stuck in the center."),
    ("puzzle", "拼图", ["组合", "方案", "拼接"], "Two interlocking puzzle pieces, one orange and one light blue."),
    ("megaphone", "喇叭", ["通知", "宣布", "传播"], "A cone-shaped megaphone with an orange body and a few sound lines."),
    ("bell", "铃铛", ["提醒", "通知", "订阅"], "A small bell with an orange body and a little clapper."),
    ("envelope", "信封", ["邮件", "私信", "联系"], "A cream envelope with a navy flap and a small orange heart seal."),
    ("clipboard", "清单板", ["清单", "检查", "任务"], "A clipboard with a sheet showing three rows of small check boxes, two checked in orange."),
    ("bar_chart", "柱状图", ["数据", "增长", "图表"], "A small bar chart with four bars of rising height in orange, yellow and light blue, with an axis."),
    ("line_chart", "折线图", ["数据", "趋势", "图表"], "A line chart on a small grid with an orange rising zigzag line and round dots."),
    ("pie_chart", "饼图", ["数据", "占比", "图表"], "A round pie chart with one wedge pulled out, orange, yellow and light blue slices."),
    ("microphone", "麦克风", ["声音", "口播", "采访"], "A standing microphone with a navy stand and an orange mesh head."),
    ("play_button", "播放键", ["视频", "播放", "演示"], "A rounded rectangle video player icon with an orange triangle in the middle."),
    ("price_tag", "标签", ["价格", "分类", "标注"], "A hanging price tag with a string and a round hole, orange."),
    ("trash", "垃圾桶", ["删除", "清理", "丢弃"], "A small trash can with a lid and a crumpled paper beside it."),
    ("box", "纸箱", ["打包", "交付", "整理"], "A cardboard box with the flaps open and a tape strip."),
    ("umbrella", "雨伞", ["保护", "兜底", "风险"], "An open umbrella in orange and navy with a handle."),
    ("anchor", "船锚", ["稳定", "航海", "船长"], "A navy ship anchor with a rope loop and a small orange ring."),
    ("sailboat", "帆船", ["航海", "船长", "出发"], "A small sailboat with a light-blue and navy sail, white hull and an orange flag, on a short wave line."),
    ("compass", "罗盘", ["方向", "导航", "船长"], "A round compass with a navy rim and an orange needle."),
    ("map", "地图", ["路线", "规划", "航线"], "A folded treasure map with a dashed route line and an orange cross mark."),
    ("hand_point", "手指", ["指向", "重点", "看这里"], "A cartoon hand with the index finger pointing to the right, cream skin tone, navy outline."),
    ("thumbs_up", "点赞", ["点赞", "认可", "好用"], "A cartoon hand giving a thumbs up, cream skin tone, navy outline, small orange sparkle."),
    ("hand_wave", "挥手", ["打招呼", "再见", "欢迎"], "A cartoon open hand waving with small motion lines, cream skin tone, navy outline."),
]
CHR = [
    ("char_surprised", "小人·惊讶", ["惊讶", "没想到", "反常识"], "The character sits at a small desk with wide round eyes and an open mouth, both hands raised near its cheeks, three short burst lines around its head."),
    ("char_tired", "小人·疲惫", ["累", "加班", "重复劳动"], "The character slumps over a small desk with half-closed eyes, a tiny sweat drop and a stack of papers beside it."),
    ("char_celebrate", "小人·庆祝", ["庆祝", "完成", "成功"], "The character jumps with both arms up, small confetti pieces and stars around it."),
    ("char_point", "小人·指向", ["指向", "看这里", "讲解"], "The character stands and points to the right with one arm, a small confident smile."),
    ("char_sign", "小人·举牌", ["展示", "宣布", "提示"], "The character holds up a blank rectangular sign board above its head with both arms."),
    ("char_laptop", "小人·敲电脑", ["电脑", "写作", "工作"], "The character sits in front of an open laptop and types with focused eyes."),
    ("char_sleep", "小人·睡觉", ["休息", "自动", "放手"], "The character sleeps on a small desk with closed eyes under a small blanket, a few small light-blue Z-shaped marks above."),
    ("char_heart", "小人·比心", ["感谢", "喜欢", "关注"], "The character makes a heart shape above its head with both arms, a small orange heart above."),
    ("char_walk", "小人·走路", ["出发", "行动", "开始"], "The character walks to the right with a small backpack, one foot forward."),
    ("char_box", "小人·搬箱子", ["整理", "搬运", "交付"], "The character carries a large cardboard box in both arms, slightly leaning back."),
    ("char_idea", "小人·有想法", ["想法", "灵感", "点子"], "The character raises one finger with a bright smile, a glowing light bulb floating above its head."),
    ("char_rocket", "小人·骑火箭", ["起飞", "增长", "加速"], "The character sits on a small rocket flying diagonally upward, arms raised, orange flame behind."),
    ("char_search", "小人·找东西", ["搜索", "查找", "调研"], "The character holds a big magnifying glass up to one eye, leaning forward."),
    ("char_read", "小人·看书", ["学习", "阅读", "输入"], "The character sits and reads an open book held in both hands."),
    ("char_coffee", "小人·喝咖啡", ["休息", "日常", "轻松"], "The character holds a cup with steam rising and a relaxed smile."),
    ("char_cheer", "小人·加油", ["鼓励", "坚持", "加油"], "The character raises a small flag with both hands and a determined smile."),
    ("char_collapse", "小人·崩溃", ["崩溃", "痛点", "吐槽"], "The character holds its head with both hands, spiral eyes, a small dark cloud above, tears as two small drops."),
    ("char_thumbs", "小人·点赞", ["认可", "好用", "推荐"], "The character gives a thumbs up with a wide smile and a small sparkle."),
    ("char_stack", "小人·被文件淹没", ["资料多", "信息过载", "整理"], "The character is half hidden behind a tall wobbly stack of papers, eyes peeking over the top."),
    ("char_robot_pair", "小人·和机器人", ["AI", "协作", "助手"], "The character stands next to a small friendly square-faced robot, both waving."),
]
SYM = [
    ("burst", "爆炸线", ["强调", "惊喜", "重点"], "A starburst made of short radiating orange and yellow lines around an empty center."),
    ("question", "问号", ["疑问", "为什么", "思考"], "A large bold navy question mark with an orange dot and two small sparkle marks."),
    ("exclaim", "感叹号", ["强调", "注意", "重点"], "A large bold orange exclamation mark with two small motion lines on each side."),
    ("bubble_talk", "对话气泡", ["说", "回复", "沟通"], "A rounded speech bubble with three small dots inside, cream with navy outline."),
    ("bubble_two", "双气泡", ["对话", "聊天", "沟通"], "Two overlapping speech bubbles, one navy and one orange, each with simple short lines inside."),
    ("bubble_think", "思考云", ["思考", "想", "琢磨"], "A cloud-shaped thought bubble with two small circles leading to it."),
    ("heart", "爱心", ["喜欢", "点赞", "关注"], "A plump orange heart with a small white highlight."),
    ("star", "星星", ["好评", "重点", "收藏"], "A fat five-point yellow star with a navy outline and a small sparkle."),
    ("cross_badge", "叉章", ["错误", "不要", "避坑"], "A round red badge with a bold white cross in the middle and a navy outline."),
    ("sweat", "汗滴", ["紧张", "压力", "尴尬"], "Three light-blue sweat drops of different sizes with small motion marks."),
    ("lightning", "闪电", ["快", "速度", "能量"], "A bold yellow lightning bolt with an orange outline and two small sparks."),
    ("sparkles_big", "闪光群", ["惊艳", "好看", "完成"], "A cluster of one large and three small four-pointed sparkle stars in yellow and orange."),
    ("arrow_cycle", "循环箭头", ["循环", "重复", "迭代"], "Two curved arrows chasing each other to form a circle, orange and navy."),
    ("plus_badge", "加号章", ["添加", "新增", "更多"], "A round orange badge with a bold white plus sign."),
    ("music", "音符", ["轻松", "声音", "背景"], "Two connected eighth notes in navy with a small orange accent."),
]
NAT = [
    ("twig", "树枝", ["自然", "装饰", "清新"], "A small twig with six leaves in light blue and teal, simple line art."),
    ("flower", "小花", ["自然", "装饰", "可爱"], "A single simple flower with five orange petals, a yellow center and a short green stem with one leaf."),
    ("cloud", "云朵", ["天气", "装饰", "云"], "A fluffy cream cloud with a light-blue shadow and a navy outline."),
    ("sun", "太阳", ["天气", "好心情", "早安"], "A round yellow sun with short orange rays and a small smile."),
    ("moon", "月亮", ["夜晚", "晚安", "熬夜"], "A crescent moon in yellow with two small stars beside it."),
    ("cactus", "仙人掌", ["盆栽", "桌面", "装饰"], "A small cactus in an orange pot with a tiny yellow flower."),
    ("plant_pot", "绿植盆栽", ["盆栽", "桌面", "生长"], "A potted sprout with two leaves in a cream pot with an orange stripe."),
    ("tree", "小树", ["自然", "成长", "装饰"], "A round-crowned tree with a brown trunk and a few yellow fruits."),
    ("mountain", "山", ["风景", "目标", "攀登"], "Two simple mountains with a small orange flag on the higher peak and a little cloud."),
    ("wave", "海浪", ["航海", "船长", "海"], "A short curling sea wave in light blue and navy with white foam dots."),
    ("rainbow", "彩虹", ["好心情", "惊喜", "装饰"], "A small arch rainbow in orange, yellow and light blue ending in two cream clouds."),
    ("leaf_big", "大叶子", ["自然", "装饰", "清新"], "One large teal leaf with a center vein and a short stem."),
]
TOOL = [
    ("terminal", "终端窗口", ["终端", "命令行", "代码"], "A small terminal window with a navy title bar, three tiny round buttons, a dark body with a short orange prompt symbol and two light lines."),
    ("code_block", "代码块", ["代码", "脚本", "编程"], "A rounded rectangle code panel with several short colored bars in orange, light blue and yellow standing for lines of code, and two angle bracket shapes."),
    ("browser", "浏览器窗口", ["网页", "浏览器", "网站"], "A browser window with a navy top bar, a small round address field, and a body with a yellow image block and two text bars."),
    ("chat_window", "聊天窗口", ["对话", "AI", "聊天"], "A chat window showing one orange bubble on the right and one cream bubble on the left, a small input bar below."),
    ("nodes", "节点网络", ["工作流", "连接", "系统"], "Five round nodes in orange, yellow and light blue connected by navy lines."),
    ("workflow", "流程节点", ["流程", "步骤", "自动化"], "Three rounded boxes connected left to right by short navy arrows, the last box orange."),
    ("doc_magic", "文档加魔法", ["生成", "自动写作", "AI"], "A sheet of paper with short lines and three sparkle stars floating over one corner."),
    ("cursor", "光标", ["点击", "操作", "鼠标"], "A bold navy arrow cursor with a white border and a small orange click burst."),
    ("toggle", "开关", ["开关", "设置", "启用"], "A rounded toggle switch turned on, orange track with a white knob on the right."),
    ("download", "下载", ["下载", "获取", "保存"], "A downward arrow pointing into an open tray, orange arrow, navy tray."),
    ("search_bar", "搜索框", ["搜索", "查找", "检索"], "A rounded search bar with a magnifier icon on the left and a blinking line, cream with navy outline."),
    ("gear_set", "齿轮组", ["设置", "系统", "自动化"], "Two meshing gears, one navy and one orange."),
    ("folder_tree", "文件夹树", ["目录", "整理", "知识库"], "A tiny folder tree: one top folder connected by lines to three small folders below, orange and yellow."),
    ("sticky_wall", "便签墙", ["想法", "整理", "头脑风暴"], "Four small sticky notes in yellow, orange, light blue and cream, slightly rotated and overlapping."),
    ("checklist", "待办清单", ["待办", "计划", "任务"], "A paper list with four rows, each with a small box and a short line; three boxes ticked in orange."),
    ("skill_card", "技能卡", ["skill", "技能", "能力"], "A rounded card with a bold lightning bolt in a circle on top and two short lines below, orange and cream."),
]

CATS = {"object": OBJ, "character": CHR, "symbol": SYM, "nature": NAT, "tool": TOOL}

if __name__ == "__main__":
    import paths
    root = paths.LIB
    (root / "_jobs").mkdir(parents=True, exist_ok=True)
    n = 0
    for cat, items in CATS.items():
        jobs = []
        for iid, cn, tags, pr in items:
            prefix = CHAR if cat == "character" else STYLE
            jobs.append({"name": iid, "prompt": prefix + pr, "w": 768, "h": 768, "seed": 1000 + n, "alpha": True})
            n += 1
        (root / "_jobs" / f"{cat}.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
        (root / cat).mkdir(exist_ok=True)
    print("jobs", n)
