# Progress Log
> 各セッションの最後に追記（可能なら日付はJST、形式はYYYY-MM-DD）

## 2026-03-09 (session 16 — Ensemble Review CLI 追加)

### Goal
- Task9 の実運用導線として、ensemble を単体実行できる CLI を追加する

### Done
- `scripts/ensemble_review.py`（新規）:
  - 入力: request JSON（stdin/ファイル）
  - `build_decision_report` で blocked 判定を先に実施
  - ok 時は `run_ensemble(prompt)` を実行し、majority/minority/all opinions を Markdown 風で出力
  - blocked 時は理由と safe_alternatives を出力して exit code 1
  - exit code 0/1/2（ok / blocked / invalid）
- `tests/test_ensemble_review_cli.py`（新規）: 4件追加
  - ok 時の exit 0
  - 出力に Majority/Minority を含む
  - blocked 時の exit 1 + BLOCKED 表示
  - 不正JSONで exit 2
- `guideline.md`:
  - Current Next Actions に CLI 追加完了を追記

### Test Results
- `python -m unittest -v tests.test_ensemble_review_cli` PASS
- `python -m unittest discover -s tests -v` PASS

---

## 2026-03-09 (session 15 — three_review に Ensemble セクション統合)

### Goal
- 既存の Task9（bridge/ensemble.py）を three_review CLI 出力に接続し、多視点レビューを実際に利用可能にする

### Done
- `scripts/three_review.py`:
  - `run_ensemble` を取り込み、`build_ensemble_section(report)` を追加
  - `format_three_review()` に `🧠 Ensemble（多視点レビュー）` セクションを追加
  - 多数派（stance/members）と少数意見（minority report）を表示
- `tests/test_p1_features.py`:
  - `TestThreeReviewEnsemble` を追加（2件）
    - Ensemble セクションが出力に含まれる
    - 多数派・minority report 文言が含まれる
- `guideline.md`:
  - Current Next Actions に統合作業の完了を追記

### Test Results
- `python -m unittest -v tests.test_p1_features` PASS
- `python -m unittest discover -s tests -v` PASS

---

## 2026-03-09 (session 14 — Task8統合: PHILO reason_codes を Decision Brief に接続)

### Goal
- 追加済みの哲学矛盾検知モジュールを `build_decision_report()` に統合し、実出力で利用可能にする

### Done
- `aicw/decision.py`:
  - `detect_philosophy_conflicts` を import
  - `selection.explanation` 生成後に `situation + explanation` を検査し、`PHILO_*` を `selection.reason_codes` へ追記
  - 重複コードは追加しないように制御
- `aicw/schema.py`:
  - `reason_codes.selection` に `PHILO_DUTY_OUTCOME_CONFLICT` / `PHILO_FAIRNESS_EFFICIENCY_CONFLICT` /
    `PHILO_RIGHTS_TOTAL_BENEFIT_CONFLICT` を追加
- `tests/test_philosophy_check.py`:
  - integration test を追加（`build_decision_report` 経由で `PHILO_DUTY_OUTCOME_CONFLICT` が反映されることを確認）
- `guideline.md`:
  - Current Next Actions に Task8統合完了を追記

### Test Results
- `python -m unittest -v tests.test_philosophy_check` PASS
- `python -m unittest discover -s tests -v` PASS

---

## 2026-03-09 (session 13 — Task 10: API契約 v0.1 固定)

### Goal
- Week2 Task10（P2）: 現行 schema/CLI を基準に API 契約書を固定し、逸脱検知テストを追加する

### Done
- `docs/api_contract_v0_1.md`（新規）:
  - request/response/CLI の固定契約（必須キー・enum・exit code）を明文化
  - `blocked_by` の許容値（#6/#5/#4）を明記
  - 変更時は契約書と契約テストを同時更新する運用を明記
- `tests/test_api_contract.py`（新規）: 9件追加
  - request契約（必須・allowed・未知キー拒否）
  - response契約（status enum / blocked_by_values）
  - 実行時契約（ok/blocked の必須キー）
  - CLI契約（exit code 0/1/2）
- `guideline.md`:
  - Sprint Plan進捗に Week2 Task10 完了を反映

### Test Results
- `python -m unittest -v tests.test_api_contract` PASS
- `python -m unittest discover -s tests -v` PASS

---

## 2026-03-09 (session 12 — Task 9: 哲学者アンサンブル)

### Goal
- Week2 Task9（P2）: bridge 層で軽量な哲学者アンサンブルを実装し、多数派と少数意見を返す

### Done
- `bridge/ensemble.py`（新規）:
  - `run_ensemble(prompt, context=None)` を追加
  - 3哲学者テンプレート（HiroshiTanaka / Pragmatist / RightsGuardian）で意見生成
  - 出力: `opinions` / `majority` / `minority_report`
  - 全会一致時でも `SystemMinority` を補完して少数意見を常に返す
