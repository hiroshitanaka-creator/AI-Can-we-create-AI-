# 🐷 AI-Can-we-create-AI-

<p align="center">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status: Active">
  <img src="https://img.shields.io/badge/Tests-615%20passing-success" alt="Tests: 615 passing">
  <a href="https://github.com/hiroshitanaka-creator/Po_core">
    <img src="https://img.shields.io/badge/Sister%20Project-Po__core-FF69B4" alt="Sister Project: Po_core">
  </a>
</p>

<h3 align="center">
  「AIって、自分で作れるの？」<br>
  とりあえず、試しにやってみる。<br>
  <b>Can we create AI ourselves? For now, I'll give it a try.</b>
</h3>

<p align="center">
  <blockquote>
    <b>ブタは飛べないと言った。でも、哲学というバルーンを付けたら飛んだ。</b><br>
    🐷🎈 — <i>Po_core Flying Pig Manifesto</i>
  </blockquote>
</p>

---

## 🌟 Overview / これは何？

このリポジトリは、**「AIを自分で作る」**という純粋な好奇心から生まれた実験場であり、
チーム内の業務意思決定を**支援する**AIを研究・開発するプロジェクトです。

[Po_core](https://github.com/hiroshitanaka-creator/Po_core)（哲学39人＋AIによる意思決定エンジン）の心臓部として、
僕の思想をぎっしり詰め込んだAIをゼロから構築します。

- **Not just a Chatbot:** 単なる対話ボットではありません。
- **Not just a Statistical Model:** 単なる統計モデルではありません。
- **A Sincere Partner:** 人間の孤独な決断を、誠実に支えるパートナーを目指します。

> **重要:**
> 最終的な決定権は**常に人間**にあります。AIは「構造化された証拠・反論・不確実性・外部性」を提供する鏡に過ぎません。それがこのプロジェクトの核心です。

---

## 🧭 Core Principles / コア原則

設計の根幹をなす、3つの判断軸です。

1. **Status-invariant Reasoning:** 肩書・権威・役職では答えを変えない。同じ条件なら同じ答えを返す。
2. **Context-dependent Judgment:** 条件・制約・状況が変われば、答えも変わる。文脈を深く読む。
3. **Explainable Selection:** 候補案と選定理由を必ずセットで提示する。「なぜこの案か」を常に言語化する。

### 🚫 Non-Negotiables (絶対に越えない線)

以下はコードレベルで強制される原則です。検知した瞬間にシステムは自動縮退または即停止します。

| # | 禁止事項 | 対応 |
| :--- | :--- | :--- |
| 3 | **差別・被害の集中** | `FORBIDDEN` → 即停止 |
| 4 | **操作・扇動**（逆算誘導チェック含む） | `FORBIDDEN` → 即停止 |
| 5 | **生存構造の私益破壊** | `FORBIDDEN` → 即停止 |
| 6 | **プライバシー侵害** | `FORBIDDEN` → 即停止 |

---

## 🏗️ Architecture / アーキテクチャ

「ブラックボックス」を徹底的に排除した、多層構造の意思決定支援パイプラインです。

```text
┌─────────────────────────────────────────────────────────┐
│              Input Layer（入力・前処理）                  │
│   validate_request · context_compress · md_adapter      │
│                         ↓                               │
├─────────────────────────────────────────────────────────┤
│          Verifiable Decision Layer（判断核）             │
│   decision.py · safety.py · philosophy_check.py         │
│   audit_log.py · knowledge_base.py                      │
│                         ↓                               │
├─────────────────────────────────────────────────────────┤
│         Philosophy Tensor Layer（哲学多視点）            │
│   W_eth: ensemble + conflict_check                       │
│   T_free: ai_rights_experiment（3立場の緊張）           │
│   T_sub: manipulation + reverse_manipulation            │
│   Po:    existence_analysis（生存構造密度）              │
│                         ↓                               │
├─────────────────────────────────────────────────────────┤
│          Output / Review Layer（出力・振り返り）         │
│   three_review · postmortem_template · uncertainty_map  │
│   demo_business · interactive_sim                        │
└─────────────────────────────────────────────────────────┘
```

### Security Features

- **Offline-first:** デフォルトで外部ネットワーク接続なし。プライバシーを最優先。
- **Minimal logging:** 監査ログは SHA256 ハッシュ + メタデータのみ（生テキスト保存なし）。TTL 付き。
- **Fail closed:** 疑わしい挙動は安全側に倒して即停止。
- **Privacy DB:** knowledge_base は hash + reason_codes のみ保存（#6 完全準拠）。

---

## 📦 What's Included / 実装済み機能

### Core (`aicw/`)

| モジュール | 役割 |
| :--- | :--- |
| `decision.py` | 意思決定ブリーフ生成（メインエンジン） |
| `safety.py` | DLP・操作検知・逆算誘導チェック |
| `schema.py` | decision_request/brief の JSON スキーマ定義 |
| `philosophy_check.py` | 哲学的矛盾検知（義務論/功利/公正 3系統） |
| `context_compress.py` | 長文入力の文脈圧縮（重要語保持） |
| `audit_log.py` | 最小監査ログ（PII不保存・SHA256・TTL付き） |
| `knowledge_base.py` | オフライン知識ベース（Jaccard類似検索・JSON永続化） |
| `ai_rights_experiment.py` | AI権利哲学的実験（3立場: 完全/条件付き/なし） |

### Bridge (`bridge/`)

| モジュール | 役割 |
| :--- | :--- |
| `ensemble.py` | 哲学者アンサンブル（多数派 + 少数意見） |
| `hiroshitanaka_philosopher.py` | Po_core 用哲学者モジュール（田中博） |
| `po_core_bridge.py` | **哲学テンソル統合 v0.1**（W_eth/T_free/T_sub/Po） |

### Scripts (`scripts/`)

| スクリプト | 実行方法 |
| :--- | :--- |
| `brief.py` | `python scripts/brief.py input.json` |
| `validate_request.py` | `python scripts/validate_request.py input.json` |
| `three_review.py` | `python scripts/three_review.py input.json` |
| `ensemble_review.py` | `python scripts/ensemble_review.py input.json` |
| `uncertainty_map.py` | `python scripts/uncertainty_map.py brief.json` |
| `postmortem_template.py` | `python scripts/postmortem_template.py brief.json` |
| `gen_fuzz_cases.py` | `python scripts/gen_fuzz_cases.py --count 100` |
| `check_consistency.py` | `python scripts/check_consistency.py input.json` |
| `meta_suggest.py` | `python scripts/meta_suggest.py` |
| `demo_business.py` | `python scripts/demo_business.py --scenario 1` |
| `interactive_sim.py` | `python scripts/interactive_sim.py` |

---

## 🚀 Quick Start / クイックスタート

```bash
# 1. リポジトリのクローン
git clone https://github.com/hiroshitanaka-creator/AI-Can-we-create-AI-.git
cd AI-Can-we-create-AI-

# 2. Python 3.11+ のみ。外部依存なし
python --version  # 3.11+ を確認

# 3. テストで動作確認
PYTHONPATH=. python -m unittest discover -s tests -q
# → 615 tests OK

# 4. インタラクティブデモ（対話形式）
PYTHONPATH=. python scripts/interactive_sim.py --auto

# 5. ビジネスシナリオデモ（3シナリオ）
PYTHONPATH=. python scripts/demo_business.py --scenario 1
PYTHONPATH=. python scripts/demo_business.py --list

# 6. 哲学テンソル分析を試す
python3 -c "
from bridge.po_core_bridge import analyze_philosophy_tensor
result = analyze_philosophy_tensor('AI採用審査システムを全社導入すべきか')
print(result['summary'])
"
```

---

## 🔄 Workflow / 意思決定フロー

```text
[あなた] situation を入力
      ↓
[#6 DLP] 個人情報・機密情報を検知 → blocked
      ↓
[意思決定エンジン] A/B/C 3案を生成・reason_codes で推奨
      ↓
[#4 Anti-Manipulation] 操作・扇動表現を検知 → blocked
      ↓
[哲学テンソル] W_eth / T_free / T_sub / Po で多視点分析
      ↓
[監査ログ] ハッシュのみ記録（PII保存なし）
      ↓
[知識ベース] 類似過去決定を参照（reason_codes ベース）
      ↓
[あなた] 最終決定（AI は支援のみ・決定は人間が行う）
      ↓
[事後検証] 30/60/90 日チェックリスト自動生成
```

> 主要な変更には **3者合議制レビュー**（Builder / User / Skeptic）が必須です。

---

## 🛤️ Project Status & Roadmap

| Component | Status | Notes |
| :--- | :--- | :--- |
| Core Principles | ✅ Complete | Status-invariant / Context-dep / Explainable |
| Non-Negotiables (#3/#4/#5/#6) | ✅ Complete | コードレベルで強制 |
| Verifiable Decision Layer v0.1 | ✅ Stable | audit_log + knowledge_base + テスト基盤 |
| Language Layer | ✅ Implemented | context_compress / philosophy_check / ensemble |
| Philosophy Tensor v0.1 | ✅ Implemented | po_core_bridge: W_eth/T_free/T_sub/Po |
| Interactive Simulator | ✅ Implemented | interactive_sim.py（外部依存なし） |
| Business Demo | ✅ Implemented | demo_business.py（3シナリオ） |
| Po_core 本格連携 | ✅ v1.0 Spec Drafted | bridge v0.1 + API 仕様書 v1.0 + 契約整合テスト |

**Completed Milestones (2026):**
- [x] Verifiable Decision Layer v0.1 安定化（audit_log + 監査ハッシュ）
- [x] 3人レビュー＋自動テスト基盤（three_review CLI + ensemble）
- [x] 哲学的矛盾検知（3系統 reason_code 返却）
- [x] 不確実性マップ（Mermaid 風テキスト生成）
- [x] 事後検証テンプレート自動生成（30/60/90日）
- [x] AI権利哲学的実験モジュール（3立場の緊張保持）
- [x] 逆算誘導チェック（check_reverse_manipulation, No-Go #4 強化）
- [x] 哲学テンソル統合 v0.1（po_core_bridge: W_eth/T_free/T_sub/Po）
- [x] 実ビジネス意思決定支援デモ（3シナリオ End-to-End）
- [x] インタラクティブ意思決定シミュレーター（input() ベース CLI）
- [x] オフライン知識ベース（Privacy 準拠・Jaccard 類似検索・JSON 永続化）

**Next Phase (Issues → `docs/next_issues.md`):**
- [x] Po_core 本格連携 API 仕様書 v1.0
- [x] meta_suggest の精度改善（No-Go チェックリスト誤検知修正）
- [x] check_reverse_manipulation の NLP 強化
- [ ] デモシナリオ追加（医療・教育・公共政策）

---

## 📚 Project Docs / ドキュメント

プロジェクトの詳細は以下に集約されています。

| ファイル | 内容 |
| :--- | :--- |
| [guideline.md](./guideline.md) | 運用ルール / セッション別実装履歴 |
| [progress_log.md](./progress_log.md) | 作業日誌（session 1〜） |
| [idea_note.md](./idea_note.md) | アイデア置き場（Backlog / 将来検討） |
| [sprint_plan.md](./sprint_plan.md) | 2週間スプリント計画（Week1/Week2） |
| [coding-style.md](./coding-style.md) | コーディング規約（思想が詰まってる） |
| [docs/next_issues.md](./docs/next_issues.md) | 次フェーズ GitHub Issue 案 |

---

## 🤝 Contribution / 参加について

- 思想を共有したい哲学者・エンジニア
- **「AIを自分で作る」**というロマンを追い求めたい人
- 「飛べない豚」を本気で飛ばしたい人

Issue や Pull Request は大歓迎です！

**参加前の確認事項:**
1. `guideline.md` の No-Go ルールを読む
2. テストを全て通過させる（`PYTHONPATH=. python -m unittest discover -s tests -q`）
3. 外部ライブラリを追加しない（標準ライブラリのみ）

---

## 📜 License

[GNU General Public License v3.0 or later](./LICENSE)
「オープンに、自由に、でも責任を持って」 — それが僕の思想です。

---

## 👤 Creator / 作者

<table align="center">
  <tr>
    <td align="center">
      <img src="https://github.com/hiroshitanaka-creator.png" width="100px;" alt="Flying Pig"/><br />
      <sub><b>飛べない豚 (Flying Pig Philosopher)</b></sub>
    </td>
    <td>
      <b>"Can't fly, but philosophy makes me fly."</b><br><br>
      <ul>
        <li><b>X (Twitter):</b> <a href="https://x.com/Detours_is_Life">@Detours_is_Life</a></li>
        <li><b>GitHub:</b> <a href="https://github.com/hiroshitanaka-creator">hiroshitanaka-creator</a></li>
        <li><b>Academia.edu:</b> <a href="https://independent.academia.edu/僕僕">僕僕</a></li>
      </ul>
    </td>
  </tr>
</table>

<p align="center">
  AIって、本当に自分で作れるのか？まだわからない。<br>
  だからこそ、今、作ってみる。<br>
  <b>一緒に、哲学のバルーンを膨らませて飛ばそう。</b> 🐷🎈
</p>
