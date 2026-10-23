# modules/auth.py
import requests
import streamlit as st


def get_auth_url() -> str:
  """Lấy đường dẫn URL Power Automate từ st.secrets một cách an toàn."""
  try:
    if hasattr(st, "secrets") and "POWER_AUTOMATE_AUTH_URL" in st.secrets:
      return st.secrets["POWER_AUTOMATE_AUTH_URL"].strip()
  except Exception:
    pass
  return ""


def verify_login(username_input: str, password_input: str):
  """Gửi username qua Power Automate, trích lục bản ghi từ SharePoint và đối soát mật khẩu.

  Trả về tuple: (success: bool, message: str, user_info: dict | None)
  """
  auth_url = get_auth_url()

  # 1. Kiểm tra cấu hình secrets
  if not auth_url:
    available_keys = list(st.secrets.keys()) if hasattr(st, "secrets") else []
    return (
        False,
        (
            "⚠️ Chưa cấu hình 'POWER_AUTOMATE_AUTH_URL' trong"
            " .streamlit/secrets.toml!\n"
            f"(Các khóa hiện có trong secrets: {available_keys})"
        ),
        None,
    )

  # 2. Chuẩn hóa dữ liệu đầu vào
  username_clean = username_input.strip().lower()
  password_clean = password_input.strip()

  if not username_clean or not password_clean:
    return False, "Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!", None

  payload = {"username": username_clean}

  # 3. Gửi request đến Power Automate
  try:
    response = requests.post(
        auth_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )

    if response.status_code != 200:
      return (
          False,
          (
              "Lỗi phản hồi từ máy chủ Power Automate (Mã lỗi"
              f" HTTP: {response.status_code})"
          ),
          None,
      )

    data = response.json()

    # Xử lý định dạng dữ liệu trả về từ SharePoint (mảng trực tiếp hoặc bọc trong thuộc tính 'value')
    if isinstance(data, dict) and "value" in data:
      items = data["value"]
    elif isinstance(data, list):
      items = data
    else:
      items = [data] if data else []

    if not items or len(items) == 0:
      return (
          False,
          f"Tài khoản '{username_clean}' không tồn tại trên hệ thống!",
          None,
      )

    # 4. Trích xuất thông tin người dùng từ bản ghi đầu tiên
    user_record = items[0]

    # Lấy mật khẩu lưu trên SharePoint List (cột listuser_password)
    db_password = str(user_record.get("listuser_password", "")).strip()

    # 5. So sánh mật khẩu
    if password_clean == db_password:
      # Gom thông tin nhân viên để đưa vào session
      user_info = {
          "id": user_record.get("ID"),
          "username": user_record.get("listuser_username", username_clean),
          "fullname": user_record.get("listuser_fullname", "Nhân viên"),
          "chucdanh": user_record.get("listuser_chucdanh", "Tư vấn viên"),
          "macuahang": str(user_record.get("listuser_macuahang", "Chưa rõ")),
          "email": user_record.get("Author", {}).get("Email", "")
          if isinstance(user_record.get("Author"), dict)
          else "",
      }
      return True, "Đăng nhập thành công!", user_info
    else:
      return False, "Mật khẩu không chính xác. Vui lòng kiểm tra lại!", None

  except requests.exceptions.Timeout:
    return (
        False,
        "Hết thời gian chờ phản hồi từ hệ thống (Timeout sau 15 giây). Vui lòng"
        " thử lại!",
        None,
    )
  except requests.exceptions.RequestException as req_err:
    return (
        False,
        f"Lỗi kết nối mạng khi gọi Power Automate: {str(req_err)}",
        None,
    )
  except Exception as e:
    return False, f"Đã xảy ra lỗi không xác định: {str(e)}", None


def check_authentication():
  """Hàm bảo vệ các trang con (trong thư mục pages/):

  Nếu chưa đăng nhập sẽ lập tức dừng thực thi trang và yêu cầu quay lại Trang
  chủ.
  """
  if not st.session_state.get("is_authenticated", False):
    st.warning("🔒 Vui lòng đăng nhập tại Trang Chủ để sử dụng chức năng này!")
    st.stop()


def logout():
  """Xóa trạng thái đăng nhập và đưa người dùng về màn hình đăng nhập."""
  st.session_state.is_authenticated = False
  st.session_state.current_user = None
  st.rerun()