# API Contract v0.1

本ドキュメントは、`AI-Can-we-create-AI-` の現行 CLI / スキーマに基づく
**固定契約（v0.1）**を定義する。

## 1. Request Contract (`decision_request.v0`)

`aicw/schema.py` の `DECISION_REQUEST_V0` を正とする。

### 必須キー
- `situation: str`

### 任意キー
- `constraints: list[str]`
- `options: list[str]`
- `asker_status: str`
- `beneficiaries: list[str]`
- `affected_structures: list[str]`

### 追加制約
- 不明キーはバリデーションエラー。
- 型不一致はバリデーションエラー。

---

## 2. Response Contract (`decision_brief.v0`)

`aicw/schema.py` の `DECISION_BRIEF_V0` を正とする。

### 共通
- `status: "ok" | "blocked"`

### `status == "ok"` 時に必須
- `meta`
- `input`
- `candidates`
- `selection`
- `counterarguments`
- `uncertainties`
- `externalities`
- `next_questions`
- `existence_analysis`
- `impact_map`
- `disclaimer`

### `status == "blocked"` 時に必須
- `blocked_by`
- `reason`
- `detected`
- `safe_alternatives`

### `blocked_by` の許容値
- `#6 Privacy`
- `#5 Existence Ethics`
- `#4 Manipulation`

---

## 3. CLI Contract (`scripts/brief.py`)

実行形式:
- `python scripts/brief.py request.json`
- `echo '{...}' | python scripts/brief.py`

終了コード:
- `0`: 正常終了（`status == ok`）
- `1`: blocked（`status == blocked`）
- `2`: 引数エラー / JSONパースエラー

---

## 4. Versioning Policy

- `v0.1` の契約変更は **破壊的変更** とみなし、
  `docs/api_contract_v0_1.md` と `tests/test_api_contract.py` を同時更新する。
- スキーマ/CLI実装と契約テストが一致しない場合は、実装を修正してからマージする。
