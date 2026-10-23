import requests
import streamlit as st

AUTH_URL = st.secrets.get("POWER_AUTOMATE_AUTH_URL", "")


def verify_login(username_input: str, password_input: str):
  """Gửi username qua Power Automate, nhận về bản ghi và so khớp mật khẩu."""
  if not AUTH_URL:
    return (
        False,
        "Chưa cấu hình POWER_AUTOMATE_AUTH_URL trong .streamlit/secrets.toml",
        None,
    )

  payload = {"username": username_input.strip().lower()}

  try:
    response = requests.post(AUTH_URL, json=payload, timeout=15)
    if response.status_code != 200:
      return (
          False,
          f"Lỗi phản hồi từ hệ thống (Mã lỗi {response.status_code})",
          None,
      )

    data = response.json()
    items = data.get("value", data) if isinstance(data, dict) else data

    if not items or len(items) == 0:
      return False, "Tài khoản người dùng không tồn tại trên hệ thống!", None

    # Lấy thông tin người dùng tìm thấy từ SharePoint
    user_data = items[0]
    db_password = str(user_data.get("listuser_password", ""))

    # So sánh mật khẩu
    if password_input == db_password:
      user_info = {
          "id": user_data.get("ID"),
          "username": user_data.get("listuser_username"),
          "fullname": user_data.get("listuser_fullname"),
          "chucdanh": user_data.get("listuser_chucdanh"),
          "macuahang": user_data.get("listuser_macuahang"),
      }
      return True, "Đăng nhập thành công!", user_info
    else:
      return False, "Mật khẩu không chính xác. Vui lòng thử lại!", None

  except requests.exceptions.Timeout:
    return (
        False,
        "Hết thời gian chờ phản hồi (Timeout). Vui lòng thử lại sau!",
        None,
    )
  except Exception as e:
    return False, f"Lỗi kết nối xác thực: {str(e)}", None


def check_authentication():
  """Hàm bảo vệ màn hình con: Chưa đăng nhập thì chặn và chuyển về trang chủ."""
  if not st.session_state.get("is_authenticated", False):
    st.warning("🔒 Vui lòng đăng nhập tại Trang Chủ để sử dụng chức năng này!")
    st.stop()