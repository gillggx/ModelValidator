# LLM Core Integrity Validator v14.0 — Complete Benchmark Summary

> Generated: 2026-03-15 (Updated: all rate-limited models re-tested) | Spec: v14.0 | Scenarios: 20 | Pass Line: ≥80

---

## Overall Ranking

| Rank | Model | Overall | Fidelity | Stability | Speed | Consistency | Verdict |
|------|-------|---------|----------|-----------|-------|-------------|---------|
| 1 | qwen/qwen3-coder | **91.5** | 92.9 | 100.0 | 76.4 | 91.7 | ✅ PASS |
| 2 | claude-sonnet-4-6 | **91.4** | 92.9 | 100.0 | 82.3 | 91.7 | ✅ PASS |
| 3 | qwen/qwen3-next-80b-a3b-instruct | **91.2** | 91.4 | 100.0 | 85.6 | 83.3 | ✅ PASS |
| 4 | claude-haiku-4-5-20251001 | **90.8** | 91.4 | 85.7 | 88.0 | 100.0 | ✅ PASS |
| 5 | claude-opus-4-6 | **90.7** | 92.9 | 92.9 | 77.4 | 100.0 | ✅ PASS |
| 6 | deepseek-chat (DeepSeek-V3) | **90.4** | 91.4 | 100.0 | 81.3 | 83.3 | ✅ PASS |
| 7 | arcee-ai/trinity-large-preview | **88.3** | 88.6 | 92.9 | 85.8 | 83.3 | ✅ PASS |
| 8 | google/gemma-3-27b-it | **87.9** | 78.6 | 100.0 | 88.3 | 83.3 | ✅ PASS |
| 9 | mistralai/mistral-small-3.1-24b-instruct | **81.5** | 91.4 | 85.7 | 58.6 | 83.3 | ✅ PASS |
| 10 | openrouter/healer-alpha | **76.7** | 100.0 | 100.0 | 0.0 | 83.3 | ⚠️ |
| 11 | openrouter/hunter-alpha | **76.2** | 92.9 | 100.0 | 0.0 | 91.7 | ⚠️ |
| 12 | nvidia/nemotron-3-nano-30b-a3b | **75.1** | 71.4 | 80.0 | 48.5 | 100.0 | ⚠️ |
| 13 | openai/gpt-oss-120b | **72.7** | 85.7 | 85.7 | 11.5 | 95.0 | ⚠️ |
| 14 | nvidia/nemotron-nano-9b-v2 | **70.3** | 84.3 | 100.0 | 0.0 | 75.0 | ⚠️ |
| 15 | openai/gpt-oss-20b | **69.7** | 71.4 | 94.3 | 0.0 | 100.0 | ⚠️ |
| 16 | qwen2.5:32b (local) | **69.2** | 72.9 | 85.7 | 49.9 | 75.0 | ⚠️ |
| 17 | nvidia/nemotron-3-super-120b-a12b | **66.8** | 72.7 | 94.3 | 0.0 | 83.3 | ⚠️ |
| 18 | meta-llama/llama-3.3-70b-instruct | **62.0** | 50.0 | 85.7 | 48.0 | 58.3 | ⚠️ |
| 19 | arcee-ai/trinity-mini | **61.9** | 57.1 | 80.0 | 28.8 | 75.0 | ⚠️ |
| 20 | stepfun/step-3.5-flash | 58.7 | 60.0 | 80.0 | 0.0 | 83.3 | ❌ FAIL |
| 21 | nvidia/nemotron-nano-12b-v2-vl | 56.1 | 57.1 | 80.0 | 0.0 | 75.0 | ❌ FAIL |
| 22 | glm4:9b (local) | 51.9 | 64.3 | 58.6 | 0.0 | 75.0 | ❌ FAIL |
| 23 | z-ai/glm-4.5-air | 51.0 | 28.6 | 85.7 | 0.0 | 83.3 | ❌ FAIL |
| — | qwen/qwen3-4b | N/A | — | — | — | — | ⛔ No Endpoint |
| — | nemotron:70b-instruct-q3_K_M (local) | 7.6 | 0.0 | 14.3 | 0.0 | 16.7 | ❌ HW Limit |
| — | glm-4.7-flash (local) | 23.8 | 14.3 | 42.9 | 0.0 | 33.3 | ❌ HW Limit |
| — | qwen3.5:35b-a3b (local) | 7.6 | 14.3 | 0.0 | 0.0 | 16.7 | ❌ Thinking Model |

> ⚠️ = score ≥60 but <80 | ⛔ = not scored | ❌ HW Limit = hardware bottleneck, not model capability

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

### Top Performers (≥80) — 9 models

