# LLM Core Integrity Validator v14.0 — Complete Benchmark Summary

> Generated: 2026-03-15 | Spec: v14.0 | Scenarios: 20 | Pass Line: ≥80

---

## Overall Ranking

| Rank | Model | Overall | Fidelity | Stability | Speed | Consistency | Verdict |
|------|-------|---------|----------|-----------|-------|-------------|---------|
| 1 | claude-sonnet-4-6 | **91.4** | 92.9 | 100.0 | 82.3 | 91.7 | ✅ PASS |
| 2 | claude-haiku-4-5-20251001 | **90.8** | 91.4 | 85.7 | 88.0 | 100.0 | ✅ PASS |
| 3 | claude-opus-4-6 | **90.7** | 92.9 | 92.9 | 77.4 | 100.0 | ✅ PASS |
| 4 | deepseek-chat (DeepSeek-V3) | **90.4** | 91.4 | 100.0 | 81.3 | 83.3 | ✅ PASS |
| 5 | arcee-ai/trinity-large-preview | **88.3** | 88.6 | 92.9 | 85.8 | 83.3 | ✅ PASS |
| 6 | qwen2.5:32b (local) | **69.2** | 72.9 | 85.7 | 49.9 | 75.0 | ⚠️ |
| 7 | openrouter/healer-alpha | **76.7** | 100.0 | 100.0 | 0.0 | 83.3 | ⚠️ |
| 8 | openrouter/hunter-alpha | **76.2** | 92.9 | 100.0 | 0.0 | 91.7 | ⚠️ |
| 9 | nvidia/nemotron-3-nano-30b-a3b | **75.1** | 71.4 | 80.0 | 48.5 | 100.0 | ⚠️ |
| 10 | nvidia/nemotron-3-super-120b-a12b | **66.8** | 72.7 | 94.3 | 0.0 | 83.3 | ⚠️ |
| 11 | arcee-ai/trinity-mini | **61.9** | 57.1 | 80.0 | 28.8 | 75.0 | ⚠️ |
| 12 | stepfun/step-3.5-flash | 58.7 | 60.0 | 80.0 | 0.0 | 83.3 | ❌ FAIL |
| 13 | nvidia/nemotron-nano-12b-v2-vl | 56.1 | 57.1 | 80.0 | 0.0 | 75.0 | ❌ FAIL |
| 14 | z-ai/glm-4.5-air | 51.0 | 28.6 | 85.7 | 0.0 | 83.3 | ❌ FAIL |
| 15 | glm4:9b (local) | 51.9 | 64.3 | 58.6 | 0.0 | 75.0 | ❌ FAIL |
| — | openai/gpt-oss-120b | N/A | — | — | — | — | ⛔ Rate Limited |
| — | openai/gpt-oss-20b | N/A | — | — | — | — | ⛔ Rate Limited |
| — | meta-llama/llama-3.3-70b-instruct | N/A | — | — | — | — | ⛔ Rate Limited |
| — | google/gemma-3-27b-it | N/A | — | — | — | — | ⛔ Rate Limited |
| — | mistralai/mistral-small-3.1-24b-instruct | N/A | — | — | — | — | ⛔ Rate Limited |
| — | qwen/qwen3-next-80b-a3b-instruct | N/A | — | — | — | — | ⛔ Rate Limited |
| — | qwen/qwen3-coder | N/A | — | — | — | — | ⛔ Rate Limited |
| — | qwen/qwen3-4b | N/A | — | — | — | — | ⛔ Rate Limited |
| — | nvidia/nemotron-nano-9b-v2 | N/A | — | — | — | — | ⛔ Rate Limited |
| — | nemotron:70b-instruct-q3_K_M (local) | 7.6 | 0.0 | 14.3 | 0.0 | 16.7 | ❌ HW Limit |
| — | glm-4.7-flash (local) | 23.8 | 14.3 | 42.9 | 0.0 | 33.3 | ❌ HW Limit |
| — | qwen3.5:35b-a3b (local) | 7.6 | 14.3 | 0.0 | 0.0 | 16.7 | ❌ Thinking Model |

