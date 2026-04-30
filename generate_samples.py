from config import config
from random import seed, shuffle, sample, choice
import os, json

seed(0)

def generate( ):
    # each component controls a set of points
    control = [[ ] for _ in range(config.k)]

    if config.type == "h":
        # horizontal: each component controls a row
        for i in range(config.k):
            for j in range(config.k):
                control[i].append((i, j))

    elif config.type == "v":
        # vertical: each component controls a column
        for i in range(config.k):
            for j in range(config.k):
                control[i].append((j, i))

    elif config.type == "r":
        # random: each component controls a random set of points
        pos = [(i, j) for i in range(config.k) for j in range(config.k)]
        shuffle(pos)
        for i in range(config.k):
            control[i] = pos[i * config.k: (i + 1) * config.k]

    elif config.type == "b":
        # block: each component controls a block
        px, py = 1, config.k
        for p in range(2, config.k - 1):
            if config.k % p == 0:
                px, py = p, config.k // p
                break
        for i in range(config.k):
            start = ((i // px) * px, (i % px) * py)
            for x in range(px):
                for y in range(py):
                    control[i].append((start[0] + x, start[1] + y))

    elif config.type == "hr":
        # h + r: half horizontal, and the rest are random
        row = [i for i in range(config.k)]
        row = sample(row, config.k // 2)
        for i in range(config.k // 2):
            for j in range(config.k):
                control[row[i]].append((row[i], j))
        pos = [(i, j) for i in range(config.k) for j in range(config.k) if i not in row]
        shuffle(pos)
        j = 0
        for i in range(config.k):
            if i in row:
                continue
            control[i] = pos[j * config.k: (j + 1) * config.k]
            j += 1
        print(row, control)

    elif config.type == "vr":
        # v + r: half vertical, and the rest are random
        col = [i for i in range(config.k)]
        col = sample(col, config.k // 2)
        for i in range(config.k // 2):
            for j in range(config.k):
                control[col[i]].append((j, col[i]))
        pos = [(i, j) for i in range(config.k) for j in range(config.k) if j not in col]
        shuffle(pos)
        j = 0
        for i in range(config.k):
            if i in col:
                continue
            control[i] = pos[j * config.k: (j + 1) * config.k]
            j += 1
        print(col, control)

    elif config.type == "hb":
        # h + b: half horizontal, and the rest are block
        px, py = 1, config.k
        for p in range(2, config.k - 1):
            if config.k % p == 0:
                px, py = p, config.k // p
                break
        labels = [0] * (config.k // 2) + [1] * ((config.k - config.k // 2) // (config.k // py))
        shuffle(labels)
        con, x = 0, 0
        for label in labels:
            if label == 0:
                for j in range(config.k):
                    control[con].append((x, j))
                con += 1
                x += 1
            else:
                for j in range(config.k // py):
                    start = (x, j * py)
                    for a in range(px):
                        for b in range(py):
                            control[con].append((start[0] + a, start[1] + b))
                    con += 1
                x += px
        print(control)

    # convert int to digit list
    def to_digit(val, length, base):
        res = [ ]
        for _ in range(length):
            res.append(val % base)
            val //= base
        res.reverse( )
        return res

    # value: pattern of the controlled points (0/1 list)
    value = [[ ] for _ in range(config.k)]
    for i in range(config.k):
        l = len(control[i])
        candidate = [i for i in range(2**l)]
        if config.u == 2 and not config.not_complementary:
            v = choice(candidate)
            value[i] = [v, v ^ (2 ** l - 1)]
        else:
            value[i] = sample(candidate, config.u)
        value[i] = [to_digit(val, l, 2) for val in value[i]]
        # print(value[i])

    # generate all samples
    input_index = [i for i in range(config.k)]
    org_index = [i for i in range(config.k)]
    if config.index_shuffle:
        while input_index == org_index:
            shuffle(input_index)
    print(input_index)
    samples = [ ]
    for b in range(config.u ** config.k):
        v = to_digit(b, config.k, config.u)
        input_str = [0] * config.k
        for i in range(config.k):
            input_str[i] = chr(ord('A') + i * config.u + v[i])
        print(v, input_str)
        input_str = " ".join(input_str)
        grid = [["." for _ in range(config.k)] for _ in range(config.k)]
        for i in range(config.k):
            val = value[i][v[i]]
            for val, (x, y) in zip(val, control[input_index[i]]):
                grid[x][y] = "*" if val else "."
        grid = "\n".join("".join(row) for row in grid)
        print(grid)
        samples.append((v, input_str, grid))

    # get d samples that cover all possible values
    d_samples = sample(samples, config.d)
    while True:
        for i in range(config.k):
            appear = set( )
            for j in range(config.d):
                appear.add(d_samples[j][0][i])
            if len(appear) != config.u:
                break
        else:
            break
        d_samples = sample(samples, config.d)

    e_samples = [x for x in samples if x not in d_samples]
    return d_samples, e_samples

# create folder dataset
if not os.path.exists("dataset"):
    os.mkdir("dataset")

# create jsonl
f_d = open(f"dataset/{config.name}.jsonl", "w")
f_e = open(f"dataset/{config.name}_ex.jsonl", "w")
for i in range(config.test_size):
    d_samples, e_samples = generate( )
    input_str = [x[1] for x in d_samples]
    output_str = [x[2] for x in d_samples]
    f_d.write(json.dumps({"input": input_str, "output": output_str}) + "\n")
    input_str = [x[1] for x in e_samples]
    output_str = [x[2] for x in e_samples]
    f_e.write(json.dumps({"input": input_str, "output": output_str}) + "\n")