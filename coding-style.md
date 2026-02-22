# Coding Style

## Target
- 目的: Po_core に持ち込める形を意識して、Python中心で試作する
- 原則: Offline-first / ログ最小化 / No-Go(#6/#3/#4)最優先

## Language / Runtime
- Language: Python
- Runtime/Version: Python >= 3.10（Po_core側の要求に合わせる想定）

## Safety Defaults（最重要）
- 外部ネットワーク通信はデフォルト禁止
- 個人情報・秘密情報・トークン等を
  - 保存しない
  - ログに書かない
  - サンプルにも入れない

## Formatting（見た目の統一）
- 1行は長くしすぎない（目安: 88文字）
- 名前の付け方:
  - 関数: snake_case（例: build_report）
  - クラス: PascalCase（例: DecisionReport）
  - 定数: UPPER_CASE（例: MAX_LEN）

## Tooling（任意・後で導入してOK）
- 自動整形（black）や軽いチェック（ruff）は、必要になったら入れる
- 今は「読みやすさ」と「安全ルール優先」
