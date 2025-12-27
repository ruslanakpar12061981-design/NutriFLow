import telebot
from telebot import types
import json
import time
from datetime import datetime
import random


TOKEN = "тимофейлох"
WEBAPP_URL = "https://admirable-centaur-9e4378.netlify.app/"

bot = telebot.TeleBot(TOKEN)
users_data = {}


def data_read():
    global users_data
    try:
        with open("Proekt.json", "r", encoding="utf8") as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users_data = {}


def data_write():
    with open("Proekt.json", "w", encoding="utf8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)


data_read()


def get_user_info(chat_id: str):
    raw = users_data.get(chat_id)
    if raw is None:
        return {"history": [], "goal": None, "calories": None}

    if isinstance(raw, dict) and ("history" in raw or "goal" in raw or "calories" in raw):
        return {
            "history": raw.get("history", []),
            "goal": raw.get("goal"),
            "calories": raw.get("calories"),
        }

    if isinstance(raw, list):
        return {"history": raw, "goal": None, "calories": None}

    if isinstance(raw, dict) and "ves" in raw:
        try:
            old_val = float(raw["ves"])
            history = [{"date": "старый формат", "ves": old_val}]
        except Exception:
            history = []
        return {"history": history, "goal": None, "calories": None}

    return {"history": [], "goal": None, "calories": None}


def what_to_eat_now():
    hour = datetime.now().hour

    breakfasts = [
        "🍳 Завтрак\n• Овсянка + ягоды\n• Яйцо / омлет\n• Чай или кофе без сахара",
        "🥣 Завтрак\n• Творог или йогурт\n• Фрукты\n• Орехи немного",
        "🥪 Завтрак\n• Цельнозерновой хлеб\n• Яйцо / авокадо\n• Овощи",
        "🍌 Завтрак\n• Каша\n• Банан или яблоко\n• Йогурт",
        "🫐 Завтрак\n• Гречка\n• Яйцо\n• Овощи или ягоды",
        "🥞 Завтрак\n• Сырники (нежирные)\n• Йогурт\n• Фрукты"
    ]

    lunches = [
        "🍛 Обед\n• Курица / рыба\n• Рис или гречка\n• Салат",
        "🥗 Обед\n• Суп\n• Кусочек хлеба\n• Овощи",
        "🍝 Обед\n• Паста из цельнозерна\n• Овощи\n• Белок (курица/тунец)",
        "🥘 Обед\n• Тушёные овощи\n• Индейка / говядина",
        "🍲 Обед\n• Чечевица/фасоль\n• Овощи\n• Салат",
        "🥔 Обед\n• Картофель запечённый\n• Рыба\n• Овощи"
    ]

    dinners = [
        "🍲 Ужин\n• Рыба или курица\n• Овощи",
        "🥚 Ужин\n• Омлет с овощами\n• Салат",
        "🥗 Ужин\n• Творог / йогурт\n• Ягоды",
        "🍆 Ужин\n• Запечённые овощи\n• Нежирный белок",
        "🥒 Ужин\n• Салат + курица\n• Чай/вода",
        "🍤 Ужин\n• Морепродукты\n• Овощи\n• Лимон/зелень"
    ]

    late = [
        "🌙 Поздно\n• Кефир или йогурт\n• Тёплый чай",
        "🌙 Поздно\n• Немного творога\n• Вода",
        "🌙 Поздно\n• Травяной чай\n• Яблоко (если очень голодно)",
        "🌙 Поздно\n• Вода\n• Чай\n• Лучше лечь спать пораньше 🙂"
    ]

    if 5 <= hour < 11:
        return random.choice(breakfasts)
    elif 11 <= hour < 17:
        return random.choice(lunches)
    elif 17 <= hour < 22:
        return random.choice(dinners)
    else:
        return random.choice(late)


def button_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    btn1 = types.KeyboardButton("Зарегистрировать новый вес")
    btn2 = types.KeyboardButton("Мой вес сейчас ⚖️")
    btn3 = types.KeyboardButton("История веса 🗓️")
    btn4 = types.KeyboardButton("Моя цель 🎯")

    btn9 = types.KeyboardButton("Что съесть сейчас 🍽️")

    btn5 = types.KeyboardButton("Калькулятор калорий за день")
    btn6 = types.KeyboardButton("Сбросить счётчик калорий 🔄")

    web_app_info = types.WebAppInfo(url=WEBAPP_URL)
    btn7 = types.KeyboardButton("Трекер привычек 📲", web_app=web_app_info)

    btn8 = types.KeyboardButton("О этом боте")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn9)
    markup.add(btn5, btn6)
    markup.add(btn7, btn8)
    return markup


