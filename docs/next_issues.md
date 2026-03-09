# 次フェーズ GitHub Issue 案

> このファイルは GitHub Issue として登録する予定の提案書です。
> 登録時はタイトル・本文をそのままコピー＆ペーストしてください。
> 優先度: 🔴 高 / 🟡 中 / 🟢 低

---

## Issue #1 🔴 Po_core 本格連携 API 仕様書 v1.0

**タイトル:** `[Enhancement] Po_core 連携 API 仕様書 v1.0 の整備`

**ラベル:** `enhancement`, `po-core`, `docs`

**本文:**

### 背景

`bridge/po_core_bridge.py` により哲学テンソル統合 v0.1 が完成し、`stable_api=True` フラグが立った。
次のステップは Po_core 側が実際にこの bridge を呼び出すための **API 仕様書** を整備することです。

### やること

- `docs/api_spec_po_core_v1.md` を作成
  - 関数シグネチャ / 入出力スキーマ / エラーコード一覧
  - `BRIDGE_VERSION = "v0.1"` の後方互換性ポリシー
  - Po_core 側の実装例（Python スニペット）
- `tests/test_api_contract.py` を `po_core_bridge` の新スキーマに対応させて更新
- semver 運用ルールを `guideline.md` に追記

### 完了条件 (DoD)

- [ ] `docs/api_spec_po_core_v1.md` が作成され、全 4 テンソル成分が文書化されている
- [ ] `get_tensor_schema()` の返り値と仕様書が一致していることをテストで確認
- [ ] 既存 615 テストが全て通過する

---

## Issue #2 🔴 meta_suggest の誤検知修正

**タイトル:** `[Bug] meta_suggest が No-Go チェックリストを「次タスク候補」として誤検知する`

**ラベル:** `bug`, `meta`

**本文:**

### 現象

`python scripts/meta_suggest.py` を実行すると、`guideline.md` の No-Go チェックリスト項目
（例: `[ ] 個人情報/秘密情報を扱っていない（#6）`）が
「未完了タスク候補」として上位にランクインしてしまう。

### 原因

`meta_suggest.py` は `[ ]` を未完了マーカーとして機械的に拾うため、
「チェックリスト形式の確認項目」と「実装タスク」を区別できていない。

### 解決策（案）

1. **除外リスト方式:** `guideline.md` の「No-Go チェックリスト」セクションを
   スキャン対象から除外する（セクションヘッダーでフィルタリング）
2. **タグ方式:** 実装タスクに `[task]` のような専用マーカーを付ける
3. **ファイル限定方式:** スキャン対象を `idea_note.md` と `sprint_plan.md` のみに絞る

### 完了条件 (DoD)

- [ ] `python scripts/meta_suggest.py` の top-3 が実装タスクのみを返す
- [ ] `tests/test_meta_suggest.py` にチェックリスト誤検知を防ぐテストケースを追加
- [ ] 既存テストが全て通過する

---

## Issue #3 🟡 check_reverse_manipulation の NLP 精度強化

**タイトル:** `[Enhancement] check_reverse_manipulation を文脈ベース推定に強化`

**ラベル:** `enhancement`, `safety`, `nlp`

**本文:**

### 背景

現在の `check_reverse_manipulation()` は **Jaccard 語彙類似度**による近似実装（P0）。
単純なキーワード重複率のため、以下の問題がある：

- **偽陽性:** 語彙が似ているだけで誘導していないケース（同じ業界の話題など）
- **偽陰性:** 異なる語彙を使って同じ結論に誘導するケース（言い換え誘導）

### 解決策（外部依存なしで実現可能な範囲）

1. **ストップワード強化:** 現在の除外語リストを拡充（業界共通語・接続詞・副詞）
2. **n-gram 重複率の併用:** 単語単位ではなく 2-gram ペアの重複も考慮
3. **テーマ一致スコア:** reason_codes の重複率と語彙類似度を組み合わせた複合スコア
4. **閾値の動的調整:** 入力の長さ・語彙の多様性に応じて閾値を変動させる

### 完了条件 (DoD)

