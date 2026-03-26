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
    # Keep prompt compact to reduce length penalty in the grader score.
    prefix = "Q:12+34\nA:46\nQ:"
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
        'max_tokens': 50,
        'temperature': 0.1,
        'top_k': 30,
        'top_p': 0.9,
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
    lines = cleaned.splitlines()

    if not lines:
        return 0

    first_line = lines[0]

    # Tier 1: If first line is a bare integer, trust it.
    m_bare = re.fullmatch(r"\s*([-+]?\d+)\s*", first_line)
    if m_bare:
        try:
            return int(m_bare.group(1))
        except:
            pass

    # Tier 2: Prefer explicit labels on first line.
    m_labeled = re.search(r"(?:A|Answer)\s*[:=]\s*([-+]?\d+)", first_line, flags=re.IGNORECASE)
    if m_labeled:
        try:
            return int(m_labeled.group(1))
        except:
            pass

    # Tier 3: Fallback to the last integer anywhere.
    all_any = re.findall(r"[-+]?\d+", cleaned)
    if all_any:
        try:
            return int(all_any[-1])
        except:
            pass

    return 0
