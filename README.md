# My Waste Classification Web

A user-friendly web application for waste classification, powered by a trained TensorFlow deep learning model. Users can upload images of waste items, and the app will predict the type of waste (e.g., paper, plastic, metal, glass, and others).

## Features
- **Upload Waste Images:** Users can upload images, and the app will classify them into predefined waste categories.
- **Leaderboard:** Track user points based on successful classifications.
- **Admin Dashboard:** Manage users, view activities, and monitor app usage.
- **History:** View user activity history.

## Requirements
- Python 3.8.20
- TensorFlow, Flask, SQLAlchemy, and other dependencies listed in `requirements.txt`

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ThinhPhan0108/my-waste-classification-web.git
2. **Navigate to the project directory:**
   ```bash
   cd my-waste-classification-web
3. **Download the model file:**
   - Click on the following [Google Drive link](https://drive.google.com/file/d/1rtxHkF5zr6nuqOwVGkcZwDowgArZnhLH/view?usp=sharing) to download the pre-trained TensorFlow model file.
   - Once the model is downloaded, move the model file to the **root directory** of the project, where your `app.py` file is located.
   - After moving the model, the path to the file should look something like this:
     ```
     /my-waste-classification-web/
       ├── app.py
       ├── model.h5  (your downloaded model)
       └── other files...
     ```
   - Now, you are ready to run the application with the pre-trained model loaded.
4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
5. **Run the application:**
   ```bash
   python app.py
   
## Dataset
The dataset used for training the model consists of categorized images of waste items. You can customize the model by retraining it with your dataset.

## License
This project is licensed under the MIT License.
