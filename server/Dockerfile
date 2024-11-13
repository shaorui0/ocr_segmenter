FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制需求文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务器代码
COPY . .

# 复制proto文件并生成gRPC代码
COPY ../proto/ocr.proto .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ocr.proto

# 暴露端口
EXPOSE 50051

# 启动服务器
CMD ["python", "ocr_server.py"]
