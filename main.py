from __future__ import annotations

import json
from pathlib import Path

from skills.customs_skill import customs_checklist


BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "memory"
SESSION_MEMORY_FILE = MEMORY_DIR / "session_memory.json"
LONG_TERM_MEMORY_FILE = MEMORY_DIR / "long_term_memory.json"


def ensure_memory_files() -> None:
    MEMORY_DIR.mkdir(exist_ok=True)
    for file_path in (SESSION_MEMORY_FILE, LONG_TERM_MEMORY_FILE):
        if not file_path.exists():
            write_memory(file_path, [])


def read_memory(file_path: Path) -> list[str]:
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [str(item) for item in data]


def write_memory(file_path: Path, facts: list[str]) -> None:
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(facts, file, ensure_ascii=False, indent=2)


def remember_fact(fact: str) -> str:
    fact = fact.strip()
    if not fact:
        return "Укажите факт после команды /remember."

    session_memory = read_memory(SESSION_MEMORY_FILE)
    session_memory.append(fact)
    write_memory(SESSION_MEMORY_FILE, session_memory)
    return "Факт сохранен в сессионную память."


def format_memory(title: str, facts: list[str]) -> str:
    if not facts:
        return f"{title} пуста."

    lines = [f"{title}:"]
    lines.extend(f"{index}. {fact}" for index, fact in enumerate(facts, start=1))
    return "\n".join(lines)


def transfer_session_to_long_term() -> str:
    # Шаг 1: явно читаем временные факты текущей сессии.
    session_memory = read_memory(SESSION_MEMORY_FILE)
    if not session_memory:
        return "Сессионная память пуста. Переносить нечего."

    # Шаг 2: явно добавляем их в долгосрочную память.
    long_term_memory = read_memory(LONG_TERM_MEMORY_FILE)
    long_term_memory.extend(session_memory)
    write_memory(LONG_TERM_MEMORY_FILE, long_term_memory)

    # Шаг 3: явно очищаем сессионную память после переноса.
    write_memory(SESSION_MEMORY_FILE, [])

    return (
        f"Перенесено фактов: {len(session_memory)}\n"
        "Сессионная память очищена."
    )


def help_text() -> str:
    return "\n".join(
        [
            "Доступные команды:",
            "/remember <факт>  добавить факт в сессионную память",
            "/session          показать сессионную память",
            "/transfer         перенести сессионную память в долгосрочную",
            "/longterm         показать долгосрочную память",
            "/skill            запустить локальный скилл customs_checklist",
            "/help             показать справку",
            "/exit             выйти из агента",
        ]
    )


def handle_command(user_input: str) -> str:
    command, _, argument = user_input.partition(" ")

    if command == "/remember":
        return remember_fact(argument)
    if command == "/session":
        return format_memory("Сессионная память", read_memory(SESSION_MEMORY_FILE))
    if command == "/transfer":
        return transfer_session_to_long_term()
    if command == "/longterm":
        return format_memory("Долгосрочная память", read_memory(LONG_TERM_MEMORY_FILE))
    if command == "/skill":
        return customs_checklist()
    if command == "/help":
        return help_text()
    if command == "/exit":
        return "Работа агента завершена."

    return "Неизвестная команда. Введите /help для списка команд."


def main() -> None:
    ensure_memory_files()
    print("Агент с памятью запущен. Введите /help для списка команд.")

    while True:
        user_input = input("\n> ").strip()
        if not user_input:
            continue

        response = handle_command(user_input)
        print(response)

        if user_input == "/exit":
            break


if __name__ == "__main__":
    main()
