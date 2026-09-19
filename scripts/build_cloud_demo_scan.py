"""Generate owned image-only PDFs that exercise the portable OCR path."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'demo-data'/'attachments'


def font(size):
    for path in [Path('/System/Library/Fonts/Supplemental/Arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if path.exists():return ImageFont.truetype(str(path),size)
    return ImageFont.load_default()


def make(role,filename):
    lines=[role,'Shipper: North Paper Ltd','Consignee: West Trading Ltd','Notify Party: West Trading Ltd',
           'Port of Loading: Singapore','Port of Discharge: Fremantle, Australia',
           "Container Count: 3 x 40'HC",'Gross Weight (KG): 22,000 KG']
    image=Image.new('RGB',(1654,1169),'white');draw=ImageDraw.Draw(image)
    draw.rectangle((55,45,1599,1124),outline='#173650',width=4)
    draw.text((105,95),'HARBOR OWNED SYNTHETIC DEMO',font=font(28),fill='#52647b')
    y=175
    for i,line in enumerate(lines):
        draw.text((105,y),line,font=font(48 if i==0 else 38),fill='black');y+=105
    image.save(OUT/filename,'PDF',resolution=150)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    make('SHIPPING INSTRUCTION','demo-07-SI.pdf')
    make('DRAFT BILL OF LADING','demo-07-BL.pdf')
    print(OUT/'demo-07-SI.pdf');print(OUT/'demo-07-BL.pdf')
