import re
import json
import requests


def _extract_json_from_string(text):
    # Паттерн для поиска JSON-массива, начинающегося с [{ и заканчивающегося }]
    pattern = r"\[\s*\{.*?\}\s*\]"
    matches = re.findall(pattern, text, re.DOTALL)

    for match in matches:
        try:
            # Пытаемся распарсить найденную строку как JSON
            data = json.loads(match)
            # Проверяем, что это список словарей с нужными полями
            if isinstance(data, list) and all(
                isinstance(item, dict)
                and {"file", "text", "changes"}.issubset(item.keys())
                for item in data
            ):
                return data
        except json.JSONDecodeError:
            continue  # Если парсинг не удался, пробуем следующий match
    return None  # Если ничего не найдено


def ollama_process(files_content, model):
    files_info = ""

    for file in files_content:
        files_info += f"""{file['file_path']}:
        {file['content']}

        """

    # Промт для обработки
    prompt = f"""Analyze the code of these files:
    {files_info}

    Find the following potential vulnerabilities:
    1. Injections (SQL, NoSQL, command, LDAP)
    2. Cross-site scripting (XSS) - stored, reflected, DOM-based
    3. Cross-site request forgery (CSRF)
    4. Insecure deserialization
    5. Use of components with known vulnerabilities
    6. Deficiencies in logging and monitoring
    7. Incorrect security settings
    8. Disclosure of sensitive data
    9. Access control flaws (vertical/horizontal)
    10. Incorrect authentication and session management
    11. Security configuration errors
    12. Protection against brute force attacks
    13. Insecure memory handling (buffer overflow, use-after-free)
    14. Incorrect input data validation and sanitization
    15. Cryptography issues (weak algorithms, improper usage)
    16. Competitive access errors (race conditions)
    17. Insecure Direct Object References (IDOR)
    18. SSRF (Server-Side Request Forgery)
    19. XXE (XML External Entity)
    20. Path traversal and file inclusion

    Fix the discovered vulnerabilities.

    The response must be only a valid JSON array. Use the following schema as the exact format. The "text" field must be the complete, corrected code for the file.
    
    JSON schema for the response::
    """
    prompt += '[{"file": "/path/to/example.py", "text": "def safe_function(): # This is the full corrected code ...", "changes": "Fixed SQL injection by using parameterized queries."}]'

    print(f"Отправка запроса {prompt}")

    # Указываем корректный URL для локального сервера Ollama
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    # Формируем тело запроса с указанием модели и промта
    data = {"model": model, "prompt": prompt, "stream": False}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=3600)
        response.raise_for_status()

        # Извлекаем результат из поля 'response' в JSON
        result = response.json()
        result = result["response"]

        print(f"Получен ответ {result}")

        result = _extract_json_from_string(result)

        return result

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")
