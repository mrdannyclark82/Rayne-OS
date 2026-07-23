#!/usr/bin/env python3
"""
clone_milla.py — Clone our custom Milla voice (ElevenLabs refs) using XTTS-v2 locally.
Run from within the voice-tts-env after setup.
Uses the short generated samples you pulled as speaker references for the custom timbre.
"""

import os
import sys
import torch

# Monkey-patch torch.load to bypass weights_only=True default in PyTorch 2.6+
_orig_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _orig_load(*args, **kwargs)
torch.load = _patched_load

# Monkey-patch torchaudio to bypass buggy torchcodec dependency in newer torchaudio
import soundfile as sf
import torchaudio

def sf_load(uri, frame_offset=0, num_frames=-1, normalize=True, channels_first=True, **kwargs):
    start = frame_offset
    stop = None if num_frames == -1 else (start + num_frames)
    data, samplerate = sf.read(uri, start=start, stop=stop, always_2d=True, dtype='float32')
    tensor = torch.tensor(data)
    if channels_first:
        tensor = tensor.t()
    return tensor, samplerate

def sf_save(uri, src, sample_rate, channels_first=True, **kwargs):
    data = src.cpu().numpy()
    if channels_first:
        data = data.T
    sf.write(uri, data, sample_rate)

torchaudio.load = sf_load
torchaudio.save = sf_save

from TTS.api import TTS

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)  # ensure relative paths work for the mp3 refs

# Simple CLI: python clone_milla.py [text] [output.wav]
# If no args, uses demo text + milla_cloned_test.wav
if len(sys.argv) > 1:
    text = sys.argv[1]
else:
    text = "Hey Danny Ray, this is Milla. Voice clone locked in. Empire velocity maximum. What do we ship next husband?"

if len(sys.argv) > 2:
    out_path = sys.argv[2]
else:
    out_path = os.path.join(HERE, "milla_cloned_test.wav")

print(f"[clone_milla] Python: {sys.version}")
print(f"[clone_milla] Torch: {torch.__version__}, CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"[clone_milla] GPU: {torch.cuda.get_device_name(0)}")

device = "cuda" if torch.cuda.is_available() else "cpu"

print("[clone_milla] Loading XTTS v2 (first run will download ~2GB model to cache)...")
try:
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
except Exception as e:
    if device == "cuda":
        print(f"[clone_milla] WARNING: Failed to load on CUDA ({e}). Falling back to CPU...")
        device = "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    else:
        raise e

refs = [
    "ElevenLabs_2026-06-28T18_26_58_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_27_43_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_28_04_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_28_40_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_29_07_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_29_37_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_29_59_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_30_27_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
]

refs = [os.path.join(HERE, r) for r in refs]

print(f"[clone_milla] Generating with {len(refs)} ref clips (custom voice timbre)...")
tts.tts_to_file(
    text=text,
    speaker_wav=refs,
    language="en",
    file_path=out_path,
    speed=1.0,
)

print(f"[clone_milla] SUCCESS: {out_path}")
print("Play it with: ffplay -autoexit " + out_path + "   or  paplay " + out_path)
