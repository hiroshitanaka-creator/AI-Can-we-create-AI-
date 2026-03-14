# Idea Notes
> 思いつき/提案/将来の改善案のメモ。採用・保留・却下を残す。

## Backlog
- [x] (2026-03-09) Idea: meta_suggest のチェックリスト除外を日本語見出しでも機能させる
  - Source: PR review feedback
  - Why: `No-Go チェックリスト` のような見出しでも誤って実装タスク抽出されないようにするため
  - Notes: `scripts/meta_suggest.py` の非タスク見出しヒントに `チェックリスト` を追加。`tests/test_meta_suggest.py` に日本語見出し回帰テストを追加
  - Status: done

- [x] (2026-03-09) Idea: meta_suggest が Safety Checklist / No-Go Checklist をタスクとして拾わないようにする
  - Source: docs/next_issues.md Issue #2
  - Why: 実装タスクと確認チェックリストを区別し、次アクション提案の精度を上げるため
  - Notes: `scripts/meta_suggest.py` に非タスク見出し除外を追加し、`tests/test_meta_suggest.py` に回帰テストを追加
  - Status: done

- [x] (2026-03-08) Idea: manipulation 検知をスコアリング化し warn/block を段階化する
  - Source: Sprint Task 6
  - Why: 単純一致の誤検知を抑えつつ、高リスク文脈は確実に block するため
  - Notes: `aicw/safety.py` の `scan_manipulation()` を拡張し、`tests/test_p0_manipulation.py` に safe/risky 各10ケースを追加
  - Status: done

- [x] (2026-03-08) Idea: 10タスクを2週間スプリントとして優先順位付きに固定する
  - Source: User
  - Why: Codexで順次実装できる実行順とDoDを先に固定し、手戻りを減らすため
  - Notes: `sprint_plan.md` を作成し、Week1/Week2 の順で実装可能な形に整理
  - Status: done

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

- [x] (2026-02-22) Idea: Markdown入力アダプタ（Markdown→decision_request.v0 JSON変換）を後付けする
  - Source: AI
  - Why: JSON編集が苦手でも使えるようにする（ただしcanonicalはJSONのまま）
  - Notes: `scripts/md_adapter.py` + `tests/test_md_adapter.py` として実装済み。契約（decision_request.v0）を維持したまま入口のみ追加
  - Status: done

- [x] (2026-02-22) Idea:リスクと改善提案
　- 誤検知の扱い
　- 現状は全て severity="block" で止める設計。運用では warn と block を分け、人間の確認フローを入れると安全です。（対応済み: `aicw/safety.py` で warn/block 段階化）
　- 正規表現の脆弱性
　- 例えばメールの正規表現は簡易版で、RFC準拠ではない。重要用途なら既存ライブラリや成熟したPII検出ライブラリを検討してください。
　- コンテキスト判定の欠如
　- scan_manipulation のような単純一致は文脈を無視するため、誤検知が多い。NLPベースの文脈判定（軽量モデルやルール＋スコアリング）を組み合わせると精度が上がります。（対応済み: スコアリング化 + reverse_manipulation を `P1-ngram` へ強化）
　- 監査ログとメタ情報
　- 何を検出したか（中身は保存しない）・いつ誰がブロックしたか等の監査ログを残す仕組みを入れると運用上安心です。（対応済み: `aicw/audit_log.py`）
　- テストカバレッジ
　- 正規表現ごとに正例・負例のユニットテストを用意し、誤検知率を定量化して閾値を決めるべ（対応済み: 関連ユニットテスト拡充）
　- きです。
  - Status: done（主要提案は実装反映済み）

- [ ] 具体的な小さな改善コード例（方針のみ）
　- Finding.severity をルールごとに設定可能にする（現在は固定）。
　- SECRET_KEYWORD の検出は周辺語を確認して「単語単体の出現」だけでブロックしない（例: password が文脈で説明的に出ているだけなら warn）。
　- ログ出力用に検出サマリを返す（件数、種類、最初の位置など）を guard_text に追加する。

---

## Backlog（Grokからのアイデア — 2026-02-28 受領）

### カテゴリ1: 検証・テスト強化

- [x] (2026-02-28) Idea: 決定リクエストのファジングテスト自動生成フレームワーク
  - Source: Grok
  - Why: 手動テストでは到達できない「矛盾制約」「超長文脈」「微妙な誘導文」を検知し、DLP・status-invariant・anti-manipulation の信頼性を指数関数的に高める
  - Notes: `scripts/gen_fuzz_cases.py` + `tests/test_fuzz_smoke.py` + `tests/data/fuzz_seed_cases.json` として実装済み（2026-03-08 session 12）
  - Status: done

- [x] (2026-02-28) Idea: 決定結果の「自己矛盾検知」自動チェックモジュール
  - Source: Grok
  - Why: 同一状況で異なる結論が出ないことをコードレベルで保証するため
  - Notes: `scripts/check_consistency.py` + `tests/test_consistency.py` として実装済み（2026-03-08 session 12）
  - Status: done

- [x] (2026-02-28) Idea: 「文化差分テスト」データセットの作成
  - Source: Grok
  - Why: Status-invariant を守りつつ、日本企業特有の「根回し文化」や「集団調和」を正しく Context-dependent に扱えるか検証するため
  - Notes: `tests/data/culture_cases.json` + `tests/test_culture_diff.py` として実装済み（2026-03-08 session 13）
  - Status: done

