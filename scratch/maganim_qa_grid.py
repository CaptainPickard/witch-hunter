"""Tile rt_render_qa_grid.py frames into one 3x2 labelled grid per clip (MAGANIM A3).
python3 scratch/maganim_qa_grid.py FRAMEDIR OUTDIR
"""
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

TILE, COLS = 400, 3


def main():
    frames, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    report = json.loads((frames / 'renders.json').read_text())
    for name, entries in report['clips'].items():
        rows = (len(entries) + COLS - 1) // COLS
        grid = Image.new('RGB', (TILE * COLS, TILE * rows + 28), (18, 22, 27))
        draw = ImageDraw.Draw(grid)
        draw.text((8, 8), f"{name}  ({report['full_range'][name]['frames_checked']} frames)",
                  fill=(230, 230, 230))
        for i, e in enumerate(entries):
            img = Image.open(e['png']).convert('RGB').resize((TILE, TILE))
            x, y = (i % COLS) * TILE, 28 + (i // COLS) * TILE
            grid.paste(img, (x, y))
            draw.text((x + 6, y + 6), f"f{e['frame']}", fill=(255, 220, 120))
        grid.save(out / f'{name}.png')
        print('grid', out / f'{name}.png')
    (out / 'renders.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
