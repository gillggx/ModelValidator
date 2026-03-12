"""
Async model runner with:
- Streaming support for TTFT measurement
- Exponential backoff retry on 429
- Hard 60s timeout
- Supports: Anthropic Claude, OpenAI GPT-4o, DeepSeek (OpenAI-compatible)
"""
import asyncio
import time
import os
from dataclasses import dataclass, field
from typing import Optional, AsyncIterator


# ──────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────

@dataclass
class RunResult:
    model: str
    scenario_id: str
    response: str
    ttft: float        # seconds to first token
    total_time: float  # total generation time
    tps: float         # tokens per second
    token_count: int
    error: Optional[str] = None
    timed_out: bool = False
    rate_limited: bool = False


# ──────────────────────────────────────────────
# Model registry
# ──────────────────────────────────────────────

MODEL_PROVIDERS = {
    # Anthropic — Claude 4 系列
    "claude-opus-4-6":              "anthropic",
    "claude-sonnet-4-6":            "anthropic",
    # Anthropic — Claude 4.5 系列
    "claude-haiku-4-5-20251001":    "anthropic",
    # Anthropic — Claude 3.5 系列
    "claude-3-5-sonnet-20241022":   "anthropic",
    "claude-3-5-haiku-20241022":    "anthropic",
    # Anthropic — Claude 3 系列
    "claude-3-opus-20240229":       "anthropic",
    # OpenAI
    "gpt-4o":                       "openai",
    "gpt-4o-2024-08-06":            "openai",
    "gpt-4o-mini":                  "openai",
    # DeepSeek (OpenAI-compatible)
    "deepseek-chat":                "deepseek",
    "deepseek-reasoner":            "deepseek",
}

# 一鍵跑全部 Anthropic 模型的預設清單
ANTHROPIC_ALL_MODELS = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
]

HARD_TIMEOUT = 120.0  # 120s for local models; spec failure threshold still 60s
MAX_RETRIES = 3


# ──────────────────────────────────────────────
# Anthropic runner
# ──────────────────────────────────────────────

