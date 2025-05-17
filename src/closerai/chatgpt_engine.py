from dotenv import load_dotenv
load_dotenv()

import os
import threading
import queue
import httpx
from openai import OpenAI

# Initialize HTTPX client to avoid proxies kwarg issues
_httpx_client = httpx.Client()

# Initialize OpenAI client with explicit HTTPX client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=_httpx_client
)

class ChatGPTEngine:
    """
    Asynchronous wrapper around OpenAI's ChatCompletion API using a background thread.
    """
    def __init__(self, system_prompt: str = None):
        # Default system prompt if not provided
        self.system_prompt = system_prompt or (
            "You are a real-time sales coach. "
            "When the customer says something, suggest one actionable talking point "
            "to guide the call forward."
        )
        # Internal queue for transcripts and their response queues
        self._q = queue.Queue()
        # Start the background worker thread
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while True:
            # Dequeue a transcript and the queue to put the suggestion into
            transcript, out_q = self._q.get()
            suggestion = None
            try:
                # Call the OpenAI ChatCompletion API
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user",   "content": transcript}
                    ],
                    max_tokens=60,
                    temperature=0.7,
                )
                # Extract the suggestion
                suggestion = response.choices[0].message.content.strip()
            except Exception as e:
                # Print errors for visibility
                print(f"[GPT error] {e}")
            # Put the result (or None) back to the caller
            out_q.put(suggestion)

    def get(self, transcript: str, timeout: float = 3.0):
        """
        Non-blocking fetch for a suggestion.

        Args:
            transcript: The customer's utterance to send to GPT.
            timeout:   How many seconds to wait before giving up.

        Returns:
            A string suggestion, or None if no response within the timeout.
        """
        out_q = queue.Queue()
        self._q.put((transcript, out_q))
        try:
            return out_q.get(timeout=timeout)
        except queue.Empty:
            return None