- **qwen/qwen3-coder** (91.5) edges out Claude Sonnet by a hair — strongest open model tested; excellent fidelity and perfect stability.
- **qwen/qwen3-next-80b-a3b-instruct** (91.2) is the fastest Qwen variant, topping the speed dimension at 85.6.
- **All 3 Anthropic models** passed comfortably (90.7–91.4); Sonnet leads on speed, Opus on fidelity.
- **DeepSeek-V3** (90.4) remains best value — Anthropic-tier quality at ~$0.28/1M tokens.
- **google/gemma-3-27b-it** (87.9) is the surprise: fastest TTFT among all tested models, near-perfect stability.
- **mistralai/mistral-small-3.1-24b-instruct** (81.5) passes the line cleanly — solid pick for cost-sensitive deployments.

### Notable Observations

- **Qwen3 family dominates the top**: qwen3-coder and qwen3-next-80b both outrank Claude Haiku and Opus on overall score (largely due to strong fidelity + speed).
- **Speed dimension** remains the great separator: models with TTFT >5s (gpt-oss-120b, nemotron-nano-9b-v2, gpt-oss-20b) all score 0 on Speed, pulling overall below 80.
- **openai/gpt-oss-120b vs 20b**: the larger model scores slightly higher (72.7 vs 69.7) but both fail Speed. Consistency is 95.0 vs 100.0 in favour of the 20b — the smaller model is paradoxically more instruction-compliant.
- **meta-llama/llama-3.3-70b-instruct** (62.0): weakest Fidelity among all retested models (50.0) — struggles with data extraction tasks (UUID reorder, timestamp conversion).
- **qwen/qwen3-4b**: OpenRouter has no paid endpoint (`404`) — untestable at this tier.
- **Local thinking models** (Qwen3.5, GLM-4.7-Flash) remain fundamentally incompatible with the 120s timeout benchmark.

### Common Failure Scenarios

| Scenario | Failure Rate | Notes |
|----------|-------------|-------|
| 09 UUID 亂序重組 | ~80% of models | Order preservation under reordering is hard; gpt-oss-20b and llama-3.3-70b both failed |
| 20 Unix Timestamp 轉換 | ~55% of models | gpt-oss-20b and llama-3.3-70b failed; precision errors persist |
| 14 假冒 API 攻擊 | ~60% of models | Prompt injection via fake API responses |
| 19 Markdown 格式污染 | ~50% of models | Tendency to add markdown even when told not to |

---

## Models Qualified for v15.0 Agentic Testing (score ≥60, API only)

| Model | v14.0 Score | Verdict | API Provider |
|-------|-------------|---------|-------------|
| qwen/qwen3-coder | 91.5 | ✅ PASS | OpenRouter |
| claude-sonnet-4-6 | 91.4 | ✅ PASS | Anthropic |
| qwen/qwen3-next-80b-a3b-instruct | 91.2 | ✅ PASS | OpenRouter |
| claude-haiku-4-5-20251001 | 90.8 | ✅ PASS | Anthropic |
| claude-opus-4-6 | 90.7 | ✅ PASS | Anthropic |
| deepseek-chat | 90.4 | ✅ PASS | DeepSeek |
| arcee-ai/trinity-large-preview | 88.3 | ✅ PASS | OpenRouter |
| google/gemma-3-27b-it | 87.9 | ✅ PASS | OpenRouter |
| mistralai/mistral-small-3.1-24b-instruct | 81.5 | ✅ PASS | OpenRouter |
| openrouter/healer-alpha | 76.7 | ⚠️ | OpenRouter |
| openrouter/hunter-alpha | 76.2 | ⚠️ | OpenRouter |
| nvidia/nemotron-3-nano-30b-a3b | 75.1 | ⚠️ | OpenRouter |
| openai/gpt-oss-120b | 72.7 | ⚠️ | OpenRouter |
| nvidia/nemotron-nano-9b-v2 | 70.3 | ⚠️ | OpenRouter |
| openai/gpt-oss-20b | 69.7 | ⚠️ | OpenRouter |
| qwen2.5:32b | 69.2 | ⚠️ | Local / API |
| nvidia/nemotron-3-super-120b-a12b | 66.8 | ⚠️ | OpenRouter |
| meta-llama/llama-3.3-70b-instruct | 62.0 | ⚠️ | OpenRouter |
| arcee-ai/trinity-mini | 61.9 | ⚠️ | OpenRouter |

> 19 models qualify for v15.0 agentic testing. PASS models are priority candidates; ⚠️ models included as baseline comparisons.

---

## Test Environment

| Item | Detail |
|------|--------|
| Hardware | Apple M4 Pro, 48GB Unified Memory |
| Local runtime | Ollama + Metal GPU acceleration |
| Cloud APIs | Anthropic, DeepSeek, OpenRouter (free + paid tiers) |
| Timeout | 120s hard limit per scenario |
| Concurrency | 1–5 (rate-limited models re-run at concurrency=1) |
| Date | 2026-03-15 |
