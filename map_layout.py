from dash import html, dcc
import dash_leaflet as dl
from config import logger

def create_map_layout():
    logger.debug("Начало создания макета для страницы карты заказов")
    layout = html.Div([
        html.H2("Карта заказов", className="mt-3"),
        html.A("Вернуться к дашборду", href="/", className="mt-3", style={'display': 'block', 'color': 'blue'}),
        dl.Map(
            id='map',
            center=[55.7558, 37.6173],  # Москва
            zoom=10,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id='markers')
            ],
            style={'width': '100%', 'height': '600px'}
        ),
        dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)  # Обновление каждые 5 секунд
    ])
    logger.debug("Макет карты заказов успешно создан")
    return layout