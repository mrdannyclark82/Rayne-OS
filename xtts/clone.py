from TTS.api import TTS
import torch

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda" if torch.cuda.is_available() else "cpu")

tts.tts_to_file(
    text="Hey Danny Ray, this is your cloned voice speaking. Empire building never stops.",
    speaker_wav="your_voice_sample.wav",  # put a clean 6-30s .wav here
    language="en",
    file_path="output.wav"
)
print("Generated output.wav")
