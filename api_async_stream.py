import asyncio
from openai import AsyncOpenAI
import time
from config import config
import os, json
from generate_prompt import generate_prompt

async def async_query_openai(query):
    aclient = AsyncOpenAI(
        base_url=config.base_url,
        api_key=config.api_key
    )
    try:
        if config.model_type == "reason":
            completion = await aclient.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "user", "content": query}
                ],
                stream=True,
                stream_options={
                    "include_usage": True
                }
            )
        else:
            completion = await aclient.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0,
                stream=True,
                stream_options={
                    "include_usage": True
                }
            )

        reasoning_content = ""
        answer_content = ""

        async for chunk in completion:
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

    except Exception as e:
        print(e)
        return None

async def async_process_queries(queries):
    results = await asyncio.gather(*(async_query_openai(query) for query in queries))
    return results

async def main( ):
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
    results = await async_process_queries([queries[i] for i in q_id])
    # results = [f"{x}" for x in q_id]
    end_time = time.time( )
    for id, result in zip(q_id, results):
        if not result:
            continue
        with open(f"{prefix}/{id}_reasoning.txt", "w") as f:
            f.write(result[0])
        with open(f"{prefix}/{id}.txt", "w") as f:
            f.write(result[1])
    print(f"Total time: {end_time - start_time:.2f} seconds")


asyncio.run(main())

