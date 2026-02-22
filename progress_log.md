# Progress Log
> 各セッションの最後に追記（可能なら日付はJST、形式はYYYY-MM-DD）

## 2026-02-22
### Goal
- SSOT 4ファイルを作り、迷子にならない運用を固定する
- Privacy事故を防ぐための最低限（.gitignore）を入れる

### Done
- guideline.md / progress_log.md / idea_note.md / coding-style.md を新規作成
- README.md にSSOTへの導線を追加（改行整形）
- .gitignore を追加（ローカル生成物・ログ等がコミットされないように）

### Decisions
- Offline-first（外部ネットワーク/外部APIはデフォルト禁止）
- No-Go (#6/#3/#4) は最優先。違反兆候が出たら縮退/停止して理由と安全な代替案を出す
- チーム内・非公開運用を前提に進める

### Risks / Unknowns
- P0テスト（機密検知/地位差分/操作検知）はまだ未実装
- 「機密検知」の対象範囲（何をPIIとして扱うか）の定義が必要
- Po_coreへ持ち込む“形”（入力/出力フォーマット）が未定

### Next
- P0: 機密検知（DLP）を“検知したら止まる”最小形で実装
- P0: 地位差分テスト（まず10ケース→100ケースへ）
- P0: 操作表現検知（煽り/説得を避ける縮退）
