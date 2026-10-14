"""OpenAI-compatible chat client for Ollama."""

import sys

import httpx

from .config import load_config


class LLM:
    """Generate commit messages using an OpenAI-compatible Ollama endpoint."""

    def __init__(self):
        """Load endpoint credentials and model settings."""
        self.config = load_config()
        self.base_url = self.config.get("base_url", "http://localhost:11434/v1").rstrip("/")
        self.model_id = self.config.get("model_id", "llama3")
        self.api_key = self.config.get("api_key", "")

    def _get_messages(self, prompt, context=None):
        """Build the chat messages sent to the model."""
        system_prompt = (
            "You are a helpful assistant that writes concise and meaningful "
            "git commit messages based on the provided git diff and log."
        )
        messages = [{"role": "system", "content": system_prompt}]
        user_content = f"Prompt: {prompt}"
        if context:
            user_content += f"\n\nContext: {context}"
        messages.append({"role": "user", "content": user_content})
        return messages

    def generate(self, prompt, context=None, debug=False):
        """Return a generated response, optionally reporting request settings."""
        messages = self._get_messages(prompt, context=context)

        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.7,
            "stream": False,
        }

        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        if debug:
            print(f"Debug: model_id={self.model_id}", file=sys.stderr)
            print(f"Debug: base_url={self.base_url}", file=sys.stderr)
            print(f"Debug: api_key={self.api_key!r}", file=sys.stderr)
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=60.0)
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Could not reach the model endpoint at {url}: {exc}") from exc
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip() or str(exc)
            if exc.response.status_code == 401:
                raise RuntimeError(
                    "The model endpoint rejected GITCRAFT_APIKEY. Check that it is a valid key "
                    f"for the configured provider. Provider response: {detail}"
                ) from exc
            raise RuntimeError(f"Model endpoint returned HTTP {exc.response.status_code}: {detail}") from exc

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("The model endpoint returned an unexpected response.") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("The model returned an empty response.")
        return content.strip()
