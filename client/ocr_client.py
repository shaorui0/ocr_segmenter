import grpc
import ocr_pb2
import ocr_pb2_grpc

def run():
    # 连接到OCR服务端
    channel = grpc.insecure_channel('ocr_server:50051')
    stub = ocr_pb2_grpc.OCRServiceStub(channel)

    # 读取PDF文件
    pdf_path = 'sample.pdf'  # 替换为实际的PDF文件路径
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()

    # 创建OCR请求
    request = ocr_pb2.OCRRequest(
        pdf_data=pdf_data,
        start_page=0,    # 起始页（0基）
        end_page=2       # 结束页（0基）
    )

    # 发送请求并接收响应
    response = stub.AnalyzePDF(request)

    # 处理响应
    for result in response.results:
        print(f"Page {result.page_number}:")
        print(f"OCR Text: {result.text}")
        print(f"LLM Response: {result.llm_response}")
        print("-" * 40)

if __name__ == '__main__':
    run()
