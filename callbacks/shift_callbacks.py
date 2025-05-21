from dash import Input, Output, State
import dash
from config import logger
from data_processing import DataProcessor
import dash_bootstrap_components as dbc

def register_shift_callbacks(app):
    # Callback для создания новой смены
    @app.callback(
        [
            Output("shift-store", "data", allow_duplicate=True),
            Output("turn-store", "data", allow_duplicate=True),
            Output("shift-grid", "rowData"),
            Output("notification-output", "children", allow_duplicate=True)
        ],
        Input("add-shift-button", "n_clicks"),
        State("shift-store", "data"),
        State("turn-store", "data"),
        prevent_initial_call=True
    )
    def add_shift(n_clicks, shift_store, turn_store):
        logger.info("Нажата кнопка 'Смена +'. Попытка создания новой смены.")
        
        # Инициализация пустых списков, если данные отсутствуют или None
        shift_store = [] if shift_store is None or not isinstance(shift_store, list) else shift_store
        turn_store = [] if turn_store is None or not isinstance(turn_store, list) else turn_store
        
        logger.debug(f"shift_store: {shift_store}, turn_store: {turn_store}")

        try:
            new_shift_store, new_turn_store, message = DataProcessor.create_shift(shift_store, turn_store)
            logger.info(f"Смена создана успешно: {message}")
            return (
                new_shift_store,
                new_turn_store,
                new_shift_store,
                dbc.Alert(message, color="success", className="mt-3")
            )
        except Exception as e:
            error_message = f"Ошибка при создании смены: {str(e)}"
            logger.error(error_message)
            return (
                shift_store,
                turn_store,
                shift_store,
                dbc.Alert(error_message, color="danger", className="mt-3")
            )

    # Callback для обновления turn-grid при выборе смены
    @app.callback(
        [
            Output("turn-grid", "rowData", allow_duplicate=True),
            Output("notification-output", "children", allow_duplicate=True)
        ],
        Input("shift-grid", "selectedRows"),
        State("turn-store", "data"),
        prevent_initial_call=True
    )
    def update_turn_grid(selected_rows, turn_store):
        logger.info("Изменён выбор строки в shift-grid.")
        if not selected_rows or not selected_rows[0]:
            logger.warning("Не выбрана смена в shift-grid.")
            return [], dbc.Alert("Выберите смену в таблице рейсов.", color="warning", className="mt-3")

        shift_id = selected_rows[0]["shift_id"]
        turn_store = [] if turn_store is None or not isinstance(turn_store, list) else turn_store
        for shift in turn_store:
            if shift["shift_id"] == shift_id:
                logger.info(f"Отображение заказов для смены {shift_id}.")
                return shift["rows"], ""
        return [], dbc.Alert(f"Данные для смены {shift_id} не найдены.", color="danger", className="mt-3")

    # Callback для переноса строк в turn-grid
    @app.callback(
        [
            Output("data-store", "data", allow_duplicate=True),
            Output("turn-store", "data", allow_duplicate=True),
            Output("grid", "rowData", allow_duplicate=True),
            Output("turn-grid", "rowData", allow_duplicate=True),
            Output("notification-output", "children", allow_duplicate=True)
        ],
        Input("transfer-button", "n_clicks"),
        State("grid", "selectedRows"),
        State("shift-grid", "selectedRows"),
        State("data-store", "data"),
        State("turn-store", "data"),
        prevent_initial_call=True
    )
    def transfer_to_turn(n_clicks, grid_selected_rows, shift_selected_rows, data_store, turn_store):
        logger.info("Нажата кнопка 'Перенести в Turn'.")
        if not grid_selected_rows:
            logger.warning("Не выбраны строки в grid.")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dbc.Alert("Не выбраны строки для переноса.", color="warning", className="mt-3")
            )
        if not shift_selected_rows or not shift_selected_rows[0]:
            logger.warning("Не выбрана смена в shift-grid.")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dbc.Alert("Выберите смену в таблице рейсов.", color="warning", className="mt-3")
            )

        shift_id = shift_selected_rows[0]["shift_id"]
        turn_store = [] if turn_store is None or not isinstance(turn_store, list) else turn_store
        new_data_store, new_turn_store, updated_rows = DataProcessor.transfer_rows(data_store, turn_store, grid_selected_rows, shift_id)
        return (
            new_data_store,
            new_turn_store,
            new_data_store,
            updated_rows if shift_selected_rows[0]["shift_id"] == shift_id else dash.no_update,
            dbc.Alert(f"Перенесено {len(grid_selected_rows)} строк в смену {shift_id}.", color="success", className="mt-3")
        )

    # Callback для редактирования shift-grid
    @app.callback(
        [
            Output("shift-store", "data", allow_duplicate=True),
            Output("notification-output", "children", allow_duplicate=True)
        ],
        Input("shift-grid", "cellValueChanged"),
        State("shift-store", "data"),
        prevent_initial_call=True
    )
    def update_shift_store(cell_changed, shift_store):
        shift_store = [] if shift_store is None or not isinstance(shift_store, list) else shift_store
        new_shift_store, message = DataProcessor.update_shift(shift_store, cell_changed)
        color = "success" if "Обновлена смена" in message else "danger"
        return new_shift_store, dbc.Alert(message, color=color, className="mt-3")