"""Shared, Unicode-safe WER/CER policy for local caption evaluation.

NFC, casefold, Unicode punctuation -> word boundary, whitespace collapse.
Combining marks, vowel signs, symbols, digits and format characters are kept.
WER uses whitespace tokens; CER uses normalized code points without spaces.
No Telugu stemming, transliteration or compound-word merging is performed.
An empty reference has no defined error rate (None), not a perfect score.
"""
import unicodedata

POLICY = 'nfc-casefold-punctuation-boundaries-v1'


def normalize(text):
    text = unicodedata.normalize('NFC', text)
    text = ''.join(' ' if unicodedata.category(c).startswith('P') else c for c in text)
    return unicodedata.normalize('NFC', ' '.join(text.casefold().split()))


def tokenize(text):
    return normalize(text).split()


def distance(reference, hypothesis):
    row = list(range(len(hypothesis) + 1))
    for i, expected in enumerate(reference, 1):
        next_row = [i]
        for j, actual in enumerate(hypothesis, 1):
            next_row.append(min(next_row[-1] + 1, row[j] + 1, row[j-1] + (expected != actual)))
        row = next_row
    return row[-1]


def score(reference, hypothesis):
    ref, hyp = normalize(reference), normalize(hypothesis)
    words, predicted = ref.split(), hyp.split()
    chars, predicted_chars = ref.replace(' ', ''), hyp.replace(' ', '')
    we, ce = distance(words, predicted), distance(chars, predicted_chars)
    return {'scoringPolicy': POLICY, 'wordErrors': we, 'referenceWords': len(words),
            'characterErrors': ce, 'referenceCharacters': len(chars),
            'WER': round(100 * we / len(words), 2) if words else None,
            'CER': round(100 * ce / len(chars), 2) if chars else None}
