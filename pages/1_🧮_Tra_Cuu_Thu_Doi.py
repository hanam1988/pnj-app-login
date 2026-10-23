from modules.auth import check_authentication
import streamlit as st

st.set_page_config(page_title="Tra Cứu Thu Đổi PNJ", page_icon="🧮", layout="wide")

# 👉 BẢO VỆ MÀN HÌNH: Nếu chưa đăng nhập sẽ lập tức dừng và yêu cầu đăng nhập
check_authentication()

# Lấy thông tin user đang đăng nhập
user = st.session_state.current_user

st.title("🧮 Quầy Tính Toán Thu Đổi Sản Phẩm PNJ")
st.caption(
    f"Nhân viên thao tác: **{user['fullname']}** ({user['chucdanh']}) - Cửa"
    f" hàng: **{user['macuahang']}**"
)

st.write("---")
st.info("Nội dung giao diện tính toán cấn trừ và phân loại PA1/PA2/PA3 ở đây...")