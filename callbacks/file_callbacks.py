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
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dbc.Alert("Файл не выбран.", color="warning", className="mt-3"),
                "Ожидание загрузки файла..."
            )

        df, error = DataProcessor.load_excel_file(contents, filename)
        if df is None:
            logger.error(f"Ошибка загрузки: {error}")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dbc.Alert(error, color="danger", className="mt-3"),
                "Ошибка при загрузке файла"
            )

        new_column_defs = [{"field": col} for col in df.columns if col != 'row_id']
        new_row_data = df.to_dict("records")
        logger.info(f"Новый файл успешно загружен: {len(new_row_data)} строк, только основная таблица обновлена.")
        return (
            new_row_data,
            dash.no_update,
            dash.no_update,
            new_column_defs,
            new_row_data,
            new_column_defs,
            False,
            False,
            False,
            dbc.Alert(f"Файл {filename} успешно загружен.", color="success", className="mt-3"),
            f"Файл {filename} загружен ({len(new_row_data)} строк)"
        )