def build_report_json(document, tables, entities):
    return {
        "raw_text": document.text,
        "tables": tables,
        "entities": entities,
        "page_count": len(document.pages)
    }
