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

---

## Backlog（Grokからのアイデア — 2026-02-28 受領）

### カテゴリ1: 検証・テスト強化

- [ ] (2026-02-28) Idea: 決定リクエストのファジングテスト自動生成フレームワーク
  - Source: Grok
  - Why: 手動テストでは到達できない「矛盾制約」「超長文脈」「微妙な誘導文」を検知し、DLP・status-invariant・anti-manipulation の信頼性を指数関数的に高める
  - Notes: Python標準ライブラリのみで実装可能（random + template変異）。生成ケース数は1万〜10万を想定。地位差分テストの自動拡張とも相補的
  - Status: backlog

- [ ] (2026-02-28) Idea: 決定結果の「自己矛盾検知」自動チェックモジュール
  - Source: Grok
  - Why: 同一状況で異なる結論が出ないことをコードレベルで保証するため
  - Notes: 同一 decision_request に対して複数回実行し、出力ハッシュが一致しない場合に警告。決定論的設計の検証にもなる
  - Status: backlog

- [ ] (2026-02-28) Idea: 「文化差分テスト」データセットの作成
  - Source: Grok
  - Why: Status-invariant を守りつつ、日本企業特有の「根回し文化」や「集団調和」を正しく Context-dependent に扱えるか検証するため
  - Notes: 日米欧の同じ状況を3パターン用意。status-invariant テストの「文化差分版」として位置づけ
  - Status: backlog

### カテゴリ2: 哲学的・説明性向上

- [ ] (2026-02-28) Idea: 軽量「哲学者アンサンブル」シミュレーター（Po_core プレビュー版）
  - Source: Grok
  - Why: 本格 Po_core 連携前に、このリポジトリだけで「哲学的議論」を体現し、説得力を高める
  - Notes: Kant / Nietzsche / Rawls など 5〜7人の簡易テンプレートを bridge/ に定義し、多数決＋反対意見リストを自動生成。HiroshiTanaka と同じ Philosopher 継承で実装できる。外部依存なし
  - Status: backlog

- [ ] (2026-02-28) Idea: 「哲学的矛盾検知」モジュール
  - Source: Grok
  - Why: 決定理由の中に「義務論と功利主義が矛盾してる」みたいな哲学的齟齬を指摘するため
  - Notes: 簡易論理矛盾チェック＋哲学キーワードマッチ。Po_core の Skeptic 役として組み込める
  - Status: backlog

- [ ] (2026-02-28) Idea: 「不確実性マップ」自動生成機能
  - Source: Grok
  - Why: 「不確実性があります」ではなく、どの部分がどれだけ不確実かを言語化するため
  - Notes: Mermaid.js 形式のテキストで「不確実性ツリー」を出力（外部依存なし、テキストのみ）。現在の uncertainties リストをツリー構造に変換するイメージ
  - Status: backlog

### カテゴリ3: 安全性・倫理的堅牢性

- [ ] (2026-02-28) Idea: 「人間の決定を逆算して誘導していないか」の動的チェック
  - Source: Grok
  - Why: static な anti-manipulation を超え、出力後に逆算して「AI が人間の結論を先読みして誘導してないか」を検知するため
  - Notes: 出力候補を人間の最終決定と比較し、類似度が異常なら警告。実装難易度は高いが、No-Go #4 の実質的な強化になる
  - Status: backlog

- [x] (2026-02-28) Idea: 「AIの限界宣言」機能を全出力に強制挿入
  - Source: Grok
  - Why: 「最終判断は人間です」をコードレベルで保証し、AIへの過信を構造的に防ぐため
  - Notes: _DISCLAIMER 定数 + report["disclaimer"] + format_report() の [Disclaimer] セクションとして実装済み（session 10）
  - Status: done

### カテゴリ4: ユーザー体験・デモ拡張

- [x] (2026-02-28) Idea: 3者レビュー（Builder/Skeptic/User）を CLI で自動実行するスクリプト
  - Source: Grok
  - Why: guideline.md の 3-Review Rule をコードで体現するため
  - Notes: scripts/three_review.py として実装済み（session 10）。パイプ対応（md_adapter | three_review）
  - Status: done

- [ ] (2026-02-28) Idea: 決定後の「事後検証テンプレート」自動生成
  - Source: Grok
  - Why: 「この決定、3ヶ月後に振り返った時に何を確認すべきか」を事前に定義するため
  - Notes: decision_brief の recommendation と next_questions から「事後チェックリスト」を自動生成。scripts/postmortem_template.py で実装可能
  - Status: backlog

- [x] (2026-02-28) Idea: 候補案の「影響範囲マップ」自動作成
  - Source: Grok
  - Why: 「誰にどんな影響が出るか」を受益者×影響構造の表で可視化するため
  - Notes: _build_impact_map() + report["impact_map"] + format_report() の [Impact Map] セクションとして実装済み（session 10）
  - Status: done

- [ ] (2026-02-28) Idea: 入力の「文脈圧縮」自動機能
  - Source: Grok
  - Why: 長文 situation を重要情報を保持したまま要約し、処理精度を上げるため
  - Notes: 標準ライブラリのみで実装（文長でフィルタリング + キーワード抽出）。外部 NLP ライブラリは使わない
  - Status: backlog

### カテゴリ5: メタ・自己改善

- [ ] (2026-02-28) Idea: 「このリポジトリ自身を改善する提案」を AI が出すメタモジュール
  - Source: Grok
  - Why: タイトル通りの「AIがAIを作る」循環を安全に体験するため（人間レビュー必須）
  - Notes: 毎回 progress_log.md / guideline.md を読んで「次にやるべきこと」を3案出す。scripts/meta_suggest.py として実装。外部 API 不使用
  - Status: backlog

---

## 将来検討（方針要確認）

- [ ] (2026-02-28) Idea: 「決定支援カーネル」を完全に独立した Python パッケージ化（pip install 可能）
  - Source: Grok
  - Why: aicw/ を他プロジェクトにも「1行で」取り込めるようにする
  - Notes: ⚠ 現時点では時期尚早。Po_core 連携が固まり、API が安定してから検討。pip パッケージ化はリリースポリシーの決定も必要
  - Status: 保留（Po_core 連携後に再検討）

- [ ] (2026-02-28) Idea: run_demo.py を「インタラクティブ意思決定シミュレーター」に進化（GUI化）
  - Source: Grok
  - Why: 企業向けデモで「実際に使ってる感」を出すため
  - Notes: ⚠ Streamlit/Gradio は**外部依存NG**（方針違反）。ただし標準ライブラリの tkinter や curses で CLI インタラクティブ版なら可能。要検討
  - Status: 保留（外部依存なし実装方法を検討してから）

- [ ] (2026-02-28) Idea: オフライン知識ベース（ローカル JSON）に「過去類似決定」を蓄積
  - Source: Grok
  - Why: 「以前似たような決定をした」という文脈を活用するため
  - Notes: ⚠ 「候補案の全文は保存しない」方針と競合する可能性あり。ハッシュ + reason_codes のみ保存なら可能かもしれない。Privacyチェック必須
  - Status: 保留（privacy 方針との整合確認後に再検討）
