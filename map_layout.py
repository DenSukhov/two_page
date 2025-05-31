from dash import html, dcc
import dash_leaflet as dl
from config import logger

def create_map_layout():
    logger.debug("Начало создания макета для страницы карты заказов")
    layout = html.Div([
        html.H1("Карта заказов", className="mt-3"),
        html.Div("Карта заказов загружена", style={'color': 'blue'}),
        html.Div("Ожидание данных в LocalStorage...", id="map-status", className="mt-3"),
        dl.Map(
            id='map',
            center=[56.8517036, 60.858846],  # Центр по умолчанию (Екатеринбург)
            zoom=10,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="markers")
            ],
            style={'width': '100%', 'height': '600px'}
        ),
        html.Div(id='map-notification', className='mt-3'),
        dcc.Interval(id='map-interval', interval=5000, n_intervals=0'),
        html.Div(id='local-storage-debug', style={'margin': '10px', 'color': 'blue'}),
        html.Div(id='map-data-input', style={'display': 'none'})  # Скрытый компонент для данных
    ], className='container', style={'border': '1px solid red'})
    logger.debug("Макет карты заказов успешно создан")
    return layout