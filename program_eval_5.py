from config import config
import json
import os
import program_extract
from program_check import program_check
from parsing_test_5 import calculate_estimate
from math import log

f = open(f"dataset/{config.name}.jsonl", "r")
data = [json.loads(x) for x in f]

root = f"result/{config.model}/{config.name}"

def check(data, i):
    res = [ ]
    for x, y in zip(data[i]["input"], data[i]["output"]):
        output = program_check(f"{root}/{i}.py", x)
        res.append(output.strip( ) == y.strip( ))
    return res

def acc(res):
    if not res:
        return None
    return sum(res) / len(res) * 100

stat = {
    "c_dict_n": [ ],
    "c_dict_m": [ ],
    "c_block_n": [ ],
    "c_block_m": [ ],
    "c_length": [ ],
    "c_error": [ ],
    "c": [ ],
    "norm_c": [ ],
    "log_norm_c": [ ],
    "in_acc": [ ],
}

for i in range(config.test_size):
    print(i)
    res = check(data, i)
    in_acc = acc(res)
    c_dict_n, c_dict_m, c_block_n, c_block_m = calculate_estimate(open(f"{root}/{i}.py", "r").read( ))
    c_n = c_dict_n + c_block_n
    c_m = c_dict_m + c_block_m
    c_n = max(c_n, config.u * config.k)
    c_m = max(c_m, config.u * config.k * config.k)
    c_n = min(c_n, config.d * config.k)
    c_m = min(c_m, config.d * config.k * config.k)
    c_length = c_n + c_m
    c_error = (len(res) - sum(res)) * (config.k + config.k * config.k)
    c = c_length + c_error
    min_c = config.u * (config.k * config.k + config.k)
    max_c = config.d * (config.k + config.k * config.k)
    norm_c = (max_c - min(max(c, min_c), max_c)) / (max_c - min_c) * 100
    log_norm_c = (log(max_c) - log(min(max(c, min_c), max_c))) / (log(max_c) - log(min_c)) * 100

    if c_length < min_c:
        print(config.type, config.index_shuffle, config.not_complementary, i)
        print(c_dict_n, c_dict_m, c_block_n, c_block_m, norm_c)
        print("-" * 20)
    f = open(f"{root}/{i}_info.json", "w")
    f.write(json.dumps({
        "c_dict_n": c_dict_n,
        "c_dict_m": c_dict_m,
        "c_block_n": c_block_n,
        "c_block_m": c_block_m,
        "c_n": c_n,
        "c_m": c_m,
        "c_length": c_length,
        "c_error": c_error,
        "c": c,
        "norm_c": norm_c,
        "log_norm_c": log_norm_c,
        "in_acc": in_acc,
    }, indent=4))
    f.close( )
    stat["c_dict_n"].append(c_dict_n)
    stat["c_dict_m"].append(c_dict_m)
    stat["c_block_n"].append(c_block_n)
    stat["c_block_m"].append(c_block_m)
    stat["c_length"].append(c_length)
    stat["c_error"].append(c_error)
    stat["c"].append(c)
    stat["norm_c"].append(norm_c)
    stat["log_norm_c"].append(log_norm_c)
    stat["in_acc"].append(in_acc)

f = open(f"{root}/stat_{config.test_size}.json", "w")
stat = {k: sum(v) / len(v) if v[0] is not None else None for k, v in stat.items( )}
print(stat)
f.write(json.dumps(stat, indent=4))





