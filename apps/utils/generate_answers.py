import random
from typing import Dict, List


async def generate_answers(correct_question: Dict, all_questions: List[Dict]) -> List[str]:
    """Генерирует 4 варианта ответа (1 правильный + 3 случайных)"""
    correct_answer = correct_question['date']

    wrong_answers = list(set([q['date'] for q in all_questions if q['date'] != correct_answer]))

    selected_wrong = random.sample(wrong_answers, min(3, len(wrong_answers)))

    all_answers = [correct_answer] + selected_wrong
    random.shuffle(all_answers)

    return all_answers

