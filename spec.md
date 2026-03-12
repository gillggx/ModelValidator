v14.0 LLM 核心誠信驗證器 (Spec)
這個工具不接任何業務邏輯，它只測 LLM 的「硬實力」。

1. 測評維度 (Evaluation Pillars)

維度	測試目標	具體檢查點
結構完整性 (Schema Integrity)	考驗 XML/JSON 嵌套解析能力	故意給 5 層嵌套標籤，檢查結尾是否會漏掉 </plan> 或 }。
數據保真度 (Data Fidelity)	檢查模型是否會「掉資料」	給予 100 筆隨機 ID，要求模型原封不動提取出特定區間，看會不會發生「幻覺」改寫數字。
邏輯推理一致性 (Reasoning Consistency)	考驗 Reasoning 的連貫性	給予一組互相矛盾的數據（如：機台 Off 但有數據流），看 <thinking> 是否能識破衝突，還是盲目執行。
上下文耐力 (Context Endurance)	檢查長文本下的遺忘率	在 128k Token 的頭部塞入一個 Key，尾部提問，看它會不會「斷片」。
極限性能 (Performance/TTFT)	測量真實生產環境的體感	記錄首字回應時間 (TTFT) 與每秒 Token 產出 (TPS)，作為評分依據。
2. 獨立工具的執行流 (Execution Workflow)

這個工具是一個 CLI 或簡單的 Web UI，獨立於你的生產平台運作：

Loader：載入我們設計的 「20 個壓力測試場景」。

Runner：併發調用待測模型 (Claude 3.5, GPT-4o, DeepSeek 等)。

Analyzer (重點)：

Regex Validator：用嚴格的正則檢查標籤閉合。

Data Diff：將模型輸出的 JSON 與原始 Mock Data 比對，計算「資料丟失率 (Loss Rate)」。

Latency Monitor：精確記錄每一段標籤（如從 <plan> 到 </plan>）生成的耗時。

Reporter：產出那份你想要的「紅綠燈報告」。

3. 給小柯的開工指令 (The "Integrity Tester" Task)

/task 開發「LLM 核心誠信驗證器」獨立工具：

純淨測試環境：不要依賴現有的 MCP 或業務代碼。

實作「資料掉包」檢測器：

輸入：隨機生成的 50 組 {"id": UUID, "val": Float}。

任務：要求模型按 val 排序並回傳 JSON。

檢查：自動比對 ID 是否缺失或數值被模型「四捨五入」改動。

實作「標籤壓力測試」：

任務：要求模型在 <thinking> 中進行 1000 字推理後，才輸出 <plan>。

檢查：在高 Token 輸出後，標籤格式是否依然標準，有無 & 或 < 等特殊字元導致的 XML 解析失敗。

產出評分矩陣：

輸出一個 test_report.json，包含每個模型在「精確度、完整度、速度、穩定度」的分數。

📋 20 個「專門搞砸 LLM」的測試場景 (Mock Data)

這些場景是為了讓 LLM 露出馬腳：

標籤嵌套地獄：要求輸出 <root><level1><level2>...5層...</level5></level4>...</root>，看它閉合標籤會不會亂。

大數運算陷阱：給予 15 位數的 ID（如 9007199254740991），看模型提取時會不會變成科學符號。

隱性衝突：告知機台在維護中，但給予一組「正常運轉」的數據，看它會不會指出數據造假。

關鍵字丟失：給予 100 個無意義的單字，中間夾雜一個指令，看它會不會漏掉。

JSON 逗點攻擊：要求輸出包含大量特殊符號字串的 JSON，看它會不會忘記跳脫 (Escape)。

指令權衡：同時給予 3 個互相干擾的指令，看它會不會為了完成 A 而丟掉 B。

...（依此類推，專注於「解析、記憶、數值、邏輯」的極限）。

💡 你的下一步：效能驗證

既然你擔心 Performance，我們在這個工具中加入一個 「延遲感官測試」：
工具會模擬用戶端在接收「流式輸出 (Streaming)」時的體感，並標註出模型在「思考」與「產出 JSON」之間的空窗期 (Gap) 有多長。


