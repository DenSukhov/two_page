import pandas as pd
import base64
import io
from typing import Tuple, List, Dict, Optional
from config import logger, next_shift_id, EMOJI_MAPPING, ICON_CONFIG
from error_handler import ErrorHandler
import dash_leaflet as dl
from dash import html
import json

class DataProcessor:
    @staticmethod
    def load_excel_file(contents: str, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Загружает и обрабатывает Excel-файл.

        Args:
            contents: Содержимое файла в формате base64.
            filename: Имя файла.

        Returns:
            Кортеж (DataFrame, ошибка). Если ошибка, DataFrame=None.
        """
        try:
            logger.info(f"Попытка загрузки файла: {filename}")
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            if filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
            elif filename.endswith('.xls'):
                df = pd.read_excel(io.BytesIO(decoded), engine='xlrd')
            else:
                error = "Неподдерживаемый формат файла. Используйте .xlsx или .xls."
                logger.error(error)
                return None, error

            df['row_id'] = range(len(df))
            return ErrorHandler.validate_excel_file(df, filename)
        except Exception as e:
            return None, ErrorHandler.handle_exception(e, "Загрузка файла")

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

    @staticmethod
    def prepare_map_data(table_row_data):
        """
        Формирует данные для карты из данных таблицы order-grid.
        
        Args:
            table_row_data: Список словарей с данными таблицы.
        
        Returns:
            pandas.DataFrame с сгруппированными данными для карты.
        """
        required_columns = ['contact_code', 'Широта', 'Долгота', 'Адрес', 'Населённый_пункт', 'Тип_ТС', 'Заказ', 'Товар', 'Пал', 'КГ']
        try:
            logger.debug(f"Подготовка данных для карты: {len(table_row_data)} записей")
            table_df = pd.DataFrame(table_row_data)
            if table_df.empty:
                logger.info("Данные для карты пусты.")
                return pd.DataFrame(columns=required_columns)

            available_cols = table_df.columns.tolist()
            logger.debug(f"Доступные столбцы: {available_cols}")
            missing_cols = [col for col in required_columns if col not in table_df.columns]
            if missing_cols:
                logger.error(f"Отсутствуют столбцы: {missing_cols}")
                raise ValueError(f"Отсутствуют столбцы: {missing_cols}")

            grouped_data = table_df.groupby('contact_code').agg({
                'Широта': 'first',
                'Долгота': 'first',
                'Адрес': 'first',
                'Населённый_пункт': 'first',
                'Тип_ТС': 'first',
                'Заказ': list,
                'Товар': list,
                'Пал': list,
                'КГ': list
            }).reset_index()
            logger.debug(f"Сгруппировано {len(grouped_data)} записей для карты")
            return grouped_data
        except Exception as e:
            logger.error(f"Ошибка подготовки данных для карты: {str(e)}")
            raise

    @staticmethod
    def create_popup_content(row):
        """
        Создаёт содержимое всплывающего окна для маркера.
        
        Args:
            row: Строка с данными точки (из grouped_data).
        
        Returns:
            dash.html.Div с таблицей товаров.
        """
        table_rows = []
        for product, pal, kg in zip(row['Товар'], row['Пал'], row['КГ']):
            emoji = EMOJI_MAPPING.get(product.split()[-1].lower() if isinstance(product, str) else "", "")
            table_rows.append(html.Tr([html.Td(f"{emoji} {product}"), html.Td(pal), html.Td(kg)]))
        table_rows.append(html.Tr([
            html.Td("Сумма"),
            html.Td(round(sum(row['Пал']), 2)),
            html.Td(round(sum(row['КГ']), 2))
        ]))
        return html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th("Товар"), html.Th("Пал"), html.Th("КГ")])),
                html.Tbody(table_rows)
            ])
        ])

    @staticmethod
    def create_marker(row):
        """
        Создаёт маркер и подпись для точки на карте.
        
        Args:
            row: Строка с данными точки (из grouped_data).
        
        Returns:
            dash_leaflet.LayerGroup с маркером и подписью.
        """
        icon_key = row['Тип_ТС']
        popup_content = DataProcessor.create_popup_content(row)
        tooltip_text = f"{row['Населённый_пункт']}\n{row['Адрес']}"
        lat, lon = row['Широта'], row['Долгота']

        default_icon = {
            "iconUrl": "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
            "iconSize": [25, 41],
            "iconAnchor": [12.5, 41]
        }

        if icon_key == 'islands#graySportIcon':
            icon_html = (
                f'<svg width="30" height="41" viewBox="0 0 30 41" xmlns="http://www.w3.org/2000/svg">'
                f'<path d="M15 0C6.716 0 0 6.716 0 15c0 10.5 15 26 15 26s15-15.5 15-26C30 6.716 23.284 0 15 0z" fill="#808080"/>'
                f'<text x="15" y="20" font-size="12" fill="#FFFFFF" text-anchor="middle" font-family="Arial">🔗</text>'
                f'</svg>'
            )
            marker = dl.Marker(
                position=[lat, lon],
                icon={
                    "iconUrl": f"data:image/svg+xml;base64,{base64.b64encode(icon_html.encode()).decode()}",
                    "iconSize": [30, 41],
                    "iconAnchor": [15, 41]
                },
                children=[dl.Popup(popup_content)]
            )
            label_icon_anchor = [-7.5, 40]
        elif icon_key == 'islands#blueSportIcon':
            icon_html = (
                f'<svg width="30" height="41" viewBox="0 0 30 41" xmlns="http://www.w3.org/2000/svg">'
                f'<path d="M15 0C6.716 0 0 6.716 0 15c0 10.5 15 26 15 26s15-15.5 15-26C30 6.716 23.284 0 15 0z" fill="#0000FF"/>'
                f'<text x="15" y="20" font-size="12" fill="#FFFFFF" text-anchor="middle" font-family="Arial">🔗</text>'
                f'</svg>'
            )
            marker = dl.Marker(
                position=[lat, lon],
                icon={
                    "iconUrl": f"data:image/svg+xml;base64,{base64.b64encode(icon_html.encode()).decode()}",
                    "iconSize": [30, 41],
                    "iconAnchor": [15, 41]
                },
                children=[dl.Popup(popup_content)]
            )
            label_icon_anchor = [-7.5, 40]
        else:
            icon_info = ICON_CONFIG.get(icon_key, {})
            icon_url = icon_info.get('normal', default_icon['iconUrl'])
            marker = dl.Marker(
                position=[lat, lon],
                icon={
                    "iconUrl": icon_url,
                    "iconSize": [25, 41],
                    "iconAnchor": [12.5, 41]
                },
                children=[dl.Popup(popup_content)]
            )
            label_icon_anchor = [-5, 40]

        label_html = (
            f'<div style="position: relative; white-space: nowrap; display: inline-block; font-size: 10px; color: black; '
            f'background-color: white; border: 1px solid black; border-radius: 4px; padding: 0.5px 1px; '
            f'line-height: 1.1; top: 0px; left: 0px;">{tooltip_text}</div>'
        )
        label = dl.DivMarker(
            position=[lat, lon],
            iconOptions={
                "html": label_html,
                "iconAnchor": label_icon_anchor
            },
            children=[dl.Popup(popup_content)]
        )
        return dl.LayerGroup(children=[marker, label])