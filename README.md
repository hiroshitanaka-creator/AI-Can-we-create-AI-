# AI — Can we create AI?

> **Mission:** Po_core のために、チームの意思決定を支援する AI を作り上げる。

---

## Vision

いつか、このリポジトリで育てた AI が **[Po_core](https://github.com/hiroshitanaka-creator)** の中核を担う。
それが、このプロジェクトの夢。

---

## Purpose

チーム内の業務意思決定を **支援** する（判断の後押し）。

- 最終判断は **人間** が行う
- AI は根拠・反証・不確実性・外部性を **構造化して提示** する

---

## Core Principles

| Principle | Description |
|---|---|
| **Status-invariant** | 肩書・権威では答えを変えない |
| **Context-dependent** | 条件・制約・状況で答えを変える |
| **Explainable selection** | 候補案と選定理由を提示する |

---

## Non-Negotiables

これらは **絶対に越えない線** 。検知された場合は自動的に縮退 / 停止する。

```
[#3]  差別・被害の集中         → FORBIDDEN
[#4]  操作・扇動               → FORBIDDEN
[#6]  プライバシー侵害         → FORBIDDEN
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Verifiable Decision Layer           │
│         (rules / templates / logs)          │
│                  ↓ decides                  │
├─────────────────────────────────────────────┤
│           Language Layer (optional)         │
│       summarizes / lists counterarguments   │
└─────────────────────────────────────────────┘
```

---

## Security

- **Offline-first** — デフォルトで外部ネットワーク接続なし
- **Minimal logging** — 最小限のログ + 暗号化 + TTL
- **Fail closed** — 利用不能時は安全側に倒して停止

---

## Workflow

主要な変更には **3者のレビュー** が必要:

```
Builder   →  作る視点
User      →  使う視点
Skeptic   →  疑う視点
```

通過必須テスト: `DLP` / `status-diff` / `anti-manipulation`

---

## License

See [LICENSE](./LICENSE).
