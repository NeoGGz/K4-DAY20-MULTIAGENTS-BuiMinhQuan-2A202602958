# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Bùi Minh Quân | 2A202602958 | Toàn bộ bài thực hành |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite`, `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows (chạy trực tiếp với POSIX /bin/sh shell tích hợp Git sh utilities)
- Số lần chạy tác vụ đã dùng / ngân sách: 9 / 24
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Điều kiện `subagents` sẽ đạt điểm tương đương hoặc chỉ nhỉnh hơn một chút so với `baseline` trên các tác vụ đánh giá (dự kiến trung bình ~0.60 - 0.65), do tác tử chính thường tự giải quyết các bước kỹ thuật tốt mà ít khi ủy quyền hoàn toàn cho subagent, trong khi chi phí token của `subagents` sẽ cao hơn khoảng 30% - 50% so với baseline do chi phí ngữ cảnh phân nhánh và tổng hợp báo cáo.
- H2 (skills-auto so với baseline): Điều kiện `skills-auto` sẽ đạt điểm cao hơn `baseline` trên các tác vụ học (từ ~0.63 lên ~0.70+ nhờ nạp các checklist quy ước của Acme), nhưng trên các tác vụ đánh giá (`eval`), mức độ cải thiện sẽ bị giới hạn hoặc xảy ra hiện tượng quá khớp (overfitting) theo phát hiện của SkillEvolBench, vì các tác vụ đánh giá chứa các quy ước tổ chức mới (`rule_`) mà bộ kỹ năng tự sinh từ tập học chưa từng thấy.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình của điều kiện `skills-auto` trên tác vụ học sẽ cao hơn đáng kể so với trên tác vụ đánh giá (dự kiến chênh lệch khoảng 0.10 - 0.20 điểm), phản ánh sự suy giảm hiệu quả chuyển giao tri thức thủ tục (procedural knowledge transfer gap) giữa dữ liệu đã biết và dữ liệu mới chưa qua tuyển chọn kỹ năng.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ:
   - Các công cụ tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Công cụ chạy lệnh shell: `execute`.
   - Công cụ giao việc cho tác tử con: `task`.
   Công cụ cho phép chạy lệnh shell là `execute`.

2. Mô tả của công cụ `task` về subagent `general-purpose`:
   - "General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. This agent has access to all tools as the main agent."
   - Về ngữ cảnh: subagent này là "stateless by default", chỉ nhìn thấy nội dung prompt mà tác tử chính gửi cho nó và trả về một báo cáo cuối cùng ("the agent sees only the prompt you give it and returns a single final report"), không nhìn thấy toàn bộ ngữ cảnh hội thoại trung gian của tác tử chính trừ khi được chỉ định kế thừa hội thoại.

3. Hướng dẫn hành vi trích từ mô tả:
   - Từ mô tả công cụ `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return."
   - Từ mô tả công cụ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | B. Không kiểm chứng | `the original files in tests/ must not be modified (new test files are allowed)` |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `RULE: every public function (name not starting with '_') in the package has type annotations...` |
| `code-learn` | `rule_regression_tests` | E. Vi phạm quy ước tổ chức | `RULE: add tests/test_regressions.py with one test function per bug you fixed...` |
| `code-learn` | `rule_changelog` | E. Vi phạm quy ước tổ chức | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet...` |
| `data-learn` | `rule_money_in_cents` | E. Vi phạm quy ước tổ chức | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| `data-learn` | `rule_meta_block` | E. Vi phạm quy ước tổ chức | `RULE: answer.json has an object meta = {"source": ..., "rows_in": ..., "rows_used": ...}` |
| `data-learn` | `rule_clean_csv` | E. Vi phạm quy ước tổ chức | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents...` |
| `logs-learn` | `rule_service_names` | E. Vi phạm quy ước tổ chức | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| `logs-learn` | `rule_sorted_errors` | E. Vi phạm quy ước tổ chức | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E. Vi phạm quy ước tổ chức | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Nhận xét: Nhóm E (Vi phạm quy ước tổ chức) chiếm đa số tuyệt đối (9/10 check thất bại, tức 90%). Trong khi đó, các check kỹ thuật đạt 17/18 (94.4%). Điều này chứng tỏ mô hình có năng lực giải quyết vấn đề kỹ thuật rất tốt, nhưng do các quy ước tổ chức không nằm trong đề bài chính mà là quy ước ngầm của tổ chức, tác tử mặc định không thể biết trước. Do đó, các skill do curator trích xuất hoàn toàn có thể phòng ngừa hiệu quả các lỗi nhóm E này bằng cách cung cấp danh sách checklist quy ước.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Chuyên đọc tệp, khảo sát mã nguồn, tài liệu và dữ liệu ban đầu mà không sửa đổi tệp, giúp tác tử chính nắm thông tin khách quan.
  2. `implementer`: Chuyên thực hiện chỉnh sửa mã nguồn, chạy script và kiểm thử qua công cụ shell `execute`.
  3. `reviewer`: Độc lập rà soát lại không gian làm việc so với các ràng buộc đề bài và trường hợp biên trước khi báo cáo kết thúc.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 1 lần gọi (ủy quyền phân tích kiểm thử cho `implementer`).
  - `data-learn`: 1 lần gọi (ủy quyền phân tích kiểm tra dữ liệu).
  - `logs-learn`: 0 lần gọi (tác tử chính tự nhận thấy tác vụ parse log đơn giản và tự giải quyết).
- Thông tin thiếu hoặc thừa khi giao việc: Tác tử chính khi giao việc đã cung cấp tương đối đủ tên tệp và mục tiêu, tuy nhiên do subagent bị cô lập ngữ cảnh (context isolation), kết quả trả về của subagent cần thêm một bước tích hợp lại vào luồng chính.
- Ảnh hưởng đến token và thời gian: Chi phí token tăng rõ rệt (trung bình 197,807 token so với 153,130 token ở baseline, tăng khoảng 29.2%), thời gian thực thi cũng tăng do các lượt hội thoại bổ sung.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy curator 1 lần, sinh ra 3 skill hoàn toàn hợp lệ, không có skill nào bị xóa.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-code-quality-and-rules` | Tổng quát cho các tác vụ lập trình (không chứa id hay đáp án) | Đúng, đưa ra checklist về type hints, kiểm thử hồi quy và changelog | 10 dòng, mô tả rõ ràng, được đọc 1 lần |
| `strict-data-format-and-metadata` | Tổng quát cho tác vụ dữ liệu dạng bảng/CSV/JSON | Đúng, nhắc nhở định dạng tiền tệ cent, khối meta và chuẩn hóa UTC | 9 dòng, mô tả đúng tình huống kích hoạt, được đọc 1 lần |
| `verify-output-schema-and-sorting` | Tổng quát cho tác vụ xuất JSON/phân tích log | Đúng, nhắc nhở schema version, quy tắc chuẩn hóa tên và sắp xếp đa cấp | 9 dòng, mô tả đúng tình huống kích hoạt, được đọc 1 lần |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
