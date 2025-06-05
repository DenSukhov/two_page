# PROJECT_CONTEXT.md

## Описание проекта
Dash-приложение для маршрутизации, предназначенное для управления заказами и их визуализации. Основной функционал:
- Загрузка и обработка Excel-файлов с данными заказов.
- Отображение данных в интерактивных таблицах (`grid`, `turn-grid`, `shift-grid`) с возможностью фильтрации, переноса строк и управления сменами.
- Визуализация заказов на карте с маркерами и всплывающими окнами.
- Логирование всех операций в файл `dashboard.log`.

Приложение состоит из двух страниц: дашборд (`/`) и карта заказов (`/map`). Использует библиотеки Dash, dash-ag-grid, dash-leaflet, pandas и dash-bootstrap-components.

## Текущая структура
- **app.py**: Основной файл, инициализирующий Dash-приложение, маршруты страниц и запуск сервера.
- **components.py**: Общие компоненты (константы, конфигурации таблиц).
- **config.py**: Настройки логирования, начальный ID смен (`next_shift_id`), конфигурация иконок и эмодзи.
- **error_handler.py**: Обработка ошибок (валидация Excel-файлов, обработка исключений).
- **utils.py**: Утилитарные функции (будут добавлены при необходимости).
- **layouts/**:
  - **dashboard.py**: Макет дашборда (таблицы, кнопки, загрузка файлов).
  - **map.py**: Макет страницы карты заказов.
  - **factory.py**: Централизованное создание макетов.
- **processing/**:
  - **file_processing.py**: Загрузка и валидация Excel-файлов.
  - **table_processing.py**: Фильтрация данных, перенос строк, управление сменами.
  - **map_processing.py**: Подготовка данных для карты, создание маркеров и всплывающих окон.
- **callbacks/**:
  - **base.py**: Регистрация всех callback-функций.
  - **file_callbacks.py**: Callback'ы для загрузки файлов.
  - **table_callbacks.py**: Callback'ы для управления таблицами.
  - **shift_callbacks.py**: Callback'ы для управления сменами.
  - **map_callbacks.py**: Callback'ы для обновления карты.
- **tests/**:
  - **test_file_processing.py**: Тесты для загрузки файлов.
  - **test_table_processing.py**: Тесты для фильтрации и управления сменами.
  - **test_map_processing.py**: Тесты для подготовки данных карты.
  - **test_callbacks.py**: Тесты для callback'ов (будет добавлен).
- **assets/**:
  - **custom.css**: Стили для таблиц.
  - **custom.js**: Клиентский JavaScript-код.
  - **style.css**: Дополнительные стили для таблиц и карты.
- **requirements.txt**: Зависимости проекта.

## История изменений
- **2025-06-04**: Реорганизация проекта:
  - Созданы директории `layouts/`, `processing/`, `callbacks/`, `tests/`.
  - Переименован `data_processing.py` в `processing/file_processing.py`, `processing/table_processing.py`, `processing/map_processing.py`.
  - Перенесён `layout.py` в `layouts/dashboard.py`, `map_layout.py` в `layouts/map.py`.
  - Создан `layouts/factory.py` для централизованного создания макетов.
  - Переименован `register_callbacks.py` в `callbacks/base.py`.
  - Создан `components.py` для общих компонентов.
  - Создан `utils.py` (пустой, для будущих утилит).
  - Обновлены импорты во всех файлах.
  - Обновлены тесты в `tests/`.
  - Сохранена текущая функциональность.
- **2025-06-05**: Исправление ошибок:
  - Добавлен `next_shift_id` в `config.py` и обновлён импорт в `table_processing.py`.
  - Исправлен тест `test_create_shift` в `test_table_processing.py`.
 