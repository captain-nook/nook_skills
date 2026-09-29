# 配乐与对拍

## 1 前置

生成音乐前：读 MiniMax-Music3 官方仓库的说明，过一遍交互门禁（一行 brief 给用户确认，用户已授权一路做到底时除外），caption 交给官方 `music-caption-rewriter` 生成，不手写。纯音乐的 lyrics 用 `[Intro]
[Instrumental]
[Instrumental]
[Outro]`。

## 2 流程

1. 上限设为片长加 30% 以上（21 秒片子给 30 秒），生成两条不同种子：`python <S>/run.py comfy music --caption cap.txt --max 30 --seeds 301,302 --out music`（`<S>` 指本 skill 的 scripts 目录）。长任务逐条提交，不连排。
2. 测每条的真实节拍、调性、每秒响度，对照剧情的情绪曲线挑一条（高潮段最该响的地方要响）。
3. 截取与对拍：`python <S>/run.py music music/music_s301.mp3 --dur 21 --end-by 20.4 --anchors <镜头切换与关键动作的故事时间>`。输出 `music_final.wav`（半小节处淡出原曲并叠同调收尾和弦）、`warp.json`（关键时间点吸附最近拍点，单点挪动不超过半拍）、`beats.json`。
4. 音效：场景的音效脚本用 `audio.Mixer(dur, to_video)`，时间点写故事时间，经 warp 换算，和画面同步。
5. 终混：`audio.final_mix(music, sfx, gain_curve)`，gain_curve 给情绪起伏不够的段落做音量自动化（危机段压到 0.4、高潮前推回）。
6. 渲染时带上 `--warp warp.json --audio final_mix.wav`。

## 3 实测结论（260927，3 条纯音乐同一种子）

文件长度严格等于 max_duration，但音乐在上限处硬切（最后 0.3 秒仍在峰值 −7 到 −15 dB）。caption 写"21 秒完整收尾"无效，上限 30 秒时照样铺满 30 秒。caption 写 120 BPM 不遵守，实测 80–96。所以让画面对音乐，不要反过来。

## 4 不用 MiniMax 的做法

纯代码风格（火柴人、扁平动态图形）可以直接用 `audio` 模块合成配乐（鼓、贝斯、拨弦），时间轴用 `mg.Beat` 按拍写，画面和音乐天然对拍，不需要上面的截取与映射。

MiniMax 官方有提示词 skill：`npx skills add MiniMax-AI/MiniMax-Music3 --skill music-caption-rewriter`。MiniMax-Music3 的使用条款以其官方仓库的 LICENSE 为准。
