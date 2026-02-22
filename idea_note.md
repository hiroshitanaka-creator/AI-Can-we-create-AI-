# Idea Notes
> 思いつき/提案/将来の改善案のメモ。採用・保留・却下を残す。

## Backlog
- [ ] (2026-02-22) Idea: 「候補案の全文」は基本保存しない（その場で表示のみ）
  - Source: AI
  - Why: Privacyリスクを最小化しつつ、Explainable selection（なぜ選ばれたか）を保つため
  - Notes: 永続ログには「候補ID（ハッシュ）」「落選理由コード」「根拠ID」「最終選定理由」だけ残す案
  - Status: backlog

- [ ] (2026-02-22) Idea: Po_coreに持ち込める“決定支援カーネル”を小さく切り出す
  - Source: AI
  - Why: このリポジトリの成果をPo_coreへ“使える形”で移植しやすくするため
  - Notes: 入力（状況/制約/選択肢）→出力（候補+理由+反証+不確実性+外部性）を固定フォーマット化する
  - Status: backlog

- [ ] (2026-02-22) Idea: 地位差分テスト用の小さな固定データセットを作る
  - Source: AI
  - Why: Status-invariantをテストで保証するため
  - Notes: 「同一内容＋肩書だけ違う」ペアを10→100へ拡張
  - Status: backlog
