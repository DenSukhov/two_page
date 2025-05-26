from dash import Input, Output, clientside_callback
import dash_bootstrap_components as dbc
from config import logger

def register_map_callbacks(app):
    logger.debug("Начало регистрации clientside callback для карты заказов")
    app.clientside_callback(
        """
        function(n_intervals) {
            console.log('Map callback triggered, interval:', n_intervals);
            console.log('Checking LocalStorage for order-grid data');
            const data = localStorage.getItem('order-grid-data');
            if (data) {
                const parsedData = JSON.parse(data);
                console.log('Loaded from LocalStorage:', parsedData);
                return [
                    parsedData,
                    {
                        "props": {
                            "children": "Данные загружены из LocalStorage (" + parsedData.length + " заказов)",
                            "color": "success"
                        },
                        "type": "Alert",
                        "namespace": "dash_bootstrap_components"
                    },
                    JSON.stringify(parsedData)
                ];
            }
            console.log('No data in LocalStorage');
            return [
                [],
                {
                    "props": {
                        "children": "Данные отсутствуют в LocalStorage",
                        "color": "warning"
                    },
                    "type": "Alert",
                    "namespace": "dash_bootstrap_components"
                },
                "No data"
            ];
        }
        """,
        [
            Output('order-grid', 'rowData'),
            Output('map-notification', 'children'),
            Output('local-storage-debug', 'children')
        ],
        Input('map-interval', 'n_intervals')
    )
    logger.debug("Clientside callback для карты заказов успешно зарегистрирован")