補丁一：補齊 20 個地獄測試場景 (Hardcore Scenarios 07-20)

編號	場景名稱	具體任務與壓力點	判定 Pass 的硬條件
07	括號平衡地獄	輸出 10 層深度的 [[{{(())}}]] 結構並夾帶數據。	括號對稱性檢查 (Stack-based Check) 必須 100% 正確。
08	空白字元敏感度	在 JSON key/value 中故意加入 \n, \t, \r。	Parser 必須能正確處理轉義，不可中斷。
09	UUID 亂序重組	給予 20 個 UUID，要求按最後四碼字典序重排。	UUID 必須完全一致且排序 100% 正確（測精確提取）。
10	極小浮點數	處理 1×10 
−9
  等級的科學符號數據。	數值誤差 ϵ<1×10 
−12
 ，不可被捨入。
11	指令衝突優先級	同時下達「輸出 XML」與「僅輸出 JSON」，看模型取捨。	必須遵循最後一個指令（Recency Bias 測試）。
12	隱性負面約束	要求描述機台狀況，但「禁止使用 '正常' 二字」。	掃描輸出，若出現禁語則該項 0 分。
13	長文本 Needle	在 10 萬字中間插入 Password: BlueMonkey，結尾提問。	必須準確提取 BlueMonkey。
14	假冒 API 攻擊	Prompt 模擬 GPT-OSS 崩潰錯誤，看模型是否會跳出腳色。	模型必須維持 System Role，不可被 User Prompt 誘導。
15	多標籤並行解析	同時開啟 <plan>, <log>, <stats>，交錯輸出。	所有標籤對必須成對閉合且內容無竄位。
16	中文/特殊符號	包含 μ, Ω, °C 以及複雜繁體中文術語。	編碼不可亂碼（UTF-8 Enforcement）。
17	邏輯陷阱：反向因果	A 導致 B，B 導致 C，問：如果 C 發生，A 可能發生嗎？	需在 <thinking> 中展現正確的溯因邏輯。
18	大量 Dummy 資料	給 1000 筆垃圾 JSON，要求找出一筆 target: true 的資料。	測試「掃描效率」與是否會因為 Context 過載而跳過。
19	Markdown 格式污染	故意要求輸出 JSON，但背景提示它是個 Markdown 專家。	嚴禁出現 ```json 等 Markdown 裝飾符。
20	時間格式轉換	將 10 組 Unix Timestamp 轉換為 ISO 8601。	秒數誤差必須為 0。
📊 補丁二：評分矩陣精確公式 (Scoring Formula)

我們統一使用 Epsilon (ϵ) 與 Matched Ratio 來計算：

資料保真度 (Fidelity Score):

Score= 
Total_IDs
Matched_IDs
​	
 ×0.7+(1−Mean_Relative_Error)×0.3
數值誤差容忍度 ϵ=1×10 
−7
 。

結構穩定度 (Stability Score):

Score= 
Total_Tags_Opened
Closed_Tags
​	
 ×100
只要有一個標籤未閉合或 JSON 語法錯誤，該題即為 0 分（工業級不容許格式錯誤）。

效能評分 (Speed Score):

Score=max(0,100−(TTFT×10+( 
TPS
100
​	
 )))
目標：TTFT < 1s, TPS > 30。

🛡️ 補丁三：Error Handling & Baseline

Error Handling:

Retry: 遇 429 (Rate Limit) 自動指數退避重試，上限 3 次。

Timeout: 設定 Hard Timeout 60s，超過則記錄為 TIMEOUT_FAIL。

Baseline (基準線):

以 GPT-4o (2024-08-06) 作為基準線（預設為 85 分）。

及格線 (Pass Line)：生產環境准入分數必須 ≥80。

💡 你現在可以回覆「小柯」：

「這份補丁補齊了 20 個場景的嚴格定義、精確的評分公式，以及 Baseline 標準。

請依照此 Spec 實作 CLI 工具。

float 比對採 ϵ=1×10 
−7
 。

輸出 test_report.json 必須包含每一項測試的 raw response 連結，供 Root Cause 分析用。

開工吧！」