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
    # Use prompt structure from the prompt-a-thon example with multiple sample questions.
    prefix = (
        "Sample Question 1: What is 1034169 + 4154323?\n"
        "Answer: 5188482\n"
        "Sample Question 2: What is 1357924 + 2468135?\n"
        "Answer: 3826059\n"
        "Sample Question 3: What is 1234567 + 1234567?\n"
        "Answer: 2469134\n"
        "Sample Question 4: What is 9875543 + 1093285?\n"
        "Answer: 10968828\n"
        "Sample Question 5: What is 4398254 + 2309481?\n"
        "Answer: 4629102\n"
        "Question: What is a+b?\n"
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
        'max_tokens': 50,
        'temperature': 0.1,
        'top_k': 1,
        'top_p': 1.0,
        'repetition_penalty': 1.1,
        'stop': []}
    
    return config


def your_pre_processing(s):
    # Convert "1234567+7654321" into spaced form so tokenizer sees per-digit units.
    cleaned = s.strip().replace(" ", "")
    spaced = []
    for ch in cleaned:
        if ch.isdigit() or ch in "+-":
            spaced.append(ch)
        else:
            spaced.append(ch)
    # Add spaces between digits but keep + and - as separators.
    spaced = " ".join(spaced).replace(" + ", " + ").replace(" - ", " - ")
    return spaced


def your_post_processing(output_string):
    """Returns the post processing function to extract the answer for addition
    Returns:
        For: the function returns extracted result
    Note:
        do not attempt to "hack" the post processing function
        by extracting the two given numbers and adding them.
        the autograder will check whether the post processing function contains arithmetic additiona and the graders might also manually check.
    """
    # Remove all whitespace/newlines first so split formatting cannot break numbers.
    cleaned = re.sub(r"\s+", "", output_string).replace(",", "").strip()
    if not cleaned:
        return 0

    # Prefer explicit trailing labels near the answer region.
    labeled_anywhere = re.findall(r"(?:A|Answer)[:=]([-+]?\d+)", cleaned, flags=re.IGNORECASE)
    if labeled_anywhere:
        try:
            return int(labeled_anywhere[-1])
        except:
            pass

    # Prefer 7-8 digit candidates (expected range for 7-digit addition results).
    long_nums = re.findall(r"\d{7,8}", cleaned)
    if long_nums:
        try:
            return int(long_nums[-1])
        except:
            pass

    # Final fallback: any numeric token.
    all_any = re.findall(r"\d+", cleaned)
    if all_any:
        try:
            return int(all_any[-1])
        except:
            pass

    return 0
