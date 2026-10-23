import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.auth import verify_login, logout

# ==========================================
# CẤU HÌNH TRANG STREAMLIT (ẨN HOÀN TOÀN SIDEBAR)
# ==========================================
st.set_page_config(
    page_title="PNJ - Hệ Thống Thu Đổi Chuyển Đổi",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kết nối Supabase an toàn (tự động qua st.secrets)
try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False

# Hàm làm sạch URL Supabase
def clean_supabase_url(raw_url: str) -> str:
    if not raw_url: return ""
    u = raw_url.strip().rstrip("/")
    if u.endswith("/rest/v1"): u = u[:-8].rstrip("/")
    return u

# Khởi tạo Supabase client trực tiếp từ st.secrets
supabase_client = None
supabase_err_msg = ""

sb_url = ""
sb_key = ""
if hasattr(st, "secrets"):
    sb_url = st.secrets.get("SUPABASE_URL", "")
    sb_key = st.secrets.get("SUPABASE_KEY", "")

if HAS_SUPABASE_LIB and sb_url and sb_key:
    try:
        supabase_client = create_client(clean_supabase_url(sb_url), str(sb_key).strip())
    except Exception as e:
        supabase_err_msg = str(e)

# ==========================================
# KHỞI TẠO SESSION STATE
# ==========================================
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if 'old_items' not in st.session_state:
    st.session_state.old_items = [{'id': 1, 'group': None, 'val': 0}]
if 'new_items' not in st.session_state:
    st.session_state.new_items = [{'id': 1, 'group': None, 'val': 0}]
if 'next_old_id' not in st.session_state:
    st.session_state.next_old_id = 2
if 'next_new_id' not in st.session_state:
    st.session_state.next_new_id = 2

# ==========================================
# CUSTOM CSS PHONG CÁCH PNJ & ẨN SIDEBAR
# ==========================================
st.markdown("""
<style>
    /* Ẩn hoàn toàn thanh Sidebar và nút mở rộng */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
    .main-header {
        background-color: #003468;
        padding: 18px 25px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #F7D070 !important;
        margin: 0;
        font-size: 24px;
        font-weight: 700;
    }
    .main-header p {
        color: #E0E0E0;
        margin: 5px 0 0 0;
        font-size: 13px;
    }
    /* Thẻ thông tin tài khoản hiển thị rõ nét trên nền xanh */
    .user-badge-box {
        background: rgba(0, 20, 50, 0.45);
        border: 1px solid #F7D070;
        border-radius: 8px;
        padding: 10px 16px;
        color: #FFFFFF;
        font-size: 13.5px;
        line-height: 1.6;
    }
    .user-badge-box .name-tag {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 15px;
    }
    .user-badge-box .role-tag {
        color: #F7D070;
        font-weight: 600;
    }
    .user-badge-box .hub-tag {
        color: #6EE7B7;
        font-weight: 600;
    }
    .user-badge-box .user-tag {
        color: #CBD5E1;
        font-family: monospace;
    }

    .card-pa {
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: white;
        font-weight: bold;
    }
    .pa1-bg { background-color: #28a745; }
    .pa2-bg { background-color: #d39e00; }
    .pa3-bg { background-color: #dc3545; }
    .del-btn-container { margin-top: 28px; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f1f3f5;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #003468 !important;
        color: #F7D070 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# TRƯỜNG HỢP 1: CHƯA ĐĂNG NHẬP ➔ FORM LOGIN
# ==========================================
if not st.session_state.is_authenticated:
    st.markdown("""
    <div style='text-align: center; margin-top: 50px; margin-bottom: 25px;'>
        <h1 style='color: #003468; margin-bottom: 5px;'>💎 PNJ RETAIL SYSTEM</h1>
        <h3 style='color: #856404; font-weight: 500;'>HỆ THỐNG XÁC THỰC & TRA CỨU CHÍNH SÁCH THU ĐỔI</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.4, 1])
    with col_center:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### 🔐 Đăng Nhập Hệ Thống")
            username = st.text_input("Tên đăng nhập (Username):", placeholder="Ví dụ: long.nh")
            password = st.text_input("Mật khẩu (Password):", type="password", placeholder="Nhập mật khẩu")
            
            submit_btn = st.form_submit_button("ĐĂNG NHẬP", type="primary", use_container_width=True)
            
            if submit_btn:
                if not username or not password:
                    st.error("⚠️ Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
                else:
                    with st.spinner("⏳ Đang đối soát với danh sách SharePoint..."):
                        success, msg, user_data = verify_login(username, password)
                        if success:
                            st.session_state.is_authenticated = True
                            st.session_state.current_user = user_data
                            st.success("🎉 Đăng nhập thành công! Đang vào ứng dụng...")
                            st.rerun()
                        else:
                            st.error(msg)
    st.stop()

# ==========================================
# TRƯỜNG HỢP 2: ĐÃ ĐĂNG NHẬP ➔ GIAO DIỆN HOME CHÍNH
# ==========================================
user = st.session_state.current_user
store_code = str(user.get("macuahang", "HUB-001"))

# Header có huy hiệu tương phản rõ ràng và nút Đăng Xuất góc phải
col_head_left, col_head_right = st.columns([3.2, 1.3])
with col_head_left:
    st.markdown("""
    <div class="main-header">
        <h1>💎 PNJ - HỆ THỐNG TRA CỨU & HƯỚNG DẪN THU ĐỔI CHUYỂN ĐỔI</h1>
        <p>Áp dụng theo QĐ 442-2026-TB-P.VHBL-TĐTGTTHML-PNJ & PL A2 (Hiệu lực từ 30/09/2026)</p>
    </div>
    """, unsafe_allow_html=True)

with col_head_right:
    st.markdown(f"""
    <div class="user-badge-box">
        👤 <span class="name-tag">{user.get('fullname', 'Nhân viên')}</span><br>
        🏷️ Chức danh: <span class="role-tag">{user.get('chucdanh', 'Tư vấn viên')}</span><br>
        🏬 Cửa hàng: <span class="hub-tag">{user.get('macuahang', 'HUB-001')}</span> | User: <span class="user-tag">{user.get('username', '')}</span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🚪 Đăng Xuất", use_container_width=True, type="secondary"):
        logout()

# ==========================================
# DỮ LIỆU MA TRẬN NHÓM HÀNG PNJ (N1 - N10)
# ==========================================
GROUPS_INFO = {
    "N1": {"name": "Vàng miếng, Nhẫn khoen, Vàng Phúc Lộc Tài, Kim Bảo", "allowed_to": ["N2", "N3", "N4", "N5", "N6", "N7"], "payment": "T+2", "schedule": "100% sau 2 ngày làm việc (T+2)"},
    "N3": {"name": "TS Công nghệ Ý, KGĐ, Dây chuyền, ECZ/CZ", "allowed_to": ["N2", "N3", "N5"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N4": {"name": "Vàng 21.9K - 24K (91.6% - 99.99%), Quà tặng sưu tầm", "allowed_to": ["N2", "N3", "N4", "N5"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N7": {"name": "Style by PNJ (KGĐ, CZ/ECZ, Dây chuyền)", "allowed_to": ["N6", "N7"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N8": {"name": "Danh mục Heart2Heart", "allowed_to": ["N8"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N9": {"name": "Danh mục Kind Heart", "allowed_to": ["N9"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N10": {"name": "Charm phong thủy đặc biệt, Bao lì xì phong thủy", "allowed_to": ["N10"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N2": {"name": "TS Kim Cương, Đá màu, Ngọc trai, TS Vỏ", "allowed_to": ["N2", "N5"], "payment": "T+120", "schedule": "10% (T/T+1) | 20% (T+30) | 25% (T+60) | 25% (T+90) | 20% (T+120)"},
    "N5": {"name": "Kim cương rời, Đá màu rời, Ngọc trai rời, Cẩm thạch", "allowed_to": ["N2", "N5"], "payment": "T+120", "schedule": "10% (T/T+1) | 20% (T+30) | 25% (T+60) | 25% (T+90) | 20% (T+120)"},
    "N6": {"name": "Style by PNJ (TS Kim cương, Đá màu, Ngọc trai)", "allowed_to": ["N6"], "payment": "T+120", "schedule": "10% (T/T+1) | 20% (T+30) | 25% (T+60) | 25% (T+90) | 20% (T+120)"}
}

# ==========================================
# KHỞI TẠO 5 TABS GIAO DIỆN
# ==========================================
tab_calculator, tab_user_guide, tab_matrix, tab_faq, tab_database = st.tabs([
    "📋 1. TÍNH TOÁN CẤN TRỪ & PHƯƠNG ÁN",
    "📖 2. HƯỚNG DẪN QUY TRÌNH THU ĐỔI",
    "📊 3. MA TRẬN MAPPING & LỘ TRÌNH",
    "❓ 4. HỎI ĐÁP Q&A THƯỜNG GẶP",
    "🗄️ 5. QUẢN LÝ DỮ LIỆU SUPABASE"
])

# ==========================================
# TAB 1: TÍNH TOÁN CẤN TRỪ (PHIẾU KIỂM TRA)
# ==========================================
with tab_calculator:
    st.subheader("📋 Tính Toán Cấn Trừ & Xác Định Phương Án Thanh Toán")
    col_input1, col_input2 = st.columns(2)
    
    # ------------------ CỘT 1: HÀNG CŨ (BẢNG KÊ) ------------------
    with col_input1:
        st.markdown("### 🛍️ 1. Hàng Cũ Thu Đổi / Mua Lại (Bảng kê)")
        old_items_processed = []
        total_old_val = 0
        to_delete_old = None

        for idx, item in enumerate(st.session_state.old_items):
            c_group, c_val, c_del = st.columns([5.5, 3.2, 1.3])
            def format_group_old(x):
                if x is None or x == "":
                    return "❓ -- Chọn nhóm hàng --"
                info = GROUPS_INFO[x]
                return f"[{info['payment']}] N{x[1:]} - {info['name'][:30]}..."

            options_list = [None] + list(GROUPS_INFO.keys())
            curr_index = options_list.index(item['group']) if item['group'] in options_list else 0

            with c_group:
                selected_g = st.selectbox(
                    f"Món BK{idx+1}:",
                    options=options_list,
                    index=curr_index,
                    format_func=format_group_old,
                    key=f"old_g_select_{item['id']}"
                )
                item['group'] = selected_g
            with c_val:
                val = st.number_input(
                    f"Giá trị BK{idx+1} (VNĐ):",
                    min_value=0,
                    value=item['val'],
                    step=1000000,
                    key=f"old_val_input_{item['id']}"
                )
                item['val'] = val
            with c_del:
                st.markdown("<div class='del-btn-container'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Xóa", key=f"del_old_{item['id']}", help="Xóa món này"):
                    to_delete_old = item['id']

            if item['group'] is not None and item['val'] > 0:
                old_items_processed.append({
                    "id": f"BK{idx+1}",
                    "group": item['group'],
                    "name": GROUPS_INFO[item['group']]["name"],
                    "value": item['val'],
                    "payment": GROUPS_INFO[item['group']]["payment"],
                    "schedule": GROUPS_INFO[item['group']]["schedule"]
                })
                total_old_val += item['val']

        if to_delete_old is not None:
            st.session_state.old_items = [x for x in st.session_state.old_items if x['id'] != to_delete_old]
            st.rerun()

        if st.button("➕ Thêm món cũ (BK)", key="add_old_btn"):
            st.session_state.old_items.append({'id': st.session_state.next_old_id, 'group': None, 'val': 0})
            st.session_state.next_old_id += 1
            st.rerun()

        st.metric("TỔNG GIÁ TRỊ HÀNG CŨ (BK):", f"{total_old_val:,.0f} VNĐ")

    # ------------------ CỘT 2: HÀNG MỚI (HÓA ĐƠN) ------------------
    with col_input2:
        st.markdown("### 🛒 2. Hàng Mới Khách Mua (Hóa đơn)")
        new_items_processed = []
        total_new_val = 0
        to_delete_new = None

        for idx, item in enumerate(st.session_state.new_items):
            c_group, c_val, c_del = st.columns([5.5, 3.2, 1.3])
            def format_group_new(x):
                if x is None or x == "":
                    return "❓ -- Chọn nhóm hàng --"
                info = GROUPS_INFO[x]
                return f"[{info['payment']}] N{x[1:]} - {info['name'][:30]}..."

            options_list_new = [None] + list(GROUPS_INFO.keys())
            curr_index_new = options_list_new.index(item['group']) if item['group'] in options_list_new else 0

            with c_group:
                selected_g_new = st.selectbox(
                    f"Món HĐ{idx+1}:",
                    options=options_list_new,
                    index=curr_index_new,
                    format_func=format_group_new,
                    key=f"new_g_select_{item['id']}"
                )
                item['group'] = selected_g_new
            with c_val:
                val = st.number_input(
                    f"Giá trị HĐ{idx+1} (VNĐ):",
                    min_value=0,
                    value=item['val'],
                    step=1000000,
                    key=f"new_val_input_{item['id']}"
                )
                item['val'] = val
            with c_del:
                st.markdown("<div class='del-btn-container'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Xóa", key=f"del_new_{item['id']}", help="Xóa món này"):
                    to_delete_new = item['id']

            if item['group'] is not None and item['val'] > 0:
                new_items_processed.append({
                    "id": f"HĐ{idx+1}",
                    "group": item['group'],
                    "name": GROUPS_INFO[item['group']]["name"],
                    "value": item['val'],
                    "rem_val": item['val']
                })
                total_new_val += item['val']

        if to_delete_new is not None:
            st.session_state.new_items = [x for x in st.session_state.new_items if x['id'] != to_delete_new]
            st.rerun()

        if st.button("➕ Thêm món mới (HĐ)", key="add_new_btn"):
            st.session_state.new_items.append({'id': st.session_state.next_new_id, 'group': None, 'val': 0})
            st.session_state.next_new_id += 1
            st.rerun()

        st.metric("TỔNG GIÁ TRỊ HÀNG MỚI (HĐ):", f"{total_new_val:,.0f} VNĐ")

    st.markdown("---")
    st.markdown("### ⚙️ Điều Kiện Vận Hành & Tuân Thủ Quầy")
    col_cond1, col_cond2, col_cond3 = st.columns(3)
    with col_cond1:
        is_hub = st.checkbox("Cửa hàng là Điểm Trung Tâm (HUB)?", value=True)
    with col_cond2:
        same_customer = st.checkbox("Hóa đơn cũ & mới CÙNG MÃ KHÁCH HÀNG?", value=True)
    with col_cond3:
        customer_phone = st.text_input("Số điện thoại / Mã KH:", value="0901234567")

    # Thuật toán tính toán cấn trừ
    can_tru_list = []
    du_item_list = []
    total_can_tru = 0
    total_chi_sau = 0
    new_pool = [{**item} for item in new_items_processed]
    
    for old in old_items_processed:
        old_val_rem = old["value"]
        for new in new_pool:
            if old_val_rem <= 0: break
            if new["rem_val"] <= 0: continue
            allowed_groups = GROUPS_INFO[old["group"]]["allowed_to"]
            if new["group"] in allowed_groups:
                matched_amount = min(old_val_rem, new["rem_val"])
                can_tru_list.append({
                    "old_id": old["id"],
                    "old_group": old["group"],
                    "new_id": new["id"],
                    "new_group": new["group"],
                    "amount": matched_amount
                })
                old_val_rem -= matched_amount
                new["rem_val"] -= matched_amount
                total_can_tru += matched_amount
        if old_val_rem > 0:
            du_item_list.append({
                "id": old["id"],
                "group": old["group"],
                "amount": old_val_rem,
                "payment": old["payment"],
                "schedule": old["schedule"]
            })
            total_chi_sau += old_val_rem

    st.markdown("---")
    st.markdown("### 🎯 KẾT QUẢ PHÂN LOẠI PHƯƠNG ÁN THANH TOÁN")
    
    has_unselected_old = any(x['group'] is None for x in st.session_state.old_items if x['val'] > 0)
    has_unselected_new = any(x['group'] is None for x in st.session_state.new_items if x['val'] > 0)
    if has_unselected_old or has_unselected_new:
        st.warning("⚠️ Vui lòng chọn Nhóm Hàng cho tất cả các món để hệ thống tính toán chính xác!")

    pa_code = "N/A"
    if total_old_val == 0 and total_new_val == 0:
        st.info("👋 Hãy chọn Nhóm hàng và nhập giá trị món hàng ở trên để bắt đầu tính toán.")
    elif total_new_val == 0:
        pa_code = "PA3"
        pa_title = "🔴 Phương Án 3: MUA LẠI HOÀN TOÀN"
        pa_bg = "pa3-bg"
        pa_desc = "Khách hàng bán lại sản phẩm và không phát sinh hóa đơn mua mới."
    elif total_chi_sau == 0 and total_can_tru == total_old_val:
        pa_code = "PA1"
        pa_title = "🟢 Phương Án 1: CHUYỂN ĐỔI HOÀN TOÀN"
        pa_bg = "pa1-bg"
        pa_desc = "Toàn bộ giá trị sản phẩm cũ được cấn trừ hết vào hóa đơn mới. Khách hàng đóng thêm tiền chênh lệch (nếu có)."
    else:
        pa_code = "PA2"
        pa_title = "🟡 Phương Án 2: CHUYỂN ĐỔI MỘT PHẦN (Chỉ thực hiện tại Cửa Hàng HUB)"
        pa_bg = "pa2-bg"
        pa_desc = f"Cấn trừ {total_can_tru:,.0f} VNĐ vào hóa đơn mới. Công ty sẽ chi trả lại phần tiền thừa {total_chi_sau:,.0f} VNĐ cho khách theo lộ trình thanh toán."

    if total_old_val > 0 or total_new_val > 0:
        st.markdown(f"""
        <div class="card-pa {pa_bg}">
            <h3 style="margin:0; color:white;">{pa_title}</h3>
            <p style="margin:5px 0 0 0; font-weight:normal;">{pa_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.success(f"**Tổng tiền cấn trừ ngay:** {total_can_tru:,.0f} VNĐ")
            if can_tru_list:
                for ct in can_tru_list:
                    st.write(f"• **{ct['old_id']}** (N{ct['old_group'][1:]}) ➔ Cấn trừ **{ct['amount']:,.0f} VNĐ** sang **{ct['new_id']}** (N{ct['new_group'][1:]})")
        with res_col2:
            st.warning(f"**Công ty chi trả sau:** {total_chi_sau:,.0f} VNĐ")
            if du_item_list:
                for du in du_item_list:
                    st.write(f"• **{du['id']}** (N{du['group'][1:]}): Dư **{du['amount']:,.0f} VNĐ** ➔ Lộ trình **{du['payment']}** ({du['schedule']})")

        # Nút Lưu Dữ Liệu vào Supabase (Hoàn toàn tự động ngầm)
        st.markdown("---")
        if st.button("💾 LƯU GIAO DỊCH VÀO SUPABASE", type="primary"):
            if supabase_client:
                try:
                    record_data = {
                        "ma_cua_hang": store_code,
                        "so_dien_thoai_kh": customer_phone,
                        "phuong_an": pa_code,
                        "tong_hang_cu": float(total_old_val),
                        "tong_hang_moi": float(total_new_val),
                        "tien_can_tru": float(total_can_tru),
                        "tien_chi_sau": float(total_chi_sau),
                        "chi_tiet_cu": old_items_processed,
                        "chi_tiet_moi": new_items_processed
                    }
                    res = supabase_client.table("giao_dich_thu_doi").insert(record_data).execute()
                    st.success("🎉 Đã lưu thành công giao dịch vào CSDL Supabase!")
                except Exception as err:
                    st.error(f"❌ Lỗi từ Supabase: {err}")
                    st.info("💡 MẸO: Hãy kiểm tra URL xem có bị thừa '/rest/v1' hay dấu '/' ở cuối không, và đảm bảo bảng đã tắt RLS trong SQL Editor.")
            else:
                st.error("⚠️ Chưa kết nối Supabase! Vui lòng kiểm tra lại SUPABASE_URL và SUPABASE_KEY trong file .streamlit/secrets.toml.")
                if supabase_err_msg:
                    st.caption(f"Chi tiết lỗi kết nối: {supabase_err_msg}")

# ==========================================
# TAB 2: HƯỚNG DẪN QUY TRÌNH THU ĐỔI
# ==========================================
with tab_user_guide:
    st.subheader("📖 Hướng Dẫn Chi Tiết Quy Trình Thu Đổi & Mua Lại Sản Phẩm PNJ")
    st.write("Tài liệu hướng dẫn trực quan dành cho Khách hàng và Nhân viên tư vấn bán hàng toàn hệ thống PNJ.")

# ==========================================
# TAB 3: MA TRẬN MAPPING & LỘ TRÌNH
# ==========================================
with tab_matrix:
    st.subheader("📊 Bảng Ma Trận Mapping Nhóm Hàng & Lộ Trình Thanh Toán PNJ")
    matrix_data = [{"Mã Nhóm": k, "Tên Dòng Sản Phẩm": v["name"], "Nhóm Cho Phép Đổi Sang": ", ".join(v["allowed_to"]), "Thời Gian Thanh Toán": v["payment"], "Chi Tiết Lộ Trình Chi Trả": v["schedule"]} for k, v in GROUPS_INFO.items()]
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

# ==========================================
# TAB 4: HỎI ĐÁP Q&A THƯỜNG GẶP
# ==========================================
with tab_faq:
    st.subheader("❓ Các Câu Hỏi Thường Gặp Của Nhân Viên & Khách Hàng (Q&A)")
    with st.expander("Q1: Khách hàng muốn bán lại món cũ nhưng cửa hàng không phải HUB thì làm thế nào?"):
        st.write("👉 **Trả lời:** Cửa hàng thường không có chức năng tiếp nhận giao dịch Mua lại (PA3) hoặc Chuyển đổi một phần (PA2). Nhân viên hướng dẫn khách hàng đến Cửa hàng HUB gần nhất trong khung giờ từ 15h00 đến 17h00 để thực hiện.")

# ==========================================
# TAB 5: QUẢN LÝ DỮ LIỆU SUPABASE
# ==========================================
with tab_database:
    st.subheader("🗄️ Quản Lý Dữ Liệu Giao Dịch Thu Đổi (Supabase)")
    if supabase_client:
        if st.button("🔄 Tải Dữ Liệu Từ Supabase"):
            try:
                response = supabase_client.table("giao_dich_thu_doi").select("*").order("created_at", desc=True).execute()
                if response.data:
                    st.dataframe(pd.DataFrame(response.data), use_container_width=True)
                else:
                    st.info("Chưa có giao dịch nào được lưu.")
            except Exception as e:
                st.error(f"❌ Lỗi truy vấn: {e}")
    else:
        st.warning("⚠️ Để xem lịch sử giao dịch từ Supabase, vui lòng cấu hình SUPABASE_URL và SUPABASE_KEY trong file .streamlit/secrets.toml.")
        if supabase_err_msg:
            st.caption(f"Chi tiết lỗi: {supabase_err_msg}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6c757d; font-size: 13px;'>© 2026 Phu Nhuan Jewelry Joint Stock Company (PNJ).</div>", unsafe_allow_html=True)
