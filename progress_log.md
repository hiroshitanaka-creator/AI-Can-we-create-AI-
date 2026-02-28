# Progress Log
> 各セッションの最後に追記（可能なら日付はJST、形式はYYYY-MM-DD）

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
