FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 创建或替换 sources.list 文件
RUN echo "deb http://mirrors.aliyun.com/debian buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian buster-updates main contrib non-free" >> /etc/apt/sources.list

# 更新软件包列表并安装所需软件
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-jpn poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 文件并安装 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用程序代码
COPY app/ ./app
COPY temp_image/ ./temp_image

# 暴露应用程序端口
EXPOSE 8080

# 运行应用程序
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
