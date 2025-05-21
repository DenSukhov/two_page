from dash import html, dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from config import logger

def create_map_layout():
    logger.debug("Начало создания макета для страницы карты заказов")
    layout = html.Div([
        html.H1("Таблица заказов", className="mt-3"),
        html.Div("Карта заказов загружена", style={'color': 'blue'}),
        html.Div("Ожидание данных в LocalStorage...", id="map-status", className="mt-3"),
        dag.AgGrid(
            id='order-grid',
            columnDefs=[{"field": "Заказы", "headerName": "Заказы"}],
            rowData=[],
            defaultColDef={"filter": True, "sortable": True, "resizable": True},
            className='ag-theme-alpine mt-3',
            style={'height': '200px'}
        ),
        html.Div(id='map-notification', className='mt-3'),
        dcc.Interval(id='map-interval', interval=5000, n_intervals=0),
        html.Div(id='local-storage-debug', style={'margin': '10px', 'color': 'blue'})
    ], className='container', style={'border': '1px solid red'})
    logger.debug("Макет карты заказов успешно создан")
    return layout