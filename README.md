# Chemical Product Fact Sheet Generator

A small Python command-line tool that generates A6 landscape PDF fact sheets
with GHS pictograms and an optional ADR orange panel.

> **Important:** The sample products and text are for illustration only. They
> do not replace safety data sheets or regulatory verification. Check all
> classifications and regulatory information before real-world use.

## Requirements

- Python 3
- pip

## Installation

From the project root:

```powershell
python -m pip install -r requirements.txt
```

## Usage

Generate fact sheets from the example products:

```powershell
python generate_factsheets.py -p products_example.json
```

PDFs are written to `generated_factsheets` by default. Choose a different
output directory with:

```powershell
python generate_factsheets.py -p products_example.json -o custom_output
```

The output directory is created if it does not exist. Existing PDFs with the
same filenames are overwritten.

## Input format

The input file is a JSON array of product objects. Each object requires a
`name`; `description`, `pictograms`, and ADR numbers are optional. Pictogram
codes range from `GHS01` to `GHS09`; numeric codes from `1` to `9` are also
accepted.

```json
[
  {
    "name": "Acetone",
    "description": "A highly flammable liquid solvent.",
    "pictograms": ["GHS02", "GHS07"],
    "hazard_number": "33",
    "un_number": "1090"
  }
]
```

The `hazard_pictograms` directory contains the PNG images used in the fact
sheets. Pictogram sources are listed in its
[README](hazard_pictograms/README.md).

## Repository contents

- `generate_factsheets.py`: PDF generation command-line tool.
- `products_example.json`: sample chemical products.
- `hazard_pictograms/`: GHS pictogram images.

Generated PDFs are excluded from the repository.

No license is included. Check the reuse terms for the pictograms and other
third-party resources before publishing or redistributing them.
