import argparse

parser = argparse.ArgumentParser( )
parser.add_argument("--k", type=int, default=4) # number of components
parser.add_argument("--u", type=int, default=2) # number of possible values
parser.add_argument("--d", type=int, default=16) # number of samples in D
parser.add_argument("--test_size", type=int, default=30) # number of D for test
parser.add_argument("--type", choices=["h", "v", "b", "r", "hr"], default="h")
parser.add_argument("--index_shuffle", action="store_true")
parser.add_argument("--model", type=str, default="deepseek-reasoner")
parser.add_argument("--api_key", default="none")

model_type = {
    "deepseek-reasoner": "reason",  # r1
    "deepseek-chat": "chat",    # v3: cut 2025-03-24
    "o1-mini": "reason",
    "o1": "reason",         # not available
    "o3-mini": "reason",
    "gpt-4o": "chat",       # 2024-08-06
    "gpt-4o-2024-11-20": "chat",
    "qwq-plus": "reason",    # cut 2025-03-05
    "qwen-max-latest": "chat",     # cut 2025-01-25
    "qwen-max": "chat",      # cut 2024-09-19
    "gemini-2.0-flash-thinking-exp-01-21": "reason",
    "gemini-2.0-flash": "chat", # my cut 2025-04-06
    "gemini-2.5-pro-exp-03-25": "reason",
    "claude-3-5-haiku-20241022": "chat",
    "claude-3-7-sonnet-20250219": "reason",
}

config = parser.parse_args( )
config.model_type = model_type[config.model] if config.model in model_type else "reason"
config.name = f"k={config.k}_u={config.u}_d={config.d}_type={config.type}"
if config.index_shuffle:
    config.name += "_index-shuffle"

print(config.model, config.name)

if "gpt" in config.model:
    config.base_url = None

elif "deepseek" in config.model:
    config.base_url = "https://api.deepseek.com"

elif "claude" in config.model:
    pass

elif "llama" in config.model:
    config.base_url = "https://api.llama-api.com"

elif "gemini" in config.model:
    config.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

elif "qwen" in config.model or "qwq" in config.model:
    config.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

elif "o1" in config.model:
    config.base_url = None

elif "o3" in config.model:
    config.base_url = "https://api.gptsapi.net/v1"
