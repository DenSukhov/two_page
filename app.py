import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from layout import create_layout
from map_layout import create_map_layout
from register_callbacks import register_callbacks
from config import logger

# Инициализация Dash-приложения (единственный экземпляр)
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Корневой макет
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(id='page-diagnostic', style={'color': 'red', 'margin': '20px', 'display': 'none'})
])

# Регистрация страниц
logger.info("Регистрация страницы дашборда")
dash.register_page(
    "dashboard",
    path='/',
    layout=create_layout,
    name="Дашборд"
)

logger.info("Регистрация страницы карты заказов")
dash.register_page(
    "map",
    path='/map',
    layout=create_map_layout,
    name="Карта заказов"
)

# Диагностический callback
@app.callback(
    dash.dependencies.Output('page-diagnostic', 'children'),
    dash.dependencies.Input('url', 'pathname')
)
def debug_page(pathname):
    logger.info(f"Открыта страница: {pathname}")
    return f"Диагностика: страница {pathname} загружена"

# Callback для рендеринга страниц
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    dash.dependencies.Input('url', 'pathname')
)
def render_page_content(pathname):
    logger.info(f"Рендеринг страницы: {pathname}")
    if pathname == '/':
        layout = create_layout()
        logger.debug(f"Макет для /: {type(layout).__name__}")
        return layout
    elif pathname == '/map':
        layout = create_map_layout()
        logger.debug(f"Макет для /map: {type(layout).__name__}")
        return layout
    logger.warning(f"Страница не найдена: {pathname}")
    return html.Div("404: Страница не найдена")

# Регистрация callback'ов
logger.info("Регистрация callback'ов")
register_callbacks(app)

# Запуск приложения
if __name__ == "__main__":
    logger.info("Запуск Dash-приложения на http://127.0.0.1:8050")
    app.run(host='127.0.0.1', port=8050, debug=False)