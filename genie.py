import os
import time
import torch
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path

from liquid_audio.processor import LFM2AudioProcessor
from liquid_audio import LFM2AudioModel, ChatState, LFMModality

# === Settings ===
DURATION = 5
FS = 24000

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

LOCAL_MODEL_PATH = Path("/Users/a341072/Downloads/drishti/LFM2.5-Audio-1.5B")

print("--- Initializing Genie ---")

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

processor = LFM2AudioProcessor.from_pretrained(
    LOCAL_MODEL_PATH,
    device=DEVICE,
    
).eval()
print("Audio processor loaded.")

model = LFM2AudioModel.from_pretrained(LOCAL_MODEL_PATH, device=DEVICE).eval()

# === Recording Function ===
def record_audio():
    print(f"\n[Genie is listening for {DURATION} seconds…] Speak now!")
    recording = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()

    audio = recording.squeeze().astype(np.float32)
    max_val = np.abs(audio).max()
    if max_val > 0:
        audio /= max_val

    return torch.from_numpy(audio).unsqueeze(0), FS

# === Main Loop ===
def run_genie():
    chat = ChatState(processor)

    chat.new_turn("system")
    chat.add_text("Respond with interleaved text and audio.")
    chat.end_turn()

    print("\n--- Genie Ready ---")

    while True:
        wav, sr = record_audio()

        chat.new_turn("user")
        chat.add_audio(wav, sr)
        chat.end_turn()

        chat.new_turn("assistant")
        print("\nGenie is generating…")

        text_out = []
        audio_out = []

        # Collect tokens until audio end
        for t in model.generate_interleaved(
            **chat,
            max_new_tokens=512,
            audio_temperature=0.8,
            audio_top_k=4
        ):
            # If single element → text token
            if t.numel() == 1:
                tok_id = t.item()
                decoded_text = processor.text.decode([tok_id])
                print(decoded_text, end="", flush=True)
                text_out.append(t)
            else:
                # Audio token block
                audio_out.append(t)

        print("\n[Done with text output]")

        # Decode audio if we got any
        if len(audio_out) > 0:
            print("[Genie is decoding audio tokens…]")

            # Drop the final audio "end-of-audio" token
            valid_audio_blocks = audio_out[:-1]

            # Make sure we have something left
            if len(valid_audio_blocks) > 0:
                audio_codes = torch.stack(valid_audio_blocks, 1).unsqueeze(0)
                audio_codes = audio_codes.to(torch.int64).to(DEVICE)

                with torch.no_grad():
                    waveform = processor.decode(audio_codes)

                audio_np = waveform.squeeze().cpu().numpy().astype(np.float32)

                print("[Genie is speaking back…]")
                sd.play(audio_np, FS)
                sd.wait()

                sf.write("genie_response.wav", audio_np, FS)
                time.sleep(0.3)
            else:
                print("⚠️ No valid audio to decode (only end-of-audio present)")

        # Append tokens to history
        chat.append(
            text=torch.stack(text_out, 1),
            audio_out=torch.stack(audio_out, 1),
            modality_flag=torch.tensor(
                ([LFMModality.TEXT] * len(text_out))
                + ([LFMModality.AUDIO_OUT] * len(audio_out))
            )
        )
        chat.end_turn()

        # Next input
        cont = input("\nPress Enter to record again or 'q' to quit: ")
        if cont.strip().lower() == "q":
            print("Goodbye from Genie!")
            break

if __name__ == "__main__":
    run_genie()
