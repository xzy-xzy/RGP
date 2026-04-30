import anthropic
from anthropic import DefaultHttpxClient
import httpx
from tqdm import tqdm
import time
from config import config
import os, json
from generate_prompt import generate_prompt
from time import sleep

client = anthropic.Anthropic(
    api_key=config.api_key,
    http_client=DefaultHttpxClient(
        proxy="http://10.7.44.253:7890",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)

def query_claude(query):
    try:
        if config.model_type == "reason":
            with client.messages.stream(
                model=config.model,
                max_tokens=20000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 16000,
                },
                messages=[
                    {"role": "user", "content": query}
                ]
            ) as stream:
                reasoning_content = ""
                answer_content = ""
                for event in stream:
                    if event.type == "content_block_delta":
                        if event.delta.type == "thinking_delta":
                            reasoning_content += event.delta.thinking
                        elif event.delta.type == "text_delta":
                            answer_content += event.delta.text
                return reasoning_content, answer_content
        else:
            completion = client.messages.create(
                model=config.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0,
            )
            return completion.content[0].text
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
    a = time.time( )
    result = query_claude(queries[i])
    if result:
        if config.model_type != "reason":
            with open(f"{prefix}/{i}.txt", "w") as f:
                f.write(result)
        else:
            with open(f"{prefix}/{i}.txt", "w") as f:
                f.write(result[1])
            with open(f"{prefix}/{i}_reasoning.txt", "w") as f:
                f.write(result[0])
    b = time.time( )
    t = b - a
    sleep(30)
end_time = time.time( )
print(f"Total time: {end_time - start_time:.2f} seconds")


