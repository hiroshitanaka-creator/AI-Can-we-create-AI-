今日の進捗ログ（時系列）
## 2026-02-22
### Goal
- リポジトリ運用の「単一の真実」4ファイルを揃え、次の一手を固定する

### Done
- guideline.md / progress_log.md / idea_note.md / coding-style.md のテンプレを用意
- guideline.md に Decision Brief Format(v0) と Safety Checklist を追加
- scripts/check_repo_health.sh を追加（必須ファイルの存在チェック）

### Decisions
- 運用の単一の真実は 4ファイル（guideline / progress_log / idea_note / coding-style）に集約する
- 外部ネットワーク/外部APIはデフォルト禁止（必要時は理由と代替案を提示して許可を取る）

### Risks / Unknowns
- README.md と既存コードの現状が未確認（次回、構造と起動方法を把握する）
- 実装言語/ランタイムが確定していない（coding-style.md は暫定）

### Next
- README.md とリポジトリ構造を共有してもらい、最小MVPを切り出す
- Decision Brief の入出力フォーマット（テキスト/JSON/YAMLなど）を決める
