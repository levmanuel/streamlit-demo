import re

bad_words = ["fraud",
    "suspicious",
    "unauthorized",
    "identity",
    "stolen",
    "compromised",
    "suspicion",
    "alert",
    "illegal",
    "forgery",
    "laundering",
    "phishing",
    "hacking",
    "scam",
    "threat",
    "risk",
    "suspicion",
    "account",
    "credit",
    "debit",
    "suspicious",
    "transaction",
    "security",
    "safety",
    "monitor",
    "watch",
    "detect",
    "unusual",
    "activity",
    "unauthorized",
    "access",
    "vulnerable",
    "exploit",
    "malicious",
    "fraudulent",
    "sensitive",
    "breach",
    "compromise",
    "alert",
    "safeguard",
    "investigate",
    "verify",
    "validate",
    "authenticate",
    "verify",
    "phishing",
    "suspicious",
    "website",
    "password",
    "suspicion",
    "identity",
    "verification",
    "cybercrime",
    "cybersecurity",
    "encryption",
    "firewall",
    "cyber",
    "ransomware",
    "virus",
    "threat",
    "cyberattack",
    "monitoring",
    "detection",
    "anomaly",
    "suspicious",
    "behavior",
    "forensic",
    "transaction",
    "blockchain",
    "bitcoin",
    "crypto",
    "currency",
    "aml",
    "kyc",
    "compliance",
    "regulation",
    "suspicion",
    "government",
    "investigation",
    "fraud",
    "crime",
    "phishing",
    "hack",
    "cybersecurity",
    "scam",
    "identity",
    "theft",
    "money",
    "laundering",
    "suspicious",
    "transaction",
    "unauthorized",
    "access"]
    
### NLP part
exlusion_list = ["ref", "our", "for", "ext", "prc", "wgs", "useri", "caceis", "luxembourg", "bank",
                "kqj", "yen", "cswnew", "roc", "isaebebbxxx", "luxe", "belgium", "bsuilull", "bran" "bra","buq",
                "scr", "userint", "rua", "qwe", "xrd", "nos", "brussels", "branc", "xxx", "isaebebb", "cbf",
                "isaefr","xxxxx", "bom", "nonref", "notprovided", "acou", "ajs", "clb", "cbb", "hev", "int"]

ccy = ['eur', 'usd', 'jpy', 'bgn', 'czk', 'dkk', 'gbp', 'huf', 'pln', 'ron', 'sek', 'chf', 'isk', 'nok', 'try', 'aud',
 'brl', 'cad', 'cny', 'hkd', 'idr', 'ils', 'inr', 'krw', 'mxn', 'myr', 'nzd', 'php', 'sgd', 'thb', 'zar', 'rub', 'cnh', 'twd']
regex = r'\b(?:' + '|'.join(ccy) + r')\b|\b(?:' + '|'.join(ccy) + r'){2,}\b'


def extract_alpha_sequences(string, max_word=None):
    if max_word == None:
        matches = re.findall(r'[A-Za-z]+', string.lower())
        matches = [i for i in matches if (len(i)> 2 and i not in exlusion_list)]
        matches = ' '.join(matches)
        matches = re.sub(regex, '[CCY]', matches)
        return matches
    else:
        matches = re.findall(r'[A-Za-z]+', string.lower())
        matches = [i for i in matches if (len(i)> 2 and i not in exlusion_list)][:max_word]
        matches = ' '.join(matches)
        matches = re.sub(regex, '[CCY]', matches)
        return matches

def has_bad_words(string):
    for i in string.split():
        if i in bad_words:
            return 1
        else:
            return 0