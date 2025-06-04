import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

# Заглушка для тестов callback'ов (будет расширена)
def test_callbacks_placeholder():
    assert True