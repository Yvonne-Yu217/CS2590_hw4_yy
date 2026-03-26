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
        "You are a maths master. Calculate the sum of two 7-digit numbers precisely.\n\n"
        "Q: 1 2 1 2 1 2 1 + 2 3 2 3 2 3 2\n"
        "A:\n"
        "- 1s: 1 + 2 = 3\n"
        "- 10s: 2 + 3 = 5\n"
        "- 100s: 1 + 2 = 3\n"
        "- 1000s: 2 + 3 = 5\n"
        "- 10000s: 1 + 2 = 3\n"
        "- 100000s: 2 + 3 = 5\n"
        "- 1000000s: 1 + 2 = 3\n"
        "Final Answer: 3535353\n\n"

        "Q: 4 5 6 0 1 2 3 + 1 2 3 0 4 5 6\n"
        "A:\n"
        "- 1s: 3 + 6 = 9\n"
        "- 10s: 2 + 5 = 7\n"
        "- 100s: 1 + 4 = 5\n"
        "- 1000s: 0 + 0 = 0\n"
        "- 10000s: 6 + 3 = 9\n"
        "- 100000s: 5 + 2 = 7\n"
        "- 1000000s: 4 + 1 = 5\n"
        "Final Answer: 5790579\n\n"

        "Q: 9 8 7 6 5 4 3 + 1 2 3 4 5 6 7\n"
        "A:\n"
        "- 1s: 3 + 7 = 10, digit 0, carry 1\n"
        "- 10s: 4 + 6 + 1 = 11, digit 1, carry 1\n"
        "- 100s: 5 + 5 + 1 = 11, digit 1, carry 1\n"
        "- 1000s: 6 + 4 + 1 = 11, digit 1, carry 1\n"
        "- 10000s: 7 + 3 + 1 = 11, digit 1, carry 1\n"
        "- 100000s: 8 + 2 + 1 = 11, digit 1, carry 1\n"
        "- 1000000s: 9 + 1 + 1 = 11, digit 1\n"
        "Final Answer: 11111110\n\n"

        "Q: 5 5 5 5 5 5 5 + 6 6 6 6 6 6 6\n"
        "A:\n"
        "- 1s: 5 + 6 = 11, digit 1, carry 1\n"
        "- 10s: 5 + 6 + 1 = 12, digit 2, carry 1\n"
        "- 100s: 5 + 6 + 1 = 12, digit 2, carry 1\n"
        "- 1000s: 5 + 6 + 1 = 12, digit 2, carry 1\n"
        "- 10000s: 5 + 6 + 1 = 12, digit 2, carry 1\n"
        "- 100000s: 5 + 6 + 1 = 12, digit 2, carry 1\n"
        "- 1000000s: 5 + 6 + 1 = 12, digit 2\n"
        "Final Answer: 12222221\n\n"

        "Q: "
    )
    suffix = "\nA:"
    return prefix, suffix


def your_config():
    config = {
        'max_tokens': 300,
        'temperature': 0.1,
        'top_k': 1,
        'top_p': 1.0,
        'repetition_penalty': 1.0,
        'stop': ['Q:', 'Question:']
    }
    return config


def your_pre_processing(s):
    s = s.replace("+", " + ")
    parts = s.split()
    processed_parts = []
    for part in parts:
        if part.isdigit():
            processed_parts.append(" ".join(list(part)))
        else:
            processed_parts.append(part)
    return " ".join(processed_parts)


def your_post_processing(output_string):

    if "Final Answer:" in output_string:
        output_string = output_string.split("Final Answer:")[-1]

    cleaned = re.sub(r"\s+", "", output_string).replace(",", "").strip()

    if not cleaned:
        return 0

    m_long = re.search(r"(\d{7,9})", cleaned)
    if m_long:
        return int(m_long.group(1))

    nums = re.findall(r"\d+", cleaned)
    if nums:
        full_num = ''.join(nums)
        return int(full_num)
    return 0
