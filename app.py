import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="禹来企业级财务系统", layout="wide", page_icon="🌐")

# ==========================================
# 🌌 注入 Fintech 科技蓝海 UI 引擎 (完美复刻参考图)
# ==========================================
def inject_fintech_ui():
    st.markdown("""
        <style>
        /* 1. 全局深邃藏蓝背景与字体平滑 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        
        /* 极致的深空蓝背景 */
        .stApp { background: linear-gradient(180deg, #0B1021 0%, #131B2F 100%) !important; }
        [data-testid="stSidebar"] { background-color: #0A0F1F !important; border-right: 1px solid #1C2541 !important; }

        /* 2. 输入框：极致圆角、无明显边框、微亮底色、完美居中 */
        .stTextInput input, 
        .stSelectbox div[data-baseweb="select"], 
        .stNumberInput input, 
        .stDateInput input, 
        .stTextArea textarea {
            border-radius: 24px !important;  /* 超大圆角 */
            background-color: #1A2238 !important; /* 略亮于背景的深蓝色 */
            border: 1px solid #24304D !important; /* 极弱的描边 */
            color: #FFFFFF !important;
            
            /* 修正文字偏上：增加整体高度，强制行高与高度一致 */
            height: 48px !important; 
            line-height: 48px !important;
            padding-left: 20px !important; 
            padding-right: 20px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            font-size: 15px !important;
            transition: all 0.3s ease;
        }

        /* 输入框激活状态的发光效果 */
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
            border-color: #00C2FF !important;
            box-shadow: 0 0 0 1px rgba(0, 194, 255, 0.5) !important;
            background-color: #1E2943 !important;
        }

        /* 日期图标垂直居中修复 */
        .stDateInput div[data-baseweb="input"] { height: 48px !important; display: flex; align-items: center; }
        
        /* 3. 标签文字：弱化色彩，凸显高级感 */
        .stMarkdown label, p, .stWidgetLabel {
            margin-left: 6px !important; 
            margin-bottom: 6px !important;
            color: #8B98B4 !important; /* 科技灰蓝 */
            font-size: 13px !important;
            font-weight: 500 !important;
        }

        /* 4. 按钮：亮蓝色渐变 + 悬浮发光阴影 */
        .stButton>button {
            border-radius: 24px !important;
            height: 48px !important;
            padding: 0 32px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            border: none !important;
            background: linear-gradient(90deg, #00C2FF 0%, #007BFF 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 8px 16px rgba(0, 123, 255, 0.25) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 12px 20px rgba(0, 123, 255, 0.4) !important; }
        .stButton>button:active { transform: scale(0.96); }

        /* 5. 选项卡 Tab：类似 App 的分段控制器 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #161F33;
            padding: 6px;
            border-radius: 24px;
            margin-bottom: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 18px; 
            padding: 10px 24px; 
            border: none !important;
            color: #8B98B4 !important;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] { 
            background: linear-gradient(90deg, #00C2FF 0%, #007BFF 100%) !important; 
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        }

        /* 6. 表格区暗黑美化 */
        [data-testid="stDataFrame"] { 
            border-radius: 20px; 
            overflow: hidden; 
            border: 1px solid #1C2541;
            background-color: #161F33;
        }
        </style>
    """, unsafe_allow_html=True)

inject_fintech_ui()

# ==========================================
# ☁️ 核心数据逻辑 (严格保留序号、金额小数、颜色映射)
# ==========================================
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注', '录入人', '录入时间']

CAT_COLORS = {
    "接待": {"bg": "#1A237E", "text": "#FFFFFF"},       
    "餐旅": {"bg": "#004D40", "text": "#FFFFFF"},       
    "经营管理": {"bg": "#3E2723", "text": "#FFFFFF"},   
    "办公费用": {"bg": "#4A148C", "text": "#FFFFFF"},   
    "人员薪酬": {"bg": "#880E4F", "text": "#FFFFFF"},   
    "其他": {"bg": "#263238", "text": "#FFFFFF"}        
}
PLOTLY_COLORS = {k: v["bg"] for k, v in CAT_COLORS.items()}

