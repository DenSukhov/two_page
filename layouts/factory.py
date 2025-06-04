from layouts.dashboard import create_layout as create_dashboard_layout
from layouts.map import create_layout as create_map_layout

def get_layout(page: str):
    """
    Возвращает макет для указанной страницы.

    Args:
        page (str): Название страницы ('dashboard' или 'map').

    Returns:
        dash.html.Div: Макет страницы.
    """
    if page == 'dashboard':
        return create_dashboard_layout()
    elif page == 'map':
        return create_map_layout()
    return None