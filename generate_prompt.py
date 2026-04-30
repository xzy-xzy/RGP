from config import config

f = open("./prompt_en.txt", "r")
prompt = f.read( )

def generate_prompt(x):
    samples = [f"Input:\n{i}\nOutput:\n{o}\n" for i, o in zip(x["input"], x["output"])]
    return prompt.replace("[samples]", "".join(samples))


def generate_prompt_cg(x):
    samples = [f"Input:\n{i}\nOutput:\n{o}\n" for i, o in zip(x["input"], x["output"])]
    prompt = "".join(samples[:8])
    prompt += f"Input:\n{x['input'][-1]}\nOutput (Only output the answer, not the process) :"
    return prompt