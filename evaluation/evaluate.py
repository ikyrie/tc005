from __future__ import annotations

import csv
import json
import pathlib
import sys
from typing import Any


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from ai_processor.ai_client import analyze_architecture
except ModuleNotFoundError:
    # Local fallback for the current folder naming while keeping the intended import path.
    import importlib.util

    ai_client_path = PROJECT_ROOT / "ai-processor" / "ai_client.py"
    spec = importlib.util.spec_from_file_location("ai_processor.ai_client", ai_client_path)
    if spec is None or spec.loader is None:
        raise
    ai_client_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ai_client_module)
    analyze_architecture = ai_client_module.analyze_architecture


def main() -> None:
    samples_dir = PROJECT_ROOT / "evaluation" / "samples"
    output_csv = PROJECT_ROOT / "evaluation" / "evaluation.csv"

    if not samples_dir.exists():
        samples_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created at '{samples_dir}'. Add .png or .jpg images and run again.")
        return

    image_files = sorted(
        [*samples_dir.glob("*.png"), *samples_dir.glob("*.jpg")],
        key=lambda path: path.name.lower(),
    )

    if not image_files:
        print(f"No .png or .jpg files found in '{samples_dir}'.")
        return

    rows: list[dict[str, Any]] = []

    for image_path in image_files:
        try:
            result_json = analyze_architecture(str(image_path))
            parsed_result = json.loads(result_json)

            components = parsed_result.get("components", [])
            risks = parsed_result.get("risks", [])

            rows.append(
                {
                    "file_name": image_path.name,
                    "components_count": len(components) if isinstance(components, list) else 0,
                    "risks_count": len(risks) if isinstance(risks, list) else 0,
                    "success": True,
                }
            )
        except Exception:
            rows.append(
                {
                    "file_name": image_path.name,
                    "components_count": 0,
                    "risks_count": 0,
                    "success": False,
                }
            )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["file_name", "components_count", "risks_count", "success"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Evaluation finished. CSV saved at '{output_csv}'.")


if __name__ == "__main__":
    main()