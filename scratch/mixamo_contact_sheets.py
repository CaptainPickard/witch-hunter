"""Generate labelled, two-clip contact sheets from delivered QA PNGs."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
for body in ['bandit', 'ghoul']:
    qa = root/'scratch/mixamo-fbx/qa'/body
    names = list(json.loads((root/f'scratch/mixamo_{body}.json').read_text()))
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 19)
    for index in range(0, len(names), 2):
        subset = names[index:index+2]
        sheet = Image.new('RGB', (1024, 548*len(subset)), '#19232c')
        draw = ImageDraw.Draw(sheet)
        for row, name in enumerate(subset):
            for col, suffix in enumerate(['', '_end']):
                image = Image.open(qa/(name+suffix+'.png')).convert('RGB')
                image.thumbnail((512,512))
                sheet.paste(image, (col*512,row*548+36))
                draw.text((col*512+8,row*548+7),name+(' / end' if suffix else ' / mid'),font=font,fill='white')
        sheet.save(qa/f'contact-{index//2+1}.jpg',quality=92)
print('Contact sheets generated for both bodies')