- [ ] 既存 12 件の `test_reverse_manipulation.py` が全て通過する
- [ ] 新たに偽陽性 5件・偽陰性 5件のテストケースを追加
- [ ] `note` フィールドに精度クラスを明示（"P0-jaccard" → "P1-ngram" など）

---

## Issue #4 🟡 デモシナリオ追加（医療・教育・公共政策）

**タイトル:** `[Enhancement] demo_business.py にシナリオ4〜6を追加`

**ラベル:** `enhancement`, `demo`

**本文:**

### 背景

現在 `demo_business.py` には 3 シナリオ（AI採用審査 / 人員再配置 / カーボンニュートラル）がある。
より多様な意思決定領域でパイプラインをデモするため、シナリオを追加したい。

### 追加するシナリオ案

| # | 領域 | 状況 |
|---|---|---|
| 4 | 医療 | 患者データをAI診断補助に使用すべきか（#6 Privacy 最重要） |
| 5 | 教育 | 学校でのAI作文支援ツール導入の是非（#3 差別・格差リスク） |
| 6 | 公共政策 | 市の監視カメラ増設と市民プライバシーのトレードオフ |

### 完了条件 (DoD)

- [ ] `SCENARIOS` dict にシナリオ 4〜6 を追加
- [ ] シナリオ 4〜6 が `--list` で表示される
- [ ] 各シナリオの `test_demo_business.py` テストを追加
- [ ] シナリオ 4（医療）で #6 blocked または警告が発生することを確認

---

## Issue #5 🟡 knowledge_base を interactive_sim に深く統合

**タイトル:** `[Enhancement] interactive_sim で過去類似決定を「ヒント」として表示`

**ラベル:** `enhancement`, `ux`

**本文:**

### 背景

現在 `interactive_sim.py` は `knowledge_base.find_similar()` の結果を表示するが、
「似た過去決定があった」という情報を入力収集フェーズに活用できていない。

### やること

- 入力フォームの後・意思決定実行の前に「似た過去決定（存在する場合）」を表示
- ユーザーが参考にできる形式で提示（date / status / reason_codes / 類似度）
- 永続化 KB ファイルパスを `--kb-path` オプションで指定できるようにする
- 「今回の決定を KB に保存しますか？（Y/n）」の確認プロンプトを追加

### 完了条件 (DoD)

- [ ] `--kb-path path/to/kb.json` オプションが機能する
- [ ] 類似過去決定が存在する場合、入力確認後に表示される
- [ ] `test_interactive_sim.py` に KB 統合テストを追加
- [ ] `--no-kb` で KB 参照も記録も完全スキップできる

---

## Issue #6 🟢 パッケージ化（pip install aicw）

**タイトル:** `[Future] aicw/ を独立 Python パッケージ化（pip install 対応）`

**ラベル:** `future`, `packaging`

**本文:**

### 背景

`idea_note.md` に記載されている「将来検討」項目。
Po_core 連携が固まり、API が安定したタイミングで実施する。

### やること

- `pyproject.toml` / `setup.py` の作成
- `aicw/` を独立パッケージとして定義（外部依存なし）
- `bridge/` は別パッケージ `aicw-bridge` として分離するか検討
- TestPyPI でリリースを検証

### 前提条件

- [ ] Po_core 連携 API 仕様書 v1.0 が完成している（Issue #1）
- [ ] `BRIDGE_VERSION` のセマンティックバージョニングが決定している
- [ ] README に「pip install aicw」のクイックスタートを追記

### 優先度

⚠️ **現時点では時期尚早。Issue #1〜#3 完了後に着手。**

---

## 優先順位サマリ

| Priority | Issue | Effort |
|---|---|---|
| 🔴 高 | #1 Po_core API 仕様書 | 中（1〜2 session） |
| 🔴 高 | #2 meta_suggest 誤検知修正 | 小（1 session） |
| 🟡 中 | #3 逆算誘導 NLP 強化 | 中（1〜2 session） |
| 🟡 中 | #4 デモシナリオ追加 | 小（1 session） |
| 🟡 中 | #5 KB + interactive_sim 統合 | 小（1 session） |
| 🟢 低 | #6 パッケージ化 | 大（要 Po_core 連携確定後） |