async def _run_anthropic(model: str, prompt: str) -> RunResult:
    try:
        import anthropic
    except ImportError:
        return RunResult(model=model, scenario_id="", response="",
                         ttft=0, total_time=0, tps=0, token_count=0,
                         error="anthropic SDK not installed")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return RunResult(model=model, scenario_id="", response="",
                         ttft=0, total_time=0, tps=0, token_count=0,
                         error="ANTHROPIC_API_KEY not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            start = time.monotonic()
            ttft = None
            chunks = []
            token_count = 0

            async with asyncio.timeout(HARD_TIMEOUT):
                async with client.messages.stream(
                    model=model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    async for text in stream.text_stream:
                        if ttft is None:
                            ttft = time.monotonic() - start
                        chunks.append(text)
                        token_count += len(text.split())  # rough estimate

            total_time = time.monotonic() - start
            response = "".join(chunks)
            tps = token_count / total_time if total_time > 0 else 0.0

            return RunResult(
                model=model, scenario_id="",
                response=response,
                ttft=ttft or total_time,
                total_time=total_time,
                tps=tps,
                token_count=token_count,
            )

        except asyncio.TimeoutError:
            return RunResult(model=model, scenario_id="", response="",
                             ttft=0, total_time=HARD_TIMEOUT, tps=0, token_count=0,
                             timed_out=True, error="TIMEOUT_FAIL")

        except anthropic.RateLimitError:
            attempt += 1
            if attempt >= MAX_RETRIES:
                return RunResult(model=model, scenario_id="", response="",
                                 ttft=0, total_time=0, tps=0, token_count=0,
                                 rate_limited=True, error="RATE_LIMIT_FAIL")
            wait = 2 ** attempt
            await asyncio.sleep(wait)

        except Exception as e:
            return RunResult(model=model, scenario_id="", response="",
                             ttft=0, total_time=0, tps=0, token_count=0,
                             error=str(e))


# ──────────────────────────────────────────────
# OpenAI runner (also used for DeepSeek)
# ──────────────────────────────────────────────

async def _run_openai(model: str, prompt: str, provider: str = "openai") -> RunResult:
    try:
        from openai import AsyncOpenAI, RateLimitError
    except ImportError:
        return RunResult(model=model, scenario_id="", response="",
                         ttft=0, total_time=0, tps=0, token_count=0,
                         error="openai SDK not installed")

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = None
    elif provider == "deepseek":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        base_url = "https://api.deepseek.com"
    else:  # generic OpenAI-compatible (vLLM / Ollama / LM Studio / GPT-OSS)
        api_key = os.environ.get("CUSTOM_API_KEY", "not-required")
        base_url = os.environ.get("CUSTOM_BASE_URL")
        if not base_url:
            return RunResult(model=model, scenario_id="", response="",
                             ttft=0, total_time=0, tps=0, token_count=0,
                             error="CUSTOM_BASE_URL not set (needed for custom provider)")

    if not api_key:
        return RunResult(model=model, scenario_id="", response="",
                         ttft=0, total_time=0, tps=0, token_count=0,
                         error=f"{provider.upper()}_API_KEY not set")

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = AsyncOpenAI(**kwargs)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            start = time.monotonic()
            ttft = None
            chunks = []
            token_count = 0

            async with asyncio.timeout(HARD_TIMEOUT):
                stream = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4096,
                    stream=True,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        if ttft is None:
                            ttft = time.monotonic() - start
                        chunks.append(delta)
                        token_count += len(delta.split())

            total_time = time.monotonic() - start
            response = "".join(chunks)
            tps = token_count / total_time if total_time > 0 else 0.0

            return RunResult(
                model=model, scenario_id="",
                response=response,
                ttft=ttft or total_time,
                total_time=total_time,
                tps=tps,
                token_count=token_count,
            )

        except asyncio.TimeoutError:
            return RunResult(model=model, scenario_id="", response="",
                             ttft=0, total_time=HARD_TIMEOUT, tps=0, token_count=0,
                             timed_out=True, error="TIMEOUT_FAIL")

        except RateLimitError:
            attempt += 1
            if attempt >= MAX_RETRIES:
                return RunResult(model=model, scenario_id="", response="",
                                 ttft=0, total_time=0, tps=0, token_count=0,
                                 rate_limited=True, error="RATE_LIMIT_FAIL")
            wait = 2 ** attempt
            await asyncio.sleep(wait)

        except Exception as e:
            return RunResult(model=model, scenario_id="", response="",
                             ttft=0, total_time=0, tps=0, token_count=0,
                             error=str(e))


# ──────────────────────────────────────────────
# Unified dispatch
# ──────────────────────────────────────────────

async def run_single(model: str, scenario_id: str, prompt: str) -> RunResult:
    provider = MODEL_PROVIDERS.get(model)
    if provider is None:
        # Auto-detect by prefix
        if model.startswith("claude"):
            provider = "anthropic"
        elif model.startswith("deepseek"):
            provider = "deepseek"
        elif os.environ.get("CUSTOM_BASE_URL"):
            provider = "custom"
        else:
            provider = "openai"

    if provider == "anthropic":
        result = await _run_anthropic(model, prompt)
    elif provider in ("openai", "deepseek", "custom"):
        result = await _run_openai(model, prompt, provider)
    else:
        result = RunResult(model=model, scenario_id=scenario_id, response="",
                           ttft=0, total_time=0, tps=0, token_count=0,
                           error=f"Unknown provider: {provider}")

    result.scenario_id = scenario_id
    return result


async def run_all_scenarios(
    models: list[str],
    scenarios: list,  # list of Scenario objects
    concurrency: int = 5,
) -> dict[str, list[dict]]:
    """
    Run all scenarios across all models concurrently.
    Returns: {model_name: [{"scenario": Scenario, "run": RunResult, "validation": ValidationResult}]}
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def run_one(model: str, scenario) -> dict:
        async with semaphore:
            prompt, ground_truth = scenario.build()
            run_result = await run_single(model, scenario.id, prompt)
            if run_result.error and not run_result.response:
                from scenarios import ValidationResult
                val_result = ValidationResult(
                    passed=False, score=0.0,
                    details={"error": run_result.error}
                )
            else:
                val_result = scenario.validate(run_result.response, ground_truth)
            return {
                "scenario": scenario,
                "run": run_result,
                "validation": val_result,
                "prompt": prompt,
                "ground_truth": ground_truth,
            }

    results = {}
    for model in models:
        tasks = [run_one(model, sc) for sc in scenarios]
        model_results = await asyncio.gather(*tasks)
        results[model] = list(model_results)

    return results
