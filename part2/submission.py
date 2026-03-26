import json
import collections
import argparse
import random
import numpy as np
import requests
import re
import os

def your_netid():
    YOUR_NET_ID = 'N16833099'
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
    # Keep QA format but add carry-heavy anchors for 7-digit addition stability.
    prefix = (
        "Question: what is 3044419+6608684?\n"
        "Answer: 9653103\n"
        "Question: what is 1756139+8493797?\n"
        "Answer: 10249936\n"
        "Question: what is "
    )
    suffix = "?\nAnswer:"

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
        'max_tokens': 50,
        'temperature': 0.1,
        'top_k': 40,
        'top_p': 0.95,
        'repetition_penalty': 1.0,
        'stop': []}
    
    return config


def your_pre_processing(s):
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
    cleaned = output_string.strip().replace(",", "")

    # First line usually contains the answer in this QA format.
    first_line = cleaned.splitlines()[0] if cleaned else ""

    # Prefer explicit "answer" marker if present.
    m_answer = re.search(r"answer\s*[:=]?\s*([-+]?\d+)", cleaned, flags=re.IGNORECASE)
    if m_answer:
        try:
            return int(m_answer.group(1))
        except:
            pass

    # If model emits "...=123", prefer number on the right-hand side.
    if "=" in first_line:
        rhs = first_line.split("=")[-1]
        m_rhs = re.search(r"[-+]?\d+", rhs)
        if m_rhs:
            try:
                return int(m_rhs.group(0))
            except:
                pass

    # Prefer first integer in the first line (e.g., "10249936" or "The answer is 10249936").
    m_first = re.search(r"[-+]?\d+", first_line)
    if m_first:
        try:
            return int(m_first.group(0))
        except:
            pass

    # Fallback to last integer anywhere in output.
    all_any = re.findall(r"[-+]?\d+", cleaned)
    if all_any:
        try:
            return int(all_any[-1])
        except:
            pass

    return 0
