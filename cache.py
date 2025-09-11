import json
import os

# Глобальная переменная для кэша
CACHE_FILE = os.path.join(os.path.expanduser("~"), ".code-security", "cache.json")


def load_cache(file_path=CACHE_FILE):
    """Инициализирует кэш из файла"""
    cache = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except:
            pass

    return cache



def save_cache(content, file_path=CACHE_FILE):
    """Сохраняет кэш в файл"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    except:
        pass