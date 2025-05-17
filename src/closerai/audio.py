import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Realtek Mic Array (4-channel input)
DEVICE_INDEX = 1  

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[Audio status] {status}")
    # indata.shape == (frames, 4); take only channel 0
    mono = indata[:, 0].copy().tobytes()
    q.put(mono)

def listen(keywords=None):
    """
    Open mic stream, run Vosk recognizer, and detect keywords.
    keywords: list of lower-cased strings to trigger suggestions.
    """
    if keywords is None:
        keywords = ["pricing", "budget", "next steps"]

    # Load your model
    model = Model("models/vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=4,            # record all 4 channels
        device=DEVICE_INDEX,   # use index 1
        callback=callback
    ):
        print("🎙 Listening... (Ctrl+C to stop)")
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
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        # print partial results inline
                        print(f"[…] {partial}", end="\r")
        except KeyboardInterrupt:
            print("\nStopped listening.")
