# Worker - CADQuery 执行器
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（CADQuery 需要大量图形库）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxmu-dev \
    libxi-dev \
    libxrender-dev \
    libxext-dev \
    libsm-dev \
    libice-dev \
    libxxf86vm-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libocct-foundation-dev \
    libocct-modeling-algorithms-dev \
    libocct-modeling-data-dev \
    libocct-ocaf-dev \
    libocct-visualization-dev \
    occt-draw \
    swig \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/

# 创建数据目录
RUN mkdir -p /app/data/models

# 设置环境变量
ENV PYTHONPATH=/app
ENV LIBGL_ALWAYS_SOFTWARE=1

CMD ["python", "-m", "app.worker"]
