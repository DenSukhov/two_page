import pandas as pd
from typing import List, Dict, Tuple
from config import logger, next_shift_id

class TableProcessor:
    @staticmethod
    def filter_data(data: List[Dict], search_value: str) -> List[Dict]:
        """
        Фильтрует данные по строке поиска.

        Args:
            data: Список словарей с данными таблицы.
            search_value: Строка для поиска.

        Returns:
            Отфильтрованный список словарей.
        """
        logger.info(f"Выполняется поиск с запросом: {search_value}")
        if not search_value:
            logger.info("Поиск сброшен, возвращены исходные данные.")
            return data
        df = pd.DataFrame(data)
        mask = df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)
        filtered_data = df[mask].to_dict("records")
        logger.info(f"Найдено {len(filtered_data)} строк по запросу.")
        return filtered_data

    @staticmethod
    def transfer_rows(data_store: List[Dict], turn_store: List[Dict], grid_selected_rows: List[Dict], shift_id: int) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Переносит выбранные строки из data_store в turn_store для указанной смены.

        Args:
            data_store: Данные основной таблицы.
            turn_store: Данные таблицы Turn.
            grid_selected_rows: Выбранные строки из основной таблицы.
            shift_id: ID смены.

        Returns:
            Кортеж (новый data_store, новый turn_store, обновлённые строки для turn-grid).
        """
        logger.info("Перенос строк в таблицу Turn.")
        selected_row_ids = {row["row_id"] for row in grid_selected_rows}
        new_data_store = [row for row in data_store if row["row_id"] not in selected_row_ids]
        new_turn_store = turn_store.copy()
        updated_rows = []
        for shift in new_turn_store:
            if shift["shift_id"] == shift_id:
                shift["rows"] = shift["rows"] + grid_selected_rows
                updated_rows = shift["rows"]
                break
        logger.info(f"Перенесено {len(grid_selected_rows)} строк в смену {shift_id}.")
        return new_data_store, new_turn_store, updated_rows

    @staticmethod
    def update_shift(shift_store: List[Dict], cell_changed: Dict) -> Tuple[List[Dict], str]:
        """
        Обновляет данные смены при изменении ячейки в shift-grid.

        Args:
            shift_store: Данные таблицы смен.
            cell_changed: Данные об изменённой ячейке.

        Returns:
            Кортеж (новый shift_store, сообщение).
        """
        logger.info("Изменено значение в shift-grid.")
        logger.debug(f"cell_changed raw: {cell_changed}")
        if not cell_changed:
            logger.warning("Данные cell_changed отсутствуют.")
            return shift_store, "Данные об изменении отсутствуют."

        cell_data = cell_changed[0] if isinstance(cell_changed, list) else cell_changed

        try:
            shift_id = cell_data["rowId"]
            field = cell_data["colId"]
            new_value = cell_data.get("newValue", cell_data.get("value", ""))
        except (KeyError, TypeError) as e:
            logger.error(f"Ошибка обработки cell_changed: {e}, cell_changed: {cell_changed}")
            return shift_store, f"Ошибка при обновлении смены: неверный формат данных."

        new_shift_store = shift_store.copy()
        for shift in new_shift_store:
            if str(shift["shift_id"]) == str(shift_id):
                shift[field] = new_value
                logger.info(f"Обновлено поле {field} для смены {shift_id}.")
                logger.debug(f"new_shift_store after update: {new_shift_store}")
                return new_shift_store, f"Обновлена смена {shift_id}."
        
        logger.warning(f"Смена с shift_id={shift_id} не найдена в shift_store.")
        return shift_store, f"Смена {shift_id} не найдена."

    @staticmethod
    def create_shift(shift_store: List[Dict], turn_store: List[Dict]) -> Tuple[List[Dict], List[Dict], str]:
        """
        Создаёт новую смену и обновляет shift_store и turn_store.

        Args:
            shift_store: Данные таблицы смен.
            turn_store: Данные таблицы Turn.

        Returns:
            Кортеж (новый shift_store, новый turn_store, сообщение).
        """
        logger.info("Создание новой смены.")
        logger.debug(f"shift_store before adding: {shift_store}")

        current_max_id = max([shift["shift_id"] for shift in shift_store], default=next_shift_id-1) if shift_store else next_shift_id-1
        new_shift_id = current_max_id + 1

        new_shift = {
            "shift_id": new_shift_id,
            "max_ts": 38,
            "col_pal": 0.0,
            "col_kg": 0.00,
            "head": "",
            "trailer": "",
            "comments": ""
        }

        new_shift_store = shift_store + [new_shift]
        new_turn_store = turn_store + [{"shift_id": new_shift_id, "rows": []}]

        logger.info(f"Создана новая смена с shift_id={new_shift_id}.")
        logger.debug(f"new_shift: {new_shift}")
        logger.debug(f"shift_store after adding: {new_shift_store}")
        return new_shift_store, new_turn_store, f"Создана смена {new_shift_id}."