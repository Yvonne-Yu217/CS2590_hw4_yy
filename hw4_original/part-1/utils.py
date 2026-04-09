import datasets
from datasets import load_dataset
from transformers import AutoTokenizer
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification
from torch.optim import AdamW
from transformers import get_scheduler
import torch
from tqdm.auto import tqdm
import evaluate
import random
import argparse
from nltk.corpus import wordnet
from nltk import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer

random.seed(0)


def example_transform(example):
    example["text"] = example["text"].lower()
    return example


### Rough guidelines --- typos
# For typos, you can try to simulate nearest keys on the QWERTY keyboard for some of the letter (e.g. vowels)
# You can randomly select each word with some fixed probability, and replace random letters in that word with one of the
# nearest keys on the keyboard. You can vary the random probablity or which letters to use to achieve the desired accuracy.


### Rough guidelines --- synonym replacement
# For synonyms, use can rely on wordnet (already imported here). Wordnet (https://www.nltk.org/howto/wordnet.html) includes
# something called synsets (which stands for synonymous words) and for each of them, lemmas() should give you a possible synonym word.
# You can randomly select each word with some fixed probability to replace by a synonym.


def custom_transform(example):
    ################################
    ##### YOUR CODE BEGINGS HERE ###

    # Design and implement the transformation as mentioned in pdf
    # You are free to implement any transformation but the comments at the top roughly describe
    # how you could implement two of them --- synonym replacement and typos.

    # You should update example["text"] using your transformation

    text = example["text"].strip()
    tokens = word_tokenize(text)
    transformed_tokens = []

    for token in tokens:
        if random.random() < 0.15 and token.isalpha():
            synsets = wordnet.synsets(token)
            synonyms = set()
            for syn in synsets:
                for lemma in syn.lemmas():
                    candidate = lemma.name().replace('_', ' ')
                    if candidate.lower() != token.lower():
                        synonyms.add(candidate)

            if synonyms:
                transformed_tokens.append(random.choice(list(synonyms)))
                continue

            if len(token) > 1:
                i = random.randrange(len(token))
                j = 1 if i == 0 else i - 1
                chars = list(token)
                chars[i], chars[j] = chars[j], chars[i]
                transformed_tokens.append(''.join(chars))
                continue

        transformed_tokens.append(token)

    example["text"] = TreebankWordDetokenizer().detokenize(transformed_tokens)

    ##### YOUR CODE ENDS HERE ######

    return example
