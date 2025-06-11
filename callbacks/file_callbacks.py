from dash import Input, Output, State, exceptions
import pandas as pd  # Добавлен импорт pandas
from processing.file_processing import FileProcessor
from config import logger
import dash
import dash_bootstrap_components as dbc

def register_file_callbacks(app):
    # Callback для обработки загруженного файла
    @app.callback(
        [Output("data-store", "data"), Output("order-data-store", "data")],
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True
    )
    def process_file(contents, filename):
        logger.info(f"Загружен новый файл через dcc.Upload. Файл: {filename}")
        if not contents:
            logger.warning("Файл не выбран.")
            raise exceptions.PreventUpdate("Файл не выбран.")

        df, error = FileProcessor.load_excel_file(contents, filename)
        if df is None:
            logger.error(f"Ошибка загрузки: {error}")
            raise exceptions.PreventUpdate(error)

        data = df.to_dict("records")
        logger.info(f"Новый файл успешно загружен: {len(data)} строк.")
        return data, data

    # Callback для обновления таблиц и интерфейса
    @app.callback(
        [Output("grid", "columnDefs"), Output("grid", "rowData"),
         Output("turn-grid", "columnDefs"), Output("turn-grid", "rowData"),
         Output("search-input", "disabled"), Output("reset-button", "disabled"),
         Output("transfer-button", "disabled"), Output("notification-output", "children"),
         Output("dashboard-status", "children")],
        Input("data-store", "data"),
        prevent_initial_call=True
    )
    def update_grids_and_ui(data):
        if not data:
            logger.warning("Данные отсутствуют для обновления таблиц.")
            return ([], [], [], [], True, True, True, dbc.Alert("Данные отсутствуют.", color="warning"), "Ожидание загрузки файла...")

        new_column_defs = [{"field": col} for col in pd.DataFrame(data).columns if col != 'row_id']
        new_row_data = data
        logger.info(f"Обновлены таблицы с {len(new_row_data)} строками.")
        return (
            new_column_defs, new_row_data,
            new_column_defs, new_row_data,
            False, False, False,
            dbc.Alert(f"Файл успешно загружен.", color="success"),
            f"Файл загружен ({len(new_row_data)} строк)"
        )