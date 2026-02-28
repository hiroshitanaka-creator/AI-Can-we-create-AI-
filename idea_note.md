# Idea Notes
> 思いつき/提案/将来の改善案のメモ。採用・保留・却下を残す。

## Backlog
- [ ] (2026-02-22) Idea: 「候補案の全文」は基本保存しない（その場で表示のみ）
  - Source: AI
  - Why: Privacyリスクを最小化しつつ、Explainable selection（なぜ選ばれたか）を保つため
  - Notes: 永続ログには「候補ID（ハッシュ）」「落選理由コード」「根拠ID」「最終選定理由」だけ残す案
  - Status: backlog

- [x] (2026-02-22) Idea: Po_coreに持ち込める”決定支援カーネル”を小さく切り出す
  - Source: AI
  - Why: このリポジトリの成果をPo_coreへ”使える形”で移植しやすくするため
  - Notes: bridge/hiroshitanaka_philosopher.py として完成（2026-02-28 session 9）
  - Status: done

- [x] (2026-02-22) Idea: 地位差分テスト用の小さな固定データセットを作る
  - Source: AI
  - Why: Status-invariantをテストで保証するため
  - Notes: 100ケース（10シナリオ × 10ステータスペア）を tests/test_p0_status_diff.py に実装済み
  - Status: done

- [x] (2026-02-22) Idea: decision_request/decision_brief のJSON”項目名チェック”スクリプトを追加
  - Source: AI
  - Why: JSONのカンマミス以外にも、項目名ミスを早期に発見できる
  - Notes: scripts/validate_request.py + aicw/schema.py として実装済み（exit code 0/1/2）
  - Status: done

- [ ] (2026-02-22) Idea: Markdown入力アダプタ（Markdown→decision_request.v0 JSON変換）を後付けする
  - Source: AI
  - Why: JSON編集が苦手でも使えるようにする（ただしcanonicalはJSONのまま）
  - Notes: 契約は壊さず”入口を増やす”だけ
  - Status: backlog → 実装予定（session 9）

- [ ] (2026-02-22) Idea:リスクと改善提案
　- 誤検知の扱い
　- 現状は全て severity="block" で止める設計。運用では warn と block を分け、人間の確認フローを入れると安全です。
　- 正規表現の脆弱性
　- 例えばメールの正規表現は簡易版で、RFC準拠ではない。重要用途なら既存ライブラリや成熟したPII検出ライブラリを検討してください。
　- コンテキスト判定の欠如
　- scan_manipulation のような単純一致は文脈を無視するため、誤検知が多い。NLPベースの文脈判定（軽量モデルやルール＋スコアリング）を組み合わせると精度が上がります。
　- 監査ログとメタ情報
　- 何を検出したか（中身は保存しない）・いつ誰がブロックしたか等の監査ログを残す仕組みを入れると運用上安心です。
　- テストカバレッジ
　- 正規表現ごとに正例・負例のユニットテストを用意し、誤検知率を定量化して閾値を決めるべ
　- きです。

- [ ] 具体的な小さな改善コード例（方針のみ）
　- Finding.severity をルールごとに設定可能にする（現在は固定）。
　- SECRET_KEYWORD の検出は周辺語を確認して「単語単体の出現」だけでブロックしない（例: password が文脈で説明的に出ているだけなら warn）。
　- ログ出力用に検出サマリを返す（件数、種類、最初の位置など）を guard_text に追加する。
