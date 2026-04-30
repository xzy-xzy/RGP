from openai import OpenAI
from tqdm import tqdm
import time
from config import config
import os, json
from generate_prompt import generate_prompt

client = OpenAI(
    base_url=config.base_url,
    api_key=config.api_key
)

def query_openai(query):
    try:
        if config.model_type == "reason":
            completion = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "user", "content": query}
                ]
            )
        else:
            completion = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0,
            )
        return completion.choices[0].message.content
    except Exception as e:
        print(e)
        return None


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
# print([queries[i] for i in q_id])
start_time = time.time( )
# results = [ ]
for i in tqdm(q_id):
    result = query_openai(queries[i])
    if result:
        with open(f"{prefix}/{i}.txt", "w") as f:
            f.write(result)
end_time = time.time( )
print(f"Total time: {end_time - start_time:.2f} seconds")
