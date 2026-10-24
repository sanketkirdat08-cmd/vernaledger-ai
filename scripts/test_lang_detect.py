import sys, os, re
sys.path.append(os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from api.index import detect_msg_language

for q in ["project baddal mahiti sanga", "project chi mahiti sanga", "mulik", "प्रोजेक्ट बद्दल माहिती सांगा", "who made this project"]:
    for l in ["mr", "en", "hi"]:
        detected = detect_msg_language(q, l)
        print(f"Query: '{q}', req_lang: '{l}' => detected: '{detected}'")
