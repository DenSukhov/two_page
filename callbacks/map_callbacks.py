from dash import Input, Output, clientside_callback
from processing.map_processing import MapProcessor
from config import logger
import dash_bootstrap_components as dbc
import pandas as pd
import json

def register_map_callbacks(app):
    # Clientside callback для загрузки данных из LocalStorage
    app.clientside_callback(
        """
        function(n_intervals) {
            console.log('Map callback triggered, interval:', n_intervals);
            const data = localStorage.getItem('order-grid-data');
            if (data) {
                console.log('Loaded from LocalStorage:', data);
                return data;
            }
            console.log('No data in LocalStorage');
            return '';
        }
        """,
        Output('map-data-input', 'children'),
        Input('map-interval', 'n_intervals')
    )

    # Серверный callback для обновления карты
    @app.callback(
        [
            Output('map', 'center'),
            Output('markers', 'children'),
            Output('map-notification', 'children'),
            Output('local-storage-debug', 'children')
        ],
        Input('map-data-input', 'children'),
        prevent_initial_call=True
    )
    def update_map(data):
        logger.debug("Обновление карты")
        default_center = [56.8517036, 60.858846]
        try:
            if not data:
                logger.info("Данные в LocalStorage отсутствуют")
                return (
                    default_center,
                    [],
                    dbc.Alert("Данные отсутствуют в LocalStorage", color="warning"),
                    "No data"
                )

            logger.debug(f"Данные из LocalStorage: {data[:100]}...")
            parsed_data = json.loads(data)
            logger.debug(f"Загружено из LocalStorage: {len(parsed_data)} записей")

            # Подготовка данных для карты
            map_data = MapProcessor.prepare_map_data(parsed_data)
            if map_data.empty:
                logger.info("Нет данных для отображения на карте")
                return (
                    default_center,
                    [],
                    dbc.Alert("Нет данных для отображения на карте", color="warning"),
                    "Empty map data"
                )

            # Вычисление центра карты
            center = [
                map_data['Широта'].mean() if not map_data['Широта'].empty else default_center[0],
                map_data['Долгота'].mean() if not map_data['Долгота'].empty else default_center[1]
            ]
            logger.debug(f"Центр карты: {center}")

            # Создание маркеров
            markers = [MapProcessor.create_marker(row) for _, row in map_data.iterrows()]
            logger.debug(f"Создано {len(markers)} маркеров")
            return (
                center,
                markers,
                dbc.Alert(f"Карта обновлена: {len(markers)} маркеров", color="success"),
                json.dumps(parsed_data, indent=2)
            )
        except Exception as e:
            logger.error(f"Ошибка обновления карты: {str(e)}")
            return (
                default_center,
                [],
                dbc.Alert(f"Ошибка: {str(e)}", color="danger"),
                f"Error: {str(e)}"
            )