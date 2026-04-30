import re, os

def extract_python(text):
    text = text.replace('\u200b', '')
    pattern = [
        r'```python(.*?)```',
        r'Begin Code\n-{6,}(.*?)-{6,}',
        r'-{6,}(.*?)-{6,}'
    ]
    for p in pattern:
        res = re.findall(p, text, re.DOTALL)
        if res:
            return res[-1]
    return ""

from config import config
root = f"result/{config.model}/{config.name}"
if os.path.exists(f"{root}/result"):
    root = f"{root}/result"
for i in range(config.test_size):
    f = open(f"{root}/{i}.txt", "r")
    text = f.read( )
    g = open(f"{root}/{i}.py", "w")
    g.write(extract_python(text))
    g.close( )

