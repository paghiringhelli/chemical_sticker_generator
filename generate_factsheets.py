"""Generate A6 landscape product fact sheet PDFs with GHS pictograms and an optional ADR panel.

Usage:
    python generate_factsheets.py -p products.json [-o output_dir]

products.json format (array of objects):
    [
      {
        "name": "Acetone",
        "description": "A highly flammable liquid solvent.",
        "pictograms": ["GHS02", "GHS07"],
        "hazard_number": "33",
        "un_number": "1090"
      }
    ]
`hazard_number` and `un_number` are optional (the orange panel is blank otherwise).
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

from reportlab.lib.colors import Color, black
from reportlab.lib.pagesizes import A6, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

PICTOGRAM_DIR = Path(__file__).parent / "hazard_pictograms"
PAGE_W, PAGE_H = landscape(A6)
MARGIN = 15 * mm
ADR_ORANGE = Color(1.0, 0.4, 0.0)
FONT, FONT_BOLD = "Helvetica", "Helvetica-Bold"


def find_pictogram(code: str) -> Path:
    """Return the PNG matching a GHS code (GHS01..GHS09)."""
    code = code.strip().upper()
    if re.fullmatch(r"\d{1,2}", code):
        code = f"GHS{int(code):02d}"
    matches = sorted(PICTOGRAM_DIR.glob(f"{code}_*.png"))
    if not matches:
        raise ValueError(f"Unknown pictogram: {code!r} (expected GHS01 through GHS09)")
    return matches[0]


def fit_text(c, text, x, y, max_width, max_size, min_size=8, font=FONT_BOLD):
    """Draw text, shrinking it as needed to fit within max_width."""
    size = max_size
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 0.5
    c.setFont(font, size)
    c.drawString(x, y, text)


def draw_adr_panel(c, x, y, width, hazard_number, un_number):
    """Draw an ADR orange panel (40:30 ratio), with hazard and UN numbers."""
    height = width * 0.75
    line_width = width * 0.0125 * 4
    c.setFillColor(ADR_ORANGE)
    c.setStrokeColor(black)
    c.setLineWidth(line_width)
    c.rect(x, y, width, height, fill=1, stroke=1)
    c.line(x, y + height / 2, x + width, y + height / 2)

    c.setFillColor(black)
    for text, center_y in ((hazard_number, y + height * 0.75), (un_number, y + height * 0.25)):
        if not text:
            continue
        size = height * 0.34
        while c.stringWidth(text, FONT_BOLD, size) > width * 0.88:
            size -= 0.5
        c.setFont(FONT_BOLD, size)
        c.drawCentredString(x + width / 2, center_y - size * 0.35, text)


def draw_pictograms(c, codes, zone_x, zone_y, zone_width, max_size):
    """Arrange pictograms in a horizontally centered row."""
    if not codes:
        return
    spacing = 3 * mm
    n = len(codes)
    size = min(max_size, (zone_width - spacing * (n - 1)) / n)
    total = n * size + (n - 1) * spacing
    x = zone_x + (zone_width - total) / 2
    for code in codes:
        c.drawImage(str(find_pictogram(code)), x, zone_y, size, size, mask="auto")
        x += size + spacing


def draw_fact_sheet(c, product):
    c.setPageSize((PAGE_W, PAGE_H))
    usable_width = PAGE_W - 2 * MARGIN

    # Title
    c.setFillColor(black)
    top = PAGE_H - MARGIN
    fit_text(c, product["name"], MARGIN, top - 8 * mm, usable_width, 24, min_size=12)
    c.setLineWidth(0.8)
    c.line(MARGIN, top - 12 * mm, PAGE_W - MARGIN, top - 12 * mm)

    # Pictograms (bottom of page)
    pictogram_size = 18 * mm
    draw_pictograms(c, product.get("pictograms", []), MARGIN, MARGIN, usable_width, pictogram_size)

    # Main area: description on the left, ADR panel on the right
    zone_top = top - 16 * mm
    zone_bottom = MARGIN + pictogram_size + 4 * mm
    panel_width = 40 * mm
    panel_height = panel_width * 0.75
    draw_adr_panel(
        c,
        PAGE_W - MARGIN - panel_width,
        zone_top - panel_height,
        panel_width,
        product.get("hazard_number", ""),
        product.get("un_number", ""),
    )

    description_width = usable_width - panel_width - 6 * mm
    size = 12
    lines = simpleSplit(product.get("description", ""), FONT, size, description_width)
    line_spacing = size * 1.25
    while len(lines) * line_spacing > zone_top - zone_bottom and size > 7:
        size -= 0.5
        line_spacing = size * 1.25
        lines = simpleSplit(product.get("description", ""), FONT, size, description_width)
    c.setFont(FONT, size)
    y = zone_top - size
    for line in lines:
        c.drawString(MARGIN, y, line)
        y -= line_spacing


def filename_stem(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", ascii_name).strip("_") or "product"


def main():
    parser = argparse.ArgumentParser(description="Generate A6 landscape product fact sheet PDFs.")
    parser.add_argument(
        "-p", "--products", required=True, type=Path, help="JSON file containing product data"
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("generated_factsheets"), help="Output directory"
    )
    args = parser.parse_args()

    products = json.loads(args.products.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)

    for product in products:
        output_path = args.output / f"{filename_stem(product['name'])}.pdf"
        c = canvas.Canvas(str(output_path), pagesize=landscape(A6))
        c.setTitle(product["name"])
        draw_fact_sheet(c, product)
        c.save()
        print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
