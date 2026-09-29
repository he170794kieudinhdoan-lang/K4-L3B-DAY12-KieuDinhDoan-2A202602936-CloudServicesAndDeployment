"""CP3 — Xác thực bằng API key.

Public URL = ai cũng gọi được. Không có lớp này, hóa đơn LLM của bạn do
người lạ quyết định.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Kiểm tra header ``X-API-Key``; trả về user_id nếu hợp lệ.

    TODO (CP3):
      1. Lấy khóa đúng từ ``get_settings().agent_api_key``.
      2. Nếu ``x_api_key`` là None hoặc không khớp → raise
         ``HTTPException(status_code=401, detail="invalid or missing API key")``.
      3. So sánh bằng ``secrets.compare_digest(a, b)``, **không dùng** ``==``.
         Toán tử ``==`` dừng ngay tại ký tự đầu khác nhau, nên thời gian trả
         lời rò rỉ thông tin về khóa (timing attack). ``compare_digest`` luôn
         chạy hết chuỗi.
      4. Hợp lệ → trả về ``x_user_id`` nếu client có gửi, ngược lại trả
         ``ANONYMOUS_USER``. user_id này là đơn vị để rate limit và tính chi phí.

    Gợi ý: dùng ``status.HTTP_401_UNAUTHORIZED`` cho dễ đọc.
    """
    # Khóa đúng lấy từ môi trường (AGENT_API_KEY), không viết cứng trong source.
    expected_key = get_settings().agent_api_key
    # Thiếu header thì không có chuỗi để so. compare_digest chỉ nhận str/bytes,
    # truyền None vào sẽ ném TypeError thay vì 401.
    missing_key = x_api_key is None
    # So hết cả hai chuỗi, không dừng ở ký tự khác đầu tiên như toán tử ==.
    # Nhờ vậy thời gian phản hồi không hé lộ khóa đang đúng đến đâu.
    key_matches = (not missing_key) and secrets.compare_digest(x_api_key, expected_key)
    if not key_matches:
        # 401: không có khóa, hoặc khóa gửi lên không trùng khóa cấu hình.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )
    # Client gửi X-User-Id thì dùng giá trị đó làm đơn vị rate limit và chi phí.
    # Không gửi (None hoặc chuỗi rỗng) thì gom vào một user ẩn danh.
    return x_user_id or ANONYMOUS_USER
