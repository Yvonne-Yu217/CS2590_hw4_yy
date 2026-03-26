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
    # Use a single carry-heavy 7-digit exemplar to guide long-addition behavior.
    prefix = "Question: what is 3044419+6608684?\nAnswer: 9653103\nQuestion: what is "
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
        'temperature': 1.0,
        'top_k': 50,
        'top_p': 1.0,
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

    # If model outputs an explicit answer label, prefer that number.
    m_answer = re.search(r"answer\s*[:=]?\s*([-+]?\d+)", cleaned, flags=re.IGNORECASE)
    if m_answer:
        try:
            return int(m_answer.group(1))
        except:
            pass

    nums_first_line = re.findall(r"[-+]?\d+", first_line)
    if nums_first_line:
        try:
            nums = [int(x) for x in nums_first_line]
            # For patterns like "a+b=answer", take the last number.
            if "+" in first_line and len(nums) >= 3:
                return nums[-1]
            # If addends are echoed with answer, answer is typically the largest.
            if len(nums) >= 2:
                return max(nums)
            return nums[0]
        except:
            pass

    # Fallback: if multiple numbers appear, prefer the largest candidate.
    all_any = re.findall(r"[-+]?\d+", cleaned)
    if all_any:
        try:
            all_nums = [int(x) for x in all_any]
            return max(all_nums)
        except:
            pass

    return 0
