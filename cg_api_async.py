import asyncio
from openai import AsyncOpenAI
import time
from config import config
import os, json
from generate_prompt import generate_prompt_cg

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
                ]
            )
        else:
            completion = await aclient.chat.completions.create(
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

async def async_process_queries(queries):
    results = await asyncio.gather(*(async_query_openai(query) for query in queries))
    return results

async def main( ):
    prefix = f"result_cg8/{config.model}/{config.name}"
    if not os.path.exists(prefix):
        os.makedirs(prefix)
    f = open(f"dataset/{config.name}.jsonl", "r")
    data = [json.loads(x) for x in f]
    queries = [generate_prompt_cg(x) for x in data]
    q_id = [ ]
    for i in range(config.test_size):
        if not os.path.exists(f"{prefix}/{i}.txt"):
            q_id.append(i)
    print(q_id)
    # print([queries[i] for i in q_id])
    start_time = time.time( )
    results = await async_process_queries([queries[i] for i in q_id])
    # results = [f"{x}" for x in q_id]
    end_time = time.time( )
    for id, result in zip(q_id, results):
        if not result:
            continue
        with open(f"{prefix}/{id}.txt", "w") as f:
            f.write(result)
    print(f"Total time: {end_time - start_time:.2f} seconds")


asyncio.run(main())

