def getMainMenu(status="start"):
    if status == "start":
        startText = "Привет! Я — Aistory 👋"
    else:
        startText = "Ты вернулся в главное меню!"

    return (f"""
{startText}  

🎯 Тренируй даты и хронологию
⚡️ Делай интенсив  
🏃 Проходи Марафон  
🔥 Держи стрик  
📊 Смотри статистику

Готов начать?
    """)

def getTrainingMenu():
    return ("""
Вы выбрали режим тренировки 🎯
    
Какой тип вы хотите?
    """)


def getStartTestMenu(diff="Любая", era="Любая"):
    return (f"""
Выбрана сложность: {diff}
Выбрана эпоха: {era}
Начнём?                                                                                                                                                                                                                                                                                                                              
    """)

def getEventDateMenu(answered_quests, total_quests, cur_quest):
    return (f"📝 Вопрос {len(answered_quests) + 1}/{total_quests}\n\n"
            f"Событие: {cur_quest['name']}\n\n"
            f"Выберите правильную дату:"
    )

def getDifficultyMenu():
    return (
        """
Какую сложность вы хотите?
        """
    )
