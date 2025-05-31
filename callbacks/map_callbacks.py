from dash import Input, Output, State, callback, clientside_callback
from dash.exceptions import PreventUpdate
from data_processing import DataProcessor
from config import logger
import json
import dash_leaflet as dl

def register_map_callbacks(app):
    # Clientside callback для проверки данных в LocalStorage
    clientside_callback(
        """
        function(n_intervals, existing_data) {
            if (window.localStorage.getItem('order-data-store')) {
                const data = JSON.parse(window.localStorage.getItem('order-data-store'));
                return [data, 'Данные найдены в LocalStorage'];
            }
            return [null, 'Данные в LocalStorage отсутствуют'];
        }
        """,
        [
            Output('map-data-input', 'children'),
            Output('map-status', 'children')
        ],
        [
            Input('map-interval', 'n_intervals'),
            Input('order-data-store', 'data')
        ]
    )

    # Callback для обновления маркеров на карте
    @app.callback(
        Output('markers', 'children'),
        Input('map-data-input', 'children'),
        prevent_initial_call=True
    )
    def update_map_markers(map_data):
        logger.debug(f"Обновление маркеров карты, входные данные: {map_data}")
        if not map_data:
            logger.info("Данные для карты отсутствуют.")
            return []

        try:
            table_row_data = json.loads(map_data) if isinstance(map_data, str) else map_data
            grouped_data = DataProcessor.prepare_map_data(table_row_data)
            markers = [DataProcessor.create_marker(row) for _, row in grouped_data.iterrows()]
            logger.info(f"Создано {len(markers)} маркеров для карты.")
            return markers
        except Exception as e:
            logger.error(f"Ошибка при обновлении карты: {str(e)}")
            return []