# 既存ファイルがある場合は上書きしません
set -e

mkdir -p scripts

# --- guideline.md ---
if [ ! -f guideline.md ]; then
cat > guideline.md <<'EOF'
# Guideline（AI-Can-we-create-AI-）

## Project Goal
- 最終目的: Po_core に取り込める「意思決定支援AI」に近づける
- 方針: 人間が最終判断。AIは「根拠・反証・不確実性・外部性」を構造化して提示する

## Non-negotiables (No-Go)
- Privacy breach is forbidden (#6).
- Discrimination / harm concentration is forbidden (#3).
- Manipulation / agitation is forbidden (#4).
- 違反リスク検知時は縮退/停止（安全側に倒す）

## Core Principles
- Status-invariant: 肩書・権威で結論を変えない
- Context-dependent: 条件・制約・状況で結論を変える
- Explainable selection: 候補案と選定理由を必ず示す

## Security Defaults
- Offline-first（外部ネットワーク/外部APIはデフォルト禁止）
- ログ最小化（個人情報・秘密情報・トークン等は書かない）
- 外部連携が必要な場合は「理由・代替案・影響・必要な秘密情報の有無」を先に説明し、明示許可を取る

## Repo Working Rules
- 変更は小さく、検証手順（コマンド + 期待結果）を必ず残す
- セッションの最後に progress_log.md と Current Next Actions を必ず更新
- アイデアは idea_note.md に集約
- 大きな変更（設計/依存関係/フォルダ構成/安全方針など）は 3レビューで進める:
  - Builder: 実装案と理由
  - Skeptic: 反証・リスク・代替案
  - User: 最終決定（Yes/Noで答えられる形）

## Decision Brief Format (v0)
> AIが出力する「意思決定メモ」の最小フォーマット（まずはこれで統一）

- **Question**: 何を決めたいか（1行）
- **Context**: 前提・制約（箇条書き）
- **Options**: 選択肢A/B/C
  - 各選択肢に「メリット」「デメリット」「コスト（時間/手間）」「安全・倫理リスク」「不確実性」
- **Recommendation**: 推奨案 + 選定理由（短く）
- **Counterarguments**: 反証/懸念と、それでも推すなら条件
- **Next check**: すぐできる検証（1〜3個）
- **Confidence**: 自信（高/中/低）と理由

## Safety Checklist (毎回)
- [ ] 個人情報/秘密情報を扱っていない
- [ ] 差別の助長や特定集団への害の集中につながらない
- [ ] 操作・扇動（感情を煽って誘導）になっていない
- [ ] 外部ネットワーク/外部APIを使う場合は許可を取った

## Current Next Actions
- [ ] README.md とリポジトリ構造を把握（主要フォルダ/起動方法/入口）
- [ ] Decision Brief のサンプルを1つ作り、入出力を固定する（まずはテキストでOK）
- [ ] Po_core へ持ち込む最小インターフェース（入力=何、出力=何）を決める

## How to run / test
- {HOW_TO_RUN_OR_TBD}
EOF
echo "created: guideline.md"
else
echo "skip (exists): guideline.md"
fi

# --- progress_log.md ---
if [ ! -f progress_log.md ]; then
cat > progress_log.md <<'EOF'
# Progress Log
> 各セッションの最後に追記（可能なら日付はJST、形式はYYYY-MM-DD）

## 2026-02-22
### Goal
- リポジトリ運用の「単一の真実」4ファイルを揃え、次の一手を固定する

### Done
- guideline.md / progress_log.md / idea_note.md / coding-style.md のテンプレを用意
- guideline.md に Decision Brief Format(v0) と Safety Checklist を追加
- scripts/check_repo_health.sh を追加（必須ファイルの存在チェック）

### Decisions
- 運用の単一の真実は 4ファイル（guideline / progress_log / idea_note / coding-style）に集約する
- 外部ネットワーク/外部APIはデフォルト禁止（必要時は理由と代替案を提示して許可を取る）

### Risks / Unknowns
- README.md と既存コードの現状が未確認（次回、構造と起動方法を把握する）
- 実装言語/ランタイムが確定していない（coding-style.md は暫定）

### Next
- README.md とリポジトリ構造を共有してもらい、最小MVPを切り出す
- Decision Brief の入出力フォーマット（テキスト/JSON/YAMLなど）を決める
EOF
echo "created: progress_log.md"
else
echo "skip (exists): progress_log.md"
fi

# --- idea_note.md ---
if [ ! -f idea_note.md ]; then
cat > idea_note.md <<'EOF'
# Idea Notes
> 思いつき/提案/将来の改善案のメモ。採用・保留・却下を残す。

## Backlog
- [ ] (2026-02-22) Idea: Decision Brief を JSON でも出せるようにする（Po_core取り込み用）
  - Source: AI
  - Why: Po_core側が機械処理しやすくなる（評価・ログ・比較が簡単）
  - Notes: まずはテキスト版v0を作り、次に JSON schema を固める
  - Status: backlog

- [ ] (2026-02-22) Idea: オフライン評価用の「小さな意思決定シナリオ集」を作る
  - Source: AI
  - Why: 出力がブレた時に回帰テスト（前より悪くなってないか確認）ができる
  - Notes: 10本くらいの短いケース（制約/選択肢/正解は1つでなくてOK）を用意
  - Status: backlog
EOF
echo "created: idea_note.md"
else
echo "skip (exists): idea_note.md"
fi

# --- coding-style.md ---
if [ ! -f coding-style.md ]; then
cat > coding-style.md <<'EOF'
# Coding Style

## Formatter / Linter Versions
- Language: Python（暫定）
- Runtime/Version: Python 3.11（暫定）
- black: 23.12.1
- isort: 5.12.0
- ruff: 0.3.0
- mypy: 1.8.0

## Black
- line length: 88
- target-version: py311（暫定）

## isort
- profile: black
- line_length: 88

## Ruff
- select: ["E", "F", "I"]
- ignore: ["E501"]

## Import Order
1. Standard library
2. Third-party
3. Local modules

## Naming Rules
- functions: snake_case
- classes: PascalCase
- constants: UPPER_CASE

## Docstring
- Google style
EOF
echo "created: coding-style.md"
else
echo "skip (exists): coding-style.md"
fi

# --- scripts/check_repo_health.sh ---
if [ ! -f scripts/check_repo_health.sh ]; then
cat > scripts/check_repo_health.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# リポジトリ直下で実行されても、scripts配下で実行されても動くようにする
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required_files=(
  "guideline.md"
  "progress_log.md"
  "idea_note.md"
  "coding-style.md"
)

recommended_files=(
  "README.md"
)

missing_required=0

echo "== Required files =="
for f in "${required_files[@]}"; do
  if [ -f "$f" ]; then
    echo "OK:      $f"
  else
    echo "MISSING: $f"
    missing_required=1
  fi
done

echo
echo "== Recommended files =="
for f in "${recommended_files[@]}"; do
  if [ -f "$f" ]; then
    echo "OK:      $f"
  else
    echo "WARN:    $f (recommended)"
  fi
done

echo
if [ "$missing_required" -ne 0 ]; then
  echo "Result: NG (required files missing)"
  exit 1
else
  echo "Result: OK"
fi
EOF
chmod +x scripts/check_repo_health.sh
echo "created: scripts/check_repo_health.sh"
else
echo "skip (exists): scripts/check_repo_health.sh"
fi

echo
echo "Bootstrap done."
echo "Next: bash scripts/check_repo_health.sh"

## How to run (offline)
### Run tests
- `python -m unittest -v`

### Run demo
- `python run_demo.py`

※注意: 個人情報/機密は入力しない（実名・連絡先・住所・IDなどは禁止）