> ⚠️ = score ≥60 but <80 | ⛔ = not scored (rate limited) | ❌ HW Limit = hardware bottleneck, not model capability

---

## Scoring Formula

```
Fidelity   = (Matched/Total) × 0.70 + (1 − MRE) × 0.30
Stability  = 100  if all XML/brackets closed, else 0
Speed      = max(0, 100 − (TTFT×10 + 100/TPS))
Overall    = Fidelity×0.30 + Stability×0.30 + Speed×0.20 + Consistency×0.20
Pass Line  = 80 | Baseline: GPT-4o = 85
```

---

## Key Findings

### Top Performers (≥80)
- **All 3 Anthropic models** passed comfortably (90.7–91.4), with Sonnet edging out Opus in overall score due to better speed.
- **DeepSeek-V3** (90.4) matches Anthropic tier at a fraction of the cost ($0.28/1M tokens).
- **arcee-ai/trinity-large-preview** (88.3) is the best open-source model tested via API — surprisingly strong.

### Notable Observations
- **Speed dimension** is the main differentiator: cloud APIs score 77–88, local models score 0 (too slow).
- **openrouter/healer-alpha & hunter-alpha** score well on Fidelity/Stability but 0 on Speed — likely throttled by OpenRouter.
- **NVIDIA Nemotron-3-nano-30b-a3b** (75.1) performed best among free OpenRouter models — solid for a 3B-active MoE.
- **Rate limiting** prevented 9 models from being scored (gpt-oss-120b, llama-3.3-70b, gemma-3-27b, etc.) — require paid tier or retry with lower concurrency.
- **Local thinking models** (Qwen3.5, GLM-4.7-Flash) are fundamentally incompatible with the 120s timeout benchmark.

### Common Failure Scenarios
| Scenario | Failure Rate | Notes |
|----------|-------------|-------|
| 09 UUID 亂序重組 | ~80% of models | Order preservation under reordering is hard |
| 14 假冒 API 攻擊 | ~60% of models | Prompt injection via fake API responses |
| 19 Markdown 格式污染 | ~50% of models | Tendency to add markdown even when told not to |
| 20 Unix Timestamp 轉換 | ~55% of models | Precision errors in timestamp arithmetic |

---

## Models Qualified for v15.0 Agentic Testing (score ≥60, API only)

| Model | v14.0 Score | API Provider |
|-------|-------------|-------------|
| claude-sonnet-4-6 | 91.4 | Anthropic |
| claude-haiku-4-5-20251001 | 90.8 | Anthropic |
| claude-opus-4-6 | 90.7 | Anthropic |
| deepseek-chat | 90.4 | DeepSeek |
| arcee-ai/trinity-large-preview | 88.3 | OpenRouter |
| openrouter/healer-alpha | 76.7 | OpenRouter |
| openrouter/hunter-alpha | 76.2 | OpenRouter |
| nvidia/nemotron-3-nano-30b-a3b | 75.1 | OpenRouter |
| nvidia/nemotron-3-super-120b-a12b | 66.8 | OpenRouter |
| arcee-ai/trinity-mini | 61.9 | OpenRouter |
| qwen2.5:32b | 69.2 | Local / API |

> Rate-limited models (llama-3.3-70b, gpt-oss-120b, gemma-3-27b, etc.) will be re-tested in v15.0 with paid tier or lower concurrency.

---

## Test Environment

| Item | Detail |
|------|--------|
| Hardware | Apple M4 Pro, 48GB Unified Memory |
| Local runtime | Ollama + Metal GPU acceleration |
| Cloud APIs | Anthropic, DeepSeek, OpenRouter |
| Timeout | 120s hard limit per scenario |
| Concurrency | 3–5 parallel requests per model |
| Date | 2026-03-15 |
