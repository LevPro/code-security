import fnmatch
import os


def should_exclude(path, exclude_dirs, exclude_files, exclude_patterns):
    """Проверяет, нужно ли исключить путь"""
    # Проверка точных совпадений директорий
    if any(os.path.abspath(path) == os.path.abspath(ex_dir) for ex_dir in exclude_dirs):
        return True

    # Проверка точных совпадений файлов
    if any(os.path.abspath(path) == os.path.abspath(ex_file) for ex_file in exclude_files):
        return True

    # Проверка по паттернам
    filename = os.path.basename(path)
    if any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns):
        return True

    return False


def file_collector(directory, extensions=None, exclude_dirs=None, exclude_files=None, exclude_patterns=None):
    if not os.path.exists(directory):
        raise ValueError(f"{directory} не найден")

    if extensions is None:
        extensions = ['php']

    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    if exclude_patterns is None:
        exclude_patterns = []

    files = []

    for root, dirs, filenames in os.walk(directory):
        # Исключаем директории из дальнейшего обхода
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_dirs, [], exclude_patterns)]

        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, filename)

                if should_exclude(file_path, [], exclude_files, exclude_patterns):
                    print(f"Исключен файл: {file_path}")
                    continue

                print(f"Добавлен файл: {file_path}")
                files.append(file_path)

    return files