import re


def validate_input(text, fields):
    offset = 0
    for i, m in enumerate(re.finditer(r"\[\[\[\s*(.*?)\s*\]\]\]", text)):
        value = m.group(1)
        field = fields[i]
        #print text[offset+m.start():offset+m.end()]
        try:
            points = field.spec.validate(value)
            msg = ' {POINTS: %d}' % points
        except ValueError, e:
            msg = ' {ERROR: %s}' % e
        text = text[:offset+m.end()] + msg + text[offset+m.end():]
        offset += len(msg)
    return offset == 0, text

def strip_messages(text):
    return re.sub(r"\s*\{(?:POINTS|ERROR):[^}]*?\}", "", text, re.DOTALL)

def normalize_newlines(s):
    return s.replace('\r\n', '\n').replace('\r', '\n')

def examiner_format(rst):
    rst = normalize_newlines(rst)
    r = re.sub(
            r"\n\n\.\. field::\s+(\S+)\s+:default:\s*(\S+).*",
            r" [\1]\n[[[ \2 ]]]",
            rst, re.MULTILINE)
    r = re.sub(
            r"\n\n\.\. field::\s+(\S+)",
            r" [\1]\n[[[  ]]]",
            r, re.MULTILINE)
    return r
