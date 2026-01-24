import re
def validate_bot_token(token: str) -> bool:
    pattern = r'^\d+:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def validate_transaction_hash(hash_str: str) -> bool:
    # длина и символы
    if not hash_str or len(hash_str) < 40:
        return False
    
    pattern = r'^[A-Fa-f0-9]+$'
    return bool(re.match(pattern, hash_str))


def validate_url(url: str) -> bool:
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))


def parse_buttons(text: str) -> list:
    buttons = []
    lines = text.strip().split('\n')
    
    for line in lines:
        if '|' in line:
            parts = line.split('|', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                url = parts[1].strip()
                if name and validate_url(url):
                    buttons.append({'name': name, 'url': url})
    
    return buttons