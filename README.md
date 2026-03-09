# 🐷 AI-Can-we-create-AI-

<p align="center">
  <img src="[https://img.shields.io/badge/License-GPLv3-blue.svg](https://img.shields.io/badge/License-GPLv3-blue.svg)" alt="License: GPL v3">
  <img src="[https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)" alt="Python">
  <img src="[https://img.shields.io/badge/Status-Experimental-orange](https://img.shields.io/badge/Status-Experimental-orange)" alt="Status: Experimental">
  <a href="[https://github.com/hiroshitanaka-creator/Po_core](https://github.com/hiroshitanaka-creator/Po_core)">
    <img src="[https://img.shields.io/badge/Sister%20Project-Po__core-FF69B4](https://img.shields.io/badge/Sister%20Project-Po__core-FF69B4)" alt="Sister Project: Po_core">
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

このリポジトリは、**「AIを自分で作る」**という純粋な好奇心から生まれた実験場であり、チーム内の業務意思決定を**支援する**AIを研究・開発するプロジェクトです。

[Po_core](https://github.com/hiroshitanaka-creator/Po_core)（哲学39人＋AIによる意思決定エンジン）の心臓部として、僕の思想をぎっしり詰め込んだAIをゼロから構築します。

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
| 4 | **操作・扇動** | `FORBIDDEN` → 即停止 |
| 6 | **プライバシー侵害** | `FORBIDDEN` → 即停止 |

---

## 🏗️ Architecture & Security

「ブラックボックス」を徹底的に排除した、多層構造の意思決定支援プロセスです。

```text
┌──────────────────────────────────────────────────┐
│           Verifiable Decision Layer              │
│         rules / templates / audit logs           │
│                      ↓ decides                   │
├──────────────────────────────────────────────────┤
│           Language Layer  (optional)             │
│   summarizes · lists counterarguments · explains │
└──────────────────────────────────────────────────┘
```

### Security Features
- **Offline-first:** デフォルトで外部ネットワーク接続なし。プライバシーを最優先。
- **Minimal logging:** 最小限のログ + 暗号化 + TTL（生存期間）の設定。
- **Fail closed:** 疑わしい挙動や利用不能時は、安全側に倒して「動作しない（完全停止）」を選択。

---

## 🔄 Workflow

主要な変更や意思決定には、以下の**3者合議制レビュー**が必須です。

- **Builder:** 作る視点でレビュー
- **User:** 使う視点でレビュー
- **Skeptic (懐疑派):** 疑う視点でレビュー

> ※ 通過必須テスト: `DLP` / `status-diff` / `anti-manipulation`

---

## 📍 Relation to Po_core

このプロジェクトは [Po_core](https://github.com/hiroshitanaka-creator/Po_core) の姉妹プロジェクトです。

Po_coreが**「哲学的アンサンブル推論」**を担う全体システムだとすれば、このリポジトリは**「業務意思決定特化の推論層（心臓部）」**を育てる実験場です。いつかここで育てたAIが、Po_coreの中核エンジンとして稼働する日を夢見ています。

---

## 🚀 Quick Start / クイックスタート

```bash
# 1. リポジトリのクローン
git clone https://github.com/hiroshitanaka-creator/AI-Can-we-create-AI-.git
cd AI-Can-we-create-AI-

# 2. 依存関係のインストール
pip install -r requirements.txt

# 3. デモの実行
python run_demo.py
```

---

## 🛤️ Project Status & Roadmap

| Component | Status | Notes |
| :--- | :--- | :--- |
| Core Principles definition | ✅ Complete | Status-invariant / Context-dep / Explainable |
| Non-Negotiables spec | ✅ Complete | #3 / #4 / #6 auto-stop |
| Verifiable Decision Layer | ✅ v0.1 stable | audit_log + rule engine + テスト基盤 |
| Language Layer | ✅ Implemented | context_compress / philosophy_check / ensemble |
| Po_core integration | 🌱 Dream | 最終目標 |

**Upcoming Milestones (2026):**
- [x] Verifiable Decision Layer v0.1 の安定化（audit_log + 監査ハッシュ）
- [x] 3人レビュー＋自動テスト基盤の実装（three_review CLI + ensemble）
- [x] AI権利に関する哲学的実験モジュールの追加（ai_rights_experiment）
- [x] 逆算誘導チェック（check_reverse_manipulation, No-Go #4 強化）
- [ ] 哲学テンソル統合 (Po_coreとの本格連携)
- [ ] 実ビジネス意思決定支援デモ (非公開企業向け)

---

## 📚 Project Docs (Single Source of Truth)

プロジェクトの詳細は以下のドキュメントに集約されています。参加前に必ずご一読ください。

- [guideline.md](./guideline.md) （運用ルール / 次にやること）
- [progress_log.md](./progress_log.md) （作業日誌）
- [idea_note.md](./idea_note.md) （僕の生の思考過程・アイデア置き場）
- [coding-style.md](./coding-style.md) （思想が詰まったコーディング規約）

---

## 🤝 Contribution / 参加について

- 思想を共有したい哲学者・エンジニア
- **「AIを自分で作る」**というロマンを追い求めたい人
- 「飛べない豚」を本気で飛ばしたい人

IssueやPull Requestは大歓迎です！

---

## 📜 License

[GNU General Public License v3.0 or later](./LICENSE)
「オープンに、自由に、でも責任を持って」 — それが僕の思想です。

---

## 👤 Creator / 作者

<table align="center">
  <tr>
    <td align="center">
      <img src="[https://github.com/hiroshitanaka-creator.png](https://github.com/hiroshitanaka-creator.png)" width="100px;" alt="Flying Pig"/><br />
      <sub><b>飛べない豚 (Flying Pig Philosopher)</b></sub>
    </td>
    <td>
      <b>"Can't fly, but philosophy makes me fly."</b><br><br>
      <ul>
        <li><b>X (Twitter):</b> <a href="[https://x.com/Detours_is_Life](https://x.com/Detours_is_Life)">@Detours_is_Life</a></li>
        <li><b>GitHub:</b> <a href="[https://github.com/hiroshitanaka-creator](https://github.com/hiroshitanaka-creator)">hiroshitanaka-creator</a></li>
        <li><b>Academia.edu:</b> <a href="[https://independent.academia.edu/僕僕](https://independent.academia.edu/僕僕)">僕僕</a></li>
      </ul>
    </td>
  </tr>
</table>

<p align="center">
  AIって、本当に自分で作れるのか？まだわからない。<br>
  だからこそ、今、作ってみる。<br>
  <b>一緒に、哲学のバルーンを膨らませて飛ばそう。</b> 🐷🎈
</p>
