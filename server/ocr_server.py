import logging
import os
import io
import base64
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import grpc
from concurrent import futures

import ocr_pb2
import ocr_pb2_grpc

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 模拟LLM处理函数
def send_to_llm(text):
    # 这里可以集成实际的LLM服务
    return f"LLM processed: {text}"

class OCRServiceServicer(ocr_pb2_grpc.OCRServiceServicer):
    def AnalyzePDF(self, request, context):
        logger.debug("Received OCRRequest")
        pdf_data = request.pdf_data
        start_page = request.start_page
        end_page = request.end_page

        # 将PDF二进制数据保存为临时文件
        temp_pdf_path = 'temp.pdf'
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_data)
        logger.debug(f"Saved temporary PDF at {temp_pdf_path}")

        # 打开PDF文档
        pdf_document = fitz.open(temp_pdf_path)
        ocr_results = []

        for page_num in range(start_page, end_page + 1):
            if page_num < 0 or page_num >= len(pdf_document):
                logger.warning(f"Page number {page_num} is out of range. Skipping.")
                continue  # 跳过无效的页码

            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            # 执行OCR
            page_text = pytesseract.image_to_string(image, lang='jpn')  # 根据需要调整语言

            # 发送到LLM
            llm_response = send_to_llm(page_text)
            logger.debug(f"LLM response for page {page_num + 1}: {llm_response}")

            ocr_result = ocr_pb2.PageOCRResult(
                page_number=page_num + 1,
                text=page_text,
                llm_response=llm_response
            )
            ocr_results.append(ocr_result)

        pdf_document.close()
        os.remove(temp_pdf_path)  # 删除临时文件
        logger.debug("Finished processing PDF and removed temporary file")

        response = ocr_pb2.OCRResponse(results=ocr_results)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ocr_pb2_grpc.add_OCRServiceServicer_to_server(OCRServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("OCR gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
