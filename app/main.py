import os
import mimetypes
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from .utils import perform_ocr  # 根据项目结构调整导入路径
import logging
import aiofiles

app = FastAPI()

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 定义保存文件的目录
SAVE_DIRECTORY = "/home/rshao/personal/ocr_segmenter/temp_image"

# 确保保存目录存在
try:
    os.makedirs(SAVE_DIRECTORY, exist_ok=True)
    logger.debug(f"保存文件的目录已确保存在: {SAVE_DIRECTORY}")
except Exception as e:
    logger.error(f"创建目录失败: {e}")
    raise

# 中间件：限制上传文件大小（例如：10 MB）
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    max_size = 10 * 1024 * 1024  # 10 MB
    if "content-length" in request.headers:
        try:
            content_length = int(request.headers["content-length"])
            if content_length > max_size:
                logger.warning("上传的文件过大。")
                raise HTTPException(status_code=413, detail="文件过大。")
        except ValueError:
            logger.warning("无效的Content-Length头。")
            raise HTTPException(status_code=400, detail="无效的Content-Length头。")
    response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    logger.debug(f"上传的文件名: {file.filename}")
    logger.debug(f"上传的文件类型: {file.content_type}")

    # 读取文件内容
    try:
        file_content = await file.read()
        file_size = len(file_content)
        logger.debug(f"上传的文件大小: {file_size} bytes")
    except Exception as e:
        logger.error(f"读取上传文件失败: {e}")
        raise HTTPException(status_code=500, detail="读取上传文件失败。")

    # 定义保存文件的路径，确保文件名安全
    secure_filename = os.path.basename(file.filename)
    file_path = os.path.join(SAVE_DIRECTORY, secure_filename)
    logger.debug(f"文件保存路径: {file_path}")

    # 异步保存上传的文件到本地
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(file_content)
        logger.debug(f"文件已成功保存到: {file_path}")
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise HTTPException(status_code=500, detail="文件保存失败。")

    # 处理 Content-Type 为 None 的情况
    if file.content_type:
        content_type = file.content_type
        logger.debug(f"检测到的 Content-Type: {content_type}")
    else:
        # 尝试通过文件扩展名推断 Content-Type
        guessed_type, _ = mimetypes.guess_type(file.filename)
        content_type = guessed_type
        logger.debug(f"通过文件扩展名推断的 Content-Type: {content_type}")

    if not content_type or not content_type.startswith('image/'):
        logger.warning("上传的文件不是图像类型。")
        # 可选：删除已保存的非图像文件
        try:
            os.remove(file_path)
            logger.debug(f"非图像文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"删除非图像文件失败: {e}")
        raise HTTPException(status_code=400, detail="上传的文件不是图像。")

    # 执行 OCR
    try:
        # 读取保存的图像文件
        async with aiofiles.open(file_path, "rb") as image_file:
            image_bytes = await image_file.read()
            logger.debug("开始执行 OCR")
            text = perform_ocr(image_bytes)
            logger.debug("OCR 执行完成")
    except Exception as e:
        logger.error(f"OCR 处理失败: {e}")
        raise HTTPException(status_code=500, detail="OCR 处理失败。")

    # 可选：删除临时保存的图像文件
    # try:
    #     os.remove(file_path)
    #     logger.debug(f"临时文件已删除: {file_path}")
    # except Exception as e:
    #     logger.warning(f"删除临时文件失败: {e}")

    return JSONResponse(content={"text": text}, status_code=200)
