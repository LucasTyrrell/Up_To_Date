import re

_SALARY_NUMBER_RE = re.compile(r'([\d,]+(?:\.\d+)?)\s*(k)?', re.IGNORECASE)

_ROLE_TYPE_MAP = {
    'graduate': 'graduate',
    'placement': 'internship',
    'internship': 'internship',
    'apprenticeship': 'apprenticeship',
}


def normalize_text(text):
    if text is None:
        return None

    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def parse_salary(text):
    if not text:
        return None

    match = _SALARY_NUMBER_RE.search(text.replace('£', '').replace(',', ''))

    if not match:
        return None

    number = float(match.group(1))

    if match.group(2):
        number *= 1000

    return int(number)


def map_role_type(job_type):
    return _ROLE_TYPE_MAP.get(job_type)

