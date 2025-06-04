import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from processing.table_processing import TableProcessor

@pytest.fixture
def table_processor():
    return TableProcessor()

def test_filter_data(table_processor):
    # Тест фильтрации данных
    data = pd.DataFrame({
        "Заказ": ["123", "456", "789"],
        "Клиент": ["Клиент А", "Клиент Б", "Клиент А"]
    }).to_dict("records")
    filtered_data = table_processor.filter_data(data, "Клиент А")
    assert len(filtered_data) == 2
    assert all(row["Клиент"] == "Клиент А" for row in filtered_data)

def test_create_shift(table_processor):
    # Тест создания новой смены
    shift_store = []
    turn_store = []
    new_shift_store, new_turn_store, message = table_processor.create_shift(shift_store, turn_store)
    assert len(new_shift_store) == 1
    assert new_shift_store[0]["shift_id"] == 1000
    assert len(new_turn_store) == 1
    assert new_turn_store[0]["shift_id"] == 1000
    assert new_turn_store[0]["rows"] == []
    assert message == "Создана смена 1000."