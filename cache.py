import json
import os

# Глобальная переменная для кэша
CACHE_FILE = os.path.join(os.path.expanduser("~"), ".code-security", "cache.json")


def load_cache():
    """Инициализирует кэш из файла"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except:
            pass

    return cache



def save_cache(content):
    """Сохраняет кэш в файл"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    except:
        pass