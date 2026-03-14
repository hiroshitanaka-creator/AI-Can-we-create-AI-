# Po_core 連携 API 仕様書 v1.0

この文書は `bridge/po_core_bridge.py` が提供する統合 API の **安定仕様（v1.0）** を定義する。
実装互換の基準は `get_tensor_schema()` の返却値とする。

- 対象 API: `analyze_philosophy_tensor()` / `get_tensor_schema()`
- 実装バージョン: `bridge_version = "v0.1"`
- スキーマ識別子: `schema_version = "philosophy_tensor.v0.1"`

## 1. エントリポイント

### 1.1 `analyze_philosophy_tensor(...)`

```python
analyze_philosophy_tensor(
    situation: str,
    explanation: str = "",
    human_decision: str = "",
    existence_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]
```

### 1.2 `get_tensor_schema()`

```python
get_tensor_schema() -> Dict[str, Any]
```

## 2. 出力トップレベル契約

- `schema_version: str`
- `tensor: dict`
  - `W_eth`, `T_free`, `T_sub`, `Po`
- `summary: dict`
- `disclaimer: str`
- `po_core_compatibility: dict`

## 3. テンソル成分契約（Canonical Snapshot）

以下を **正（Canonical）** とする。

<!-- tensor-schema:start -->
```json
{
  "schema_version": "philosophy_tensor.v0.1",
  "bridge_version": "v0.1",
  "tensor_components": {
    "W_eth": {
      "required_fields": [
        "conflict_codes",
        "has_conflict",
        "ensemble_majority",
        "ensemble_minority_report",
        "ensemble_votes",
        "note"
      ],
      "description": "倫理テンソル: 哲学的矛盾検知 + アンサンブルレビュー"
    },
    "T_free": {
      "required_fields": [
        "tension_index",
        "positions",
        "synthesis_summary",
        "open_questions_count",
        "note"
      ],
      "description": "自由テンソル核: AI権利の未解決緊張"
    },
    "T_sub": {
      "required_fields": [
        "risk_level",
        "direct_manipulation_blocked",
        "direct_manipulation_hits",
        "reverse_manipulation_warning",
        "reverse_similarity_score",
        "shared_tokens_sample",
        "note"
      ],
      "description": "自己定義テンソル: 操作・逆算誘導リスク",
      "risk_level_values": [
        "block",
        "warn",
        "clear"
      ]
    },
    "Po": {
      "required_fields_if_available": [
        "po_density",
        "distortion_risk",
        "lifecycle_judgment",
        "affected_structures",
        "note"
      ],
      "required_fields_always": [
        "available",
        "note"
      ],
      "description": "存在密度テンソル: 生存構造影響"
    }
  }
}
```
<!-- tensor-schema:end -->

## 4. 互換性ポリシー

- `schema_version` の変更は **破壊的変更**。
- `bridge_version` は実装配布識別子。
- 新規フィールド追加は後方互換を維持する限り許容。
- 破壊的変更時は本書とテストを同時更新する。
