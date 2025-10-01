import argparse
import concurrent.futures
from functools import partial

# Импортируем функции для сбора файлов и обработки данных с использованием модели ollama
from file_collector import file_collector
from ollama_process import ollama_process
from encoding_converter import convert_dir_to_utf8


def process_single_file(file_path, model, requirements, extensions):
    """Обрабатывает один файл с использованием модели Ollama"""
    try:
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
    except Exception as e:
        print(f"Ошибка чтения файла {file_path}: {e}")
        return None

    # Обрабатываем содержимое файла с использованием указанной модели
    try:
        process_result = ollama_process(original_content, model, requirements, extensions)
    except Exception as e:
        print(f"Ошибка обработки файла {file_path}: {e}")
        return None

    # Записываем результат обратно в файл
    if process_result['result'] != '':
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(process_result['result'])

    return (file_path, process_result['processing_time'])


def main():
    # Расширения по умолчанию
    extensions = [
        # Языки общего назначения
        ".py",  # Python
        ".java",  # Java
        ".cpp", ".cc", ".cxx", ".c++",  # C++
        ".cs",  # C#
        ".rb",  # Ruby
        ".go",  # Go
        ".swift",  # Swift
        ".kotlin",  # Kotlin
        ".php",  # PHP

        # Языки скриптового программирования
        ".js",  # JavaScript (Node.js, browser)
        ".ts",  # TypeScript
        ".pl",  # Perl
        ".sh", ".bash", ".zsh",  # Shell Script (Bash, Zsh и т.д.)
        ".r",  # R (язык программирования для статистики)

        # Языки системного программирования
        ".c",  # C
        ".asm", ".s",  # Assembly

        # Функциональные языки программирования
        ".hs",  # Haskell
        ".scala",  # Scala
        ".elm",  # Elm

        # Языки для веб-разработки
        ".html",  # HTML
        ".css",  # CSS
        ".scss", ".sass",  # Sass/SCSS
        ".less",  # Less

        # Языки для мобильной разработки
        ".xml",  # XML (часто используется в Android)
        ".gradle",  # Gradle (для сборки Android-приложений)

        # Языки для игры разработки
        ".lua",  # Lua (часто используется в игровых движках)
        ".gdscript",  # GDScript (Язык скриптового программирования для Godot Engine)

        # Другие языки и специализированные форматы
        ".rkt",  # Racket (Scheme-подобный язык)
        ".dart",  # Dart (язык от Google для разработки мобильных приложений)
        ".clojure",  # Clojure
        ".clj",  # Clojure
        ".coffee",  # CoffeeScript
        ".dart",  # Dart
        ".elm",  # Elm
        ".groovy",  # Groovy (язык для JVM, совместимый с Java)
        ".scala",  # Scala (для JVM)
        ".vbs",  # Visual Basic Script
        ".bat",  # Batch Script

        # Маркапы и другие форматы
        ".json",  # JSON
        ".xml",  # XML
        ".yaml", ".yml",  # YAML
        ".md",  # Markdown
    ]

    # Создаём парсер аргументов командной строки для удобного взаимодействия с программой
    parser = argparse.ArgumentParser(description="Поиск всех файлов с указанными расширениями в заданной директории.")

    # Добавляем аргумент для пути к директории, которую будем искать
    parser.add_argument("directory", type=str, help="Путь к директории")

    # Добавляем аргумент для имени модели, которая будет использоваться для обработки файлов
    parser.add_argument("-m", "--model", type=str, required=True, help="Имя модели")

    # Добавляем возможность указать несколько расширений файлов для поиска
    parser.add_argument("-e", "--extensions", nargs="+", required=False, default=extensions, help="Список расширений файлов для поиска")

    # Добавляем возможность указать количество потоков
    parser.add_argument("-t", "--threads", type=int, required=False, default=5, help="Количество потоков")

    # Добавляем директории, которые необходимо исключить
    parser.add_argument("-ed", "--exclude-dirs", nargs="+", help="Директории для исключения", default=[])

    # Добавляем файлы, которые необходимо исключить
    parser.add_argument("-ef", "--exclude-files", nargs="+", help="Файлы для исключения", default=[])

    # Добавляем паттерны, которые необходимо исключить
    parser.add_argument("-ep", "--exclude-patterns", nargs="+", help="Патерны для исключения", default=[])

    # Добавляем дополнительные требования
    parser.add_argument("-r", "--requirements", nargs="+", help="Дополнительные требования", default=[])

    # Парсим аргументы командной строки
    args = parser.parse_args()

    # Изменяем кодировку файлов
    convert_dir_to_utf8(args.directory, args.extensions)

    # Собираем файлы с указанными расширениями в директории
    files = file_collector(args.directory, args.extensions, exclude_dirs=args.exclude_dirs, exclude_files=args.exclude_files, exclude_patterns=args.exclude_patterns)

    # Создаем частичную функцию для обработки файлов
    process_func = partial(process_single_file, model=args.model, requirements=args.requirements, extensions=args.extensions)

    # Многопоточная обработка файлов
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Отправляем все файлы на обработку
        future_to_file = {executor.submit(process_func, file_path): file_path for file_path in files}

        # Обрабатываем результаты по мере их завершения
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    print(f"Обновлён файл: {result[0]}. Время обработки файла: {result[1]:.2f} сек")
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")


# Если скрипт запущен как основная программа, вызываем функцию main()
if __name__ == "__main__":
    main()