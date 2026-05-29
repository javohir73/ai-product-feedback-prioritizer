from __future__ import annotations

import argparse

from .prioritizer import load_feedback, prioritize, roadmap_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Prioritize product feedback into roadmap themes.")
    parser.add_argument("csv_path")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    themes = prioritize(load_feedback(args.csv_path))
    print(roadmap_markdown(themes, top=args.top))


if __name__ == "__main__":
    main()

