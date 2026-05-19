from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image, UnidentifiedImageError


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
PDF_EXTENSION = ".pdf"
OUTPUT_FILENAME = "page-1.png"


def normalize_to_png(input_path: str, output_base_dir: str, analysis_id: str) -> str:
    """Normalize a PDF or image file into a standard PNG representation.

    The resulting file is always stored under output_base_dir/analysis_id/page-1.png.
    """

    source_path = Path(input_path)
    destination_dir = Path(output_base_dir) / analysis_id
    destination_dir.mkdir(parents=True, exist_ok=True)
    output_path = destination_dir / OUTPUT_FILENAME

    extension = source_path.suffix.lower()

    try:
        if extension == PDF_EXTENSION:
            with fitz.open(source_path) as document:
                if len(document) == 0:
                    raise ValueError(f"PDF file has no pages: {source_path}")

                first_page = document.load_page(0)
                pixmap = first_page.get_pixmap(alpha=False)
                pixmap.save(output_path)
        elif extension in SUPPORTED_IMAGE_EXTENSIONS:
            with Image.open(source_path) as image:
                image.convert("RGB").save(output_path, format="PNG")
        else:
            raise ValueError(f"Unsupported input format: {extension or 'unknown'}")
    except (fitz.FileDataError, UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError(f"Failed to normalize file '{source_path}': {exc}") from exc

    return str(output_path.resolve())
