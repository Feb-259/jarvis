# JARVIS — Roadmap 10 sprint

## Đích đến

Xây một trợ lý cá nhân chạy local, giao tiếp tự nhiên bằng text và giọng nói,
nhớ thông tin người dùng cho phép lưu, và dùng một số công cụ giao tiếp hữu
hạn khi được cấp quyền rõ ràng.

“Giống JARVIS” ở đây là định hướng trải nghiệm hội thoại, không phải sao chép
nhân vật hay xây hệ thống điều khiển như trong phim. JARVIS **không** được
phép tự ý điều khiển máy tính, chạy shell, đọc toàn bộ file, gửi thông tin
hoặc thực hiện hành động ngoài phạm vi đã cấp.

## Phạm vi và giả định

- Mỗi sprint dự kiến **3 ngày làm việc**; tổng kế hoạch là 30 ngày làm việc,
  không tính thời gian chờ quyết định, cài đặt/tải model hoặc xử lý blocker.
- Triển khai ban đầu trên máy Windows cá nhân, Ollama và model local.
- Giao diện đầu tiên là terminal; chỉ mở rộng giao diện nếu cần sau khi luồng
  trợ lý ổn định.
- STT/TTS chạy local trong lúc sử dụng. Nếu tải phần mềm/model cần Internet,
  tài liệu phải nói rõ; không được gọi đó là chạy hoàn toàn offline trước khi
  xác minh.
- Workflow phê duyệt được đưa vào roadmap sau nền tảng voice, nhưng chưa phải
  ưu tiên ngay lúc này.
- Trạng thái mặc định là `Chưa bắt đầu`. Code đã tồn tại không đồng nghĩa
  sprint đã hoàn tất hoặc đã go-live.

## Tổng quan

| Sprint | Kết quả chính | Trạng thái |
|---|---|---|
| 1 | Nền tảng chat local ổn định, có lịch sử hội thoại | Đang thực hiện; Ollama API đã hoạt động, block chính ở Docker/PostgreSQL |
| 2 | Voice terminal offline: STT → chat → TTS | Chưa bắt đầu |
| 3 | Trải nghiệm hội thoại nhất quán, lỗi và phiên dùng rõ ràng | Chưa bắt đầu |
| 4 | Bộ nhớ cá nhân có kiểm soát, xem/sửa/xóa được | Chưa bắt đầu |
| 5 | Kiến trúc agent và tool registry an toàn, ban đầu chỉ read-only | Chưa bắt đầu |
| 6 | Quyền hạn tối thiểu, phê duyệt, hết hạn và audit | Chưa bắt đầu |
| 7 | Tích hợp công cụ giao tiếp được chọn, có giới hạn quyền | Chưa bắt đầu |
| 8 | Gia cố bảo mật, riêng tư, khôi phục và xử lý sự cố | Chưa bắt đầu |
| 9 | Tích hợp voice, memory, agent và đánh giá chất lượng end-to-end | Chưa bắt đầu |
| 10 | Đóng gói, tài liệu, kiểm tra go-live và phát hành V1 | Chưa bắt đầu |

## Sprint 1 — Nền tảng chat local

**Mục tiêu:** Người dùng chat ổn định với Ollama trên máy cá nhân; lượt chat
được lưu và hội thoại tiếp tục đúng ngữ cảnh.

**Hiện trạng code:** Đã có FastAPI, provider Ollama/mock, PostgreSQL store và
truy xuất tối đa 20 tin nhắn hội thoại. Đã xác minh API local với Ollama chạy
thành công; vẫn cần xác minh lưu/đọc PostgreSQL thật và xử lý blocker Docker
trên máy hiện tại.

**Công việc**

- [x] Kiểm tra Ollama đang chạy và model `qwen2.5:3b` sẵn sàng.
- [x] Chạy API với cấu hình Ollama và xác minh chat qua `/v1/chat`.
- [ ] Khởi chạy PostgreSQL, áp dụng schema và kiểm tra lưu/đọc hội thoại.
- [x] Kiểm tra tiếp tục hội thoại với cùng `conversation_id`.
- [ ] Kiểm tra lỗi khi Ollama hoặc PostgreSQL không sẵn sàng.
- [ ] Chốt cách khởi động/dừng từng thành phần trên Windows.

**Tiêu chí hoàn thành**

- Chat text chạy end-to-end qua Ollama local.
- Hội thoại được lưu và ngữ cảnh trước đó được gửi tới model.
- Lỗi dịch vụ có thông báo rõ, không làm mất dữ liệu âm thầm.

## Sprint 2 — Voice terminal offline

**Mục tiêu:** Nói vào microphone, nhận câu trả lời bằng giọng nói; giữ chat
text làm phương án dự phòng.

**Công việc**

