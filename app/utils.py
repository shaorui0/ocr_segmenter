import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def perform_ocr(image_bytes: bytes) -> str:
    """
    对图像字节进行OCR处理并返回提取的文本。

    参数：
        image_bytes (bytes): 图像文件的字节数据。

    返回：
        str: 提取的文本。
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang='jpn')  # 根据需要更改语言
        logger.info(f"OCR 提取成功。\n{text}\n")
        return text
    except Exception as e:
        logger.error(f"OCR 处理错误: {e}")
        raise e
