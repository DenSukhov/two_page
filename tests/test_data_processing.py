import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from data_processing import DataProcessor

@pytest.fixture
def data_processor():
    return DataProcessor()

def test_load_excel_file_invalid_format(data_processor):
    # Тест обработки неверного формата файла
    invalid_content = "not an excel file"
    # Проверяем, что метод возвращает кортеж с None и сообщением об ошибке
    result, message = data_processor.load_excel_file(invalid_content, "test.txt")
    assert result is None
    assert message == "Загрузка файла: not enough values to unpack (expected 2, got 1)"

def test_filter_data(data_processor):
    # Тест фильтрации данных
    data = pd.DataFrame({
        "Заказ": ["123", "456", "789"],
        "Клиент": ["Клиент А", "Клиент Б", "Клиент А"]
    })
    filtered_data = data_processor.filter_data(data, "Клиент А")
    if isinstance(filtered_data, list):
        filtered_data = pd.DataFrame(filtered_data)
    assert len(filtered_data) == 2
    assert all(filtered_data["Клиент"] == "Клиент А")

def test_create_shift(data_processor):
    # Тест создания новой смены
    shift_store = []
    turn_store = []
    new_shift_store, new_turn_store, message = data_processor.create_shift(shift_store, turn_store)
    assert len(new_shift_store) == 1
    assert new_shift_store[0]["shift_id"] == 1000
    assert len(new_turn_store) == 1
    assert new_turn_store[0]["shift_id"] == 1000
    assert new_turn_store[0]["rows"] == []
    assert message == "Создана смена 1000."