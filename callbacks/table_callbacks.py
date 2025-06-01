from dash import Input, Output, State, clientside_callback
import dash
from config import logger
from data_processing import DataProcessor

def register_table_callbacks(app):
    # Clientside callback для управления LocalStorage
    app.clientside_callback(
        """
        function(gridVirtualRowData, turnVirtualRowData, gridRowData, turnRowData, activeTable, uploadContents, uploadClicks, transferClicks, shiftClicks, gridClicks, turnClicks, orderDataStore) {
            console.log('Clientside callback triggered');
            console.log('Active table:', activeTable);
            console.log('Grid virtualRowData:', gridVirtualRowData ? gridVirtualRowData.length : 'null', 'Grid rowData:', gridRowData ? gridRowData.length : 'null');
            console.log('Turn virtualRowData:', turnVirtualRowData ? turnVirtualRowData.length : 'null', 'Turn rowData:', turnRowData ? turnRowData.length : 'null');
            console.log('Order data store:', orderDataStore ? orderDataStore.length : 'null');

            // Очистка LocalStorage при загрузке нового файла
            if (uploadContents && uploadClicks && window.lastUploadClicks !== uploadClicks) {
                console.log('New file uploaded, clearing LocalStorage');
                localStorage.clear();
                sessionStorage.clear();
                console.log('LocalStorage and SessionStorage cleared');
                window.lastUploadClicks = uploadClicks;
                return null;
            }

            // Пропуск, если активная таблица не определена
            if (!activeTable) {
                console.log('Active table not defined, clearing LocalStorage');
                localStorage.removeItem('order-grid-data');
                return null;
            }

            let tableId = activeTable === 'turn-grid' ? 'turn-grid' : 'grid';
            let virtualRowData = activeTable === 'turn-grid' ? turnVirtualRowData : gridVirtualRowData;
            let rowData = activeTable === 'turn-grid' ? turnRowData : gridRowData;

            console.log('Selected table:', tableId);

            if (!window.dash_ag_grid || !window.dash_ag_grid.getApi) {
                console.log('dash_ag_grid or getApi not available');
                localStorage.removeItem('order-grid-data');
                return null;
            }

            return new Promise(resolve => {
                let attempts = 0;
                const maxAttempts = 1000;
                const interval = setInterval(() => {
                    attempts++;
                    console.log('Attempt', attempts, 'to initialize table:', tableId);
                    const api = window.dash_ag_grid.getApi(tableId);
                    if (api || attempts >= maxAttempts) {
                        clearInterval(interval);
                        if (!api) {
                            console.log('Table', tableId, 'not initialized after', maxAttempts, 'attempts');
                            localStorage.removeItem('order-grid-data');
                            resolve(null);
                            return;
                        }
                        let dataToSave = virtualRowData && virtualRowData.length > 0 ? virtualRowData : null;
                        if (!dataToSave) {
                            console.log('No virtualRowData, checking rendered nodes for', tableId);
                            const renderedNodes = api.getRenderedNodes();
                            console.log('Rendered nodes:', renderedNodes ? renderedNodes.length : 'null');
                            if (renderedNodes && renderedNodes.length > 0) {
                                dataToSave = renderedNodes.map(node => node.data);
                                console.log('Using rendered nodes data:', dataToSave.length);
                            } else if (rowData && rowData.length > 0) {
                                console.log('No rendered nodes, falling back to rowData:', rowData.length);
                                dataToSave = rowData;
                            }
                        }
                        if (!dataToSave || dataToSave.length === 0) {
                            console.log('No data to save for table:', tableId);
                            localStorage.removeItem('order-grid-data');
                            resolve(null);
                            return;
                        }
                        // Получаем номера заказов
                        const orders = dataToSave
                            .filter(row => row && row['Заказ'])
                            .map(row => row['Заказ']);
                        console.log('Orders found in', tableId, ':', orders.length);
                        // Сопоставляем с order-data-store
                        console.log('Order data store content:', orderDataStore);
                        const fullData = orderDataStore && orders.length > 0
                            ? orderDataStore.filter(row => row && row['Заказ'] && orders.includes(row['Заказ']))
                            : [];
                        console.log('Full data to save:', fullData.length);
                        console.log('Full data content:', fullData);
                        localStorage.setItem('order-grid-data', JSON.stringify(fullData));
                        console.log('Saved to LocalStorage:', fullData);
                        resolve(null);
                    }
                }, 300);
            });
        }
        """,
        Output("local-storage-clear", "children"),
        [
            Input("grid", "virtualRowData"),
            Input("turn-grid", "virtualRowData"),
            Input("grid", "rowData"),
            Input("turn-grid", "rowData"),
            Input("active-table-store", "data"),
            Input("upload-data", "contents"),
            Input("upload-data", "n_clicks"),
            Input("transfer-button", "n_clicks"),
            Input("add-shift-button", "n_clicks"),
            Input("grid", "cellClicked"),
            Input("turn-grid", "cellClicked"),
            Input("order-data-store", "data")  # Восстановлен
        ],
        prevent_initial_call=True
    )

    # Callback для обновления активной таблицы
    @app.callback(
        Output("active-table-store", "data"),
        Input("grid", "cellClicked"),
        Input("turn-grid", "cellClicked"),
        Input("shift-grid", "selectedRows"),
        prevent_initial_call=True
    )
    def update_active_table(grid_click, turn_click, shift_selected_rows):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "grid"

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if triggered_id == "shift-grid":
            if shift_selected_rows and len(shift_selected_rows) > 0:
                logger.info("Выбрана смена в shift-grid, активная таблица: turn-grid")
                return "turn-grid"
            else:
                logger.info("Сброс выбора в shift-grid, активная таблица: grid")
                return "grid"
        elif triggered_id == "grid":
            logger.info("Клик по grid, активная таблица: grid")
            return "grid"
        elif triggered_id == "turn-grid":
            logger.info("Клик по turn-grid, активная таблица: turn-grid")
            return "turn-grid"
        
        return dash.no_update

    # Callback для поиска
    @app.callback(
        Output("grid", "rowData", allow_duplicate=True),
        Input("search-input", "value"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def filter_table(search_value, original_data):
        logger.info("Выполняется фильтрация таблицы по запросу")
        return DataProcessor.filter_data(original_data, search_value)

    # Callback для сброса фильтров
    @app.callback(
        [
            Output("grid", "rowData", allow_duplicate=True),
            Output("grid", "filterModel"),
            Output("search-input", "value")
        ],
        Input("reset-button", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def reset_filters(n_clicks, original_data):
        logger.info("Нажата кнопка 'Сбросить фильтры'.")
        return original_data, {}, ""