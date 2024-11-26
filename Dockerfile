# Sử dụng Python 3.8 slim
FROM python:3.8-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies cần thiết, bao gồm build-essential và python3-distutils
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-distutils \
    && apt-get clean

# Sao chép toàn bộ file từ project vào container
COPY . /app

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Expose cổng 80 để Render có thể kết nối
EXPOSE 80

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