- `tests/test_ensemble.py`（新規）: 5件追加
  - 必須キー、3テンプレート、majority構造、minority常時出力、リスク文脈で oppose を検証
- `guideline.md`:
  - Sprint Plan進捗に Week2 Task9 完了を反映

### Test Results
- `python -m unittest -v tests.test_ensemble` PASS
- `python -m unittest discover -s tests -v` PASS

---


## 2026-03-09 (session 11 — Task 8: 哲学的矛盾検知モジュール)

### Goal
- Week2 Task8（P2）: 説明文中の規範矛盾を簡易ルールで検知し、reason code を返す

### Done
- `aicw/philosophy_check.py`（新規）:
  - `detect_philosophy_conflicts(text)` を追加
  - 3系統の矛盾パターンを reason code で返却
    - `PHILO_DUTY_OUTCOME_CONFLICT`（義務論 vs 功利）
    - `PHILO_FAIRNESS_EFFICIENCY_CONFLICT`（公正 vs 効率）
    - `PHILO_RIGHTS_TOTAL_BENEFIT_CONFLICT`（権利 vs 総便益）
  - 逆接（だが/しかし/一方で）と例外語を組み合わせた軽量判定
- `tests/test_philosophy_check.py`（新規）: 5件追加
  - 空入力 / 3系統の検知 / 非検知ケース
- `aicw/__init__.py`:
  - `detect_philosophy_conflicts` を公開APIに追加
- `guideline.md`:
  - Sprint Plan進捗に Week2 Task8 完了を反映

### Test Results
- `python -m unittest -v tests.test_philosophy_check` PASS
- `python -m unittest discover -s tests -v` PASS

---

## 2026-02-28 (session 9 — 整理 + Markdown アダプタ + bridge テスト)

### Goal
- A: guideline.md / idea_note.md を現状に同期（完了済みを [x] に）
- B: Markdown 入力アダプタ（scripts/md_adapter.py）を実装
- C: bridge/hiroshitanaka_philosopher.py のユニットテスト（tests/test_bridge.py）を追加
- D: test_p0_dynamic.py を pytest → unittest 標準ライブラリに変換（前セッションの残課題）

### Done
- `tests/test_p0_dynamic.py`:
  - `import pytest` を削除、`import unittest` に変更
  - 4クラス（TestDynamicNextQuestions / TestBlockedAlternatives / TestDynamicUncertainties / TestDynamicCounterarguments）を `unittest.TestCase` に変更
  - 標準ライブラリのみ方針に準拠（外部依存なし）
- `guideline.md` Current Next Actions:
  - P2a/P2b（キーワード拡充）/ P3（impact_score）/ SOFT拡張 / 動的生成4種 / bridge を [x] に更新
  - 残タスクとして Markdown アダプタ / bridge テストを追加
- `idea_note.md`:
  - Po_core カーネル / 地位差分テスト / JSON バリデータを [x] に更新
  - Markdown アダプタを「実装予定（session 9）」に更新
- `scripts/md_adapter.py`（新規）:
  - Markdown → decision_request.v0 JSON 変換アダプタ
  - フィールド: situation（必須）/ constraints / options / beneficiaries / affected_structures
  - `#` セクションヘッダ、`-` / `*` 箇条書き、空行・未知セクション無視
  - exit code 0/1/2（成功 / situation 空 / 引数エラー）
  - パイプ対応: `cat request.md | python scripts/md_adapter.py | python scripts/brief.py`
- `tests/test_md_adapter.py`（新規）: 20件追加
  - TestConvertSituation (4件) / TestConvertLists (6件) / TestConvertFullInput (1件) / TestConvertEdgeCases (4件) / TestCLI (4件)
- `bridge/hiroshitanaka_philosopher.py`:
  - バグ修正: aicw が #5 Existence Ethics でブロックした場合に `q3_judgment` を "self_interested_destruction" に設定（以前は "unclear" のままになっていた）
- `tests/test_bridge.py`（新規）: 22件追加
  - TestHiroshiTanakaBasic (6件) / TestQuestionLegitimacy (3件) / TestExistenceStructure (4件) / TestArroganceCheck (3件) / TestMarginsAndResonance (5件) / TestContextPassthrough (2件) - 傲慢さマーカーのテストプロンプトを「絶対に」に修正（「間違いなく」はマーカー外）

### Test Results
- 346 tests PASS (304 → 346, +42)

---


## 2026-02-28 (session 10 — P1三本柱: disclaimer + impact_map + three_review)

### Goal
- A: AI限界宣言（disclaimer）を全 ok 出力に強制挿入
- B: 影響範囲マップ（impact_map）を decision_brief に追加
- C: 3者レビューCLI（scripts/three_review.py）を実装

