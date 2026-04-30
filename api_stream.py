from openai import OpenAI
import os
from config import config
import time
import os, json
from generate_prompt import generate_prompt

client = OpenAI(
    base_url=config.base_url,
    api_key=config.api_key
)

def stream_query(query):

    reasoning_content = ""
    answer_content = ""

    completion = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "user", "content": query}
        ],
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                reasoning_content += delta.reasoning_content
            else:
                answer_content += delta.content

    return reasoning_content, answer_content


prefix = f"result/{config.model}/{config.name}"
if not os.path.exists(prefix):
    os.makedirs(prefix)
f = open(f"dataset/{config.name}.jsonl", "r")
data = [json.loads(x) for x in f]
queries = [generate_prompt(x) for x in data]
q_id = [ ]
for i in range(config.test_size):
    if not os.path.exists(f"{prefix}/{i}.txt"):
        q_id.append(i)

print(q_id)
print([queries[i] for i in q_id])
start_time = time.time( )
results = [ ]
for i in q_id:
    results.append(stream_query(queries[i]))
end_time = time.time( )
for id, result in zip(q_id, results):
    with open(f"{prefix}/{id}_reasoning.txt", "w") as f:
        f.write(result[0])
    with open(f"{prefix}/{id}.txt", "w") as f:
        f.write(result[1])
print(f"Total time: {end_time - start_time:.2f} seconds")
