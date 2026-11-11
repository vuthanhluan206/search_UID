# search_UID

# Locket UID Lookup Lab

Project thử nghiệm tra cứu UID từ username hoặc link hồ sơ Locket.

Công nghệ:
- Python 3.12
- FastAPI
- HTTPX
- HTML/CSS/JavaScript
- Vercel

## Chức năng

1. Nhập link Locket hoặc username.
2. Kiểm tra định dạng link.
3. Tách username từ đường dẫn.
4. Thử tra cứu UID bằng API không chính thức.
5. Hiển thị UID nếu API trả về hợp lệ.
6. Hiển thị thông báo lỗi nếu API từ chối.

## Deploy lên Vercel

1. Tạo repository GitHub mới.
2. Đưa app.py, requirements.txt, .python-version,
   .gitignore và README.md vào thư mục gốc.
3. Mở https://vercel.com/new
4. Import repository.
5. Root Directory: ./
6. Cấu hình biến môi trường.
7. Deploy project.

## Environment Variables

LOOKUP_ADMIN_KEY
Khóa quản trị để truy cập API tra cứu.

LOCKET_BEARER_TOKEN
Token phiên API Locket hợp lệ, được phép sử dụng.
Đây là biến tùy chọn.

Không đưa token thật lên GitHub.

## Kiểm tra

Mở đường dẫn trang chủ sau khi deploy.

Ví dụ:

https://locket.cam/vt.l

Trang web sẽ tự tách username:

vt.l

Nếu chưa có LOCKET_BEARER_TOKEN, kết quả sẽ có:

{
  "username": "vt.l",
  "uid": null,
  "status": "not_configured"
}

## Giới hạn

API getUserByUsername không phải API chính thức
được Locket bảo đảm hỗ trợ.

Endpoint có thể thay đổi hoặc yêu cầu App Check.

Project không vượt qua xác thực hoặc lấy
thông tin đăng nhập của người dùng.

Project không cấp Gold, không thay đổi quyền
thuê bao và không lưu UID vào database.

## Kiểm tra cục bộ

Cài thư viện:

python -m pip install -r requirements.txt

Chạy server:

uvicorn app:app --reload

Mở:

http://127.0.0.1:8000

Cần đặt LOOKUP_ADMIN_KEY trong môi trường
trước khi thử API.

Nên bật Vercel Deployment Protection hoặc
giới hạn tốc độ trước khi sử dụng nhiều người.