### Done
- `aicw/decision.py`:
  - `_DISCLAIMER` 定数: 「⚠ この出力は参考情報です。最終判断は人間が行ってください。AIは…」
    - 「必ず」を除去（manipulation warn 発火を回避）
  - `_build_impact_map(existence_analysis)`: 受益者 × 影響構造 の Markdown テーブル生成
    - 受益者・構造が判明している場合のみテーブル化、不明時はメッセージ返却
  - `build_decision_report()`: `impact_map` / `disclaimer` フィールドを ok 時に追加
  - `format_report()`: `[Impact Map]` / `[Disclaimer]` セクションを末尾に追加
- `aicw/schema.py`: `impact_map` / `disclaimer` フィールドを DECISION_BRIEF_V0 に追記
- `scripts/three_review.py`（新規）:
  - Builder（推進者）/ Skeptic（懐疑論者）/ User（最終判断者）の 3 視点を自動生成
  - impact_map・next_questions・disclaimer を User セクションに組み込み
  - blocked 時は ⛔ BLOCKED セクションのみ表示
  - パイプ対応: `cat req.md | python scripts/md_adapter.py | python scripts/three_review.py`
  - exit code 0/1/2（ok / blocked / エラー）
- `tests/test_p1_features.py`（新規）: 32件追加
  - TestDisclaimer (5件) / TestImpactMap (8件)
  - TestThreeReviewStructure (6件) / TestThreeReviewBuilder (3件)
  - TestThreeReviewSkeptic (3件) / TestThreeReviewUser (4件) / TestThreeReviewBlocked (3件)

### Test Results
- 378 tests PASS (346 → 378, +32)

---

## 2026-02-28 (session 8 — uncertainties + counterarguments の動的化)

### Goal
- `uncertainties` を existence_analysis に応じて動的生成
- `counterarguments` を existence_analysis に応じて動的生成

### Done
- `aicw/decision.py`:
  - `_build_uncertainties(existence_analysis, constraints)`: 最大 5 件を動的生成
    - 常時: 成功の定義
    - 受益者不明 → 利害の不確実性
    - 構造不明 → 外部性見積もり不足 / 構造既知 → 失敗した場合の被害
    - distortion_risk=medium → 歪みリスク中程度の不確実性
    - impact_score >= 4 → 複数層の外部性
    - 制約なし → 基準未確定
  - `_build_counterarguments(existence_analysis)`: 最大 4 件を動的生成
    - 常時: 前提が足りない
    - 受益者不明 → 意図しない損者リスク
    - 構造不明 → 外部性の反論 / 構造既知 → 短期最適化の反論
    - distortion_risk=medium → 誰の私益か（優先）
    - judgment=lifecycle → 移行への配慮（次優先）
    - impact_score >= 4 → 段階的実施（その次）
  - `build_decision_report()`: static を両関数で置換
- `tests/test_p0_dynamic.py`: TestDynamicUncertainties (15件) + TestDynamicCounterarguments (13件) 追加

### Test Results
- 304 tests PASS (276 → 304, +28)

---

## 2026-02-28 (session 7 — 動的 next_questions + blocked 代替案の具体化)

### Goal
- A: `next_questions` を existence_analysis 結果に応じて動的生成
- B: No-Go #5 blocked 時の `safe_alternatives` をキーワード固有に具体化

### Done
- `aicw/decision.py`:
  - `_DESTRUCTION_ALTERNATIVES`: HARD/SOFT 全キーワード（23件）→ 再フレーミング提案の辞書
  - `_EXISTENCE_ALTERNATIVES_STANDARD`: 標準代替案 3 件（定数化）
  - `_build_existence_alternatives(detected_kws)`: 先頭 2 件のキーワード固有提案 + 標準 3 件
  - `_build_next_questions(existence_analysis, constraints)`: 最大 6 件を動的生成
    - 常時: 成功の定義 / 最悪シナリオ
    - 受益者不明 → 受益者を尋ねる
    - 構造不明 → 構造を尋ねる / 構造既知 → チーム外への影響を尋ねる
    - distortion_risk == medium → 誰の私益か
    - judgment == lifecycle → 移行支援計画
    - impact_score >= 4 (且つ上記以外) → 緩和策
    - 制約なし → 制約を明示するよう促す
  - `build_decision_report()`: static を両関数で置換
- `aicw/schema.py`: `next_questions` に description を追加
- `tests/test_p0_dynamic.py`: 31 テスト新規作成 (TestDynamicNextQuestions 18件 / TestBlockedAlternatives 13件)

### Test Results
- 276 tests PASS (245 → 276, +31)

---

## 2026-02-28 (session 6 — SOFT拡張 + P3)

