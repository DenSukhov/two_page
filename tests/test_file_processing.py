import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from processing.file_processing import FileProcessor

@pytest.fixture
def file_processor():
    return FileProcessor()

def test_load_excel_file_invalid_format(file_processor):
    # Тест обработки неверного формата файла
    invalid_content = "not an excel file"
    # Проверяем, что метод возвращает кортеж с None и сообщением об ошибке
    result, message = file_processor.load_excel_file(invalid_content, "test.txt")
    assert result is None
    assert message == "Загрузка файла: not enough values to unpack (expected 2, got 1)"