- [ ] Chọn STT/TTS chạy local, tương thích Windows; đánh giá chất lượng tiếng
  Việt, license, cấu hình máy và cách cài model.
- [ ] Giải thích dependency/model cần thêm trước khi cài hoặc tải.
- [ ] Tạo thao tác terminal rõ ràng để bắt đầu/kết thúc thu âm.
- [ ] Chuyển giọng nói thành text và gửi vào API chat hiện có.
- [ ] Đọc câu trả lời bằng TTS local.
- [ ] Xử lý lỗi microphone, thiết bị phát, STT/TTS và cho phép chuyển về text.

**Tiêu chí hoàn thành**

- Hoàn tất một lượt nói → nhận dạng → trả lời → phát giọng nói trên Windows.
- Không gọi dịch vụ STT/TTS cloud trong lúc sử dụng.
- Lỗi voice không làm người dùng mất khả năng chat text.

## Sprint 3 — Trải nghiệm hội thoại

**Mục tiêu:** Làm luồng tương tác dễ dùng và nhất quán trước khi thêm khả năng
agent.

**Công việc**

- [ ] Chuẩn hóa vòng đời phiên: tạo hội thoại, tiếp tục, kết thúc và bắt đầu
  hội thoại mới.
- [ ] Hiển thị transcript nhận dạng, câu trả lời và trạng thái đang nghe/đang
  xử lý/đang nói.
- [ ] Thêm cách hủy thao tác hoặc dừng phát giọng nói khi khả thi với engine
  đã chọn.
- [ ] Giữ lỗi kỹ thuật riêng với câu trả lời của model; không báo thành công
  giả.
- [ ] Kiểm tra nhiều lượt trao đổi liên tiếp và chuyển text ↔ voice.

**Tiêu chí hoàn thành**

- Người dùng nhận biết JARVIS đang ở trạng thái nào và có thể bắt đầu hội
  thoại mới hoặc tiếp tục hội thoại cũ.
- Có thể phục hồi từ lỗi một lượt mà không phải khởi động lại toàn bộ ứng
  dụng.

## Sprint 4 — Bộ nhớ cá nhân có kiểm soát

**Mục tiêu:** Cho phép cá nhân hóa qua thông tin người dùng chủ động cho lưu,
không tự biến toàn bộ lịch sử thành hồ sơ lâu dài.

**Công việc**

- [ ] Phân biệt lịch sử hội thoại với memory dài hạn.
- [ ] Chỉ lưu memory qua thao tác/ý định lưu rõ ràng của người dùng.
- [ ] Xác định cấu trúc, nguồn gốc và thời điểm tạo/cập nhật memory.
- [ ] Cho phép liệt kê, xem, sửa, xóa memory và tắt tính năng.
- [ ] Đặt giới hạn dữ liệu đưa vào prompt và không lưu secrets nhạy cảm theo
  mặc định.
- [ ] Kiểm thử memory không rò rỉ giữa các conversation/user boundary dự kiến.

**Tiêu chí hoàn thành**

- Người dùng biết JARVIS đang nhớ gì và có thể sửa/xóa/tắt.
- Model chỉ nhận phần memory liên quan và được phép sử dụng.
- Xóa memory có hiệu lực với các lần gọi model tiếp theo.

## Sprint 5 — Nền tảng agent và tool an toàn

**Mục tiêu:** Cho model đề xuất gọi công cụ qua giao diện có cấu trúc; ứng
dụng kiểm tra và thực thi, không giao quyền tùy ý cho model.

**Công việc**

- [ ] Thiết kế tool registry với schema input/output, mô tả, chủ sở hữu quyền
  và mức rủi ro cho từng tool.
- [ ] Tách ý định gọi tool của model khỏi quyết định cho phép của ứng dụng.
- [ ] Từ chối tool không đăng ký, input sai schema và payload vượt giới hạn.
- [ ] Tạo một tool mẫu chỉ đọc, vô hại và xác định (ví dụ xem ngày/giờ local).
- [ ] Ghi log tool được đề xuất, kết quả và lý do từ chối.
- [ ] Không thêm shell tùy ý, thực thi code, truy cập file tổng quát hay điều
  khiển UI.

**Tiêu chí hoàn thành**

- Chỉ tool được đăng ký mới có thể được gọi.
- Model không thể tự nâng quyền hoặc quyết định policy.
- Tool mẫu có test cho input hợp lệ, input không hợp lệ và lỗi thực thi.

## Sprint 6 — Permission và workflow phê duyệt

**Mục tiêu:** Người dùng cấp quyền có phạm vi rõ; thao tác cần xác nhận không
được chạy trước khi người dùng chấp thuận.

**Công việc**

- [ ] Định nghĩa mức quyền tối thiểu: read-only, thao tác cục bộ có thể đảo
  ngược, và thao tác cần phê duyệt.