### カテゴリ2: 哲学的・説明性向上

- [x] (2026-02-28) Idea: 軽量「哲学者アンサンブル」シミュレーター（Po_core プレビュー版）
  - Source: Grok
  - Why: 本格 Po_core 連携前に、このリポジトリだけで「哲学的議論」を体現し、説得力を高める
  - Notes: 3哲学者テンプレート（HiroshiTanaka / Pragmatist / RightsGuardian）を `bridge/ensemble.py` に実装し、多数派意見 + 少数意見（全会一致時は SystemMinority 補完）を返す設計で完了（2026-03-09 session 11）。
  - Status: done

- [x] (2026-02-28) Idea: 「哲学的矛盾検知」モジュール
  - Source: Grok
  - Why: 決定理由の中に「義務論と功利主義が矛盾してる」みたいな哲学的齟齬を指摘するため
  - Notes: `aicw/philosophy_check.py` で 3系統（義務論/功利、公正/効率、権利/総便益）の矛盾 reason code 検知を実装し、`aicw/decision.py` 側の `reason_codes` にも接続済み（2026-03-09 session 11）。
  - Status: done

- [x] (2026-02-28) Idea: 「不確実性マップ」自動生成機能
  - Source: Grok
  - Why: 「不確実性があります」ではなく、どの部分がどれだけ不確実かを言語化するため
  - Notes: `scripts/uncertainty_map.py` + `tests/test_uncertainty_map.py` として実装済み（2026-03-08 session 15）
  - Status: done

### カテゴリ3: 安全性・倫理的堅牢性

- [x] (2026-02-28) Idea: 「人間の決定を逆算して誘導していないか」の動的チェック
  - Source: Grok
  - Why: static な anti-manipulation を超え、出力後に逆算して「AI が人間の結論を先読みして誘導してないか」を検知するため
  - Notes: `aicw/safety.py` に `check_reverse_manipulation()` を追加（Jaccard 語彙類似度による近似推定）。`tests/test_reverse_manipulation.py` 12件追加（2026-03-09 session 17）
  - Status: done（初期近似実装。将来 NLP ベースへの強化は継続課題）

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

- [x] (2026-02-28) Idea: 決定後の「事後検証テンプレート」自動生成
  - Source: Grok
  - Why: 「この決定、3ヶ月後に振り返った時に何を確認すべきか」を事前に定義するため
  - Notes: `scripts/postmortem_template.py` + `tests/test_postmortem_template.py` として実装済み（2026-03-08 session 13）
  - Status: done

- [x] (2026-02-28) Idea: 候補案の「影響範囲マップ」自動作成
  - Source: Grok
  - Why: 「誰にどんな影響が出るか」を受益者×影響構造の表で可視化するため
  - Notes: _build_impact_map() + report["impact_map"] + format_report() の [Impact Map] セクションとして実装済み（session 10）
  - Status: done

- [x] (2026-02-28) Idea: 入力の「文脈圧縮」自動機能
  - Source: Grok
  - Why: 長文 situation を重要情報を保持したまま要約し、処理精度を上げるため
  - Notes: `aicw/context_compress.py` + `tests/test_context_compress.py` を追加（2026-03-08 session 13）。外部依存なし
  - Status: done

### カテゴリ5: メタ・自己改善

- [x] (2026-02-28) Idea: 「このリポジトリ自身を改善する提案」を AI が出すメタモジュール
  - Source: Grok
  - Why: タイトル通りの「AIがAIを作る」循環を安全に体験するため（人間レビュー必須）
  - Notes: `scripts/meta_suggest.py` と `tests/test_meta_suggest.py` を追加し、未完了チェックボックスを収集して上位3提案をJSONで返すCLIとして実装（2026-03-09 session 16）。外部 API 不使用
  - Status: done

---

## 将来検討（方針要確認）

- [ ] (2026-02-28) Idea: 「決定支援カーネル」を完全に独立した Python パッケージ化（pip install 可能）
  - Source: Grok
  - Why: aicw/ を他プロジェクトにも「1行で」取り込めるようにする
  - Notes: ⚠ 現時点では時期尚早。Po_core 連携が固まり、API が安定してから検討。pip パッケージ化はリリースポリシーの決定も必要
  - Status: 保留（Po_core 連携後に再検討）

- [x] (2026-02-28) Idea: run_demo.py を「インタラクティブ意思決定シミュレーター」に進化（GUI化）
  - Source: Grok
  - Why: 企業向けデモで「実際に使ってる感」を出すため
  - Notes: `scripts/interactive_sim.py` として `input()` ベース CLI で実装（外部依存なし）。`--auto` / `--json` / `--no-kb` オプション対応。stdin 差し替えでテスト可能（2026-03-09 session 19）
  - Status: done（CLIインタラクティブ版として実装完了）

- [x] (2026-02-28) Idea: オフライン知識ベース（ローカル JSON）に「過去類似決定」を蓄積
  - Source: Grok
  - Why: 「以前似たような決定をした」という文脈を活用するため
  - Notes: `aicw/knowledge_base.py` として実装。decision_hash + status + reason_codes + timestamp のみ保存（生テキスト保存なし）。Jaccard 類似度で類似過去決定を検索。JSON ファイル永続化対応（2026-03-09 session 19）
  - Status: done（#6 Privacy 完全準拠で実装完了）
