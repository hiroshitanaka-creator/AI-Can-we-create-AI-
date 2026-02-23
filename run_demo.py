from aicw import build_decision_report, format_report


def main() -> None:
    print("※注意: 個人情報/機密は入れない。実名・連絡先・住所・IDは『顧客A』『A社』に置換。")
    situation = input("状況（短く）> ").strip()

    constraints_raw = input("制約（任意。'/'区切り）> ").strip()
    constraints = [c.strip() for c in constraints_raw.split("/") if c.strip()] if constraints_raw else []

    options = []
    for label in ["A", "B", "C"]:
        v = input(f"候補{label}（任意。空ならデフォルト）> ").strip()
        if v:
            options.append(v)

    req = {
        "situation": situation,
        "constraints": constraints,
        "options": options,
    }

    report = build_decision_report(req)
    print()
    print(format_report(report))


if __name__ == "__main__":
    main()
