from config import config
import json

f = open(f"dataset/{config.name}.jsonl", "r")
data = [json.loads(x) for x in f]

root = f"result_cg8/{config.model}/{config.name}"

rit, tot = 0, 0

for i in range(config.test_size):
    f = open(f"{root}/{i}.txt", "r")
    f = f.readlines( )
    res = [ ]
    for x in f:
        x = x.strip( )
        if len(x) == 4 and all([c in ['.', '*'] for c in x]):
            res.append(x)
    res = "".join(res)
    g = data[i]["output"][-1]
    g = g.replace("\n", "")
    tot += 1
    rit += (g == res)

print(rit, tot, rit / tot * 100)




