from modules.auth import verify_login
import streamlit as st

st.set_page_config(
    page_title="PNJ - Đăng Nhập Hệ Thống", page_icon="💎", layout="centered"
)

# Khởi tạo trạng thái phiên (Session State)
if "is_authenticated" not in st.session_state:
  st.session_state.is_authenticated = False
if "current_user" not in st.session_state:
  st.session_state.current_user = None

# GIAO DIỆN KHI ĐÃ ĐĂNG NHẬP THÀNH CÔNG
if st.session_state.is_authenticated:
  user = st.session_state.current_user
  st.success(f"Xin chào, **{user['fullname']}**! 👋")

  with st.container(border=True):
    st.markdown("### 👤 Thông Tin Tài Khoản")
    col1, col2 = st.columns(2)
    col1.write(f"• **Chức danh:** {user['chucdanh']}")
    col1.write(f"• **Mã Cửa Hàng:** {user['macuahang']}")
    col2.write(f"• **Tên đăng nhập:** `{user['username']}`")
    col2.write(f"• **ID Hệ thống:** {user['id']}")

  st.info(
      "👈 Vui lòng chọn các màn hình chức năng ở thanh menu bên trái để làm"
      " việc."
  )

  if st.button("🚪 Đăng Xuất", type="secondary"):
    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    st.rerun()

# GIAO DIỆN FORM ĐĂNG NHẬP
else:
  st.markdown(
      "<h2 style='text-align: center; color: #003468;'>💎 PNJ - ĐĂNG NHẬP HỆ"
      " THỐNG</h2>",
      unsafe_allow_html=True,
  )
  st.write("")

  with st.form("login_form", clear_on_submit=False):
    username = st.text_input(
        "Tên đăng nhập (Username):", placeholder="Ví dụ: long.nh"
    )
    password = st.text_input(
        "Mật khẩu (Password):", type="password", placeholder="Nhập mật khẩu"
    )

    submit_btn = st.form_submit_button(
        "🔐 ĐĂNG NHẬP", type="primary", use_container_width=True
    )

    if submit_btn:
      if not username or not password:
        st.error("Vui lòng điền đầy đủ cả tên đăng nhập và mật khẩu!")
      else:
        with st.spinner("Đang xác thực thông tin tài khoản..."):
          success, msg, user_data = verify_login(username, password)
          if success:
            st.session_state.is_authenticated = True
            st.session_state.current_user = user_data
            st.success("Đăng nhập thành công! Đang chuyển hướng...")
            st.rerun()
          else:
            st.error(msg)