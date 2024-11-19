from PIL import Image
import os

# Đường dẫn đến thư mục chứa dữ liệu
directories = ['data/train', 'data/validation']

for directory in directories:
    for subdir, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            try:
                img = Image.open(file_path)  # Mở thử ảnh
                img.verify()  # Kiểm tra xem ảnh có hợp lệ không
            except (IOError, SyntaxError) as e:
                print(f"Ảnh không hợp lệ hoặc bị hỏng: {file_path}")
                os.remove(file_path)  # Xóa ảnh không hợp lệ
