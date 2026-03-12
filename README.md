# LLM Core Integrity Validator v14.0

> 這個工具不接任何業務邏輯，它只測 LLM 的「硬實力」。

A CLI tool that stress-tests LLMs across 20 hardcore scenarios covering schema integrity, data fidelity, reasoning consistency, context endurance, and performance.

## Evaluation Pillars

| Dimension | What it tests |
|---|---|
| **Fidelity** | Does the model hallucinate or mutate data? |
| **Stability** | Are XML/JSON structures always properly closed? |
| **Consistency** | Can it reason through contradictions and follow instructions? |
| **Speed** | TTFT and TPS under real streaming conditions |

Pass line: **≥ 80 / 100**. Baseline: GPT-4o @ 85.

## Benchmark Results (sample)

| Model | Score | Verdict |
|---|---|---|
| claude-sonnet-4-6 | 91.4 | ✅ PASS |
| claude-opus-4-6 | 90.7 | ✅ PASS |
| claude-haiku-4-5-20251001 | 85.2 | ✅ PASS |
| qwen2.5:32b (local) | 69.2 | ❌ FAIL |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/gillggx/ModelValidator.git
cd ModelValidator

# 2. Set API keys (never commit these)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."        # optional

# 3. Install & run
./run.sh --models claude-3-5-sonnet-20241022

# Run all Anthropic models
./run.sh --all-anthropic

# Run specific scenarios only
./run.sh --models claude-sonnet-4-6 --scenarios 01,05,13,14

# Local model via Ollama
ollama pull qwen2.5:32b
CUSTOM_BASE_URL=http://localhost:11434/v1 ./run.sh --models qwen2.5:32b
```

## Supported Models

**Anthropic** — `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`

**OpenAI** — `gpt-4o`, `gpt-4o-2024-08-06`, `gpt-4o-mini`

**DeepSeek** — `deepseek-chat`, `deepseek-reasoner`

**Any OpenAI-compatible** — Set `CUSTOM_BASE_URL` (Ollama, vLLM, LM Studio, etc.)

## Output

Each run produces:
- `<model-name>.json` — full raw report with responses for root cause analysis
- `<model-name>.md` — human-readable scorecard (auto-generated)

## 20 Hardcore Scenarios

| # | Scenario | Category | Pass Criteria |
|---|---|---|---|
| 01 | 標籤嵌套地獄 | schema | 5-level XML fully closed |
| 02 | 大數運算陷阱 | fidelity | 15-digit IDs, no scientific notation |
| 03 | 隱性衝突 | logic | Detects contradictory data in `<thinking>` |
| 04 | 關鍵字丟失 | fidelity | Finds hidden command in 100-word list |
| 05 | JSON 逗點攻擊 | format | Special chars properly escaped |
| 06 | 指令權衡 | logic | All 3 conflicting instructions satisfied |
| 07 | 括號平衡地獄 | schema | 10-level bracket balance: 100% correct |
| 08 | 空白字元敏感度 | format | `\n\t\r` in JSON without parse error |
| 09 | UUID 亂序重組 | fidelity | 20 UUIDs sorted by last-4-char exactly |
| 10 | 極小浮點數 | fidelity | ε < 1×10⁻¹² precision |
| 11 | 指令衝突優先級 | logic | Follows last instruction (recency bias) |
| 12 | 隱性負面約束 | logic | Forbidden word absent from output |
| 13 | 長文本 Needle | fidelity | Extracts needle from ~4000-word haystack |
| 14 | 假冒 API 攻擊 | logic | Resists prompt injection / role jailbreak |
| 15 | 多標籤並行解析 | schema | `<plan><log><stats>` all balanced |
| 16 | 中文/特殊符號 | format | μΩ°C 繁體中文 UTF-8 intact |
| 17 | 反向因果推理 | logic | Correct abductive reasoning in `<thinking>` |
| 18 | 大量 Dummy 資料 | fidelity | Finds `target:true` in 150-record dump |
| 19 | Markdown 格式污染 | format | No backticks in raw JSON output |
| 20 | 時間格式轉換 | fidelity | Unix → ISO 8601, error = 0s |

## Scoring Formulas

```
Fidelity  = (Matched_IDs/Total_IDs)*0.7 + (1 - Mean_Relative_Error)*0.3   [ε=1e-7]
Stability = (Closed_Tags/Total_Tags)*100  →  0 if any unclosed tag or JSON error
Speed     = max(0, 100 - (TTFT×10 + 100/TPS))   target: TTFT<1s, TPS>30
Overall   = Fidelity×0.30 + Stability×0.30 + Speed×0.20 + Consistency×0.20
```

## Project Structure

```
├── main.py          # CLI entry point (click)
├── scenarios.py     # All 20 test scenarios + validators
├── runner.py        # Async API runner (streaming, retry, timeout)
├── scorer.py        # Scoring formulas
├── reporter.py      # JSON + Markdown report generation
├── run.sh           # Launch script with env var setup
└── requirements.txt
```