- [ ] Gắn mỗi quyền vào tool cụ thể, phạm vi dữ liệu và thời hạn; mặc định
  deny khi chưa cấp quyền.
- [ ] Tạo yêu cầu phê duyệt hiển thị rõ hành động và dữ liệu sắp dùng.
- [ ] Thực thi đúng một lần sau khi được duyệt; xử lý từ chối, hết hạn, hủy và
  quyết định lặp.
- [ ] Không cho phép approval cũ dùng lại với payload khác.
- [ ] Lưu audit trail cho yêu cầu, quyết định và kết quả.

**Tiêu chí hoàn thành**

- Hành động cần duyệt không chạy khi pending, bị từ chối hoặc hết hạn.
- Chỉ đúng payload/phạm vi đã trình bày mới được thực thi.
- Trạng thái và audit có test tự động; lỗi không tạo trạng thái thành công giả.

## Sprint 7 — Tích hợp công cụ giao tiếp

**Mục tiêu:** Thêm từng khả năng giao tiếp hữu ích, không biến JARVIS thành
agent điều khiển máy tính tổng quát.

**Phạm vi gợi ý; chọn provider và tài khoản cụ thể trước khi triển khai**

- [ ] Tool lịch ở chế độ chỉ đọc để xem lịch/sự kiện được cấp quyền.
- [ ] Ghi chú hoặc nhắc việc cá nhân với xác nhận phù hợp trước khi ghi.
- [ ] Tìm kiếm thông tin online chỉ khi người dùng bật tính năng; phân biệt
  nội dung web không đáng tin với chỉ dẫn hệ thống.
- [ ] Email/tin nhắn chỉ xem khi đã cấp quyền hẹp; gửi luôn cần xác nhận nội
  dung và người nhận ngay trước khi gửi.
- [ ] Mỗi tích hợp có quyền thu hồi riêng, xử lý token an toàn và test lỗi /
  giới hạn API.

**Tiêu chí hoàn thành**

- Chỉ tích hợp được người dùng chọn và cấp quyền mới hoạt động.
- Thao tác ghi/gửi có xác nhận đúng lúc; không gửi nhầm người nhận hoặc nội
  dung khi dữ liệu thay đổi.
- Nếu chưa chốt provider/tài khoản hoặc secrets management, mục tương ứng
  được để ngoài phạm vi thay vì giả lập go-live.

## Sprint 8 — Bảo mật, riêng tư và độ tin cậy

**Mục tiêu:** Giảm rủi ro khi dùng agent có memory và tích hợp dữ liệu cá nhân.

**Công việc**

- [ ] Rà soát ranh giới tin cậy: prompt injection từ web/tài liệu không được
  phép thay đổi system policy hoặc cấp quyền.
- [ ] Giới hạn kích thước/rate của request, lịch sử, tool input và thời gian
  chờ; ghi log đủ để chẩn đoán nhưng không chứa secrets.
- [ ] Kiểm tra bind loopback, CORS và các endpoint không chủ định công khai.
- [ ] Quy định retention và cách xóa hội thoại, memory, approval, audit.
- [ ] Bảo vệ backup/database và xác minh quy trình restore.
- [ ] Kiểm tra secrets không nằm trong source, log hoặc prompt ngoài ý muốn.
- [ ] Kiểm thử lỗi model/database, timeout, restart và dữ liệu không hợp lệ.

**Tiêu chí hoàn thành**

- Các ranh giới quyền được cưỡng chế trong code, không chỉ dựa vào prompt.
- Có quy trình backup/restore và xóa dữ liệu được kiểm tra.
- Không còn lỗi nghiêm trọng đã biết trong luồng chat, memory, permission và
  tool được chọn cho V1.

## Sprint 9 — Tích hợp agent giao tiếp end-to-end

**Mục tiêu:** Kết hợp hội thoại, voice, memory, tool và permission thành trải
nghiệm nhất quán, vẫn để người dùng giữ quyền quyết định.

**Công việc**

- [ ] Chạy các kịch bản thực tế: hỏi đáp, tiếp tục hội thoại, nhớ/xóa memory,
  tra cứu read-only và yêu cầu hành động cần duyệt.
- [ ] Xác nhận voice transcript, tool proposal và kết quả đều hiển thị/nghe
  được rõ ràng.
- [ ] Đo thời gian phản hồi trên máy mục tiêu; xử lý chờ/hủy mà không tạo
  thao tác trùng.
- [ ] Xây bộ đánh giá tiếng Việt và kiểm tra tính chính xác, từ chối quyền
  không phù hợp, không bịa rằng tool đã chạy.
- [ ] Chạy kiểm thử regression, quyền chéo, prompt injection cơ bản và lỗi
  tích hợp.
