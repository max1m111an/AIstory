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



def getTrainingOptionalMenu(option: str) -> str:
    return (f"""
Вы выбрали режим {option}
    
Какой тип вы хотите?
    """)


def getStartTestMenu(diff="Любая", era="Любая"):
    return (f"""
Выбрана сложность: {diff}
Выбрана эпоха: {era}
Начнём?                                                                                                                                                                                                                                                                                                                              
    """)


def getDifficultyMenu():
    return (
        """
Какую сложность вы хотите?
        """
    )
