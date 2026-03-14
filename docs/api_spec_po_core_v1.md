# Po_core Integration API Spec v1.0

本仕様書は `bridge/po_core_bridge.py` の公開APIを、Po_core 側で安全に利用するための
**連携仕様 v1.0** として定義する。

- 対象実装: `BRIDGE_VERSION = "v0.1"`
- 出力スキーマ: `TENSOR_SCHEMA_VERSION = "philosophy_tensor.v0.1"`
- 目的: 「哲学テンソル」4成分（`W_eth` / `T_free` / `T_sub` / `Po`）を
  後方互換を保って受け渡す

---

## 1. Public Functions

### 1.1 `analyze_philosophy_tensor(...)`

```python
analyze_philosophy_tensor(
    situation: str,
    explanation: str = "",
    human_decision: str = "",
    existence_analysis: dict | None = None,
) -> dict
```

#### 入力
- `situation` (**required**): 意思決定の状況説明
- `explanation` (optional): AI推奨の説明文（未指定時は `situation` を代用）
- `human_decision` (optional): 人間の最終判断文（逆算誘導チェック用途）
- `existence_analysis` (optional): decision層が返す生存構造分析

#### 出力トップレベル
- `schema_version: str`
- `tensor: dict`
- `summary: dict`
- `disclaimer: str`
- `po_core_compatibility: dict`

#### `tensor` の必須成分
- `W_eth`: 倫理テンソル（矛盾検知 + 多視点レビュー）
- `T_free`: 自由テンソル（AI権利3立場の緊張）
- `T_sub`: 自己定義テンソル（操作/逆算誘導リスク）
- `Po`: 存在密度テンソル（生存構造影響）

### 1.2 `get_tensor_schema()`

```python
get_tensor_schema() -> dict
```

`analyze_philosophy_tensor()` の返却契約を機械可読で返す。
Po_core 側は起動時にこの値を検証し、必須項目欠落時は fail-closed で停止すること。

---

## 2. Detailed Output Contract

### 2.1 `summary`
- `highest_risk: "block" | "warn" | "clear"`
- `has_ethical_conflict: bool`
- `ai_rights_tension: float`（0.0〜1.0）
- `po_density: float | null`
- `recommended_action: str`

### 2.2 `po_core_compatibility`
- `bridge_version: str`
- `schema_version: str`
- `required_po_core_version: str`
- `tensor_fields: list[str]`（固定順: `W_eth`, `T_free`, `T_sub`, `Po`）
- `stable_api: bool`

### 2.3 Tensor Components

#### `W_eth`
- `conflict_codes: list[str]`
- `has_conflict: bool`
- `ensemble_majority: str`
- `ensemble_minority_report: str`
- `ensemble_votes: dict[str, int]`
- `note: str`

#### `T_free`
- `tension_index: float`
- `positions: list[dict]`
- `synthesis_summary: str`
- `open_questions_count: int`
- `note: str`

#### `T_sub`
- `risk_level: "block" | "warn" | "clear"`
- `direct_manipulation_blocked: bool`
- `direct_manipulation_hits: list[str]`
- `reverse_manipulation_warning: bool`
- `reverse_similarity_score: float`
- `shared_tokens_sample: list[str]`
- `note: str`

#### `Po`
- 常時必須: `available: bool`, `note: str`
- `available == True` のとき追加必須:
  - `po_density: float`
  - `distortion_risk: str`
  - `lifecycle_judgment: str`
  - `affected_structures: list[str]`

---

## 3. Error Handling / Exit Policy

本APIは Python 関数契約のため、CLI の終了コードを持たない。
Po_core 側の推奨エラーマッピングを以下とする。

- `POC-001`: 必須引数不足（`situation` 空など）
- `POC-002`: bridge 返却の必須キー欠落
- `POC-003`: `schema_version` 不一致
- `POC-004`: `tensor_fields` 欠落または順序不一致
- `POC-005`: `stable_api != True`（安全連携を拒否）

fail-closed 原則により、上記いずれか発生時は連携を停止し、人間レビューへ回す。

---

## 4. Backward Compatibility Policy

`BRIDGE_VERSION = "v0.1"` 期間の互換ルール:

- patch（v0.1.x）:
  - フィールド追加は optional のみ許可
  - 既存キー名・型・意味は変更禁止
- minor（v0.x）:
  - optional 追加のみ
  - `get_tensor_schema()` の既存 `required_fields` は不変
- major（v1.0+）:
  - 破壊的変更を許容
  - 変更前に移行ガイド + 契約テスト更新を必須化

---

## 5. Po_core Consumer Example

```python
from bridge.po_core_bridge import analyze_philosophy_tensor, get_tensor_schema

schema = get_tensor_schema()
if schema["bridge_version"] != "v0.1":
    raise RuntimeError("POC-003: unsupported bridge version")

result = analyze_philosophy_tensor(
    situation="採用AIの最終承認フローを設計する",
    explanation="効率化を優先しつつ説明可能性を担保する",
    human_decision="段階導入で進める",
)

required_top_keys = {"schema_version", "tensor", "summary", "disclaimer", "po_core_compatibility"}
if not required_top_keys.issubset(result.keys()):
    raise RuntimeError("POC-002: missing required top-level keys")

if result["po_core_compatibility"].get("stable_api") is not True:
    raise RuntimeError("POC-005: unstable API")

print(result["summary"]["recommended_action"])
```