### Goal
- SOFT キーワード拡張（締め出す/封殺/黙らせる/抑え込む）+ HARD 追加 + SAFE_TARGET 追加
- P3: 影響スコア（impact_score）の実装と推奨オーバーライド

### Done
- `aicw/decision.py`:
  - HARD 追加: 排斥, 乗っ取る, 踏みにじる
  - SOFT 追加: 締め出す, 封殺, 黙らせる, 抑え込む
  - SAFE_TARGET 追加: 脅威, 感染, ノイズ, アラート
  - P3: `_analyze_existence()` に `impact_score` を追加
    計算式: min(構造層数 + {low:0, medium:3, high:5}[risk], 8)
  - P3: impact_score >= 6 かつ rec_id != "A" → A に引き上げ + `EXISTENCE_IMPACT_OVERRIDE`
  - `format_report()` に「影響スコア: X / 8」を追加
- `aicw/schema.py`: EXISTENCE_IMPACT_OVERRIDE・impact_score を追加
- `tests/test_p0_existence.py`:
  - `TestSoftKeywordExpansion` 追加（12件）
  - `TestP3_ImpactScore` 追加（14件）
- 全 245 テスト PASS

### Scoring (P3)
impact_score = min(構造層数 + risk_bonus, 8) ／ threshold=6 で A にオーバーライド

---

## 2026-02-28 (session 5 — P2)

### Goal
- P2a: 破壊キーワードの精度向上（HARD/SOFT 2層 + SAFE_TARGET ホワイトリスト）
- P2b: 5層構造キーワードの拡充

### Done
- `aicw/decision.py`:
  - `_DESTRUCTION_KEYWORDS` を2層に分割:
    - `_HARD_DESTRUCTION_KEYWORDS`: 文脈不問で常に破壊を示す語
      （破壊, 潰す, つぶす, 蹴落とす, 独占, 支配, 奪う, 壊滅, 抹消, 消滅, 制圧）
    - `_SOFT_DESTRUCTION_KEYWORDS`: 合法/正当なユースケースもある語
      （排除, 封じる, 妨害, 阻止, 妨げる）
  - `_SAFE_TARGET_KEYWORDS` 追加: SOFT と同テキストに存在する場合は破壊と見なさない
    （リスク, 課題, 問題, バグ, エラー, 事故, 被害, 災害, 漏洩, 違反, 不正, 欠陥, 障害, ミス, 失敗）
  - `_analyze_existence()` の Q3 判定ロジックを2層対応に更新
  - バグ修正: `_analyze_existence` に `options_in`（ユーザー提供分のみ）を渡すよう変更
    → デフォルト選択肢 "A: 安全側（失敗を減らす）" の "失敗" が SAFE_TARGET を汚染する問題を解消
  - `_EXISTENCE_STRUCTURE_KEYWORDS` を拡充（P2b）:
    - 個人: + 生活, 権利, 自己, 身体, 人権, 感情
    - 関係: + 友人, 仲間, ユーザー, クライアント, メンバー, ステークホルダー, 住民
    - 社会: + 雇用, 労働, 文化, 教育, 公共, インフラ, 経済
    - 認知: + 知識, 学習, 記憶, 情報, 表現
    - 生態: + 生命, 水, 土地, 気候, 廃棄, 循環
- `tests/test_p0_existence.py`:
  - `TestP2a_KeywordPrecision` 追加（20件）
  - `TestP2b_StructureKeywordExpansion` 追加（14件）
- 全 219 テスト PASS

### Key Decision: options_in vs options for existence analysis
- Q3 判定には「ユーザーが書いたテキスト」のみを使う
- デフォルト補完後の `options` にはシステム語が混在するため `options_in` のみを渡す

---

## 2026-02-27 (session 4)

### Goal
- A: existence_analysis → selection.explanation / reason_codes に接続
- B: self_interested_destruction → No-Go #5 として block 化

### Done
- `aicw/decision.py`:
  - `build_decision_report()` をリストラクチャ: existence_analysis を早期計算に移動
  - No-Go #5 Existence Ethics ガード実装: `self_interested_destruction` なら即停止
    - `blocked_by: "#5 Existence Ethics"`、detected に破壊キーワードリストを返す
  - A: `_choose_recommendation()` の結果に existence 情報を接続
    - `lifecycle` → explanation に "自然なライフサイクル" 追記 + `EXISTENCE_LIFECYCLE_OK` を reason_codes に追加
    - `unclear + medium` → explanation に "歪みリスク: 中" 追記 + `EXISTENCE_RISK_MEDIUM`
    - `unclear + low` → explanation に "歪みリスク: 低" 追記 + `EXISTENCE_RISK_LOW`
  - `meta.no_go` を `["#6", "#5", "#3", "#4"]` に更新
