# Progress Log
> 各セッションの最後に追記（可能なら日付はJST、形式はYYYY-MM-DD）

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
