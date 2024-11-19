import os
from google_images_search import GoogleImagesSearch

# Điền API key và CX của bạn vào đây
GCS_DEVELOPER_KEY = 'AIzaSyAzwZSrQCK4N2mxRn4N2Lr3irTahivro9c'
GCS_CX = '448f7f17f59684566'

gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

# Các loại rác cần tải
waste_types = ['plastic waste', 'glass waste', 'metal waste']

# Số lượng ảnh cần tải cho mỗi loại
num_train_images = 50
num_validation_images = 10

# Đường dẫn đến thư mục train và validation trên máy của bạn
train_dir = r'C:\Users\Dell\waste_classification_web\data\train'
validation_dir = r'C:\Users\Dell\waste_classification_web\data\validation'

# Hàm tạo thư mục nếu chưa có
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Tạo thư mục train và validation cho mỗi loại rác
for waste_type in waste_types:
    folder_name = waste_type.replace(" ", "_")  # Thay đổi tên cho phù hợp với cấu trúc thư mục
    create_directory(os.path.join(train_dir, folder_name))
    create_directory(os.path.join(validation_dir, folder_name))

# Tải ảnh cho mỗi loại rác và lưu vào đúng thư mục
for waste_type in waste_types:
    folder_name = waste_type.replace(" ", "_")  # Đổi tên thư mục để tránh khoảng trắng
    
    # Tải ảnh cho tập huấn luyện
    search_params = {
        'q': waste_type,
        'num': num_train_images,
        'safe': 'high',
        'fileType': 'jpg',
        'imgType': 'photo',
        'imgSize': 'MEDIUM',
        'rights': 'cc_publicdomain'
    }
    gis.search(search_params=search_params)
    train_path = os.path.join(train_dir, folder_name)
    for image in gis.results():
        image.download(train_path)

    # Tải ảnh cho tập kiểm tra
    search_params['num'] = num_validation_images
    gis.search(search_params=search_params)
    validation_path = os.path.join(validation_dir, folder_name)
    for image in gis.results():
        image.download(validation_path)

print("Đã tải xong dữ liệu!")
