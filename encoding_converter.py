import os
import re
import chardet
import concurrent.futures


def convert_file_to_utf8(file_path):
    """Конвертирует файл в UTF-8, если он в другой кодировке"""
    try:
        # Читаем файл в бинарном режиме для определения кодировки
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # Определяем кодировку
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']

        # Пропускаем бинарные файлы и файлы с низкой уверенностью определения
        if encoding is None or confidence < 0.5:
            print(f"Не удалось определить кодировку для {file_path} (уверенность: {confidence})")
            return False

        # Если файл уже в UTF-8, пропускаем
        if encoding.lower() == 'utf-8':
            return False

        # Декодируем и перекодируем в UTF-8
        try:
            text = raw_data.decode(encoding)
            # Заменяем множественные переносы строк
            text = re.sub(r'\n{2,}', '\n', text)
            # Удаляем переносы в конце файла
            text = re.sub(r'\n+$', '\n', text)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Конвертирован {file_path} из {encoding} в UTF-8")
            return True
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            print(f"Ошибка перекодировки {file_path}: {e}")
            return False

    except Exception as e:
        print(f"Ошибка обработки файла {file_path}: {e}")
        return False


def convert_dir_to_utf8(directory, extensions=None):
    """Рекурсивно конвертирует файлы в директории в UTF-8"""
    if extensions is None:
        extensions = ['.php', '.html', '.css', '.js', '.txt', '.json', '.xml', '.md', '.py']

    converted_count = 0
    files_to_convert = []

    # Сначала собираем все файлы для конвертации
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                files_to_convert.append(file_path)

    # Многопоточная конвертация файлов
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(convert_file_to_utf8, files_to_convert)
        converted_count = sum(results)

    print(f"Конвертировано файлов: {converted_count}")