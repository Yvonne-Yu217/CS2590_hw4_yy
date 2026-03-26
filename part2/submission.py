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
        "You are a precise math master. Calculate the sum of two 7-digit numbers "
        "accurately by adding them digit by digit from right to left.\n\n"
        "Q: 2384756 + 1928374\nA: 4313130\n\n"
        "Q: 5069182 + 3827465\nA: 8896647\n\n"
        "Q: 9182736 + 1234567\nA: 10417303\n\n"
        "Q: 4567890 + 2345678\nA: 6913568\n\n"
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
        'repetition_penalty': 1.2,
        'stop': ['\n', 'Q:']
    }
    return config


def your_pre_processing(s):
    # 不再手动加空格，直接返回原始算式
    return s.strip()


def your_post_processing(output_string):
    # 1. 彻底清除所有空白字符和逗号（防止模型输出 1,234,567）
    cleaned = re.sub(r"\s+", "", output_string).replace(",", "").strip()

    if not cleaned:
        return 0

    # 2. 优先找符合 7 到 9 位长度的数字序列（这最可能是答案）
    m_long = re.search(r"(\d{7,9})", cleaned)
    if m_long:
        return int(m_long.group(1))

    # 3. 兜底逻辑：抓取第一个数字块
    all_nums = re.findall(r"\d+", cleaned)
    return int(all_nums[0]) if all_nums else 0
