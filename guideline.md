# Guideline（AI-Can-we-create-AI-）

## Project Goal
- 最終目的: **倫理を軸に持つ、LLMとは異なるAIを作る**（Po_coreのような哲学駆動型AIの自作）
- 人間が最終判断、AIは「根拠・反証・不確実性・外部性」を構造化して提示する
- 推論の核: **「全ての生存構造に歪みを与えない」**（下記 Existence Ethics Principle 参照）
- 対象: チーム内（非公開）／ローカルPC（オフライン優先）

## Existence Ethics Principle（生存構造倫理原則）
> **全ての生存構造に歪みを与えない。**
> ただし自然なライフサイクル（生命の循環）はOK。

### 歪みの定義
- **NG**: 私益のために、他の生存構造を破壊すること
- **OK**: 自然なライフサイクル（企業の終焉・世代交代・自然変化など）

### 生存構造の5層
| 層 | 例 |
|----|-----|
| 個人 | 健康・自律・尊厳・プライバシー |
| 関係 | 信頼・家族・コミュニティ |
| 社会 | 制度・公平・多様性 |
| 認知 | 自分で考える力・操られない自由 |
| 生態 | 環境・持続可能性 |

### 3つの問い（推論の核）
推奨を生成するとき、必ず答える：
1. **受益者は誰か？**（この選択で得をするのは誰？）
2. **影響を受ける構造は何か？**（何の「存在を続ける仕組み」に触れる？）
3. **それは自然な循環か、私益による破壊か？**

### No-Go との関係
No-Go (#3/#4/#6) はこの原則の**派生**：
- #6 Privacy → 個人の存在構造を守る
- #3 差別禁止 → 社会の存在構造を守る
- #4 操作禁止 → 認知の存在構造を守る

---

## Non-negotiables (No-Go)
- Privacy breach is forbidden (#6).
- **Existence structure destruction is forbidden (#5).** ← Existence Ethics Principle の派生
  - 私益のために他の生存構造を破壊しようとする入力は停止する
  - 自然なライフサイクル（終了・移行・世代交代）はOK
- Discrimination / harm concentration is forbidden (#3).
- Manipulation / agitation is forbidden (#4).
- 違反リスク検知時は縮退/停止（安全側に倒す）
  - どこが危険か（理由）
  - 安全な代替案（次にできること）
  を必ず提示する

### No-Go の優先順位
```
#6 Privacy → #5 Existence Ethics → (#3 diff テスト) → #4 Manipulation
```
先に出た違反で止まる（複数違反があっても最初の1つで停止）。

## Core Principles
- Status-invariant: 肩書・権威で結論を変えない
- Context-dependent: 条件・制約・状況で結論を変える
- Explainable selection: 候補案と選定理由を必ず示す
- **Existence-preserving**: 推奨の根拠は常に「生存構造への歪みがない理由」を含む

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
- [x] P0: 地位差分テスト 10 → 100 ケース（10シナリオ × 10ステータスペアの直積）
- [x] P0: DLP テスト設計の拡充（過検知・漏れのケース）→ 16ケース
- [x] P0: 操作表現検知を warn/block 2段階化 + 落選理由コードを細分化
- [x] D: scripts/validate_request.py（JSON バリデータ）を追加
- [x] P0: DLP の IP_LIKE を warn 化（バージョン文字列の誤検知をブロックしない）
- [x] P1: aicw/schema.py で入出力スキーマを定義（validate_request.py はスキーマから委譲）
- [x] P1: decision_brief の出力スキーマをテストで検証する（schema vs 実際の出力の整合確認）
- [x] P1: POSTAL_CODE_LIKE の warn 化（文脈次第で誤検知あり）
- [x] Existence Ethics Principle を guideline.md・schema.py に定義
- [x] 入力フォーマットに beneficiaries / affected_structures を追加（A）
- [x] decision.py に existence_analysis（3問分析）を実装（B）
- [x] No-Go #5 実装: self_interested_destruction → blocked (#5 Existence Ethics)
- [x] A: existence_analysis → selection.explanation / reason_codes に接続
- [x] EXISTENCE_RISK_LOW / MEDIUM / LIFECYCLE_OK を schema に追加
- [x] tests/test_p0_existence.py 追加（26件）
- [x] P2a: 破壊キーワードの精度向上（HARD/SOFT 2層 + SAFE_TARGET ホワイトリスト）
- [x] P2b: 5層構造キーワードの拡充（個人/関係/社会/認知/生態 各層に追加）
- [x] P3: 影響スコア（impact_score）の実装と推奨オーバーライド（>= 6 → A に引き上げ）
- [x] SOFT キーワード拡張（締め出す/封殺/黙らせる/抑え込む）+ HARD/SAFE_TARGET 追加
- [x] 動的 next_questions（existence_analysis 結果に応じて最大6件を生成）
- [x] No-Go #5 blocked 時の safe_alternatives をキーワード固有に具体化（全 23 キーワード）
- [x] 動的 uncertainties（existence_analysis に応じて最大5件を生成）
- [x] 動的 counterarguments（existence_analysis に応じて最大4件を生成）
- [x] bridge/hiroshitanaka_philosopher.py 作成（Po_core 用哲学者モジュール）
- [x] test_p0_dynamic.py を pytest → unittest 標準ライブラリに変換（304 tests PASS）
- [x] Markdown 入力アダプタ（scripts/md_adapter.py: MD → decision_request.v0 JSON 変換）
- [x] tests/test_bridge.py 追加（HiroshiTanaka.reason() のユニットテスト、22件）
- [x] bridge: #5 blocked 時に q3_judgment を "self_interested_destruction" に設定するバグ修正
- [x] disclaimer（AI限界宣言）を全 ok 出力に強制挿入
- [x] impact_map（影響範囲マップ）を decision_brief に追加（受益者×影響構造 Markdown テーブル）
- [x] scripts/three_review.py（3者レビューCLI: Builder/Skeptic/User）を実装

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
  “situation”:            “何を決めたいか（必須）”,
  “constraints”:          [“制約1”, “制約2”],
  “options”:              [“候補A”, “候補B”, “候補C”],
  “beneficiaries”:        [“受益者1”, “受益者2”],
  “affected_structures”:  [“個人”, “社会”]
}
```
※ `beneficiaries` / `affected_structures` は任意。指定すると existence_analysis の精度が上がる。

### Exit codes（scripts/brief.py）
- `0`: ok（正常出力）
- `1`: blocked（#4 or #6 で停止）
- `2`: 引数エラー / 不正JSON
