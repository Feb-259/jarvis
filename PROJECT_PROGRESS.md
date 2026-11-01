# JARVIS — Theo dõi tiến độ

Cập nhật gần nhất: 2026-10-30

Đây là bản ghi tiến độ hiện tại và lịch sử cập nhật của dự án. Khi bắt đầu
phiên làm việc mới, hãy đọc file này trước, sau đó kiểm tra workspace thực tế
để xác minh trạng thái.

## Trạng thái hiện tại

**Giai đoạn:** Đang thực hiện Sprint 1 — xác minh nền tảng chat local.
Workflow phê duyệt được để lại ngoài phạm vi hiện tại.

### Đã có

- API FastAPI với endpoint `/health` và `/v1/chat`.
- Giao diện LLM provider độc lập, provider mock mặc định và adapter Ollama
  (`qwen2.5:3b`).
- Lưu lượt chat thành công qua `ConversationStore`, có implementation
  PostgreSQL và migration schema.
- Với hội thoại đã có `conversation_id`, truy xuất tối đa 20 tin nhắn gần
  nhất theo thứ tự thời gian và gửi chúng làm ngữ cảnh cho provider.
- Chính sách xác định mức rủi ro hành động, từ chối hành động bị cấm và yêu
  cầu phê duyệt cho hành động consequential.
- Test cho API, Ollama adapter, policy và PostgreSQL.

### Chưa hoàn thành

- Chưa có voice I/O (STT → trợ lý → TTS).
- Chưa xác minh lưu/đọc hội thoại end-to-end với PostgreSQL thật.
- Docker Desktop được báo đã cài thành công, nhưng terminal hiện chưa nhận
  lệnh `docker`; chưa thể khởi động PostgreSQL bằng Docker Compose.
- Chưa xác minh STT/TTS offline trên Windows.

### Sprint 1 — Tiến độ hiện tại

- Ollama API local hoạt động và model `qwen2.5:3b` đã trả lời request.
- Smoke test API `/v1/chat` qua Ollama đã chạy thành công; request thứ hai
  dùng lại cùng `conversation_id` và kiểm chứng history được gửi tới provider.
- Smoke test API trên dùng store trong bộ nhớ để kiểm tra luồng ứng dụng,
  **không** xác minh dữ liệu được lưu bền vững qua PostgreSQL.
- PostgreSQL chưa hoạt động ở `127.0.0.1:5432`; máy không tìm thấy Docker CLI
  trong terminal tại lần kiểm tra gần nhất.
- Người dùng đã cài Docker Desktop qua `winget`; sau cài đặt, lệnh `docker`
  vẫn chưa được nhận diện. Cần reboot nếu chưa reboot sau khi bật WSL, mở
  Docker Desktop/chờ Engine sẵn sàng, rồi mở terminal mới và kiểm tra lại.
- Sprint 1: **Đang thực hiện, bị block tại thiết lập Docker/PostgreSQL**;
  chưa đánh dấu hoàn thành.

### Kiểm chứng gần nhất

- Lệnh: `.\.venv\Scripts\python.exe -m pytest -q`
- Kết quả: **23 passed**, 1 cảnh báo deprecation của Starlette liên quan đến
  `httpx`/`starlette.testclient`.
- Lệnh: `.\.venv\Scripts\ruff.exe check src tests`
- Kết quả: **All checks passed**.
- Đây là kết quả kiểm thử tự động; không đồng nghĩa đã xác minh các dịch vụ
  Ollama/PostgreSQL bên ngoài.

### Trạng thái Git

- Nhánh hiện tại: `master`.
- Dự án hiện được giữ hoàn toàn local; chưa cần tạo commit. Các tệp dự án
  đang là untracked, phù hợp với trạng thái làm việc hiện tại.

## Bước tiếp theo đề xuất

Tiếp tục theo [SPRINT_PLAN.md](SPRINT_PLAN.md), Sprint 1:

1. Hoàn tất reboot Windows nếu chưa khởi động lại sau khi bật WSL; khởi động Docker
   Desktop và đợi Docker Engine sẵn sàng.
2. Mở terminal mới, kiểm tra `docker --version`, `docker compose version` và
   `docker info`. Nếu CLI vẫn không tìm thấy, kiểm tra PATH và file
   `C:\Program Files\Docker\Docker\resources\bin\docker.exe`.
3. Chạy `docker compose up -d postgres`, xác nhận container healthy và cấu
   hình database theo `.env.example`/`docker-compose.yml`.
4. Áp dụng `migrations\001_initial.sql`; kiểm tra chat API lưu và đọc lại lịch
   sử thật từ PostgreSQL, rồi xác minh lỗi khi dịch vụ không sẵn sàng.

Workflow phê duyệt và thực thi hành động hiện nằm ngoài phạm vi V1.

## Lịch sử cập nhật

| Ngày | Cập nhật |
|---|---|
| 2026-10-30 | Ghi nhận trạng thái nền tảng MVP; xác nhận 20 test đạt; thống nhất truy xuất ngữ cảnh hội thoại là bước tiếp theo. |
| 2026-10-30 | Xác nhận dự án tiếp tục làm việc local; chưa cần commit. |
| 2026-10-30 | Thêm truy xuất tối đa 20 tin nhắn hội thoại làm ngữ cảnh; xác nhận 23 test đạt và Ruff sạch. |
| 2026-10-30 | Xác định ưu tiên V1 local gồm chat Ollama và voice terminal offline; tạo kế hoạch Sprint 1 dài 3 ngày. |
| 2026-10-30 | Bắt đầu xác minh Sprint 1: Ollama và smoke test API hoạt động; PostgreSQL chưa chạy do Docker CLI chưa được nhận diện sau khi cài Docker Desktop. |

## Quy ước cập nhật file

- Khi bắt đầu phiên mới, đọc phần trạng thái này và kiểm tra code/test hiện
  tại; không coi ghi chú thay thế cho việc kiểm tra workspace.
- Không cập nhật file tiến độ sau mỗi thay đổi trong phiên.
- Chỉ cập nhật file khi người dùng yêu cầu, hoặc khi chuẩn bị kết thúc phiên;
  khi đó ghi trạng thái, kết quả kiểm chứng và thêm một dòng vào lịch sử cập
  nhật.
- Nếu thông tin trong file khác với code thực tế, code và kết quả kiểm thử
  hiện tại là nguồn sự thật; sửa file theo bằng chứng mới.