def ves(message):
    chat_id = str(message.chat.id)
    text = (message.text or "").strip()

    try:
        new_ves = float(text.replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Введите число (например: 62.5).")
        bot.register_next_step_handler_by_chat_id(message.chat.id, ves)
        return

    user_info = get_user_info(chat_id)
    history = user_info["history"]
    goal = user_info["goal"]
    old_ves = history[-1]["ves"] if history else None

    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    history.append({"date": now_str, "ves": new_ves})
    user_info["history"] = history
    users_data[chat_id] = user_info
    data_write()

    if old_ves is None:
        diff_text = "Это ваша первая запись веса 📝"
    else:
        diff = round(new_ves - old_ves, 1)
        if diff > 0:
            diff_text = f"Вы поправились на {diff} кг 🍰"
        elif diff < 0:
            diff_text = f"Вы похудели на {abs(diff)} кг 💪"
        else:
            diff_text = "Ваш вес не изменился ⚖️"

    if goal is not None:
        diff_goal = round(new_ves - goal, 1)
        if diff_goal > 0:
            goal_text = f"До цели нужно сбросить {abs(diff_goal)} кг 🎯"
        elif diff_goal < 0:
            goal_text = f"Вы уже легче цели на {abs(diff_goal)} кг! 🔥"
        else:
            goal_text = "Вы достигли своей цели! 🎉"
    else:
        goal_text = "Цель пока не установлена. Нажмите «Моя цель 🎯»."

    bot.send_message(
        message.chat.id,
        f"✅ Вес сохранён!\n"
        f"📅 {now_str}\n"
        f"📈 Текущий: {new_ves} кг\n\n"
        f"{diff_text}\n\n{goal_text}",
    )


def set_goal(message):
    chat_id = str(message.chat.id)
    text = (message.text or "").strip()
    try:
        goal_weight = float(text.replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Введите число (например: 60.0).")
        bot.register_next_step_handler_by_chat_id(message.chat.id, set_goal)
        return

    user_info = get_user_info(chat_id)
    user_info["goal"] = goal_weight
    users_data[chat_id] = user_info
    data_write()

    bot.send_message(
        message.chat.id,
        f"🎯 Цель установлена: {goal_weight} кг.\nТеперь бот будет отслеживать прогресс!",
    )


def start_calories(message):
    chat_id = str(message.chat.id)
    user_info = get_user_info(chat_id)
    today = datetime.now().strftime("%Y-%m-%d")
    calories = user_info.get("calories")

    if not isinstance(calories, dict) or calories.get("date") != today:
        calories = {"date": today, "total": 0.0}
        bot.send_message(
            message.chat.id,
            "🍽️ Калькулятор калорий запущен.\n"
            "Отправляйте количество калорий, например: 250\n"
            "Чтобы увидеть итог — напишите «итог».\n"
            "Каждый день счётчик обнуляется.",
        )
    else:
        bot.send_message(
            message.chat.id,
            f"Сегодня вы уже набрали {calories['total']} ккал.\n"
            "Можете добавить ещё или написать «итог».",
        )

    user_info["calories"] = calories
    users_data[chat_id] = user_info
    data_write()
    bot.register_next_step_handler_by_chat_id(message.chat.id, calories_input)


def calories_input(message):
    chat_id = str(message.chat.id)
    text = (message.text or "").strip().lower()
    user_info = get_user_info(chat_id)
    today = datetime.now().strftime("%Y-%m-%d")
    calories = user_info.get("calories")

    if not isinstance(calories, dict) or calories.get("date") != today:
        calories = {"date": today, "total": 0.0}

    if text in ["итог", "готово", "все", "всё", "стоп"]:
        total = calories.get("total", 0.0)
        bot.send_message(
            message.chat.id,
            f"🍽️ За сегодня вы набрали {total} ккал.\nЗавтра счётчик начнёт с нуля.",
        )
        user_info["calories"] = calories
        users_data[chat_id] = user_info
        data_write()
        return

    try:
        add_cals = float(text.replace(",", "."))
        calories["total"] = round(calories.get("total", 0.0) + add_cals, 1)
        user_info["calories"] = calories
        users_data[chat_id] = user_info
        data_write()

        bot.send_message(
            message.chat.id,
            f"✅ Добавлено {add_cals} ккал.\n"
            f"Всего сегодня: {calories['total']} ккал.\n"
            f"Введите следующее значение или напишите «итог».",
        )
        bot.register_next_step_handler_by_chat_id(message.chat.id, calories_input)
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Введите число калорий или слово «итог».")
        bot.register_next_step_handler_by_chat_id(message.chat.id, calories_input)


def reset_calories(chat_id):
    user_info = get_user_info(str(chat_id))
    today = datetime.now().strftime("%Y-%m-%d")
    user_info["calories"] = {"date": today, "total": 0.0}
    users_data[str(chat_id)] = user_info
    data_write()
    bot.send_message(
        chat_id,
        "🔄 Счётчик калорий сброшен!\nНачните новый день с чистого листа 🍏",
    )


@bot.message_handler(commands=["start"])
def handle_start(message):
    name = message.from_user.first_name or ""
    bot.send_message(message.chat.id, f"Здравствуйте, {name}!")
    menu = button_menu()
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в Nutri Flow — ваш помощник по весу, целям и калориям 💪",
        reply_markup=menu,
    )


@bot.message_handler(func=lambda message: True)
def handle_all(message):
    chat_id = message.chat.id
    text = (message.text or "").strip().lower()
    chat_id_str = str(chat_id)

    if text == "зарегистрировать новый вес":
        bot.send_message(chat_id, "Введите свой текущий вес (например: 62.5).")
        bot.register_next_step_handler_by_chat_id(chat_id, ves)

    elif text == "мой вес сейчас ⚖️":
        user_info = get_user_info(chat_id_str)
        history = user_info["history"]
        if not history:
            bot.send_message(chat_id, "Пока нет записей. Добавьте первый вес 📋")
        else:
            last = history[-1]
            bot.send_message(chat_id, f"⚖️ Последний вес: {last['ves']} кг\n📅 {last['date']}")

    elif text == "история веса 🗓️":
        user_info = get_user_info(chat_id_str)
        history = user_info["history"]
        if not history:
            bot.send_message(chat_id, "История пуста. Добавьте вес 💪")
        else:
            lines = [f"{r['date']}: {r['ves']} кг" for r in history[-10:]]
            bot.send_message(chat_id, "🗓️ История:\n" + "\n".join(lines))

    elif text == "моя цель 🎯":
        bot.send_message(chat_id, "Введите целевой вес (например: 60.0).")
        bot.register_next_step_handler_by_chat_id(chat_id, set_goal)

    elif text == "что съесть сейчас 🍽️":
        bot.send_message(chat_id, what_to_eat_now())

    elif text == "калькулятор калорий за день":
        start_calories(message)

    elif text == "сбросить счётчик калорий 🔄":
        reset_calories(chat_id)


    elif text == "о этом боте":

        bot.send_message(

            chat_id,

            "🤖 **Nutri Flow** — простой помощник для осознанного контроля.\n\n"

            "Что умеет бот:\n"
            "• 📉 записывать и показывать вес\n"
            "• 🎯 хранить цель по весу\n"
            "• 🍽️ считать калории за день (вручную)\n"
            "• 🥗 подсказывать полезные идеи еды по времени\n"
            "• 📲 открывать мини-приложение с трекером привычек\n\n"
            "Без сложных формул и давления — только то, что удобно использовать каждый день 💚"

        )


    else:
        bot.send_message(chat_id, "Я вас не понимаю. Нажмите ➡️ /start")


while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Ошибка в боте: {e}")
        time.sleep(1)
