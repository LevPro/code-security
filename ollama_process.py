import time
import re
import requests
import hashlib

from functools import lru_cache
from cache import load_cache, save_cache


def _strip_code_fences(text: str) -> str:
    """Убирает внешние тройные бэктики ```...``` и возможный язык после них, не трогая содержимое.
    Работает построчно: если первая строка начинается с ``` — убираем её; если последняя строка — тоже ``` — убираем.
    Ничего не удаляем внутри тела.
    """
    if not text:
        return text
    lines = text.splitlines()
    # trim leading/trailing empty lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    if not lines:
        return ""

    first = lines[0].strip()
    last = lines[-1].strip()

    if first.startswith("```"):
        # убрать первую строку (может быть ``` или ```php)
        lines = lines[1:]
        # убрать возможные пустые строки в начале
        while lines and lines[0].strip() == "":
            lines.pop(0)
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    elif last.startswith("```"):
        # только закрывающая — убираем её
        lines = lines[:-1]

    text = "\n".join(lines)

    # Заменяем множественные переносы строк
    text = re.sub(r'\n{2,}', '\n', text)
    # Удаляем переносы в конце файла
    text = re.sub(r'\n+$', '\n', text)

    return text


@lru_cache(maxsize=1000)
def _generate_prompt_hash(file_content, requirements):
    """Генерирует хэш для кэширования промптов"""
    content = f"{file_content}_{'_'.join(requirements)}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def ollama_process(file_content, model, requirements):
    # Генерируем хэш для кэширования
    content_hash = _generate_prompt_hash(file_content, tuple(requirements))

    # Проверяем, есть ли результат в кэше
    cache = load_cache()

    if content_hash in cache:
        cached_result = cache[content_hash]
        return {
            "processing_time": cached_result["processing_time"],
            "result": cached_result["result"]
        }
    # Добавляем дополнительные требования
    requirements_info = ""
    if len(requirements) > 0:
        start_num = 21
        for requirement in requirements:
            requirements_info = requirements_info + f"{start_num}. {requirement}\n"
            start_num += 1

    # Упрощенный промпт для ускорения обработки
    prompt = f"""Проанализируй предоставленный код на потенциальные уязвимости безопасности, включая:
        1. Инъекции (SQL, NoSQL, командные, LDAP)
        2. Межсайтовый скриптинг (XSS) - хранимый, отраженный, DOM-based
        3. Подделка межсайтовых запросов (CSRF)
        4. Небезопасные десериализации
        5. Использование компонентов с известными уязвимостями
        6. Недостатки логирования и мониторинга
        7. Неправильные настройки безопасности
        8. Раскрытие конфиденциальных данных
        9. Недостатки контроля доступа (вертикальный/горизонтальный)
        10. Некорректная аутентификация и управление сессиями
        11. Ошибки конфигурации безопасности
        12. Защита от атак перебора
        13. Небезопасная работа с памятью (переполнение буфера, use-after-free)
        14. Некорректная валидация входных данных и санитизация
        15. Проблемы с криптографией (слабые алгоритмы, неправильное использование)
        16. Ошибки конкурентного доступа (race conditions)
        17. Небезопасные прямые ссылки на объекты (IDOR)
        18. SSRF (Server-Side Request Forgery)
        19. XXE (XML External Entity)
        20. Path traversal и file inclusion
        {requirements_info}
        
        После анализа внеси необходимые исправления для устранения найденных уязвимостей. 

        ВАЖНО: Верни только исправленную версию полного кода без каких-либо комментариев, объяснений или дополнительного текста. Исходная структура и функциональность кода должны быть сохранены.

        Код для анализа и исправления:
        {file_content}"""

    # Начало отсчета времени
    start_time = time.time()

    # Указываем корректный URL для локального сервера Ollama
    url = 'http://localhost:11434/api/generate'
    headers = {'Content-Type': 'application/json'}

    # Формируем тело запроса с указанием модели и промта
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=600)
        response.raise_for_status()

        # Извлекаем результат из поля 'response' в JSON
        result = response.json()
        result = result['response']

        # Окончание отсчета времени
        end_time = time.time()
        processing_time = end_time - start_time

        # Сохраняем результат в кэш
        cache[content_hash] = {
            "processing_time": processing_time,
            "result": result
        }

        save_cache(cache)

        return {
            "processing_time": processing_time,
            "result": result
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")