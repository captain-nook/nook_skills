# 样例工程

每个文件夹是一条完整的短片：`scene.py`（画面）、`sfx.py`（音效）、`mix.py`（终混），带素材和时间表。`<S>` 指本 skill 的 `scripts/` 目录。

| 文件夹 | 风格 | 技术档位 | 时长 |
|---|---|---|---|
| `02_draw_direction` | 手绘线稿 | 纯代码 | 20 秒 |
| `05_last_pizza` | 火柴人 | 纯代码 | 16 秒 |
| `06_cat_day` | 扁平动态图形 | 纯代码，代码合成配乐 | 约 20 秒 |
| `07_paper_cake`《蛋糕保卫战》 | 纸片定格 | 千问出图 + Music3 配乐 | 18.5 秒 |
| `08_collage_rain`《撕开下雨天》 | 撕纸拼贴 | 千问出图 + Music3 配乐 | 19 秒 |
| `09_ink_cat`《墨猫与月亮》 | 水墨水彩 | 千问出图 + Music3 配乐 | 19 秒 |
| `tutorial_kit` | 教程桌面舞台 | 共用件，素材不随库提供 | — |

## 看画面

```bash
cd 07_paper_cake
python <S>/run.py render scene.py sheet --every 1.2     # 抽帧拼图
python <S>/run.py render scene.py stills 6.0 9.4        # 指定时刻的静帧
```

## 渲染带声音的成片（07、08、09）

配乐的原曲 `music/*.mp3` 已经在文件夹里。先按故事里的关键时刻对拍，再合成音效和终混，最后渲染：

```bash
# 07_paper_cake
python <S>/run.py music music/music_s401.mp3 --dur 18.5 --end-by 17.9 --anchors 4.0,5.0,8.0,12.0,14.6,16.0 --out-dir .
# 08_collage_rain
python <S>/run.py music music/music_s402.mp3 --dur 19 --end-by 18.4 --anchors 4.4,6.2,7.6,9.4,12.0,15.0 --out-dir .
# 09_ink_cat
python <S>/run.py music music/music_s402.mp3 --dur 19 --end-by 18.4 --anchors 1.35,3.2,6.0,7.2,11.05,15.2 --out-dir .

python sfx.py && python mix.py
python <S>/run.py render scene.py video --out film.mp4 --audio final_mix.wav --warp warp.json
```

## 重新出素材

`jobs_r1.json`（底图与角色母版）、`jobs_r2.json`（从母版编辑出的姿势）、`jobs_text.json`（标题字）是出图任务，提示词照着改就能换故事。需要本地 ComfyUI 和千问 Image 2.1；没有 8 步加速 LoRA 的机器，任务里已经写了 `"lora": null`。`cap.txt` 是 Music3 的配乐提示词。样例里的素材已经压缩过，重新出图可以得到更高质量。

## 许可

素材由千问 Image 2.1 生成，配乐由 MiniMax Music3 生成。两者的使用条款以各自官方仓库的 LICENSE 为准。
