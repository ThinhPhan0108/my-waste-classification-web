# Sử dụng Python base image
FROM python:3.8-slim

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file project vào container
COPY . /app

# Cài đặt các dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose cổng 80 để Render có thể kết nối
EXPOSE 80

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
