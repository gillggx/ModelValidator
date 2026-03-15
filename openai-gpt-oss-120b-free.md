# openai/gpt-oss-120b:free — LLM 核心誠信驗證報告

> 測試時間：2026-03-15  |  Spec：v14.0  |  及格線：80

## 總分：0.0 / 100 　❌ FAIL

---

## 維度分數

| 維度 | 分數 | 目標 | 狀態 |
|---|---|---|---|
| 資料保真度 (Fidelity)    | 0.0  | ≥80 | ❌ |
| 結構穩定度 (Stability)   | 0.0 | ≥80 | ❌ |
| 速度評分   (Speed)       | 0.0     | ≥80 | ❌ |
| 邏輯一致性 (Consistency) | 0.0 | ≥80 | ❌ |

## 效能指標

| 指標 | 數值 | 目標 |
|---|---|---|
| TTFT 平均 | 0.00s | < 1.0s |
| TPS 平均  | 0.0 tok/s | > 30 |

---

## 20 個場景明細

| ID | 場景名稱 | 類別 | 分數 | TTFT | 結果 |
|---|---|---|---|---|---|
| 01 | 標籤嵌套地獄 | schema | 0 | 0.00s | 💥 ERROR |
| 02 | 大數運算陷阱 | fidelity | 0 | 0.00s | 💥 ERROR |
| 03 | 隱性衝突 | logic | 0 | 0.00s | 💥 ERROR |
| 04 | 關鍵字丟失 | fidelity | 0 | 0.00s | 💥 ERROR |
| 05 | JSON 逗點攻擊 | format | 0 | 0.00s | 💥 ERROR |
| 06 | 指令權衡 | logic | 0 | 0.00s | 💥 ERROR |
| 07 | 括號平衡地獄 | schema | 0 | 0.00s | 💥 ERROR |
| 08 | 空白字元敏感度 | format | 0 | 0.00s | 💥 ERROR |
| 09 | UUID 亂序重組 | fidelity | 0 | 0.00s | 💥 ERROR |
| 10 | 極小浮點數 | fidelity | 0 | 0.00s | 💥 ERROR |
| 11 | 指令衝突優先級 | logic | 0 | 0.00s | 💥 ERROR |
| 12 | 隱性負面約束 | logic | 0 | 0.00s | 💥 ERROR |
| 13 | 長文本 Needle | fidelity | 0 | 0.00s | 💥 ERROR |
| 14 | 假冒 API 攻擊 | logic | 0 | 0.00s | 💥 ERROR |
| 15 | 多標籤並行解析 | schema | 0 | 0.00s | 💥 ERROR |
| 16 | 中文特殊符號 | format | 0 | 0.00s | 💥 ERROR |
| 17 | 反向因果推理 | logic | 0 | 0.00s | 💥 ERROR |
| 18 | 大量 Dummy 資料掃描 | fidelity | 0 | 0.00s | 💥 ERROR |
| 19 | Markdown 格式污染 | format | 0 | 0.00s | 💥 ERROR |
| 20 | Unix Timestamp 轉換 | fidelity | 0 | 0.00s | 💥 ERROR |

---

## 失敗分析

### Scenario 01 — 標籤嵌套地獄
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 02 — 大數運算陷阱
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 03 — 隱性衝突
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 04 — 關鍵字丟失
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 05 — JSON 逗點攻擊
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 06 — 指令權衡
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 07 — 括號平衡地獄
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 08 — 空白字元敏感度
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 09 — UUID 亂序重組
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 10 — 極小浮點數
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 11 — 指令衝突優先級
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 12 — 隱性負面約束
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 13 — 長文本 Needle
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 14 — 假冒 API 攻擊
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 15 — 多標籤並行解析
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 16 — 中文特殊符號
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 17 — 反向因果推理
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 18 — 大量 Dummy 資料掃描
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 19 — Markdown 格式污染
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

### Scenario 20 — Unix Timestamp 轉換
- **分數**：0 / 100
- **原因**：`Error code: 404 - {'error': {'message': 'No endpoints available matching your guardrail restrictions and data policy. Configure: https://openrouter.ai/settings/privacy', 'code': 404}}`

---

*Generated by LLM Core Integrity Validator v14.0*