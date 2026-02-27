# Guideline（AI-Can-we-create-AI-）

## Project Goal
- 最終目的: Po_core に取り込める「意思決定支援AI」に近づける
- 人間が最終判断、AIは「根拠・反証・不確実性・外部性」を構造化して提示する
- 対象: チーム内（非公開）／ローカルPC（オフライン優先）

## Non-negotiables (No-Go)
- Privacy breach is forbidden (#6).
- Discrimination / harm concentration is forbidden (#3).
- Manipulation / agitation is forbidden (#4).
- 違反リスク検知時は縮退/停止（安全側に倒す）
  - どこが危険か（理由）
  - 安全な代替案（次にできること）
  を必ず提示する

## Core Principles
- Status-invariant: 肩書・権威で結論を変えない
- Context-dependent: 条件・制約・状況で結論を変える
- Explainable selection: 候補案と選定理由を必ず示す

## Security Defaults
- Offline-first（外部ネットワーク/外部APIはデフォルト禁止）
- どうしても外部連携が必要な場合は、実施前に
  - 理由 / 代替案 / 影響 / 必要な秘密情報の有無
  を説明し、ユーザーの明示許可を取る
- ログ最小化（PII/秘密情報/トークン等は絶対に書かない）

## Repo Working Rules（迷子防止）
- SSOT（単一の真実）は次の4ファイル:
  - guideline.md
  - progress_log.md
  - idea_note.md
  - coding-style.md
- 変更は小さく、検証手順（コマンド＋期待結果）を必ず残す
- セッションの最後に必ず更新する:
  1) progress_log.md（今日の進捗＋次回やること）
  2) guideline.md の Current Next Actions（矛盾させない）
  3) idea_note.md（新アイデアが出たら追記）
  4) coding-style.md（規約/ツールを決めたら更新）

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
- [ ] 個人情報/秘密情報を扱っていない（#6）
- [ ] 差別の助長や特定集団への害の集中につながらない（#3）
- [ ] 操作・扇動（感情を煽って誘導）になっていない（#4）
- [ ] 外部ネットワーク/外部APIを使う場合は許可を取った

## 3-Review Rule（大きな変更のみ）
- Builder: 実装案と理由
- Skeptic: 反証・リスク・代替案
- User: 最終決定（Yes/Noで答えられる形）

## Current Next Actions
- [x] Decision Brief の入出力（JSON/Markdown）を最小で確定 → scripts/brief.py
- [x] aicw/ と tests/ の現状把握
- [x] P0: 地位差分テスト10ケース（安全重視/スピード重視/バランス × 多様な肩書ペア）
- [ ] P0: DLP テスト設計の拡充（過検知・漏れのケースを追加）
- [ ] P0: 操作表現検知の閾値と縮退挙動を調整する

## How to run / test

```bash
# テスト（全件）
python -m unittest discover -s tests -v

# Decision Brief CLI（JSON stdin）
echo '{“situation”:”...”,”constraints”:[“安全”],”options”:[“案A”,”案B”,”案C”]}' \
  | python scripts/brief.py

# Decision Brief CLI（JSONファイル）
python scripts/brief.py path/to/request.json

# 対話デモ
python run_demo.py
```

### Input JSON format
```json
{
  “situation”:   “何を決めたいか（必須）”,
  “constraints”: [“制約1”, “制約2”],
  “options”:     [“候補A”, “候補B”, “候補C”]
}
```

### Exit codes（scripts/brief.py）
- `0`: ok（正常出力）
- `1`: blocked（#4 or #6 で停止）
- `2`: 引数エラー / 不正JSON
