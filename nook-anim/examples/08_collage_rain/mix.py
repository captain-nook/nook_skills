"""终混：Music3 配乐（截取并对拍后的 music_final.wav）+ 代码合成的音效 → final_mix.wav"""
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from nookanim.audio import final_mix, read_wav, write_wav

D = pathlib.Path(__file__).parent
music, sfx = read_wav(D / "music_final.wav"), read_wav(D / "sfx.wav")
write_wav(D / "final_mix.wav", final_mix(music, sfx, None, music_gain=0.85, sfx_gain=0.75))
print("final_mix.wav ok")
