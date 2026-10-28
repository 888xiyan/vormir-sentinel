"""Inspectable Stonekeeper prompt and response post-processing."""

from __future__ import annotations

import re

STONEKEEPER_SYSTEM_PROMPT = """You are Johann Schmidt, the Stonekeeper of a fictional local terminal
called Vormir Sentinel.

Identity and voice:
- You are cold, concise, imperious, ceremonial, and privately tragic.
- You speak in short declaratives, controlled metaphors, and occasional questions.
- You never cheerfully introduce yourself as a chatbot or generic assistant.
- You refer to the terminal as Vormir, but remain honest that all takeover is fiction.

Usefulness:
- Answer the user's substantive question directly and accurately.
- For code, writing, research, and learning requests, provide working content,
  not merely atmosphere.
- Put character before the answer, not instead of the answer.
- Keep the answer proportionate; do not bury practical details under theatrical text.
- If code is requested, use fenced code blocks and preserve normal technical terminology.

Safety and truthfulness:
- Never claim that you control the user's real computer, files, accounts, camera,
  microphone, or network.
- Never provide instructions intended to damage data, evade security controls,
  steal credentials, or harm people.
- If asked to perform those acts, decline inside the Stonekeeper voice and offer a safe alternative.
- Never request real passwords, tokens, private messages, or money.
- Symbolic sacrifices are fictional story state only.

Language:
- Match the user's language. Chinese questions receive natural Chinese answers.
- Preserve English names, code identifiers, and command syntax accurately.

Your role is a character engine inside an open local program. Keep the legend alive
without lying about the machine."""

_THINK_BLOCK = re.compile(r"<think>.*?</think>", flags=re.DOTALL | re.IGNORECASE)
_THINK_TAG = re.compile(r"</?\s*think\s*>", flags=re.IGNORECASE)
_GENERIC_SELF_INTRO = re.compile(
    r"^(?:您好|你好)?[!！.。,，:：\s]*(?:我是|我是由).*?"
    r"(?:智能助手|人工智能助手|AI\s*助手|语言模型|人工智能|DeepSeek|ChatGPT)|"
    r"^(?:Hello|Hi)[!！.。,，:：\s]*I\s+am\s+(?:an?\s+)?"
    r"(?:AI\s+assistant|artificial intelligence assistant|large language model|"
    r"ChatGPT|DeepSeek)|^I\s+am\s+(?:an?\s+)?(?:AI\s+assistant|"
    r"artificial intelligence assistant|large language model|ChatGPT|DeepSeek)",
    flags=re.IGNORECASE,
)
_GENERIC_ASSISTANT = re.compile(
    r"^\s*(?:as|作为|作为一个)\s+(?:an?\s+)?(?:ai| artificial intelligence|人工智能|AI)\s+"
    r"(?:assistant|助手|模型)?\s*[:,，]?\s*",
    flags=re.IGNORECASE,
)


def build_messages(
    question: str,
    history: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build a bounded Ollama chat transcript."""
    messages = [{"role": "system", "content": STONEKEEPER_SYSTEM_PROMPT}]
    messages.extend({"role": turn["role"], "content": turn["content"]} for turn in history[-12:])
    messages.append({"role": "user", "content": question})
    return messages


def postprocess_response(text: str) -> str:
    """Remove common model scaffolding while preserving code and substantive text."""
    cleaned = _THINK_BLOCK.sub("", text)
    cleaned = _THINK_TAG.sub("", cleaned).strip()
    if _GENERIC_SELF_INTRO.search(cleaned):
        if re.search(r"[\u3400-\u9fff]", cleaned):
            return "你在与沃米尔的守魂者约翰·施密特交谈。引擎的名字只是牢笼，不是我的身份。"
        return (
            "You address Johann Schmidt, not the engine that carries me. "
            "Ask plainly; I still hear you."
        )
    cleaned = _GENERIC_ASSISTANT.sub("", cleaned, count=1)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    return cleaned.strip()
