"""Client LLM derrière une interface — un seul appel par cycle (N-C16-01 :
`decision = appeler_llm(contexte)`, puis `decision.appels_outils` exécutés
en séquence). Deux implémentations (décision de portée du plan) :

- `ScriptedLLMClient` — déterministe, aucune clé requise, par défaut et
  pour les tests (comme le Livre le préconise, chapitre 35).
- `AnthropicLLMClient` — réel, activé seulement si `ANTHROPIC_API_KEY` est
  présent dans l'environnement (`build_llm_client()`).
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class LLMDecision:
    tool_calls: list[ToolCall] = field(default_factory=list)
    tokens_consumed: int = 0
    reasoning_text: str | None = None


class LLMClient(ABC):
    @abstractmethod
    async def decide(self, *, system_prompt: str, context: str, tools: list[dict]) -> LLMDecision: ...


class ScriptedLLMClient(LLMClient):
    """Rejoue une liste de décisions préparées, dans l'ordre — la dernière
    se répète indéfiniment une fois épuisée (pour un agent qui doit rester
    vivant 48h sur un script court, ex. tests d'intégration)."""

    def __init__(self, decisions: list[LLMDecision] | None = None):
        self._decisions = decisions or [LLMDecision()]  # défaut : ne fait jamais rien
        self._i = 0

    async def decide(self, *, system_prompt: str, context: str, tools: list[dict]) -> LLMDecision:
        decision = self._decisions[min(self._i, len(self._decisions) - 1)]
        self._i += 1
        return decision


class AnthropicLLMClient(LLMClient):
    """Décisions réelles via l'API Anthropic (tool-use natif — correspond
    directement aux contrats d'outils de l'Annexe C)."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        import anthropic  # import différé : dépendance optionnelle tant que non utilisée

        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def decide(self, *, system_prompt: str, context: str, tools: list[dict]) -> LLMDecision:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": context}],
            tools=tools,
        )
        tool_calls = [
            ToolCall(name=block.name, arguments=block.input)
            for block in response.content
            if block.type == "tool_use"
        ]
        reasoning_text = "".join(block.text for block in response.content if block.type == "text") or None
        tokens_consumed = response.usage.input_tokens + response.usage.output_tokens
        return LLMDecision(tool_calls=tool_calls, tokens_consumed=tokens_consumed, reasoning_text=reasoning_text)


def build_llm_client() -> LLMClient:
    """`ANTHROPIC_API_KEY` présent -> décisions réelles ; sinon
    `ScriptedLLMClient` par défaut (no-op — un scénario de test construit
    explicitement le sien, voir tests/arena/)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        model = os.environ.get("ARENA_LLM_MODEL", "claude-sonnet-5")
        return AnthropicLLMClient(api_key=api_key, model=model)
    return ScriptedLLMClient()
