from dash import Input, Output, State
from data_processing import DataProcessor
from config import logger
import dash
import dash_bootstrap_components as dbc

def register_file_callbacks(app):
    # Callback для загрузки нового файла
    @app.callback(
        [
            Output("data-store", "data"),
            Output("turn-store", "data"),
            Output("shift-store", "data"),
            Output("order-data-store", "data"),  # Добавлено для сохранения данных
            Output("grid", "columnDefs"),
            Output("grid", "rowData"),
            Output("turn-grid", "columnDefs"),
            Output("search-input", "disabled"),
            Output("reset-button", "disabled"),
            Output("transfer-button", "disabled"),
            Output("notification-output", "children"),
            Output("dashboard-status", "children")
        ],
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True
    )
    def update_file(contents, filename):
        logger.info(f"Загружен новый файл через dcc.Upload. Файл: {filename}, Contents: {'не пустой' if contents else 'пустой'}")
        if not contents:
            logger.warning("Файл не выбран.")
            return (
                dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update, dash.no_update,
                True, True, True,
                dbc.Alert("Файл не выбран.", color="warning", dismissable=True),
                "Ожидание загрузки файла..."
            )

        df, error = DataProcessor.load_excel_file(contents, filename)
        if error:
            logger.error(f"Ошибка загрузки файла: {error}")
            return (
                dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update, dash.no_update,
                True, True, True,
                dbc.Alert(error, color="danger", dismissable=True),
                "Ошибка при загрузке файла."
            )

        logger.info(f"Файл успешно загружен: {filename}, строк: {len(df)}")
        columns = [{"headerName": col, "field": col} for col in df.columns]
        row_data = df.to_dict("records")
        turn_columns = [
            {"headerName": "Заказ", "field": "Заказ"},
            {"headerName": "Товар", "field": "Товар"},
            {"headerName": "Пал", "field": "Пал"},
            {"headerName": "КГ", "field": "КГ"}
        ]
        data_store = row_data
        turn_store = [{"shift_id": 1000, "rows": []}]
        shift_store = [{
            "shift_id": 1000,
            "max_ts": 38,
            "col_pal": 0.0,
            "col_kg": 0.00,
            "head": "",
            "trailer": "",
            "comments": ""
        }]
        order_data_store = row_data  # Сохраняем данные в order-data-store

        return (
            data_store,
            turn_store,
            shift_store,
            order_data_store,
            columns,
            row_data,
            turn_columns,
            False,
            False,
            False,
            dbc.Alert(f"Файл {filename} успешно загружен.", color="success", dismissable=True),
            f"Файл загружен: {filename}"
        )