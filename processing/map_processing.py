import pandas as pd
from typing import List, Dict
import dash_leaflet as dl
from dash import html
from config import logger, EMOJI_MAPPING, ICON_CONFIG
import base64

class MapProcessor:
    @staticmethod
    def prepare_map_data(table_row_data: List[Dict]) -> pd.DataFrame:
        """
        Формирует данные для карты из данных таблицы order-grid.
        
        Args:
            table_row_data: Список словарей с данными таблицы.
        
        Returns:
            pandas.DataFrame с сгруппированными данными для карты.
        """
        required_columns = ['contact_code', 'Широта', 'Долгота', 'Адрес', 'Населённый_пункт', 'Тип_ТС', 'Заказ', 'Товар', 'Пал', 'КГ']
        try:
            logger.debug(f"Подготовка данных для карты: {len(table_row_data)} записей")
            table_df = pd.DataFrame(table_row_data)
            if table_df.empty:
                logger.info("Данные для карты пусты.")
                return pd.DataFrame(columns=required_columns)

            available_cols = table_df.columns.tolist()
            logger.debug(f"Доступные столбцы: {available_cols}")
            missing_cols = [col for col in required_columns if col not in table_df.columns]
            if missing_cols:
                logger.error(f"Отсутствуют столбцы: {missing_cols}")
                raise ValueError(f"Отсутствуют столбцы: {missing_cols}")

            grouped_data = table_df.groupby('contact_code').agg({
                'Широта': 'first',
                'Долгота': 'first',
                'Адрес': 'first',
                'Населённый_пункт': 'first',
                'Тип_ТС': 'first',
                'Заказ': list,
                'Товар': list,
                'Пал': list,
                'КГ': list
            }).reset_index()
            logger.debug(f"Сгруппировано {len(grouped_data)} записей для карты")
            return grouped_data
        except Exception as e:
            logger.error(f"Ошибка подготовки данных для карты: {str(e)}")
            raise

    @staticmethod
    def create_popup_content(row):
        """
        Создаёт содержимое всплывающего окна для маркера.
        
        Args:
            row: Строка с данными точки (из grouped_data).
        
        Returns:
            dash.html.Div с таблицей товаров.
        """
        table_rows = []
        for product, pal, kg in zip(row['Товар'], row['Пал'], row['КГ']):
            emoji = EMOJI_MAPPING.get(product.split()[-1].lower() if isinstance(product, str) else "", "")
            table_rows.append(html.Tr([html.Td(f"{emoji} {product}"), html.Td(pal), html.Td(kg)]))
        table_rows.append(html.Tr([
            html.Td("Сумма"),
            html.Td(round(sum(row['Пал']), 2)),
            html.Td(round(sum(row['КГ']), 2))
        ]))
        return html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th("Товар"), html.Th("Пал"), html.Th("КГ")])),
                html.Tbody(table_rows)
            ])
        ])

    @staticmethod
    def create_marker(row):
        """
        Создаёт маркер и подпись для точки на карте.
        
        Args:
            row: Строка с данными точки (из grouped_data).
        
        Returns:
            dash_leaflet.LayerGroup с маркером и подписью.
        """
        icon_key = row['Тип_ТС']
        popup_content = MapProcessor.create_popup_content(row)
        tooltip_text = f"{row['Населённый_пункт']}\n{row['Адрес']}"
        lat, lon = row['Широта'], row['Долгота']

        default_icon = {
            "iconUrl": "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
            "iconSize": [25, 41],
            "iconAnchor": [12.5, 41]
        }

        if icon_key == 'islands#graySportIcon':
            icon_html = (
                f'<svg width="30" height="41" viewBox="0 0 30 41" xmlns="http://www.w3.org/2000/svg">'
                f'<path d="M15 0C6.716 0 0 6.716 0 15c0 10.5 15 26 15 26s15-15.5 15-26C30 6.716 23.284 0 15 0z" fill="#808080"/>'
                f'<text x="15" y="20" font-size="12" fill="#FFFFFF" text-anchor="middle" font-family="Arial">🔗</text>'
                f'</svg>'
            )
            marker = dl.Marker(
                position=[lat, lon],
                icon={
                    "iconUrl": f"data:image/svg+xml;base64,{base64.b64encode(icon_html.encode()).decode()}",
                    "iconSize": [30, 41],
                    "iconAnchor": [15, 41]
                },
                children=[dl.Popup(popup_content)]
            )
            label_icon_anchor = [-7.5, 40]
        elif icon_key == 'islands#blueSportIcon':
            icon_html = (
                f'<svg width="30" height="41" viewBox="0 0 30 41" xmlns="http://www.w3.org/2000/svg">'
                f'<path d="M15 0C6.716 0 0 6.716 0 15c0 10.5 15 26 15 26s15-15.5 15-26C30 6.716 23.284 0 15 0z" fill="#0000FF"/>'
                f'<text x="15" y="20" font-size="12" fill="#FFFFFF" text-anchor="middle" font-family="Arial">🔗</text>'
                f'</svg>'
            )
            marker = dl.Marker(
                position=[lat, lon],
                icon={
                    "iconUrl": f"data:image/svg+xml;base64,{base64.b64encode(icon_html.encode()).decode()}",
                    "iconSize": [30, 41],
                    "iconAnchor": [15, 41]
                },
                children=[dl.Popup(popup_content)]
            )
            label_icon_anchor = [-7.5, 40]
        else:
            icon_info = ICON_CONFIG.get(icon_key, {})
            icon_url = icon_info.get('normal', default_icon['iconUrl'])
            marker = dl.Marker(
                position=[lat, lon],
                icon={
                    "iconUrl": icon_url,
                    "iconSize": [25, 41],
                    "iconAnchor": [12.5, 41]
                },
                children=[dl.Popup(popup_content)]
            )
            label_icon_anchor = [-5, 40]

        label_html = (
            f'<div style="position: relative; white-space: nowrap; display: inline-block; font-size: 10px; color: black; '
            f'background-color: white; border: 1px solid black; border-radius: 4px; padding: 0.5px 1px; '
            f'line-height: 1.1; top: 0px; left: 0px;">{tooltip_text}</div>'
        )
        label = dl.DivMarker(
            position=[lat, lon],
            iconOptions={
                "html": label_html,
                "iconAnchor": label_icon_anchor
            },
            children=[dl.Popup(popup_content)]
        )
        return dl.LayerGroup(children=[marker, label])