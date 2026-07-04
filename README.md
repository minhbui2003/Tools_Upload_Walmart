# Upload Toni Pro

Upload Toni Pro là một ứng dụng Desktop (sử dụng PySide6) được thiết kế để tự động hóa quy trình upload sản phẩm POD (Print on Demand) lên nền tảng Walmart.

## 🚀 Tính năng chính

- **Đổi tên ảnh tự động**: Hỗ trợ copy và đổi tên ảnh chuẩn hóa theo mã SKU/Image code.
- **Tích hợp Cloudinary**: Tự động tải ảnh (Mockup, Swatch, Instruction) lên Cloudinary và lấy link (URL) trực tiếp.
- **Xử lý dữ liệu Excel**:
  - Đọc file Template mẫu.
  - Sử dụng file Mapping Config để tự động ghép nối (map) dữ liệu vào file Walmart Seller Template.
  - Xử lý các file dữ liệu bổ sung (Title, Price, Description, Feature, Variant Group...).
- **Xuất file Walmart-ready**: Tạo ra file `.xlsx` hoàn chỉnh, sẵn sàng để upload lên Walmart.

## 🛠 Cài đặt và Chạy môi trường Dev

Yêu cầu hệ thống: Python 3.11+

1. **Clone repository này về máy:**
   ```bash
   git clone <URL_CUA_REPO>
   cd Upload-Toni
   ```

2. **Cài đặt thư viện (Dependencies):**
   Khuyến khích sử dụng môi trường ảo (Virtual Environment):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Mac/Linux
   venv\Scripts\activate     # Trên Windows

   pip install -r requirements.txt
   ```

3. **Cấu hình môi trường (.env):**
   Tạo file `.env` (dựa trên `.env.example` nếu có) ở thư mục gốc chứa cấu hình Cloudinary:
   ```env
   CLOUD_NAME=your_cloud_name
   API_KEY=your_api_key
   API_SECRET=your_api_secret
   ```

4. **Chạy ứng dụng:**
   ```bash
   python main.py
   ```

## 📦 Build và Release (Tự động)

Dự án này đã được tích hợp **GitHub Actions** để tự động build thành phần mềm hoàn chỉnh cho macOS và Windows mà không cần cài đặt Python.

1. Mỗi khi bạn đẩy code (push) lên nhánh `main`, hệ thống sẽ tự động build thử nghiệm:
   - File `Upload-Toni-Windows.exe`
   - File `Upload-Toni-MacOS.zip` (chứa file `.app`)

2. **Cách tạo phiên bản chính thức (Release)**:
   Để tạo link tải về chính thức, bạn chỉ cần gán thẻ (tag) trên git:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   Sau khi hoàn tất, bạn có thể vào mục **Releases** trên GitHub để tải phần mềm về máy tính.
