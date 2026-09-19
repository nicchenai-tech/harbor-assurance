"""Bounded OCR workers: Apple Vision locally or Tesseract in the cloud image."""
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def recognize_pdf_page(path, index):
    import pypdfium2 as pdfium
    with tempfile.TemporaryDirectory(prefix='harbor-ocr-') as folder:
        image=Path(folder)/'page.png'
        pdf=pdfium.PdfDocument(str(path))
        page=pdf[index]
        bitmap=page.render(scale=3)
        bitmap.to_pil().save(image)
        bitmap.close();page.close();pdf.close()
        proc=subprocess.run([sys.executable,'-m','harbor.ocr',str(image)],capture_output=True,text=True,timeout=40)
        if proc.returncode:
            raise RuntimeError(proc.stderr.strip()[-250:] or 'OCR engine unavailable.')
        return json.loads(proc.stdout)


def available_backend():
    requested=os.getenv('HARBOR_OCR_BACKEND','auto').lower()
    if requested=='none': return 'unavailable'
    if requested in ('auto','apple') and sys.platform=='darwin':
        try:
            import Vision  # noqa: F401
            return 'apple_vision'
        except ImportError:
            if requested=='apple': return 'unavailable'
    if requested in ('auto','tesseract') and shutil.which('tesseract'):
        return 'tesseract'
    return 'unavailable'


def _crop(path):
    from PIL import Image
    original=Image.open(path).convert('RGB')
    mask=original.convert('L').point(lambda p:255 if p<150 else 0)
    bbox=mask.getbbox() or (0,0,original.width,original.height)
    left=max(0,bbox[0]-16);top=max(0,bbox[1]-16)
    right=min(original.width,bbox[2]+16);bottom=min(original.height,bbox[3]+16)
    return original,original.crop((left,top,right,bottom)),(left,top,right,bottom)


def _apple_rows(image_path,original,cropped,cropbox):
    # Import here so Linux installations can run every native-text path.
    import Vision
    from Foundation import NSURL
    left,top,_,_=cropbox
    request=Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    request.setRecognitionLanguages_(['en-US'])
    request.setUsesLanguageCorrection_(False)
    request.setMinimumTextHeight_(0.003)
    handler=Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_(image_path),{})
    ok,error=handler.performRequests_error_([request],None)
    if not ok: raise RuntimeError(str(error))
    rows=[]
    for observation in request.results() or []:
        candidates=observation.topCandidates_(1)
        if not candidates: continue
        box=observation.boundingBox()
        rows.append({'text':str(candidates[0].string()),'backend':'apple_vision','bbox':[(left+box.origin.x*cropped.width)/original.width,
             (top+(1-box.origin.y-box.size.height)*cropped.height)/original.height,
             box.size.width*cropped.width/original.width,box.size.height*cropped.height/original.height]})
    rows.sort(key=lambda r:(round(r['bbox'][1],2),r['bbox'][0]))
    return rows


def _tesseract_rows(tsv,original_size,cropped_size,cropbox):
    """Turn word-level TSV into stable, source-locatable text lines."""
    ow,oh=original_size;cw,ch=cropped_size;left,top,_,_=cropbox
    grouped={}
    for row in csv.DictReader(io.StringIO(tsv),delimiter='\t'):
        text=(row.get('text') or '').strip()
        if not text: continue
        try:
            key=(row['page_num'],row['block_num'],row['par_num'],row['line_num'])
            x=int(row['left']);y=int(row['top']);w=int(row['width']);h=int(row['height'])
            confidence=float(row.get('conf') or -1)
        except (KeyError,ValueError):
            continue
        group=grouped.setdefault(key,{'words':[],'left':x,'top':y,'right':x+w,'bottom':y+h,'confidence':[]})
        group['words'].append(text);group['left']=min(group['left'],x);group['top']=min(group['top'],y)
        group['right']=max(group['right'],x+w);group['bottom']=max(group['bottom'],y+h)
        if confidence>=0:group['confidence'].append(confidence)
    rows=[]
    for group in grouped.values():
        rows.append({'text':' '.join(group['words']),'backend':'tesseract',
          'confidence':round(sum(group['confidence'])/len(group['confidence']),1) if group['confidence'] else None,
          'bbox':[(left+group['left'])/ow,(top+group['top'])/oh,
                  (group['right']-group['left'])/ow,(group['bottom']-group['top'])/oh]})
    rows.sort(key=lambda r:(round(r['bbox'][1],3),r['bbox'][0]))
    return rows


def _tesseract(image_path,original,cropped,cropbox):
    proc=subprocess.run(['tesseract',str(image_path),'stdout','-l','eng','--psm','6','tsv'],
                        capture_output=True,text=True,timeout=35)
    if proc.returncode: raise RuntimeError(proc.stderr.strip()[-250:] or 'Tesseract OCR failed.')
    return _tesseract_rows(proc.stdout,original.size,cropped.size,cropbox)


def main():
    original,cropped,cropbox=_crop(sys.argv[1])
    scratch=tempfile.NamedTemporaryFile(suffix='.png',delete=False);scratch.close();cropped.save(scratch.name)
    try:
        backend=available_backend()
        if backend=='apple_vision': rows=_apple_rows(scratch.name,original,cropped,cropbox)
        elif backend=='tesseract': rows=_tesseract(scratch.name,original,cropped,cropbox)
        else: raise RuntimeError('No OCR backend is installed.')
        print(json.dumps(rows))
    finally:
        Path(scratch.name).unlink(missing_ok=True)


if __name__=='__main__': main()
