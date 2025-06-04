import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from processing.map_processing import MapProcessor

@pytest.fixture
def map_processor():
    return MapProcessor()

def test_prepare_map_data_empty(map_processor):
    # Тест подготовки данных для пустого набора
    data = []
    result = map_processor.prepare_map_data(data)
    assert result.empty
    assert list(result.columns) == ['contact_code', 'Широта', 'Долгота', 'Адрес', 'Населённый_пункт', 'Тип_ТС', 'Заказ', 'Товар', 'Пал', 'КГ']