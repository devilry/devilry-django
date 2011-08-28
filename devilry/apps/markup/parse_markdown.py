import markdown


def markdown_full(inputMarkdown):
    md = markdown.Markdown(output_format='xhtml1',
                           safe_mode="escape",
                           extensions=['fenced_code'])
    return md.convert(inputMarkdown)
