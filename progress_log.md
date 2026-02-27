# Progress Log
> 各セッションの最後に追記（可能なら日付はJST、形式はYYYY-MM-DD）

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
