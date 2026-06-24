# 样本标题与模式标注

These are calibration examples for high-density AI-media title patterns. Treat them as style examples, not as facts for new work.

## High-Density AI News Samples

- GPT-5正秘密训练!DeepMind联创爆料,这模型比GPT-4大100倍
  - Pattern: entity + leak/claim + number + comparison
  - Notes: requires clear source boundary because it is an爆料/claim.

- GPT-4.5 Turbo提前泄露?Altman亲自暗示新模型要来,传言本周四上线
  - Pattern: product + uncertainty + person + timing
  - Notes: question mark and `传言` preserve uncertainty.

- OpenAI把微软电网搞崩!GPT-6被曝25年发布,训练刷爆10万张H100
  - Pattern: company + dramatic action + version + year + GPU count
  - Notes: very high click strength; high fact-boundary burden.

- GPT-5恐被叫停!马斯克、图灵奖得主等千名专家呼吁暂停超强AI研发,至少6个月
  - Pattern: model + risk + named people/group + number + action demand
  - Notes: depends on whether `恐被叫停` is justified.

- 炸翻AI和生化环材圈!GPT-4学会自己搞科研,手把手教人类做实验
  - Pattern: affected community + model ability + human impact
  - Notes: must avoid overclaiming if only a narrow demo.

- OpenAI逆天发布ChatGPT API!100万个单词才18元,价格打骨折
  - Pattern: company + release + price number + cost consequence
  - Notes: numbers carry the title.

- Nature|AI检测器又活了?成功率高达98%,吊打OpenAI
  - Pattern: source badge + problem revival + number + comparison
  - Notes: `吊打` requires direct comparison.

- GPT-4「变懒」bug被修复,价格暴降80%!OpenAI连更5款新模型,性能狂飙
  - Pattern: problem fixed + number + company update + performance result
  - Notes: dense but readable because every segment has a concrete fact.

- Claude自己写出Claude!2小时干完两月活,人类在工位上多余了?
  - Pattern: model self-reference + time contrast + human-impact joke
  - Notes: high impact; keep question mark if claim is rhetorical.

- Claude 3再次登顶!化学专业一骑绝尘,全面碾压GPT-4
  - Pattern: model + ranking + domain + comparison
  - Notes: ranking and benchmark must be real.

- 90分钟攻破20年Linux漏洞!Claude 5.0惊现内测,Anthropic都害怕
  - Pattern: time + old problem + model version + organization reaction
  - Notes: organization emotion must be source-supported or softened.

- 前端圈炸了!React大神用Claude造出15KB引擎,排版速度狂飙1200倍,1800万人围观
  - Pattern: community + person + model/tool + number stack + social proof
  - Notes: strong when all numbers are in source.

## Screenshot-Inspired Candidate Shapes

- 刚刚，豆包2.1全量上线！Coding/Agent跨过生产级质变点
- 豆包2.1杀进生产级AI战场！1.96元跑Agent，硬刚Claude Opus
- 字节豆包2.1上线！Coding追平Claude，NL2Repo领先GPT-5.5
- 1.96元跑生产级Agent！豆包2.1 Pro上线，开发者工作流变天
- 500+ Agent协同作业！豆包2.1 Pro千次工具调用，一座3D城市建成

## What To Learn

- The title does not hide the subject. The model/company usually appears immediately.
- A number often carries the credibility.
- The title needs a second beat after punctuation: comparison, consequence, benchmark, or affected group.
- The strongest versions combine a concrete technical fact with a human or industry consequence.
