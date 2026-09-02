'''End-to-end evaluation of the supply chain agent.

Each case in ``questions.json`` is a natural-language question whose answer
is grounded in the live ``supply_chain`` database. The agent is asked the
question and its final reply is checked for the ``expected_facts`` strings
(case-insensitive substring match). This exercises the full loop: the model
choosing a tool, the tool hitting Postgres, and the model summarising the
result.

Requires ``OPENAI_API_KEY`` and a reachable ``supply_chain`` database.

Run directly:

    python -m tests.evaluations.evaluation
    python -m tests.evaluations.evaluation --verbose

Exits non-zero if any case fails, so it can gate CI.
'''

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

from langchain_core.messages import HumanMessage

QUESTIONS_PATH = Path(__file__).with_name('questions.json')


@dataclass
class CaseResult:
    case_id: str
    question: str
    answer: str
    missing_facts: list[str]

    @property
    def passed(self) -> bool:
        return not self.missing_facts


def load_cases() -> list[dict]:
    with QUESTIONS_PATH.open() as handle:
        return json.load(handle)


def _normalize(text: str) -> str:
    '''Lower-case and drop digit-group separators so "4,670" matches "4670".'''

    return re.sub(r'(?<=\d),(?=\d)', '', text.lower())


def run_case(agent, case: dict) -> CaseResult:
    config = {'configurable': {'thread_id': str(uuid.uuid4())}}

    response = agent.invoke(
        {'messages': [HumanMessage(content=case['question'])]},
        config,
    )
    answer = response['messages'][-1].content or ''
    haystack = _normalize(answer)

    missing = [
        fact for fact in case['expected_facts']
        if _normalize(fact) not in haystack
    ]

    return CaseResult(
        case_id=case['id'],
        question=case['question'],
        answer=answer,
        missing_facts=missing,
    )


def evaluate(verbose: bool = False) -> list[CaseResult]:
    # Imported lazily so ``--help`` works without credentials configured.
    from app.agent.graph import agent

    results = []

    for case in load_cases():
        result = run_case(agent, case)
        results.append(result)

        status = 'PASS' if result.passed else 'FAIL'
        print(f'[{status}] {result.case_id}: {result.question}')

        if verbose or not result.passed:
            print(f'       answer: {result.answer.strip()}')
        if not result.passed:
            print(f'       missing: {", ".join(result.missing_facts)}')

    passed = sum(1 for result in results if result.passed)
    print(f'\n{passed}/{len(results)} cases passed')

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='print the agent answer for every case, not just failures',
    )
    args = parser.parse_args()

    results = evaluate(verbose=args.verbose)

    return 0 if all(result.passed for result in results) else 1


if __name__ == '__main__':
    sys.exit(main())
