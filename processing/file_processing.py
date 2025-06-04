import pandas as pd
import base64
import io
from typing import Tuple, Optional
from config import logger
from error_handler import ErrorHandler

class FileProcessor:
    @staticmethod
    def load_excel_file(contents: str, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Загружает и обрабатывает Excel-файл.

        Args:
            contents: Содержимое файла в формате base64.
            filename: Имя файла.

        Returns:
            Кортеж (DataFrame, ошибка). Если ошибка, DataFrame=None.
        """
        try:
            logger.info(f"Попытка загрузки файла: {filename}")
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            if filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
            elif filename.endswith('.xls'):
                df = pd.read_excel(io.BytesIO(decoded), engine='xlrd')
            else:
                error = "Неподдерживаемый формат файла. Используйте .xlsx или .xls."
                logger.error(error)
                return None, error

            df['row_id'] = range(len(df))
            return ErrorHandler.validate_excel_file(df, filename)
        except Exception as e:
            return None, ErrorHandler.handle_exception(e, "Загрузка файла")