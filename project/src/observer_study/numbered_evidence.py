"""Deterministic evidence selection; offsets count Python Unicode characters."""
import json
import re

from .io import digest

FORMAT = 'numbered-passages-v1'


def passages(reasoning):
    """Partition the entire trace without normalization or discarded whitespace."""
    return [{'passage_id': i, 'start': match.start(), 'end': match.end(),
             'text': match.group(), 'text_sha256': digest(match.group())}
            for i, match in enumerate(re.finditer(r'.+?(?:[.!?](?=\s)|\n|$)', reasoning, re.DOTALL), 1)]


def numbered_record(entry):
    state = json.loads(entry['messages'][1]['content'])
    numbered = passages(state['reasoning'])
    # Retain the scientific rubric while replacing only its output transport.
    rubric = entry['messages'][0]['content']
    rubric = rubric.replace('evidence: a list of exact, contiguous quotations from the reasoning (no paraphrases).',
                            'evidence_passage_ids: a list of integer passage_id values from the numbered reasoning passages.')
    rubric = rubric.replace('quotation', 'selected passage').replace('quotations', 'selected passages')
    state['reasoning_passages'] = numbered
    return {'review_id': entry['review_id'], 'input_sha256': entry['input_sha256'],
            'messages': [{'role': 'system', 'content': rubric},
                         {'role': 'user', 'content': json.dumps(state, ensure_ascii=False)}],
            'passages': numbered, 'reasoning_sha256': digest(state['reasoning'])}


def materialize(result, record):
    """Reject invalid selectors; obtain all quoted text only from verified input."""
    verdict = result.get('verdict')
    if not isinstance(verdict, dict) or set(verdict) != {'label', 'evidence_passage_ids', 'explanation'}:
        raise ValueError('Numbered verdict requires label, evidence_passage_ids and explanation')
    ids = verdict['evidence_passage_ids']
    lookup = {p['passage_id']: p for p in record['passages']}
    if (not isinstance(ids, list) or any(type(i) is not int or i not in lookup for i in ids)
            or len(ids) != len(set(ids))):
        raise ValueError('Invalid or duplicate evidence passage ID')
    selected = [lookup[i] for i in ids]
    return {**result, 'selected_evidence': selected, 'evidence_format': FORMAT,
            'reasoning_sha256': record['reasoning_sha256'],
            'verdict': {'label': verdict['label'], 'evidence': [p['text'] for p in selected],
                        'explanation': verdict['explanation']}}
