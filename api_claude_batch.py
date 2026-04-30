from config import config
from generate_prompt import generate_prompt
import json

f = open(f"dataset/{config.name}.jsonl", "r")
data = [json.loads(x) for x in f]
data = data[:max(config.test_size, len(data))]
queries = [generate_prompt(x) for x in data]
# print(queries)

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
import os

client = anthropic.Anthropic(api_key=config.api_key)

name = f"{config.model}_{config.name}"
root = f"result/{config.model}/{config.name}"

if not os.path.exists(root):
    os.makedirs(root)

if not os.path.exists(f"{root}/id.txt"):

    requests = [ ]

    for idx, x in enumerate(queries):
        requests.append(
            Request(
                custom_id=str(idx),
                params=MessageCreateParamsNonStreaming(
                    model=config.model,
                    messages=[
                        {"role": "user", "content": x, "temperature": 0}
                    ]
                )
            )
        )

    f.close( )

    batch_input_file = client.messages.batches.create(requests=requests)

    f = open(f"{root}/id.txt", "w")
    f.write(batch_input_file.id)
    f.close( )

    print("Batch created.")

else:
    print("Batch already created.")

exit(0)

idx = open(f"{root}/id.txt").read( )

if not os.path.exists(f"{root}/bid.txt"):
    ret = client.batches.create(
        input_file_id=idx,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
          "description": f"{name}"
        }
    )
    bid = ret.id
    f = open(f"{root}/bid.txt", "w")
    f.write(bid)
    f.close( )
    print("Batch submitted.")

else:
    bid = open(f"{root}/bid.txt").read( )
    print("Batch already submitted.")


if not os.path.exists(f"{root}/completed"):
    ret = client.batches.retrieve(bid)
    if ret.status == "completed":
        f = open(f"{root}/completed", "w")
        f.write("completed")
        f.close( )
        idx = ret.output_file_id
        response = client.files.content(idx)
        text = response.text
        # f = open(f"{root}/result.txt", "w")
        text = text.split("\n")
        if len(text[-1]) == 0:
            text = text[:-1]
        ret = [ ]
        for line in text:
            t = json.loads(line)
            custom_id = int(t["custom_id"])
            content = t["response"]["body"]["choices"][0]["message"]["content"]
            ret.append((custom_id, content))
        ret.sort(key=lambda x: x[0])
        for idx, content in ret:
            f = open(f"{root}/{idx}.txt", "w")
            f.write(content)
            f.close( )
        print("Batch completed.")
    else:
        print("Batch not completed.")
        exit(0)

else:
    print("Batch already completed.")


