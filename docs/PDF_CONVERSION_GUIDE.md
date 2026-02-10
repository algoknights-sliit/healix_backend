# Converting Documentation to PDF

## Option 1: Using Pandoc (Recommended)

### Install Pandoc
```bash
# Windows (using chocolatey)
choco install pandoc

# Or download from: https://pandoc.org/installing.html
```

### Convert to PDF
```bash
# Navigate to docs folder
cd docs

# Convert with nice formatting
pandoc COMPLETE_DEVELOPER_GUIDE.md -o Healix_Developer_Guide.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=2 \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V documentclass=report

# If you don't have LaTeX installed, use wkhtmltopdf engine instead
pandoc COMPLETE_DEVELOPER_GUIDE.md -o Healix_Developer_Guide.pdf \
  --pdf-engine=wkhtmltopdf \
  --toc
```

---

## Option 2: Using Markdown to PDF Chrome Extension

1. Open `COMPLETE_DEVELOPER_GUIDE.md` in VS Code
2. Install "Markdown PDF" extension
3. Right-click in editor → "Markdown PDF: Export (pdf)"
4. PDF will be saved in same folder

---

## Option 3: Using Online Converter

1. Go to https://www.markdowntopdf.com/
2. Upload `docs/COMPLETE_DEVELOPER_GUIDE.md`
3. Click "Convert"
4. Download PDF

---

## Option 4: Using GitHub/GitLab

1. Push to GitHub/GitLab
2. View the file online (it will render)
3. Use browser's "Print to PDF" function (Ctrl+P)
4. Adjust print settings:
   - Remove headers/footers
   - Enable background graphics
   - Set margins to default

---

## Best Quality Output

For best results, use Pandoc with LaTeX:

```bash
pandoc COMPLETE_DEVELOPER_GUIDE.md -o Healix_Developer_Guide.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=3 \
  --number-sections \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V documentclass=report \
  -V mainfont="Arial" \
  --highlight-style=tango
```

This will create a professional PDF with:
- Table of contents
- Page numbers
- Section numbering
- Syntax highlighting
- Proper margins

---

## File Locations

**Main Documentation:**
- `README.md` - Project overview and quick start
- `docs/COMPLETE_DEVELOPER_GUIDE.md` - Full developer documentation (for PDF)

**Supporting Docs:**
- `docs/PATIENT_SCHEMA_UPDATE.md` - Authentication system
- `docs/NIC_UPLOAD_SYSTEM.md` - Upload workflow
- `docs/REPORT_PROCESSING_GUIDE.md` - Processing pipeline
- `docs/BIOMARKER_REF_RANGE_FIX.md` - Technical fix details

**Suggested PDF Name:**
`Healix_Backend_Developer_Guide_v2.0.pdf`

---

## Tips for Presentation

1. **Add Cover Page**: Create a simple cover page with:
   - Project name: "Healix Backend"
   - Version: 2.0
   - Date: February 2026
   - Your organization logo

2. **Print Settings**:
   - Double-sided printing for professional look
   - Color printing for diagrams and code

3. **Binding**:
   - For 100+ page document, consider spiral binding
   - Or use a presentation folder

4. **Digital Distribution**:
   - PDF is best for email/sharing
   - Include in project repository for easy access
