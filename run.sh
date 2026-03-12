#!/usr/bin/env bash
# LLM Core Integrity Validator — 啟動腳本
# 使用方式:
#   ./run.sh                          # 預設跑單一模型
#   ./run.sh --all-anthropic          # 一次跑全部 5 個 Anthropic 模型
#   ./run.sh --models <m1,m2>         # 指定模型
#   ./run.sh --scenarios 01,05,13     # 指定場景
#   ./run.sh --output my_report.json  # 指定輸出
set -euo pipefail

# ──────────────────────────────────────────────
# 環境變數（填入你的 API Keys）
# ──────────────────────────────────────────────
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-your-anthropic-api-key-here}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}"
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-your-deepseek-api-key-here}"
# 自架 OpenAI-compatible 模型（vLLM / Ollama / LM Studio / GPT-OSS 等）
# 填入後即可用 --models <model-name> 測試，CUSTOM_API_KEY 若不需驗證可留空
export CUSTOM_BASE_URL="${CUSTOM_BASE_URL:-}"           # e.g. http://localhost:8000/v1
export CUSTOM_API_KEY="${CUSTOM_API_KEY:-not-required}" # e.g. ollama / sk-xxx

# ──────────────────────────────────────────────
# 全部 Anthropic 模型清單
# ──────────────────────────────────────────────
ANTHROPIC_ALL="claude-opus-4-6,claude-sonnet-4-6,claude-haiku-4-5-20251001,claude-3-5-sonnet-20241022,claude-3-5-haiku-20241022"

# ──────────────────────────────────────────────
# 預設參數
# ──────────────────────────────────────────────
MODELS="claude-3-5-sonnet-20241022"
SCENARIOS="all"
OUTPUT="test_report.json"
CONCURRENCY=3   # 多模型時調低，避免 rate limit

# 解析命令列參數
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all-anthropic) MODELS="$ANTHROPIC_ALL"; shift ;;
    --models)        MODELS="$2";             shift 2 ;;
    --scenarios)     SCENARIOS="$2";          shift 2 ;;
    --output)        OUTPUT="$2";             shift 2 ;;
    --concurrency)   CONCURRENCY="$2";        shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# ──────────────────────────────────────────────
# 路徑
# ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# ──────────────────────────────────────────────
# 確認 venv 存在，否則自動建立
# ──────────────────────────────────────────────
if [[ ! -f "$VENV_PYTHON" ]]; then
  echo ">>> venv not found, creating..."
  python3 -m venv "$SCRIPT_DIR/.venv"
  "$SCRIPT_DIR/.venv/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
  echo ">>> Dependencies installed."
fi

# ──────────────────────────────────────────────
# 印出當前設定（隱藏 key 後半段）
# ──────────────────────────────────────────────
mask() {
  local val="$1"
  if [[ ${#val} -le 8 || "$val" == *"your-"* ]]; then
    echo "(not set)"
  else
    echo "${val:0:8}****${val: -4}"
  fi
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   LLM Core Integrity Validator v14.0             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  [ENV]"
echo "  ANTHROPIC_API_KEY : $(mask "$ANTHROPIC_API_KEY")"
echo "  OPENAI_API_KEY    : $(mask "$OPENAI_API_KEY")"
echo "  DEEPSEEK_API_KEY  : $(mask "$DEEPSEEK_API_KEY")"
echo "  CUSTOM_BASE_URL   : ${CUSTOM_BASE_URL:-(not set)}"
echo "  CUSTOM_API_KEY    : $(mask "${CUSTOM_API_KEY:-}")"
echo ""
echo "  [CONFIG]"
echo "  Models      : $MODELS"
echo "  Scenarios   : $SCENARIOS"
echo "  Output      : $OUTPUT"
echo "  Concurrency : $CONCURRENCY"
echo ""

# ──────────────────────────────────────────────
# 執行
# ──────────────────────────────────────────────
cd "$SCRIPT_DIR"
"$VENV_PYTHON" main.py run \
  --models "$MODELS" \
  --scenarios "$SCENARIOS" \
  --output "$OUTPUT" \
  --concurrency "$CONCURRENCY"
