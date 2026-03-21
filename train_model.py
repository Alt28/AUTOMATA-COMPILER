"""
Fine-tune all-mpnet-base-v2 on GAL knowledge base for better retrieval.

Strategy: MultipleNegativesRankingLoss with (query, positive) pairs.
  - Each training phrase is paired with a "topic label" string
  - Phrases from the same topic should be close, different topics far apart

This produces a fine-tuned model saved to ./gal-mpnet-finetuned/
"""

import sys, os, random
sys.path.insert(0, "Backend")

from sentence_transformers import (
    SentenceTransformer,
    InputExample,
    losses,
    evaluation,
)
from torch.utils.data import DataLoader

# ── 1. Load the knowledge base ────────────────────────────────────
import gal_fallback as fb

topics = []  # list of (phrases, short_label)
for i, (phrases, response) in enumerate(fb._KNOWLEDGE_BASE):
    # Create a short label from the first phrase
    label = phrases[0][:80]
    topics.append((phrases, label, response))

print(f"Loaded {len(topics)} topics with {sum(len(t[0]) for t in topics)} total phrases")

# ── 2. Generate training pairs ────────────────────────────────────
# Strategy: for each phrase, pair it with:
#   a) Other phrases in the same topic (positive pairs)
#   b) A condensed description of the topic (anchor-passage pair)

train_examples = []

for phrases, label, response in topics:
    # Take first 200 chars of response as a condensed passage
    passage = response[:200].strip()

    for phrase in phrases:
        # Pair each phrase with the passage (query → answer)
        train_examples.append(InputExample(texts=[phrase, passage]))

        # Pair with other phrases in same topic (query ↔ query)
        others = [p for p in phrases if p != phrase]
        if others:
            partner = random.choice(others)
            train_examples.append(InputExample(texts=[phrase, partner]))

# Also add synonym-expanded versions
for term, gal_equiv in fb._SYNONYMS.items():
    # "what is int" → "what is seed"
    train_examples.append(
        InputExample(texts=[f"what is {term} in GAL", f"what is {gal_equiv} in GAL"])
    )
    train_examples.append(
        InputExample(texts=[f"how to use {term}", f"how to use {gal_equiv}"])
    )

random.shuffle(train_examples)
print(f"Generated {len(train_examples)} training pairs")

# ── 3. Setup evaluation ──────────────────────────────────────────
# Build a small eval set: for each topic, take one phrase as query
# and the response snippet as the expected match
eval_sentences1 = []
eval_sentences2 = []
eval_scores = []

for phrases, label, response in topics:
    if len(phrases) >= 2:
        eval_sentences1.append(phrases[-1])  # last phrase as query
        eval_sentences2.append(response[:200].strip())  # passage
        eval_scores.append(1.0)  # should be similar

evaluator = evaluation.EmbeddingSimilarityEvaluator(
    eval_sentences1, eval_sentences2, eval_scores, name="gal-eval"
)

# ── 4. Fine-tune ─────────────────────────────────────────────────
model = SentenceTransformer("all-mpnet-base-v2")

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

output_path = "./gal-mpnet-finetuned"

print("Starting fine-tuning...")
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=5,
    evaluation_steps=50,
    warmup_steps=10,
    output_path=output_path,
    show_progress_bar=True,
)

print(f"\nFine-tuned model saved to: {output_path}")
print("Done!")