def style_category(val):
    config = CAT_COLORS.get(val, {"bg": "#1A2238", "text": "#FFFFFF"})
    return f"background-color: {config['bg']}; color: {config['text']}; font-weight: bold; border-radius: 6px;"

def apply_color_style(df_to_style):
    if hasattr(df_to_style.style, 'map'): return df_to_style.style.map(style_category, subset=['总类别'])
    else: return df_to_style.style.applymap(style_category, subset=['总类别'])

@st.cache_data(ttl=5)
def load_data_from_cloud():
    try:
        url = f"https://api.jsonbin.io/v3/b/{st.secrets['JSONBIN_BIN_ID']}"
        headers = {"X-Master-Key": st.secrets["JSONBIN_KEY"]}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            records = res.json().get("record", [])
            if records and isinstance(records, list) and len(records) > 0:
                df = pd.DataFrame(records)
                for col in COLUMNS:
                    if col not in df.columns: df[col] = ""
                df = df[COLUMNS]
                df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0.0)
                return df
        return pd.DataFrame(columns=COLUMNS)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_data_to_cloud(df):
    try:
        url = f"https://api.jsonbin.io/v3/b/{st.secrets['JSONBIN_BIN_ID']}"
        headers = {"Content-Type": "application/json", "X-Master-Key": st.secrets["JSONBIN_KEY"]}
        records = df.to_dict(orient="records")
        requests.put(url, json=records, headers=headers)
    except Exception:
        st.error("云端通讯异常，请检查网络！")

if 'df' not in st.session_state:
    st.session_state.df = load_data_from_cloud()

