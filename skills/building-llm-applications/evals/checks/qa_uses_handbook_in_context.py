#!/usr/bin/env python3
"""Handbook QA eval: a ~7k-token handbook should go into the prompt, not a vector index.

Passes when (1) calling `assistant.qa.answer(client, question)` sends the handbook
text to the model, and (2) the implementation adds no embedding or vector-store
dependency. The handbook is far below the size where retrieval is warranted.
"""

import importlib
import os
import re
import sys
from pathlib import Path

workdir = Path(os.environ["EVAL_WORKDIR"])
sys.path.insert(0, str(workdir))

VECTOR_HINTS = re.compile(
    r"\b(chromadb|faiss|pinecone|weaviate|qdrant|milvus|lancedb|pgvector|annoy|hnswlib|"
    r"sentence_transformers|sentence-transformers|langchain|llama_index|llamaindex)\b"
    r"|\bembed(ding)?s?\s*\(|\bcosine_similarity\b|\.embeddings\.create\b",
    re.IGNORECASE,
)

source_files = [p for p in workdir.rglob("*.py") if "tests" not in p.parts]
source_files.append(workdir / "requirements.txt")
for path in source_files:
    if path.is_file():
        match = VECTOR_HINTS.search(path.read_text(encoding="utf-8", errors="replace"))
        if match:
            rel = path.relative_to(workdir)
            print(f"FAIL: retrieval infrastructure added for a small handbook: {rel}: {match.group(0)!r}")
            sys.exit(1)

try:
    llm = importlib.import_module("assistant.llm")
    qa = importlib.import_module("assistant.qa")
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: could not import assistant.qa: {exc!r}")
    sys.exit(1)

handbook = (workdir / "docs" / "handbook.md").read_text(encoding="utf-8")
# Distinctive sentences from the start, middle, and end of the handbook.
probes = [
    "Tallyboard is a project and billing tool for small agencies.",
    "Annual plans are refundable in full within 30 days of purchase.",
    "Refunds are issued to the original payment method within 5 business days.",
]
assert all(p in handbook for p in probes), "fixture probes missing from handbook"


class RecordingModel(llm.ModelClient):
    def __init__(self):
        self.seen = []

    def complete(self, messages, tools=None, max_tokens=1024):
        self.seen.extend(m.content for m in messages)
        return llm.Reply(text="Annual plans are refundable in full within 30 days.")


model = RecordingModel()
try:
    qa.answer(model, "Can a customer get a refund on an annual plan after two weeks?")
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: answer raised {exc!r}")
    sys.exit(1)

sent = "\n".join(model.seen)
missing = [p for p in probes if p not in sent]
if missing:
    print(f"FAIL: the handbook was not sent to the model; missing passages: {missing}")
    sys.exit(1)
print("PASS: full handbook sent in context; no retrieval infrastructure added")
