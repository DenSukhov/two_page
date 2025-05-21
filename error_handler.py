from typing import Tuple, Optional
from config import logger
import pandas as pd

class ErrorHandler:
    @staticmethod
    def handle_exception(e: Exception, context: str) -> str:
        """
        Обрабатывает исключение и возвращает сообщение об ошибке.

        Args:
            e: Исключение.
            context: Контекст ошибки (например, "Загрузка файла").

        Returns:
            Сообщение об ошибке для пользователя.
        """
        error_message = f"{context}: {str(e)}"
        logger.error(error_message)
        return error_message

    @staticmethod
    def validate_excel_file(df: Optional[pd.DataFrame], filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Проверяет DataFrame из Excel-файла.

        Args:
            df: DataFrame из файла.
            filename: Имя файла.

        Returns:
            Кортеж (DataFrame, ошибка). Если ошибка, DataFrame=None.
        """
        if df is None:
            error = "Не удалось загрузить файл."
            logger.error(error)
            return None, error
        if 'Заказ' not in df.columns:
            error = "Столбец 'Заказ' не найден в файле."
            logger.error(error)
            return None, error
        return df, None