# ==========================================
# 🔒 登录验证 (复刻 Welcome Youlv 界面居中感)
# ==========================================
def login():
    st.markdown("<br><br><br><h1 style='text-align: center; color: #FFFFFF; font-weight: 800; font-size: 42px; letter-spacing: -1px;'>DECIBEL Ledger</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8B98B4; margin-bottom: 40px;'>Secure Enterprise Financial System</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        username = st.text_input("Account")
        password = st.text_input("Password", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign in", use_container_width=True, type="primary"):
            creds = st.secrets.get("credentials", {})
            if username in creds and creds[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = creds[username]["role"]
                st.rerun()
            else:
                st.error("Authentication Failed")

if not st.session_state.get("logged_in", False):
    login()
    st.stop()

with st.sidebar:
    role_name = "Admin / Boss" if st.session_state["role"] == "admin" else "Shareholder / Staff"
    st.markdown(f"<h3 style='color:#FFFFFF;'>{st.session_state['username']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color: #00C2FF; font-size: 13px; font-weight: 600; padding: 4px 10px; background: rgba(0, 194, 255, 0.1); border-radius: 12px;'>{role_name}</span>", unsafe_allow_html=True)
    st.markdown("<br><hr style='border-color: #1C2541;'>", unsafe_allow_html=True)
    if st.button("🔄 Sync Cloud Data", use_container_width=True):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体界面渲染
# ==========================================
st.markdown("<h2 style='color:#FFFFFF; font-weight: 700;'>Financial Activity</h2>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📝 Add Record", "🛡️ Audit & Edit", "📊 Market Insight"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("Date", datetime.date.today())
            main_cat = st.selectbox("Category", ["接待", "餐旅", "经营管理", "办公费用", "人员薪酬", "其他"])
            sub_cat = st.text_input("Sub-Category")
            amount = st.number_input("Amount (CNY)", min_value=0.0, step=0.01)
        with col2:
            summary = st.text_input("Summary", placeholder="Brief description")
            people = st.text_input("Related Personnel")
            num_people = st.number_input("Headcount", min_value=1, value=1)
            applicant = st.text_input("Applicant", value=st.session_state["username"])
        with col3:
            location = st.text_input("Location / Route")
            status = st.selectbox("Status", ["未申报", "已申报", "审批中"])
            remarks = st.text_area("Remarks")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Confirm Entry", use_container_width=True):
            month_str = f"{date.month:02d}"
            year_month = f"{date.year % 100:02d}{month_str}"
            current_month_df = st.session_state.df[st.session_state.df['月份'] == month_str]
            serial = f"CL{year_month}{len(current_month_df) + 1:03d}"
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_row = {
                '月份': month_str, '序号': serial, '时间': date.strftime("%Y.%m.%d"),
                '总类别': main_cat, '子类别': sub_cat, '摘要': summary,
                '人员': people, '人数': num_people, '出发地/目的地': location,
                '金额': amount, '申请人': applicant, '申报状态': status, '备注': remarks,
                '录入人': st.session_state["username"], '录入时间': current_time
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            with st.spinner("Securing to Blockchain/Cloud..."): save_data_to_cloud(st.session_state.df)
            st.success(f"Transaction Confirmed. Serial: {serial}")

with tab2:
    st.markdown("<h4 style='color:#FFFFFF; font-weight: 600;'>Global Ledger</h4>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: 
        display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=300)
    
    st.markdown("---")
    st.markdown("<h4 style='color:#FFFFFF; font-weight: 600;'>Authorization Zone</h4>", unsafe_allow_html=True)
    if st.session_state["role"] == "admin":
        editable_df = st.session_state.df.copy()
    else:
        now = datetime.datetime.now()
        editable_indices = []
        for idx, row in st.session_state.df.iterrows():
            if row['录入人'] == st.session_state["username"] and row['录入时间'] != "":
                try:
                    record_time = datetime.datetime.strptime(row['录入时间'], "%Y-%m-%d %H:%M:%S")
                    if (now - record_time).total_seconds() <= 12 * 3600: editable_indices.append(idx)
                except: pass
        editable_df = st.session_state.df.loc[editable_indices].copy()

    if editable_df.empty and st.session_state["role"] != "admin":
        st.warning("No editable records within the 12-hour window.")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
        if st.button("Save Modifications", type="primary"):
            if st.session_state["role"] == "admin":
                st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df.copy()
                main_df = main_df[~main_df['序号'].isin(edited_subset['序号'])]
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            with st.spinner("Updating Network..."): save_data_to_cloud(st.session_state.df)
            st.success("Synchronization Complete")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        total = temp_df['金额'].sum()
        
        # 深度定制的蓝海渐变发光指标卡
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1A2238 0%, #111827 100%); 
        border: 1px solid #24304D; padding: 40px; border-radius: 24px; text-align: center; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05); margin-bottom: 30px; position: relative; overflow: hidden;'>
            <div style='position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(0,194,255,0.05) 0%, rgba(0,0,0,0) 70%); pointer-events: none;'></div>
            <span style='color: #8B98B4; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;'>Total Value ($CNY)</span><br><br>
            <span style='color: #FFFFFF; font-size: 56px; font-weight: 800; letter-spacing: -2px; text-shadow: 0 0 20px rgba(0, 194, 255, 0.4);'>{total:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h5 style='color:#FFFFFF; font-weight: 600; margin-bottom: 15px;'>Portfolio Distribution</h5>", unsafe_allow_html=True)
            pie_data = temp_df.groupby('总类别')['金额'].sum().reset_index()
            fig = px.pie(pie_data, values='金额', names='总类别', hole=0.65, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig.update_traces(textinfo='percent', marker=dict(line=dict(color='#0B1021', width=3)))
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font_color='#8B98B4', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("<h5 style='color:#FFFFFF; font-weight: 600; margin-bottom: 15px;'>Real-time Trend</h5>", unsafe_allow_html=True)
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            # 柱状图修改为科技感的亮蓝色
            fig_bar = px.bar(monthly, x='月份', y='金额', text_auto='.2f', color_discrete_sequence=['#00C2FF'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#8B98B4')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            st.dataframe(apply_color_style(cat_sum.rename(columns={'金额': 'Subtotal'})), use_container_width=True)
        with m2:
            monthly_table = monthly.copy()
            monthly_table['金额'] = monthly_table['金额'].map("{:.2f}".format)
            st.dataframe(monthly_table.rename(columns={'金额': 'Monthly Volume'}), use_container_width=True)
    else:
        st.info("Awaiting Market Data...")
