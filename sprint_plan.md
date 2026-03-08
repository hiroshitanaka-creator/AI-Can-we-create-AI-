# 2週間スプリント実行計画（Codex実装用）

## スプリント目標
- 安全性・一貫性・再現性を「研究段階」から「運用手前」へ引き上げる。
- 既存の decision_brief パイプラインを壊さず、テスト駆動で機能追加する。

## 優先順位（高→低）
1. ファジングテスト自動生成基盤
2. 同一入力の一貫性（自己矛盾）検知
3. 文化差分テストデータセット整備
4. 事後検証テンプレート自動生成
5. 文脈圧縮機能（長文入力）
6. anti-manipulation の動的チェック強化
7. 不確実性マップ（ツリー）出力
8. 哲学的矛盾検知モジュール
9. 哲学者アンサンブル（軽量）
10. Po_core 統合インターフェース v0.1 固定

---

## Week 1（実装の土台を固める）

### Task 1（P0）: ファジングテスト自動生成基盤
- **目的**: DLP / status-invariant / manipulation の境界ケースを網羅的に検出する。
- **追加ファイル**:
  - `scripts/gen_fuzz_cases.py`
  - `tests/test_fuzz_smoke.py`
  - `tests/data/fuzz_seed_cases.json`
- **DoD**:
  - 1000件生成を5秒以内で完了（ローカル目安）
  - 既存テストを壊さない
  - smokeテストで生成物のスキーマ整合を確認
- **Codex実装プロンプト**:
  - 「標準ライブラリのみで fuzz case 生成器を追加し、decision_request.v0 準拠のケースを出力。ランダム種を固定できるCLIにしてください」

### Task 2（P0）: 同一入力の一貫性（自己矛盾）検知
- **目的**: 同一入力で recommendation や reason_codes が揺れないことを保証。
- **追加ファイル**:
  - `tests/test_consistency.py`
  - （必要なら）`scripts/check_consistency.py`
- **DoD**:
  - 同一入力100回実行でハッシュ一致
  - 差分時は最小診断情報を表示
- **Codex実装プロンプト**:
  - 「同一 request を複数回流して出力安定性を検証するテストを追加。失敗時は差分キーを列挙してください」

### Task 3（P1）: 文化差分テストデータセット整備
- **目的**: status-invariant を保持しつつ context-dependent な差分を検証。
- **追加ファイル**:
  - `tests/data/culture_cases.json`
  - `tests/test_culture_diff.py`
- **DoD**:
  - JP/US/EU 3系列 × 同一論点で期待条件を定義
  - 地位ラベル差し替えで recommendation が不変
- **Codex実装プロンプト**:
  - 「文化差分データセットを作成し、statusラベル変更に対する不変性を検証するテストを追加してください」

### Task 4（P1）: 事後検証テンプレート自動生成
- **目的**: 意思決定後の振り返りを運用可能な形式に統一。
- **追加ファイル**:
  - `scripts/postmortem_template.py`
  - `tests/test_postmortem_template.py`
- **DoD**:
  - recommendation / next_questions から 30/60/90日チェック項目を自動生成
  - blocked時のテンプレ分岐を実装
- **Codex実装プロンプト**:
  - 「decision_brief から事後検証テンプレートを生成するCLIを追加。ok/blockedで出力を分け、テストも追加してください」

### Task 5（P1）: 文脈圧縮機能（長文入力）
- **目的**: 長文 situation の情報密度を維持したまま処理可能にする。
- **追加ファイル**:
  - `aicw/context_compress.py`
  - `tests/test_context_compress.py`
- **DoD**:
  - 重要語保持率のルールを明示（例: キーワード保持）
  - 圧縮ON/OFFを切替可能
- **Codex実装プロンプト**:
  - 「外部依存なしで長文 situation 圧縮ユーティリティを追加し、保持ルールをテストで固定してください」

---

## Week 2（安全性と説明性を拡張）

### Task 6（P1）: anti-manipulation の動的チェック強化
- **目的**: 単純キーワード一致から文脈スコア併用へ。
- **追加ファイル**:
  - `aicw/safety.py`（拡張）
  - `tests/test_p0_manipulation.py`（拡張）
- **DoD**:
  - warn/block の閾値ルールを明文化
  - 誤検知/見逃しケースを各10件以上追加
- **Codex実装プロンプト**:
  - 「scan_manipulation にスコアリングを追加し、warn/block判定を段階化。既存仕様を壊さずテスト拡張してください」

### Task 7（P2）: 不確実性マップ（ツリー）出力
- **目的**: uncertainties を構造化し、意思決定リスクを可視化。
- **追加ファイル**:
  - `scripts/uncertainty_map.py`
  - `tests/test_uncertainty_map.py`
- **DoD**:
  - decision_brief から Mermaid風テキストを生成
  - ノード上限と深さ上限を設定
- **Codex実装プロンプト**:
  - 「uncertainties配列をツリー化してテキスト出力するCLIを追加。循環防止と上限管理を実装してください」

### Task 8（P2）: 哲学的矛盾検知モジュール
- **目的**: 説明文中の規範矛盾を早期警告。
- **追加ファイル**:
  - `aicw/philosophy_check.py`
  - `tests/test_philosophy_check.py`
- **DoD**:
  - 最低3系統（義務論/功利/公正）で矛盾パターン検知
  - 警告理由コードを返す
- **Codex実装プロンプト**:
  - 「簡易ルールベースで哲学的矛盾検知を追加し、reason code を返す関数とテストを作成してください」

### Task 9（P2）: 哲学者アンサンブル（軽量）
- **目的**: 多視点レビューを bridge 層で疑似再現。
- **追加ファイル**:
  - `bridge/ensemble.py`
  - `tests/test_ensemble.py`
- **DoD**:
  - 3〜5哲学者テンプレートで賛否・保留を集約
  - minority report を必ず出力
- **Codex実装プロンプト**:
  - 「外部依存なしで哲学者アンサンブルを実装し、多数派意見と少数意見を返す設計にしてください」

### Task 10（P2）: Po_core 統合インターフェース v0.1 固定
- **目的**: 将来統合時の破壊的変更を防止。
- **追加ファイル**:
  - `docs/api_contract_v0_1.md`
  - `tests/test_api_contract.py`
- **DoD**:
  - 入出力契約（必須キー・enum・exit code）を明記
  - 契約逸脱を検知するテストを追加
- **Codex実装プロンプト**:
  - 「現行 schema/CLI に基づき API 契約書 v0.1 を作成し、契約テストを追加してください」

---

## 実行順（Codex用コマンド）
```bash
# 0) ブランチ作成
# git checkout -b sprint/2026wXX-hardening

# 1) Week1 P0
PYTHONPATH=. pytest -q tests/test_fuzz_smoke.py tests/test_consistency.py

# 2) Week1 P1
PYTHONPATH=. pytest -q tests/test_culture_diff.py tests/test_postmortem_template.py tests/test_context_compress.py

# 3) Week2 P1/P2
PYTHONPATH=. pytest -q tests/test_p0_manipulation.py tests/test_uncertainty_map.py tests/test_philosophy_check.py tests/test_ensemble.py tests/test_api_contract.py

# 4) 最終回帰
PYTHONPATH=. pytest -q
```

## リスクと回避策
- **リスク**: ルール追加で誤検知が増える
  - **回避**: warn/block 2段階 + 回帰テスト強化
- **リスク**: 機能追加で仕様が拡散
  - **回避**: schema 契約テストと API 文書を先に固定
- **リスク**: 実装過多で2週間を超過
  - **回避**: P0/P1 を Week1で必達、P2は優先順で打ち切り可能に設計
