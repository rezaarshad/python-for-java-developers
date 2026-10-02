import os, sys
import json
from typing import List, Optional, Dict
import re


def parse_tags(raw, seen=[]):
    l = []
    for t in raw.split(","):
        t = t.strip().lower()
        if t == "": continue
        if not t in seen:
            seen.append(t)
            l.append(t)
    return l


def average_words(notes: List[Dict]) -> int:
    if len(notes) == 0:
        return None
    total = 0
    for n in notes:
        total = total + len(n["body"].split())
    return total / len(notes)


def find_note(notes: List[dict], note_id) -> Optional[dict]:
    for n in notes:
        if n["id"] == note_id:
            return n
    return None


def load_config(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except:
        data = {}
    if data.get("model") == None:
        data["model"] = f"claude-opus-5-5"
    return data


def slug(title:str)->str:
    return re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