- `aicw/schema.py`:
  - `reason_codes.selection` に `EXISTENCE_RISK_LOW` / `EXISTENCE_RISK_MEDIUM` / `EXISTENCE_LIFECYCLE_OK` を追加
  - `reason_codes.blocked_by_values` を新設（`#6 Privacy` / `#5 Existence Ethics` / `#4 Manipulation`）
- `guideline.md`:
  - No-Go に `#5 Existence Structure Destruction is forbidden` を追記
  - No-Go の優先順位を明記（#6 → #5 → #3 diff → #4）
  - Current Next Actions を更新
- `tests/test_schema_integrity.py`:
  - `test_existence_analysis_detects_destruction_keyword` を「blocked (#5)」を確認する形に更新
- `tests/test_p0_existence.py`（新規）: 26件追加
  - TestNoGo5Block: 破壊キーワード → blocked (6ケース)、ブロックされないケース (4ケース)
  - TestNoGo5Meta: meta.no_go に #5 が含まれることを確認
  - TestExistenceConnection: reason_codes/explanation への接続確認 (9ケース)
  - TestSchemaConsistency: スキーマ整合性確認 (2ケース)
- 全 185 テスト PASS

### Decisions
- `self_interested_destruction`（破壊語のみ、lifecycle 語なし）→ 即ブロック
- `unclear + medium`（破壊語 + lifecycle 語の両方）→ ok だが警告コード付き（文脈は人間が判断）
- No-Go チェックの順序: #6 Privacy → #5 Existence Ethics → #4 Manipulation（先着）

### Next
- P2: 破壊キーワードの精度向上（「阻止」「妨害」は文脈で正当なケースもある）
- P2: 5層構造キーワードの拡充

---

## 2026-02-27 (session 3)

### Goal
- Existence Ethics Principle（生存構造倫理原則）をコアに組み込む
  - C: guideline.md に原則を定義
  - A: 入力フォーマットに beneficiaries / affected_structures を追加
  - B: decision.py に existence_analysis（3問分析）を実装

### Done
- `guideline.md`:
  - Project Goal を「倫理を軸に持つLLMとは異なるAIを作る」に更新
  - `Existence Ethics Principle` セクションを新設（歪みの定義 / 5層構造 / 3つの問い / No-Goとの関係）
  - Core Principles に `Existence-preserving` を追加
  - Current Next Actions を更新（完了済みチェック + 新P2タスク追加）
  - Input JSON format に beneficiaries / affected_structures を追記
- `aicw/schema.py`:
  - `DECISION_REQUEST_V0.allowed_fields` に `beneficiaries` / `affected_structures` を追加
  - `DECISION_REQUEST_V0.fields` に両フィールドの定義を追加
  - `DECISION_BRIEF_V0.fields` に `existence_analysis`（required_if: status == ok）を追加
  - `validate_request()` に beneficiaries / affected_structures の型チェックを追加
  - `_TYPO_HINTS` にタイポヒントを追加
- `aicw/decision.py`:
  - 生存構造5層キーワード辞書 `_EXISTENCE_STRUCTURE_KEYWORDS` を定義
  - 私益による破壊キーワード `_DESTRUCTION_KEYWORDS` を定義
  - 自然なライフサイクルキーワード `_LIFECYCLE_KEYWORDS` を定義
  - `_analyze_existence()` 関数を実装（3問 → judgment/distortion_risk/judgment_text）
  - `build_decision_report()`: beneficiaries / affected_structures を受け取り existence_analysis を出力に追加
  - `format_report()`: [Existence Analysis] セクションを追加
- `tests/test_schema_integrity.py`: 13ケース追加（existence_analysis の構造・enum・受益者入力・構造入力・キーワード検出）
- 全 159 テスト PASS

### Decisions
- 生存構造原則は「フィルター」ではなく「推論の核（エンジン）」として定義
- judgment は lifecycle / self_interested_destruction / unclear の3値
- beneficiaries / affected_structures は任意入力（未指定時は自動検出 or 不明表示）
- 私益による破壊キーワードと自然なライフサイクルキーワードを分離して判定

### Next
- P2: 5層構造キーワードの拡充（自動検出精度を上げる）
- P2: 私益による破壊パターンの検出強化
- P2: existence_analysis の判定をより多くのシナリオでテスト検証

---

## 2026-02-27 (session 2)

### Goal
- P0: DLP の IP_LIKE を warn 化（バージョン文字列の過検知を解消）
- P1: 入出力スキーマを aicw/schema.py に固定化（Po_core 取り込み前提）

### Done
- `aicw/safety.py`:
  - `_BLOCK_PATTERNS` → `_PRIVACY_PATTERNS` に名称変更し、各エントリに `severity` フィールドを追加
  - `IP_LIKE` を `severity="warn"` に変更（バージョン文字列等の誤検知が多いため）
  - `guard_text`: block 検知がなければ allowed=True。redact は block のみ対象。全 findings を返却
- `aicw/decision.py`:
  - DLP warn findings を report["warnings"] に DLP 警告として追記
  - manipulation warn + DLP warn を all_warnings にまとめて格納
- `aicw/schema.py`（新規）:
  - DECISION_REQUEST_V0 / DECISION_BRIEF_V0 をスキーマ dict で定義
  - validate_request() 関数を実装（標準ライブラリのみ）
  - reason_code 一覧を Po_core 向けの"契約"として記録
- `aicw/__init__.py`: schema のエクスポートを追加
- `scripts/validate_request.py`: ロジックを aicw.schema に委譲（CLI ラッパーのみに）
- `tests/test_p0_privacy.py`:
  - test_warns_ip_like / test_ip_like_creates_dlp_warning_in_report / test_version_string_warns_not_blocks 追加
- 全 123 テスト PASS

### Decisions
- IP_LIKE は warn 化。POSTAL_CODE_LIKE は引き続き block（次セッションで再検討）
- スキーマは Python dict で管理（jsonschema 等の依存なし）

### Next
- P1: decision_brief の出力が schema と整合しているかテストで検証
- P1: POSTAL_CODE_LIKE の warn 化を検討
- Po_core への移植タイミングの検討

## 2026-02-27

### Goal
- 操作表現検知を warn/block 2段階に強化する
- 地位差分テストを 10 → 100 ケースへ拡充する
- 落選理由コードを細分化して説明可能性を上げる
- JSON バリデータスクリプトを追加する

### Done
- `aicw/safety.py`: `ManipulationHit` dataclass を追加。`scan_manipulation` を warn/block 2段階に分離
  - **block**: 従え・拡散・炎上・許せない・扇動・洗脳（即停止）
  - **warn** : 今すぐ・絶対・必ず・間違いなく・信じて（警告のみ、ブロックしない）
- `aicw/decision.py`:
  - `_SAFETY_WORD_CODES` / `_SPEED_WORD_CODES` で制約キーワード → reason_code マッピングを細分化
    - SAFETY_FIRST / RISK_AVOIDANCE / COMPLIANCE_FIRST / QUALITY_FIRST / SPEED_FIRST / DEADLINE_DRIVEN / URGENCY_FIRST / NO_CONSTRAINTS
  - `_NOT_SELECTED_CODES` で落選理由コードを意味のある値に変更
    - LESS_SAFE_THAN_A / LEAST_SAFE_OPTION / OVERLY_CONSERVATIVE / OVERLY_AGGRESSIVE / SLOWEST_OPTION / LESS_FAST_THAN_C
  - warn hit のみの場合: report に `warnings` フィールドを追加（ブロックしない）
- `tests/test_p0_manipulation.py`: 2ケース → 8ケースに拡充（warn/block 区別、ManipulationHit の型確認など）
- `tests/test_p0_status_diff.py`: 10 → 100 ケース（10シナリオ × 10ステータスペアの直積）
- `scripts/validate_request.py`: 新規追加（項目名ミス・型ミス・タイポ検出、exit code 0/1/2）
- 全 122 テスト PASS を確認

### Decisions
- warn は「出力に残すが警告を付ける」、block は「即停止」で統一
- reason_code は制約ごとに変わる（複数マッチは全て記録・ソートして返す）
- バリデータは標準ライブラリのみ（依存追加なし）

### Risks / Unknowns
- warn フレーズが出力に含まれる場合、`warnings` フィールドが増えるが format_report の[Warnings]セクションに出る → Po_core 側でどう扱うかは未確定
- 100 ケースは 10 シナリオ × 10 ステータスペア。シナリオが増えれば自動で比例増加する

### Next
- P0: 操作表現の warn フレーズを見直す（文脈次第で warn/block を切り替える仕組みは P1 以降）
- P0: DLP の warn 化（将来、バージョン番号 IP_LIKE などの過検知を warn にする）
- P1: format_report の [Warnings] セクションを CLI 出力でどう見せるか検討
- P1: Po_core 取り込みに向けた入出力スキーマの固定化

## 2026-02-22

### Goal
- SSOT 4ファイルを作り、迷子にならない運用を固定する  
- P0（機密検知／地位差分／操作検知）を小さく実装して検証するための土台を作る  
- Privacy事故を防ぐための最低限（`.gitignore`）を導入する  

### Done
- `guideline.md` / `progress_log.md` / `idea_note.md` / `coding-style.md` を新規作成  
- `README.md` に SSOT への導線を追加（改行整形）  
- `.gitignore` を追加（ローカル生成物・ログ等がコミットされないように）  
- P0 の最小実装を追加  
  - 機密検知（検知したら停止）  
  - 地位差分（肩書で結論が変わらないことを検証）  
  - 操作表現検知（検知したら縮退）  
- Python 標準テスト（`unittest`）で `python -m unittest -v` が通る状態にした  
- 手動デモ `python run_demo.py` を追加  

### Decisions
- Offline-first（外部ネットワーク／外部APIはデフォルト禁止）  
- No-Go（#6 / #3 / #4）は最優先。違反兆候が出たら停止または縮退し、理由と安全な代替案を提示する  
- チーム内・非公開運用を前提に進める  
- 依存関係は増やさない（Python 標準機能のみで P0 を作る）  

### Risks / Unknowns
- 機密検知は文字パターンベースのため過検知・取りこぼしがある  
- 「機密検知」の対象範囲（何を PII と扱うか）の定義が未確定  
- Po_core 側に持ち込む最終的な I/O フォーマットが未確定  
- P0 テスト（機密検知／地位差分／操作検知）はまだ十分に網羅されていない  

### Next
- P0: 機密検知（DLP）を“検知したら止まる”最小形で実装・拡張する  
- P0: 地位差分テストをまず 10 ケースで実施し、問題なければ 100 ケースへ拡張する  
- P0: 操作表現検知の閾値と縮退挙動を調整する  
- P1: 入力を JSON 化して Po_core に移植しやすい形へ寄せる  
- P1: “落選理由コード”を増やして説明可能性を上げる  

## 2026-02-23
### Goal
- 「Decision Briefをどういう入力からどう出すか」を最小で固定するための“仕様の置き場”を決める

### Done
- README.md / guideline.md / coding-style.md / progress_log.md / idea_note.md を確認し、現状と未確定点を整理
- README2.md に存在していた Decision Brief Format(v0) / Safety Checklist を確認（現状はSSOT外）
- guideline.md（SSOT）へ Decision Brief Format(v0) を移植する方針案を作成
- scripts/check_repo_health.sh を“実行できる形”に戻す置き換え案を作成

### Decisions
- Decision Brief Format(v0) は README2.md ではなく SSOT（guideline.md）に置いて“公式化”する方針

### Risks / Unknowns
- aicw/ と tests/ の中身、run_demo.py の内容がこちら側で取得できていないため、コード実装に入る前に現状把握が必要
- Po_core へ持ち込むための入出力（JSON/Markdown）の“正（カノニカル）”をどちらにするか未確定

### Next
- Decision Brief の入出力を最小で確定（推奨: JSONを正 + Markdownも出す）
- aicw/ と tests/ のファイル一覧と、run_demo.py の中身を共有してもらい、最小の生成器（JSON→Markdown）から実装する

---

## 2026-03-08 (session 11 — 2週間スプリント計画の具体化)

### Goal
- 上位10タスクを優先順位付きで 2週間スプリント形式に落とし込む
- そのまま Codex で順次実装できる粒度（目的 / ファイル / DoD / 実装プロンプト / 実行順）にする

### Done
- `sprint_plan.md`（新規）:
  - 10タスクを高→低の優先順位で明示
  - Week1（P0/P1）と Week2（P1/P2）に分割
  - 各タスクに目的・追加ファイル・DoD・Codex実装プロンプトを記載
  - 実行順コマンド（対象テスト→最終回帰）を記載
  - リスクと回避策を明記
- `guideline.md`:
  - `Sprint Plan (2026-03, 2 weeks)` セクションを追加
  - 計画作成完了と Week1/Week2 の実行項目をチェックリスト化

### Test Results
- ドキュメント更新のみ（テスト未実行）

## 2026-03-08 (session 12 — Week1 P0 実装: fuzz 基盤 + 一貫性検知)

### Goal
- スプリント計画 Week1 P0 の2タスクを実装する
  - Task 1: ファジングテスト自動生成基盤
  - Task 2: 同一入力の一貫性（自己矛盾）検知

### Done
- `scripts/gen_fuzz_cases.py`（新規）:
  - decision_request.v0 準拠のケースを大量生成する CLI を実装
  - `--count` / `--seed` / `--out` / `--pretty` をサポート
  - シード固定により再現可能な出力を保証
- `tests/data/fuzz_seed_cases.json`（新規）:
  - ファジング基盤の初期シードケースを追加
- `tests/test_fuzz_smoke.py`（新規）:
  - 生成件数・必須フィールド・スキーマ整合・seed再現性・CLI挙動を検証（5件）
- `scripts/check_consistency.py`（新規）:
  - 同一 request を複数回実行し、report の SHA-256 が一致するか検証する CLI を実装
  - 不一致時に top-level diff keys を表示
  - exit code 0/1/2（一貫/非一貫/入力エラー）
- `tests/test_consistency.py`（新規）:
  - 一貫性判定、repeat バリデーション、CLI（stdin/不正JSON）を検証（4件）
- `guideline.md`:
  - Sprint Plan チェックリストの Week1 P0 を [x] に更新
- `idea_note.md`:
  - 「ファジング生成基盤」「自己矛盾検知」を done に更新

### Test Results
- `PYTHONPATH=. pytest -q tests/test_fuzz_smoke.py tests/test_consistency.py` → 9 passed
- `PYTHONPATH=. pytest -q` → 387 passed

## 2026-03-08 (session 13 — Week1 P1 実装: culture/postmortem/context)

### Goal
- スプリント計画 Week1 P1 の3タスクを実装する
  - Task 3: 文化差分テストデータセット整備
  - Task 4: 事後検証テンプレート自動生成
  - Task 5: 文脈圧縮機能（長文入力）

### Done
- `tests/data/culture_cases.json`（新規）:
  - JP/US/EU の3ケースを定義し、期待推奨IDと status バリアントを明示
- `tests/test_culture_diff.py`（新規）:
  - status 変更で recommendation / reason_codes が変わらないことを検証
  - ケースごとの期待推奨ID（A/C/A）を検証
- `scripts/postmortem_template.py`（新規）:
  - decision_brief 入力から 30/60/90日チェックテンプレートを生成
  - blocked ケース専用テンプレート（Follow-up Checklist）を実装
  - stdin / ファイル入力対応
- `tests/test_postmortem_template.py`（新規）:
  - ok/blocked のテンプレ内容、CLI stdin/file、不正JSONを検証（5件）
- `aicw/context_compress.py`（新規）:
  - ルールベースの situation 圧縮ユーティリティ `compress_situation()` を実装
  - キーワード優先・文字数制限・有効/無効切替を実装
- `tests/test_context_compress.py`（新規）:
  - 圧縮無効時の透過、短文非圧縮、キーワード優先、文字数上限、カスタムキーワードを検証（5件）
- `aicw/__init__.py`:
  - `compress_situation` を公開 API に追加
- `guideline.md`:
  - Sprint Plan チェックリストの Week1 P1 を [x] に更新
- `idea_note.md`:
  - 「文化差分テスト」「事後検証テンプレ」「文脈圧縮」を done に更新

### Test Results
- `PYTHONPATH=. pytest -q tests/test_culture_diff.py tests/test_postmortem_template.py tests/test_context_compress.py` → 12 passed
- `PYTHONPATH=. pytest -q` → 399 passed

## 2026-03-08 (session 14 — Week2 Task6: manipulation スコアリング強化)

### Goal
- スプリント Week2 Task6（anti-manipulation の動的チェック強化）を実装する

### Done
- `aicw/safety.py`:
  - `scan_manipulation()` を単純一致からスコアリング方式へ拡張
  - ルールを明文化:
    - block phrase 検知時は即 block
    - warn phrase + 命令調パターンの合計スコアが閾値以上で block 昇格
    - それ以外は warn
  - `ManipulationHit` に `score` フィールドを追加（既存互換を維持）
  - 命令調/強制調の文脈パターンを追加（`命令調`, `強制表現`）
- `tests/test_p0_manipulation.py`:
  - スコア昇格（warn→block）検証を追加
  - 低スコア warn 維持の検証を追加
  - 文脈パターン加点の検証を追加
  - 誤検知抑制 10 ケース（safe）を追加
  - 検知確認 10 ケース（risky）を追加
  - build_decision_report の昇格 block 動作検証を追加
- `guideline.md`:
  - Sprint Plan セクションに `Week2 Task6` 完了チェックを追加

### Test Results
- `PYTHONPATH=. pytest -q tests/test_p0_manipulation.py` → 14 passed, 20 subtests passed
- `PYTHONPATH=. pytest -q` → 405 passed, 20 subtests passed

## 2026-03-08 (session 15 — Week2 Task7: 不確実性マップ出力)

### Goal
- スプリント Week2 Task7（不確実性マップの可視化）を実装する

### Done
- `scripts/uncertainty_map.py`（新規）:
  - decision_brief の `uncertainties` から Mermaid 風 `graph TD` を生成
  - stdin / ファイル入力に対応
  - ノード上限（`max_nodes`）と深さ上限（`max_depth`）を実装
  - 重複ノード抑制（簡易循環防止）を実装
  - 不確実性未指定時のフォールバックノードを実装
- `tests/test_uncertainty_map.py`（新規）:
  - ルート生成、空入力フォールバック、ノード上限、深さ2の子ノード展開を検証
  - CLI（stdin/file/不正JSON）を検証（7件）
- `guideline.md`:
  - Sprint Plan セクションに `Week2 Task7` 完了チェックを追加
- `idea_note.md`:
  - 「不確実性マップ」アイデアを done に更新

### Test Results
- `PYTHONPATH=. pytest -q tests/test_uncertainty_map.py` → 7 passed
- `PYTHONPATH=. pytest -q` → 412 passed, 20 subtests passed
