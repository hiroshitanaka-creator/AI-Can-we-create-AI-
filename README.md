# AI — Can we create AI?

> **Core Tagline:** "ブタは飛べないと言った。でも、哲学というバルーンを付けたら飛んだ。🐷🎈"
> ── inspired by [Po_core](https://github.com/hiroshitanaka-creator/Po_core)

---

## Overview

**AI — Can we create AI?** は、チーム内の業務意思決定を **支援する** AI を研究・開発するリポジトリ。

最終判断は常に **人間** が行う。AI は根拠・反証・不確実性・外部性を **構造化して提示** するだけ。

**夢:** いつか、ここで育てた AI が [Po_core](https://github.com/hiroshitanaka-creator/Po_core) の中核エンジンとして稼働する。

---

## Key Features

### Status-invariant Reasoning
肩書・権威・役職では答えを変えない。同じ条件なら同じ答えを返す。

### Context-dependent Judgment
条件・制約・状況が変われば、答えも変わる。文脈を読む。

### Explainable Selection
候補案と選定理由を必ずセットで提示する。「なぜこの案か」を開示する。

---

## Non-Negotiables

以下は **絶対に越えない線**。検知した瞬間に自動縮退 / 停止する。

| # | 禁止事項 | 対応 |
|---|---|---|
| 3 | 差別・被害の集中 | `FORBIDDEN` → 即停止 |
| 4 | 操作・扇動 | `FORBIDDEN` → 即停止 |
| 6 | プライバシー侵害 | `FORBIDDEN` → 即停止 |

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│           Verifiable Decision Layer              │
│         rules / templates / audit logs           │
│                      ↓ decides                   │
├──────────────────────────────────────────────────┤
│           Language Layer  (optional)             │
│   summarizes · lists counterarguments · explains │
└──────────────────────────────────────────────────┘
```

---

## Project Status

| Component | Status | Notes |
|---|---|---|
| Core Principles definition | ✅ Complete | Status-invariant / Context-dep / Explainable |
| Non-Negotiables spec | ✅ Complete | #3 / #4 / #6 auto-stop |
| Verifiable Decision Layer | 🔬 Research | rules + templates |
| Language Layer | 🔬 Research | summarization / counterargument listing |
| Po_core integration | 🌱 Dream | 最終目標 |

---

## Security

- **Offline-first** — デフォルトで外部ネットワーク接続なし
- **Minimal logging** — 最小限のログ + 暗号化 + TTL
- **Fail closed** — 利用不能時は安全側に倒して完全停止

---

## Workflow

主要な変更には **3者レビュー** が必要:

```
Builder  →  作る視点でレビュー
User     →  使う視点でレビュー
Skeptic  →  疑う視点でレビュー
```

通過必須テスト: `DLP` / `status-diff` / `anti-manipulation`

---

## Relation to Po_core

このプロジェクトは [Po_core](https://github.com/hiroshitanaka-creator/Po_core) の姉妹プロジェクト。

Po_core が **哲学的アンサンブル推論** を担うとすれば、
このリポジトリは **業務意思決定特化の推論層** を育てることを目指す。
いつか二つが合流する日を夢見て。

---

## License

[GNU General Public License v3.0 or later](./LICENSE)

## Project docs (Single Source of Truth)
- guideline.md（運用ルール / 次にやること）
- progress_log.md（作業日誌）
- idea_note.md（アイデア置き場）
- coding-style.md（コーディング規約）
