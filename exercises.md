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

> Lần mình deploy lên Railway quên set `AGENT_API_KEY`. Service đứng luôn,
> log báo `agent_api_key: Field required`. Nhìn là biết thiếu secret, chưa kịp
> cho `/ask` chạy. Nếu để mặc định `"changeme"` thì app vẫn sống, ai đoán được
> key là gọi API thoải mái, tiền token cháy luôn.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Log mình lấy được kiểu này:
> `{"event":"ask_completed","level":"info","timestamp":"2026-09-29T03:31:56+00:00","user_id":"sv-test","tokens_in":12,"tokens_out":18,"cost_usd":0.00003}`.
> Có JSON thì mình grep theo `event` / `user_id` / `level` để lần lỗi cho
> nhanh. Còn cộng `cost_usd` với token rồi set alert cũng làm được. Còn
> `print("đã trả lời xong")` thì chỉ là chữ, máy lọc hay tính toán gì cũng
> không ra.

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

> Mình đo bằng `docker images` luôn. Bản 1 stage lấy `python:3.11` full, để
> lại hết tool build với file tạm lúc `pip install`. Bản multi-stage dùng
> `python:3.11-slim`, stage chạy chỉ copy lib đã cài và source thôi, nên không
> kéo theo OS thừa và mấy thứ chỉ cần lúc build.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Sửa mỗi `app/main.py` thì layer base image, `WORKDIR`, copy
> `requirements.txt` và `pip install` vẫn cache. Layer `COPY . .` với mấy
> layer sau phải build lại. Nếu đưa `COPY . .` lên trước `pip install` thì sửa
> source cái là layer copy đổi, pip chạy lại từ đầu dù `requirements.txt`
> không đụng tới, build lâu hơn hẳn.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Code Python bị lỗ hổng thì attacker có thể chạy lệnh trong container. Mà
> process đang là root thì lệnh đó cũng root luôn. Rồi nếu mount lung tung
> hoặc quyền container rộng, họ đọc secret, sửa file, thậm chí nhảy ra host.
> `USER appuser` chặn ngay lúc chạy lệnh: code bị chiếm chỉ còn UID 10001,
> quyền hẹp, không còn mặc định root nữa.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Được tối đa 20 request trong khoảng 2 giây. Cách làm: spam 10 request lúc
> `10:00:59` gần hết phút, đợi reset lúc `10:01:00` rồi bắn thêm 10. Mỗi phút
> vẫn chỉ thấy 10, nhưng thực tế dồn 20 phát sát nhau. Sliding window 60s thì
> lách kiểu này không được.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit đếm số request trong 60 giây. Cost guard thì nhìn tổng tiền của
> user trong tháng. Ví dụ gửi ít request nhưng mỗi phát nuốt nhiều token thì
> rate limit vẫn cho qua, cost guard cắt khi hết budget. Ngược lại còn tiền
> nhưng request thứ 11 trong một phút thì rate limit chặn, cost guard thì
> không quan tâm vì chưa cháy tiền.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Gộp health với check Redis thì Redis sập 30 giây là cả 3 container bị đánh
> unhealthy dù Python vẫn chạy. Orchestrator đá ra rồi restart. Container mới
> lên cũng không nối được Redis nên lại unhealthy, restart vòng vòng, service
> chết hết. Redis sống lại thì instance mới pass check rồi mới nhận traffic.
> Tách `/health` với `/ready` thì process không bị restart oan, `/ready` chỉ
> báo là chưa sẵn sàng nhận request phụ thuộc Redis.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Redis thì 3 instance dùng chung lịch sử nên `history_length` tăng đều,
> request rơi container nào cũng vậy. Đổi sang dict Python thì mỗi container
> một dict riêng: đụng lại đúng container thì số tăng, load balancer chuyển
> container khác thì số tụt hoặc về 0. Container restart là mất sạch history
> trong dict luôn.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi mình gặp: `POST /ask` với `/ready` trả `500 Internal Server Error`. Mở
> `railway logs` thấy traceback Pydantic `agent_api_key: Field required`.
> Check Variables của service app thì lúc đó chỉ có `REDIS_URL`, quên đẩy
> `AGENT_API_KEY` từ `.env` lên Railway. Mình add `AGENT_API_KEY` vào
> Variables, giữ `REDIS_URL=${{Redis.REDIS_URL}}`, đợi redeploy rồi test lại:
> `/health` `/ready` 200, `/ask` không có key thì 401 đúng như mong đợi.
