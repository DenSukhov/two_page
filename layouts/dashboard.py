from dash import html, dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from config import logger

def create_layout():
    logger.debug("Создание макета для дашборда")
    layout = html.Div([
        html.H2("Дашборд", className="mt-3"),
        html.A("Открыть карту заказов", href="/map", target="_blank", className="mt-3", style={'display': 'block', 'color': 'blue'}),
        html.Div("Дашборд загружен", style={'color': 'blue'}),
        html.Div("Ожидание загрузки файла...", id="dashboard-status", className="mt-3"),
        dcc.Upload(
            id='upload-data',
            children=dbc.Button('Загрузить файл', color='primary', className='me-2'),
            multiple=False,
            accept='.xlsx, .xls'
        ),
        dcc.Loading(
            id="loading",
            type="circle",
            children=html.Div(id='notification-output', className='mt-3')
        ),
        dbc.Input(
            id='search-input',
            type='text',
            placeholder='Поиск по всем столбцам...',
            className='form-control mt-3 mb-2',
            style={'width': '300px'}
        ),
        dbc.Button('Сброс фильтров', id='reset-filters-button', color='secondary', className='mt-3 mb-2'),
        dbc.Button('Перенести в Turn', id='transfer-button', color='success', className='mt-3 me-2', disabled=True),
        dbc.Button('Смена +', id='add-shift-button', color='info', className='mt-3'),
        dag.AgGrid(
            id='grid',
            columnDefs=[],
            rowData=[],
            columnSize="sizeToFit",
            defaultColDef={"filter": True, "sortable": True, "floatingFilter": True, "resizable": True},
            dashGridOptions={"rowSelection": "multiple"},
            className='ag-theme-alpine mt-3',
            style={'height': '400px'}
        ),
        dag.AgGrid(
            id='turn-grid',
            columnDefs=[],
            rowData=[],
            columnSize="sizeToFit",
            defaultColDef={"filter": True, "sortable": True, "floatingFilter": True, "resizable": True},
            dashGridOptions={"rowSelection": "multiple"},
            className='ag-theme-alpine mt-3',
            style={'height': '300px'}
        ),
        dag.AgGrid(
            id='shift-grid',
            columnDefs=[
                {"field": "shift_id", "headerName": "ID смены"},
                {"field": "max_ts", "headerName": "Макс. ТС", "editable": True},
                {"field": "col_pal", "headerName": "Кол. паллет", "editable": True},
                {"field": "col_kg", "headerName": "Кол. кг", "editable": True},
                {"field": "head", "headerName": "Голова", "editable": True},
                {"field": "trailer", "headerName": "Прицеп", "editable": True},
                {"field": "comments", "headerName": "Комментарии", "editable": True}
            ],
            rowData=[],
            defaultColDef={"filter": True, "sortable": True, "resizable": True},
            dashGridOptions={"rowSelection": "single"},
            className='ag-theme-alpine mt-3',
            style={'height': '200px'}
        ),
        dcc.Store(id='data-store'),
        dcc.Store(id='turn-store'),
        dcc.Store(id='shift-store'),
        dcc.Store(id='order-data-store'),
        dcc.Store(id='active-table-store', data='grid'),
        html.Div(id='local-storage-clear', style={'display': 'none'})
    ], className='container', style={'border': '1px solid red'})
    logger.debug("Макет дашборда создан")
    return layout