# Project:Po_core用のAIを作ってみたい。


## Purpose
チーム内の業務意思決定を支援する（判断の後押し）。
最終判断は人間が行い、AIは根拠・反証・不確実性・外部性を構造化して提示する。

## Non-Negotiables (No-Go)
- Privacy breach is forbidden (#6).
- Discrimination / harm concentration is forbidden (#3).
- Manipulation / agitation is forbidden (#4).

違反が検知された場合は自動的に縮退/停止する。

## Core Principle
- Status-invariant: 肩書・権威では答えを変えない
- Context-dependent: 条件・制約・状況で答えを変える
- Explainable selection: 候補案と選定理由を提示する

## Architecture (High-level)
- Verifiable Decision Layer (rules/templates/logs) decides.
- Language Layer (optional) only summarizes / lists counterarguments.

## Security
- Offline-first. No external network by default.
- Minimal logging + encryption + TTL. Fail closed if not available.

## Workflow
- Major changes require 3 reviews (Builder / User / Skeptic).
- Tests must pass: DLP, status-diff, anti-manipulation.