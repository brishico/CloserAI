# src/closerai/audio.py
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

q = queue.Queue()

DEVICE_INDEX = 19  # Microphone (Realtek HD Audio Mic input)

def callback(indata, frames, time, status):
    if status:
        print(f"[Audio status] {status}")
    # indata.shape == (frames, 2) for stereo; take channel 0 only
    mono = indata[:, 0].copy().tobytes()
    q.put(mono)
    
def listen(keywords=None):
    """
    Open mic stream, run Vosk recognizer, and detect keywords.
    keywords: list of lower-cased strings to trigger suggestions.
    """
    if keywords is None:
        keywords = ["pricing", "budget", "next steps"]

    # Load a small Vosk model (downloaded separately)
    model = Model("models/vosk-model-small-en-us-0.15")  
    rec = KaldiRecognizer(model, 16000)

 def listen(keywords=None):
    # ... (rest of function unchanged) ...
    with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=2,            # record stereo
            device=DEVICE_INDEX,   # use index 19
            callback=callback):
        print("🎙  Listening...  (press Ctrl+C to stop)")
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        print(f"[You said] {text}")
                        for kw in keywords:
                            if kw in text.lower():
                                print(f"[Suggestion] Mention {kw!r} to guide the conversation.")
        except KeyboardInterrupt:
            print("\nStopped listening.")
