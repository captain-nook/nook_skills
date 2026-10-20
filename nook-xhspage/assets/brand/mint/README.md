# 通用款：薄荷

任何人拿到这个 skill 都能直接用的品牌套装：一个虚拟 IP 人物加一套明亮的薄荷风格。

- 人物「薄荷」：圆框眼镜、栗色短发、薄荷绿连帽衫的年轻虚拟形象，不带性别和年龄标签，不属于任何真人。
- `pose_a.png` 抱臂（封面），`pose_b.png` 讲解（内页收尾），`pose_c.png` 邀请（封底），透明底。
- `logo_light.png`、`logo_dark.png` 是同一个圆形头像徽章，浅底和深底通用。
- 底图在 `../../themes/mint/`：`bg_cover.jpg` 封面和收尾页，`bg_inner.jpg` 内页。

全部由本机 ComfyUI（Qwen Image 2.1）自生成，不含任何他人形象、Logo 或文字，随库一起授权，可以直接作为自己账号的形象，也可以换成自己的人物。换成自己的：

    python xhs.py setup --name "账号名" --pose-a 人物.png --logo-light logo.png

想让人物出现在别的场景：用 `nook-qwen-image-2.1` 的编辑模式，以 `pose_a.png` 为参考图，写“保持脸、眼镜、发型、薄荷绿连帽衫不变，只改姿势”，同一个人物可以延展出更多姿态。
