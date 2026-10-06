---
name: verify-output-schema-and-sorting
description: DÙNG KHI NÀO tạo tệp cấu trúc JSON hoặc phân tích log để đảm bảo schema, quy tắc đặt tên trường và thứ tự sắp xếp hoàn toàn khớp yêu cầu.
---
1. Kiểm tra kỹ các yêu cầu về schema cấp cao (ví dụ: phiên bản schema, định danh công cụ tạo) trong tệp kết quả JSON.
2. Tuân thủ chính xác quy tắc đặt tên định danh (ví dụ: chữ thường, thay dấu gạch ngang bằng dấu gạch dưới cho tên dịch vụ).
3. Đảm bảo danh sách các mục kết quả được sắp xếp theo đúng các tiêu chí đa cấp (ví dụ: theo dịch vụ trước, sau đó theo thời gian tăng dần) đúng như quy tắc đề ra.
4. Đọc lại tệp kết quả hoàn chỉnh bằng tập lệnh hoặc công cụ đọc tệp để xác thực cấu trúc trước khi kết thúc tác vụ.
