# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay từng dòng giữ chỗ bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Kiều Đình Đoàn  Mã học viên: 2A202602936

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Ví dụ khi deploy lên Railway, nếu tôi quên đặt `AGENT_API_KEY` thì service
> dừng ngay với lỗi validation `agent_api_key: Field required`. Nhờ vậy tôi
> biết cấu hình production đang thiếu secret trước khi endpoint `/ask` hoạt
> động. Nếu dùng mặc định `"changeme"`, service vẫn chạy và người khác có thể
> đoán được khóa, gọi API công khai và làm phát sinh chi phí.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Một dòng log thu được có dạng:
> `{"event":"ask_completed","level":"info","timestamp":"2026-09-29T03:31:56+00:00","user_id":"sv-test","tokens_in":12,"tokens_out":18,"cost_usd":0.00003}`.
> Với log JSON, tôi có thể lọc chính xác theo `event`, `user_id` hoặc `level`
> để điều tra lỗi; đồng thời có thể tổng hợp `cost_usd`, token và tạo cảnh báo
> tự động. Chuỗi `print("đã trả lời xong")` không có các trường dữ liệu ổn
> định để máy lọc hay tính toán.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.73 GB |
| Multi-stage | 272 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Tôi đo bằng `docker images` trên máy. Bản một stage dùng image
> `python:3.11` đầy đủ và giữ lại toàn bộ công cụ, file trung gian dùng trong
> lúc cài dependency. Bản multi-stage dùng `python:3.11-slim`; stage runtime
> chỉ nhận thư viện đã cài từ builder và source cần chạy, nên không mang theo
> phần hệ điều hành và công cụ build không cần thiết.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi chỉ sửa `app/main.py`, các layer lấy base image, đặt `WORKDIR`, copy
> `requirements.txt` và chạy `pip install` vẫn được lấy từ cache. Layer
> `COPY . .` và các layer đứng sau nó phải chạy lại. Nếu đặt `COPY . .`
> trước `RUN pip install`, mọi thay đổi source đều làm layer copy đổi, kéo
> theo việc cài lại toàn bộ dependency dù `requirements.txt` không thay đổi,
> khiến build chậm hơn nhiều.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Một lỗ hổng Python có thể cho kẻ tấn công thực thi lệnh trong container.
> Nếu tiến trình chạy bằng root, các lệnh đó cũng có quyền root trong
> container; kết hợp với lỗi runtime, cấu hình mount nhạy cảm hoặc quyền
> container quá rộng, kẻ tấn công có thể đọc secret, sửa filesystem hay thoát
> ra host với quyền cao. `USER appuser` cắt chuỗi ở bước thực thi lệnh: mã bị
> chiếm quyền chỉ có UID 10001 với quyền hạn chế, không còn mặc định là root.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Người dùng có thể gửi tối đa 20 request trong khoảng 2 giây: gửi 10 request
> ngay trước khi phút hiện tại kết thúc, ví dụ lúc `10:00:59`, rồi gửi thêm
> 10 request ngay sau khi bộ đếm reset lúc `10:01:00`. Mỗi phút riêng vẫn chỉ
> ghi nhận 10 request, nhưng lưu lượng thực tế bị dồn thành 20 request sát
> nhau. Sliding window 60 giây ngăn được cách lách ranh giới này.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn số request trong 60 giây, còn cost guard giới hạn tổng
> tiền của từng user trong tháng. Một user gửi ít request nhưng mỗi request
> dùng rất nhiều token vẫn qua rate limit, trong khi cost guard phải chặn khi
> vượt ngân sách. Ngược lại, user còn nguyên ngân sách nhưng gửi request thứ
> 11 trong một phút sẽ bị rate limit chặn, dù cost guard vẫn cho phép về mặt
> chi phí.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu endpoint liveness cũng kiểm tra Redis, khi Redis mất kết nối thì cả ba
> container lần lượt bị đánh dấu unhealthy dù tiến trình Python vẫn sống.
> Orchestrator sẽ loại chúng khỏi phục vụ và khởi động lại, nhưng container
> mới vẫn không kết nối được Redis nên tiếp tục unhealthy, tạo thành vòng lặp
> restart và làm toàn bộ service gián đoạn. Khi Redis hoạt động lại, các
> container mới vượt health check và được đưa vào phục vụ. Tách `/health`
> khỏi `/ready` giúp tiến trình không bị restart vô ích, còn `/ready` vẫn báo
> rằng instance chưa sẵn sàng nhận traffic phụ thuộc Redis.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Khi dùng Redis, cả ba instance đọc và ghi cùng một lịch sử nên
> `history_length` tăng nhất quán dù request được chuyển tới container nào.
> Nếu dùng dict Python, mỗi container có một dict riêng: request gặp lại cùng
> container thì số tăng, nhưng khi load balancer chuyển sang container khác
> thì số có thể giảm hoặc quay về 0. Khi container restart, toàn bộ lịch sử
> trong dict của container đó cũng bị mất.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi tôi gặp là `POST /ask` và `/ready` trả `500 Internal Server Error`.
> Tôi chạy `railway logs` và thấy traceback của Pydantic:
> `agent_api_key: Field required`. Kiểm tra danh sách biến của đúng service
> app cho thấy lúc đó chỉ có `REDIS_URL`; `AGENT_API_KEY` chưa được chuyển từ
> file `.env` cục bộ lên Railway. Tôi thêm `AGENT_API_KEY` vào Variables của
> service app, giữ `REDIS_URL=${{Redis.REDIS_URL}}`, chờ Railway redeploy rồi
> kiểm tra lại: `/health` và `/ready` trả 200, còn `/ask` không gửi key trả
> đúng 401.
