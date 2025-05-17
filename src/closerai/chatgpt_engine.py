import os
from openai import OpenAI

class ChatGPTEngine:
    """
    Wraps the OpenAI client to maintain a short context window of
    the last N utterances (agent + customer) and then ask GPT
    for a coaching suggestion based on that history.
    """
    def __init__(self, max_history: int = 5):
        # Load API key from .env
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)

        self.system_prompt = (
            "You are a real-time sales coach. "
            "Based on the recent conversation, provide a concise, actionable suggestion "
            "to help the salesperson advance the deal."
        )

        # Mixed history of the last N lines: entries like "Agent: …" or "Customer: …"
        self.history: list[str] = []
        self.max_history = max_history

    def _trim(self):
        # Keep only the most recent max_history entries
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

    def record_agent(self, agent_text: str):
        """Call this whenever the salesperson speaks."""
        self.history.append(f"Agent: {agent_text}")
        self._trim()

    def record_customer(self, customer_text: str):
        """Call this whenever the customer speaks."""
        self.history.append(f"Customer: {customer_text}")
        self._trim()

    def suggest(self) -> str:
        """
        Build a GPT prompt from system + history, then return GPT's suggestion.
        """
        context = "\n".join(self.history)
        messages = [
            {"role": "system",  "content": self.system_prompt},
            {
                "role": "user",
                "content": (
                    f"Here is the recent conversation:\n{context}\n\n"
                    "Based on that, what is one concise suggestion the salesperson "
                    "should make next to advance the deal?"
                ),
            },
        ]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=60,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
