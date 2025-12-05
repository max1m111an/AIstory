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


def getEventDateMenu(diff="Любая", era="Любая"):
    return (f"""
Выбрана сложность: {diff}
Выбрана эпоха: {era}
Начнём?                                                                                                                                                                                                                                                                                                                              
    """)

def getStartTestMenu(event):
    return (
        f"""
Вопрос N:
Назовите дату события: 
{event}
        """
    )

def getDifficultyMenu():
    return (
        """
Какую сложность вы хотите?
        """
    )
