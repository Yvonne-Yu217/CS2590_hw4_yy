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
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    # 彻底删掉所有带空格的指令，回归最原始的 Q&A 模式
    prefix = (
        "Q: 1111111 + 2222222\nA: 3333333\n\n"
        "Q: 7654321 + 1234567\nA: 8888888\n\n"
        "Q: 9876543 + 1234567\nA: 11111110\n\n"
        "Q: "
    )
    suffix = "\nA:"

    return prefix, suffix


def your_config():
    """Returns a config for prompting api
    Returns:
        For both short/medium, long: a dictionary with fixed string keys.
    Note:
        do not add additional keys. 
        The autograder will check whether additional keys are present.
        Adding additional keys will result in error.
    """
    config = {
        'max_tokens': 20,
        'temperature': 0.1,
        'top_k': 1,
        'top_p': 1.0,
        'repetition_penalty': 1.2,
        'stop': ["\n", "Q:"]}
    
    return config


def your_pre_processing(s):
    # 简单粗暴，不做任何干扰
    return s.strip()


def your_post_processing(output_string):
    """Returns the post processing function to extract the answer for addition
    Returns:
        For: the function returns extracted result
    Note:
        do not attempt to "hack" the post processing function
        by extracting the two given numbers and adding them.
        the autograder will check whether the post processing function contains arithmetic additiona and the graders might also manually check.
    """
    # 1. 删掉所有空格和逗号，防止模型输出 1,234,567 或 1 2 3...
    cleaned = re.sub(r"\s+", "", output_string).replace(",", "").strip()

    # 2. 在清理后的字符串里，找第一个出现的 7 到 9 位数字（加法结果的合理长度）
    m_long = re.search(r"(\d{7,9})", cleaned)
    if m_long:
        return int(m_long.group(1))

    # 3. 如果没找到长数字，就抓第一个看到的数字序列
    m_any = re.search(r"\d+", cleaned)
    if m_any:
        return int(m_any.group(0))

    return 0
