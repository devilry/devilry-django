import markdown


def markdown_full(inputMarkdown):
    md = markdown.Markdown(output_format='xhtml1',
                           safe_mode="escape",
                           extensions=['codehilite'])
    return md.convert(inputMarkdown)
