from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "milestone_2_stackoverflow_eda.ipynb"


def main():
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    namespace = {"__name__": "__main__"}

    for idx, cell in enumerate(nb.cells, start=1):
        if cell.cell_type != "code":
            continue
        print(f"Running code cell {idx}...")
        exec(compile(cell.source, f"<notebook cell {idx}>", "exec"), namespace)

    print("Notebook code cells executed successfully.")


if __name__ == "__main__":
    main()
