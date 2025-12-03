import random
from typing import Dict, List



class TestManager:
    def __init__(self):
        self.questions: List[Dict] = []
        self.current_index: int = 0
        self.score: int = 0
        self.total_questions: int = 0

    async def start_new_test(self, questions_count: int = 5):
        from handles import get_events_name_date
        """Начинает новый тест с указанным количеством вопросов"""
        all_questions = await get_events_name_date()
        random.shuffle(all_questions)
        self.questions = all_questions[:questions_count]
        self.current_index = 0
        self.score = 0
        self.total_questions = len(self.questions)
        return self.questions

    def get_current_question(self) -> Dict:
        """Возвращает текущий вопрос"""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def check_answer(self, answer: str) -> bool:
        """Проверяет ответ и возвращает True если правильный"""
        current_question = self.get_current_question()
        if current_question and answer == current_question['date']:
            self.score += 1
            return True
        return False

    def next_question(self) -> bool:
        """Переходит к следующему вопросу, возвращает False если вопросы закончились"""
        self.current_index += 1
        return self.current_index < len(self.questions)

    def get_progress(self) -> str:
        """Возвращает строку прогресса"""
        return f"{self.current_index + 1}/{self.total_questions}"

    def get_results(self) -> Dict:
        """Возвращает результаты теста"""
        return {
            'score': self.score,
            'total': self.total_questions,
            'percentage': (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        }

    def is_test_finished(self) -> bool:
        """Проверяет, завершен ли тест"""
        return self.current_index >= len(self.questions)
