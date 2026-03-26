import json
import collections
import argparse
import random
import numpy as np
import requests
import re
import os

def your_netid():
    YOUR_NET_ID = 'yy5919'
    return YOUR_NET_ID

def your_hf_token():
    YOUR_HF_TOKEN = os.getenv('HF_TOKEN', '')
    return YOUR_HF_TOKEN


# for adding small numbers (1-6 digits) and large numbers (7 digits), write prompt prefix and prompt suffix separately.
def your_prompt():
    prefix = (
        "You are a mathematical assistant that performs addition by column.\n"
        "Break the numbers into digits and add them from right to left.\n\n"
        "Q: 1 2 1 2 1 2 1 + 2 3 2 3 2 3 2\n"
        "A: (Step-by-step work) Final Answer: 3535353\n\n"
        "Q: 4 5 6 0 1 2 3 + 1 2 3 0 4 5 6\n"
        "A: (Step-by-step work) Final Answer: 5790579\n\n"
        "Q: 9 8 7 6 5 4 3 + 1 2 3 4 5 6 7\n"
        "A: (Step-by-step work) Final Answer: 11111110\n\n"
        "Q: 5 5 5 5 5 5 5 + 6 6 6 6 6 6 6\n"
        "A: (Step-by-step work) Final Answer: 12222221\n\n"
        "Q: "
    )
    suffix = "\nA:"
    return prefix, suffix


def your_config():
    config = {
        'max_tokens': 50,
        'temperature': 0.1,
        'top_k': 1,
        'top_p': 1.0,
        'repetition_penalty': 1.1,
        'stop': ['\n', 'Q:']
    }
    return config


def your_pre_processing(s):
    # 不再手动加空格，直接返回原始算式
    return s.strip()


def your_post_processing(output_string):
    # 1. 寻找最后一个 "A:" 标记，因为它通常跟在推理步骤之后
    if "A:" in output_string:
        output_string = output_string.split("A:")[-1]

    # 2. 清除所有空格、逗号等干扰项
    cleaned = re.sub(r"[^0-9]", "", output_string).strip()

    if not cleaned:
        return 0

    # 3. 在处理后的文本中抓取第一个 7-9 位的长数字
    match = re.search(r"(\d{7,9})", cleaned)
    if match:
        return int(match.group(1))

    # 4. 兜底逻辑：抓取第一个看到的数字块
    all_nums = re.findall(r"\d+", cleaned)
    return int(all_nums[0]) if all_nums else 0
