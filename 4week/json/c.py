import json
def patch(sou, pat):
    for key, value in pat.items():
        if value is None:
            if key in sou:
                del sou[key]
        elif isinstance(value, dict) and isinstance(sou.get(key), dict):
            patch(source[key], value)
        else:
            sou[key] = value
    return sou
sou = json.loads(input())
pat = json.loads(input())
result = patch(sou, pat)
print(json.dumps(result, separators=(',', ':'), sort_keys=True))