# Thesis Defense Speech — Full Reference

## PPTX Extraction (without python-pptx)

### Why This Works

PPTX files are ZIP archives containing XML. The text lives in `ppt/slides/slideN.xml` under `a:t` (text) elements.

### Full Extraction Function

```python
import zipfile, os, xml.etree.ElementTree as ET

def extract_pptx_text(pptx_path):
    """Returns dict of {slide_num: [text_lines]}"""
    out_dir = "/tmp/pptx_extracted"
    os.makedirs(out_dir, exist_ok=True)
    
    with zipfile.ZipFile(pptx_path, 'r') as z:
        z.extractall(out_dir)
    
    slides_dir = os.path.join(out_dir, "ppt/slides")
    slides = sorted([f for f in os.listdir(slides_dir) 
                     if f.endswith('.xml') and not f.startswith('_')])
    
    result = {}
    for i, f in enumerate(slides, 1):
        tree = ET.parse(os.path.join(slides_dir, f))
        root = tree.getroot()
        texts = []
        for t in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
            if t.text and t.text.strip():
                texts.append(t.text.strip())
        result[i] = texts
    return result
```

### Getting Slides in Display Order

```python
import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile(pptx_path, 'r') as z:
    pres_xml = z.read('ppt/presentation.xml')

ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
root = ET.fromstring(pres_xml)
sldIdLst = root.find('.//p:sldIdLst', ns)
if sldIdLst is not None:
    for child in sldIdLst:
        rid = child.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        print(f"  rId={rid}")
```

### Common PPTX XML Text Elements

| XML Tag | Content | Notes |
|---------|---------|-------|
| `a:t` | Text run | Main text content, may be split across multiple `<a:t>` per paragraph |
| `a:p` | Paragraph | Contains one or more `<a:r>` (runs), each with an `<a:t>` |
| `a:r` | Text run | A span of text with uniform formatting |

### Speech Template

```markdown
# 硕士论文答辩稿

## 开场白
各位老师好！我是XX学院的武士淳，导师是马建民教授。我的论文题目是《...》。

## 第一部分：研究背景与意义
[对应 slides 研究背景部分]

## 第二部分：安全型阻燃电解液 (FDPT)
[对应 slides FDPT部分]

## 第三部分：长循环复合电解液 (BLSN)
[对应 slides BLSN部分]

## 第四部分：总结与展望
[对应总结部分]

## 致谢
感谢导师、课题组、家人、评审专家...
```

### Verification Checklist

- [ ] All slides accounted for (no orphaned slides)
- [ ] Speech follows PPT display order
- [ ] Each slide has at least 2–3 sentences of content
- [ ] Data points match thesis (capacity retention, cycle numbers, ratios)
- [ ] File saved to `/opt/data/青桑/答辩稿_<PPT文件名>.md`
- [ ] User can read it slide-by-slide while presenting

### Notes for This User's Defense PPT

- Slides contain mixed Chinese and English (chemical formulas, abbreviations)
- Some slides have minimal text (mostly figures) — for these, extract content from the thesis chapter instead
- Figure captions appear as regular `a:t` elements
- The last few slides (背景, 展望, 致谢) often appear last in the file but belong early in the speech
