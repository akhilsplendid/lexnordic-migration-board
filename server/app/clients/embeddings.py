from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.settings import Settings


@dataclass(frozen=True)
class EmbeddingUsage:
    total_tokens: int | None = None


class AimlEmbeddingClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        expected_dimension: int,
        max_input_chars: int,
        timeout_seconds: float = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.expected_dimension = expected_dimension
        self.max_input_chars = max_input_chars
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings) -> "AimlEmbeddingClient":
        api_key = settings.secret_value(settings.aiml_api_key)
        if not api_key:
            raise RuntimeError("AIML_API_KEY is required for legal embeddings")
        return cls(
            base_url=settings.aiml_base_url,
            api_key=api_key,
            model=settings.legal_embedding_model,
            expected_dimension=settings.legal_embedding_dimension,
            max_input_chars=settings.legal_embedding_max_chars,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        prepared_texts = [self._prepare_text(text) for text in texts]

        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "input": prepared_texts},
            timeout=self.timeout_seconds,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500].replace("\n", " ")
            raise RuntimeError(f"Embedding request failed: {detail}") from exc
        payload = response.json()
        rows = payload.get("data")
        if not isinstance(rows, list):
            raise RuntimeError("Embedding response did not include a data list")

        indexed_rows = []
        for position, row in enumerate(rows):
            if not isinstance(row, dict):
                raise RuntimeError("Embedding response row was not an object")
            index = row.get("index", position)
            vector = row.get("embedding")
            if not isinstance(vector, list):
                raise RuntimeError("Embedding response row did not include an embedding")
            if len(vector) != self.expected_dimension:
                raise RuntimeError(
                    "Embedding dimension mismatch: "
                    f"expected {self.expected_dimension}, got {len(vector)}"
                )
            indexed_rows.append((int(index), [float(value) for value in vector]))

        indexed_rows.sort(key=lambda item: item[0])
        vectors = [vector for _, vector in indexed_rows]
        if len(vectors) != len(prepared_texts):
            raise RuntimeError(f"Expected {len(prepared_texts)} embeddings, got {len(vectors)}")
        return vectors

    def _prepare_text(self, text: str) -> str:
        cleaned = " ".join(text.split())
        if not cleaned:
            return " "
        if len(cleaned) <= self.max_input_chars:
            return cleaned
        return cleaned[: self.max_input_chars].rstrip()
