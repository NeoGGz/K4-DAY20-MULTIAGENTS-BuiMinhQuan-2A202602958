---
name: enforce-code-quality-and-rules
description: DÙNG KHI NÀO trước khi hoàn thành tác vụ lập trình để đảm bảo tuân thủ toàn bộ các quy tắc về kiểu dữ liệu, nhật ký thay đổi và kiểm thử.
---
1. Đọc kỹ tất cả các quy tắc (RULE) trong yêu cầu bài toán trước khi bắt đầu viết hoặc sửa mã.
2. Kiểm tra nghiêm ngặt việc thêm type hints cho tất cả các tham số và giá trị trả về của mọi hàm công khai.
3. Tuyệt đối không chỉnh sửa hoặc xóa các tệp kiểm thử có sẵn (chỉ được phép tạo tệp kiểm thử mới nếu cần).
4. Viết đầy đủ các tệp kiểm thử hồi quy (regression tests) cho từng lỗi đã được sửa theo đúng quy định.
5. Ghi lại đầy đủ mọi thay đổi/sửa lỗi vào tệp nhật ký (CHANGELOG.md) theo đúng định dạng và đề mục yêu cầu.
