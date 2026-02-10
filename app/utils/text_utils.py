def get_text(doc_element, document_text):
    """Slices the document text based on the text_anchor in the element."""
    text = ""
    for segment in doc_element.text_anchor.text_segments:
        start_index = int(segment.start_index) if segment.start_index else 0
        end_index = int(segment.end_index)
        text += document_text[start_index:end_index]
    return text.strip()

def extract_tables(document):
    tables = []
    for page in document.pages:
        for table in page.tables:
            rows = []
            for row in table.body_rows:
                cells = []
                for cell in row.cells:
                    cells.append(get_text(cell.layout, document.text))
                rows.append(cells)
            tables.append(rows)
    return tables


def extract_entities(document):
    return [
        {
            "type": entity.type_,
            "value": entity.mention_text if entity.mention_text else get_text(entity, document.text),
            "confidence": entity.confidence
        }
        for entity in document.entities
    ]
