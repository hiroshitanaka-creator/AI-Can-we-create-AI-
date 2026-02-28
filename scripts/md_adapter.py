"""
scripts/md_adapter.py

Markdown → decision_request.v0 JSON 変換アダプタ

カノニカルは JSON のまま。このスクリプトは"入口を増やす"だけ。

## 入力フォーマット（Markdown）

```markdown
# situation
何を決めたいか（1行または複数行）

# constraints
- 制約1
- 制約2

# options
- 案A の内容
- 案B の内容

# beneficiaries
- 受益者1
- 受益者2

# affected_structures
- 個人
- 社会
```

## ルール
- `# situation` は必須。他はすべて省略可。
- `#` の大文字小文字は問わない（situation / Situation 両方OK）。
- `-` 箇条書き / `*` 箇条書き のどちらも受け付ける。
- セクション内の空行は無視する。
- 認識できないセクション名は無視する（エラーにしない）。

## 使い方

    # stdin から
    cat request.md | python scripts/md_adapter.py

    # ファイル指定
    python scripts/md_adapter.py request.md

    # パイプで brief.py へ
    cat request.md | python scripts/md_adapter.py | python scripts/brief.py

Exit codes:
    0 : 変換成功（JSON を stdout に出力）
    1 : situation が空
    2 : 引数エラー / ファイル読み込みエラー
"""
from __future__ import annotations

import json
import re
import sys
from typing import Dict, List, Any


# ─────────────────────────────────────────────────────────────────────────────
# 内部ロジック
# ─────────────────────────────────────────────────────────────────────────────

_LIST_ITEM = re.compile(r"^[\-\*]\s+(.+)$")
_SECTION_HEADER = re.compile(r"^#+\s*(\w+)\s*$", re.IGNORECASE)

# 受け付けるセクション名（すべて小文字で比較）
_KNOWN_SECTIONS = {
    "situation",
    "constraints",
    "options",
    "beneficiaries",
    "affected_structures",
}

# リスト形式で受け取るフィールド
_LIST_FIELDS = {"constraints", "options", "beneficiaries", "affected_structures"}


def parse_markdown(text: str) -> Dict[str, Any]:
    """
    Markdown テキストを decision_request dict に変換する。
    """
    sections: Dict[str, List[str]] = {}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # セクションヘッダの検出
        m = _SECTION_HEADER.match(line)
        if m:
            key = m.group(1).lower()
            if key in _KNOWN_SECTIONS:
                current = key
                sections.setdefault(current, [])
            else:
                current = None  # 未知セクションは無視
            continue

        if current is None:
            continue

        # 空行はスキップ
        if not line:
            continue

        # 箇条書き
        lm = _LIST_ITEM.match(line)
        if lm:
            sections[current].append(lm.group(1).strip())
        else:
            # 箇条書きでない行は situation / テキストフィールド向けにそのまま追加
            sections[current].append(line)

    return _to_request(sections)


def _to_request(sections: Dict[str, List[str]]) -> Dict[str, Any]:
    req: Dict[str, Any] = {}

    # situation: 行をスペースで結合
    sit_lines = sections.get("situation", [])
    req["situation"] = " ".join(sit_lines).strip()

    # リストフィールド: 空リストは含めない（スキーマ上は任意）
    for field in _LIST_FIELDS:
        values = sections.get(field, [])
        if values:
            req[field] = values

    return req


def convert(text: str) -> Dict[str, Any]:
    """parse_markdown のパブリック API（テスト・外部利用向け）"""
    return parse_markdown(text)


# ─────────────────────────────────────────────────────────────────────────────
# CLI エントリポイント
# ─────────────────────────────────────────────────────────────────────────────

def _read_input(args: List[str]) -> str:
    if not args:
        return sys.stdin.read()
    if len(args) == 1:
        try:
            with open(args[0], encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            print(f"[md_adapter] ファイル読み込みエラー: {e}", file=sys.stderr)
            sys.exit(2)
    print("[md_adapter] 引数は最大1つ（ファイルパス）です", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    text = _read_input(sys.argv[1:])
    req = convert(text)

    if not req.get("situation"):
        print("[md_adapter] エラー: # situation セクションが空、または見つかりません", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(req, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
