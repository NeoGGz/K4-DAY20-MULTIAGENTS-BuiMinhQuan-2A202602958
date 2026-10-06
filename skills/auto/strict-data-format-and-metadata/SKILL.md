---
name: strict-data-format-and-metadata
description: DÙNG KHI NÀO thực hiện xử lý dữ liệu và xuất tệp kết quả (như JSON hoặc CSV) để đảm bảo định dạng tiền tệ, cấu trúc meta và chuẩn hóa trường dữ liệu chính xác.
---
1. Đọc và tuân thủ tuyệt đối các quy tắc định dạng đầu ra (ví dụ: tiền tệ phải tính bằng cent dạng số nguyên, tên cột CSV, định dạng thời gian UTC).
2. Kiểm tra xem tệp kết quả có yêu cầu khối siêu dữ liệu (`meta`) chứa thông tin nguồn, số dòng đầu vào (bao gồm cả dòng trùng) và số dòng được sử dụng hay không.
3. Xử lý chuẩn hóa toàn bộ các trường văn bản (như viết hoa, loại bỏ khoảng trắng thừa) và chuẩn hóa định dạng thời gian về chuẩn ISO / UTC.
4. Kiểm tra lại toàn bộ tệp kết quả bằng tập lệnh kiểm tra trước khi hoàn thành để đảm bảo không bỏ sót bất kỳ ràng buộc định dạng nào.
