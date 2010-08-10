import re


valuepatt = r"\[\[\[\s*(.*?)\s*\]\]\]" 

def validate_input(text, fields):
    offset = 0
    errors = 0
    for i, m in enumerate(re.finditer(valuepatt, text)):
        value = m.group(1)
        field = fields[i]
        #print text[offset+m.start():offset+m.end()]
        try:
            points = field.spec.validate(value)
            msg = ' {POINTS: %d}' % points
        except ValueError, e:
            msg = ' {ERROR: %s}' % e
            errors += 1
        text = text[:offset+m.end()] + msg + text[offset+m.end():]
        offset += len(msg)
    return errors, text

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

def insert_values(rst, values):
    offset = 0
    for i, m in enumerate(re.finditer(valuepatt, rst)):
        value = '[[[ %s ]]]' % values[i]
        current = rst[offset+m.start():offset+m.end()]
        rst = rst[:offset+m.start()] + value + rst[offset+m.end():]
        offset += len(value) - len(current)
    return rst


def extract_values(rst):
    return re.findall(valuepatt, rst)

def extract_valuedict(rst):
    r = {}
    for i, value in enumerate(extract_values(rst)):
        r['rstschema_field_%s' % i] = value
    return r