- [ ] Sửa các lỗi ưu tiên; giới hạn rõ khả năng chưa đáng tin.

**Tiêu chí hoàn thành**

- Kịch bản đầu-cuối chạy được lặp lại và cho kết quả quan sát được.
- Không có tool nào được gọi chỉ vì model nói rằng nó đã gọi.
- Người dùng nhìn/nghe được lúc nào JARVIS đang suy luận, chờ quyền hoặc gặp
  lỗi.

## Sprint 10 — Đóng gói và go-live V1

**Mục tiêu:** Cài đặt, khởi động, sử dụng, sao lưu và xử lý sự cố theo hướng
dẫn trên máy Windows cá nhân.

**Công việc**

- [ ] Chuẩn hóa cấu hình, kiểm tra dependency/model, startup/shutdown và
  thông báo lỗi dễ hiểu.
- [ ] Viết hướng dẫn cài mới, cập nhật, cấu hình local, quyền tích hợp, backup
  và gỡ cài đặt/xóa dữ liệu.
- [ ] Chạy test tự động, lint và checklist thủ công trên đúng máy mục tiêu.
- [ ] Xác minh microphone/loa, Ollama, database, memory, tool permission và
  restore từ backup.
- [ ] Kiểm tra lại bind local, secrets, log, retention và không gửi dữ liệu
  ngoài phạm vi đã công bố.
- [ ] Ghi known limitations, phương án rollback và quyết định go/no-go.

**Tiêu chí hoàn thành**

- Có thể cài và sử dụng theo tài liệu mà không cần thao tác ngầm hoặc quyền
  không được giải thích.
- Các luồng cốt lõi có test và smoke test trên máy thật đạt.
- Go-live chỉ khi không còn blocker nghiêm trọng; nếu chưa đạt thì ghi rõ
  phạm vi phát hành giới hạn, không gọi là bản hoàn chỉnh.

## Quy tắc quyền hạn cho toàn bộ roadmap

- Deny-by-default: không có quyền nếu chưa đăng ký/cấp cụ thể.
- Quyền read-only và quyền ghi/gửi tách biệt; chỉ cấp đúng phạm vi cần thiết.
- Model chỉ đề xuất; ứng dụng xác thực quyền, policy, schema và trạng thái.
- Hành động bên ngoài hoặc khó đảo ngược phải có xác nhận rõ ràng ngay trước
  khi thực thi.
- Có thể thu hồi quyền, xem lịch sử sử dụng và xóa dữ liệu.
- Không cho phép tự sửa policy, tự cấp quyền, shell tổng quát hoặc điều khiển
  thiết bị vật lý.

## Ngoài mục tiêu sản phẩm

- Điều khiển robot, xe, vũ khí, thiết bị vật lý hoặc hệ thống an toàn trọng
  yếu.
- Tự hành động ngoài giao tiếp và công cụ đã được người dùng cấp quyền.
- Tự gửi email/tin nhắn, mua hàng, đăng nội dung hoặc thay đổi dữ liệu mà
  không có xác nhận cần thiết.
- Đảm bảo mọi câu trả lời của LLM luôn chính xác; giao diện phải thể hiện sự
  không chắc chắn và cho phép người dùng kiểm chứng.

## Nhật ký và cập nhật tiến độ

- Ngày bắt đầu/kết thúc mỗi sprint được chốt lúc sprint thực sự khởi động;
  không giả định sprint bắt đầu từ ngày tạo roadmap.
- Cập nhật trạng thái và ghi kết quả/blocker trong file này khi người dùng yêu
  cầu cập nhật tiến độ hoặc trước khi kết thúc phiên.
- Không tự tạo commit trừ khi người dùng yêu cầu.

| Sprint | Trạng thái | Kết quả / blocker |
|---|---|---|
| 1 | Đang thực hiện | Ollama API/model đã hoạt động; cần Docker/PostgreSQL thật để xác minh lưu hội thoại end-to-end |
| 2 | Chưa bắt đầu | Chưa chọn/cài engine STT/TTS |
| 3 | Chưa bắt đầu | Phụ thuộc trải nghiệm voice cơ bản |
| 4 | Chưa bắt đầu | Cần chốt chính sách lưu memory và retention |
| 5 | Chưa bắt đầu | Bắt đầu bằng tool read-only |
| 6 | Chưa bắt đầu | Chưa có workflow permission/approval end-to-end |
| 7 | Chưa bắt đầu | Chọn tích hợp/provider sau khi permission framework sẵn sàng |
| 8 | Chưa bắt đầu | Phạm vi test phụ thuộc các tích hợp được chọn |
| 9 | Chưa bắt đầu | Phụ thuộc các luồng cốt lõi Sprint 2–8 |
| 10 | Chưa bắt đầu | Chỉ go-live sau khi qua checklist và quyết định go/no-go |
