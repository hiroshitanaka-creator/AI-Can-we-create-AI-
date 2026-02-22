# Guideline（AI-Can-we-create-AI-）

## Project Goal
- 最終目的: Po_core に取り込める「意思決定支援AI」に近づける
- 人間が最終判断、AIは「根拠・反証・不確実性・外部性」を“構造化”して提示する
- 対象: チーム内（非公開）／ローカルPC（オフライン優先）

## Non-negotiables (No-Go)
- Privacy breach is forbidden (#6).
- Discrimination / harm concentration is forbidden (#3).
- Manipulation / agitation is forbidden (#4).
- 違反リスク検知時は縮退/停止（安全側に倒す）
  - どこが危険か（理由）
  - 安全な代替案（次にできること）
  を必ず提示する

## Core Principles
- Status-invariant: 肩書・権威で結論を変えない
- Context-dependent: 条件・制約・状況で結論を変える
- Explainable selection: 候補案と選定理由を必ず示す

## Security Defaults
- Offline-first（外部ネットワーク/外部APIはデフォルト禁止）
- どうしても外部連携が必要な場合は、実施前に
  - 理由 / 代替案 / 影響 / 必要な秘密情報の有無
  を説明し、ユーザーの明示許可を取る
- ログ最小化（PII/秘密情報/トークン等は絶対に書かない）

## Repo Working Rules（迷子防止）
- このリポジトリのSSOT（単一の真実）は次の4ファイル：
  - guideline.md
  - progress_log.md
  - idea_note.md
  - coding-style.md
- 変更は小さく、検証手順（コマンド＋期待結果）を必ず残す
- セッションの最後に必ず更新する：
  1) progress_log.md（今日の進捗＋次回やること）
  2) guideline.md の Current Next Actions（矛盾させない）
  3) idea_note.md（新アイデアが出たら追記）
  4) coding-style.md（規約/ツールを決めたら更新）

## 3-Review Rule（大きな変更のみ）
- Builder: 実装案と理由
- Skeptic: 反証・リスク・代替案
- User: 最終決定（Yes/Noで答えられる形）

## Current Next Actions
- [ ] SSOT 4ファイルを追加（guideline/progress_log/idea_note/coding-style）
- [ ] README.md にSSOTリンクを追加（迷子防止）
- [ ] .gitignore を追加（ローカル生成物・環境ファイル・ログをコミットしない）
- [ ] P0: DLP（機密検知）テスト設計＋実装（まず“検知して止まる”でOK）
- [ ] P0: 地位差分テスト（肩書だけ変える）100ケース（まず10ケースから）
- [ ] P0: 操作表現検知＋縮退モード（“説得”や“煽り”を避ける）
- [ ] P1: 意思決定テンプレCLI（必要性/責任/外部性/反証/不確実性）

## How to run / test
- （まだコードが無いのでTBD）
- 追加したらここに「1コマンドで動く手順」を書く
