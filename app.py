import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="禹来企业级财务系统", layout="wide", page_icon="🍎")

# ==========================================
# 🍎 注入 Apple Dark Mode (苹果深色模式) 终极 UI 引擎
# ==========================================
def inject_apple_ui():
    st.markdown("""
        <style>
        /* 1. 消除默认边距与字体平滑 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", sans-serif !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        .stApp { background-color: #000000; }
        [data-testid="stSidebar"] { background-color: #1C1C1E !important; }

        /* 2. 核心修复：输入框等距与对齐 */
        /* 针对所有文本、数字、日期、下拉框的统一处理 */
        .stTextInput input, 
        .stSelectbox div[data-baseweb="select"], 
        .stNumberInput input, 
        .stDateInput input, 
        .stTextArea textarea {
            border-radius: 12px !important; 
            background-color: #1C1C1E !important; 
            border: 1px solid #2C2C2E !important; 
            color: #FFFFFF !important;
            
            /* 关键点：通过组合 padding 和 height 修正视觉位移 */
            padding-left: 15px !important;   /* 确保文字不紧贴左侧圆角 */
            padding-right: 15px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            
            height: 44px !important;         /* 增加到苹果标准 44px 高度 */
            line-height: 44px !important;    /* 行高与高度相等，强制垂直居中 */
            font-size: 15px !important;
        }

        /* 针对日期选择器的图标对齐修正 */
        .stDateInput div[data-baseweb="input"] {
            height: 44px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* 针对下拉框内部容器的二次对齐 */
        div[data-baseweb="select"] > div {
            padding-left: 8px !important;
            background-color: transparent !important;
        }

        /* 3. 标签（Label）美化：模仿苹果副标题样式 */
        .stMarkdown label, p, .stWidgetLabel {
            margin-left: 2px !important; 
            margin-bottom: 8px !important;
            font-weight: 500 !important;
            color: #8E8E93 !important;      /* iOS 系统灰色 */
            font-size: 13px !important;      /* 稍微缩小，突出精致感 */
            text-transform: uppercase;       /* 模仿苹果的小标题风格 */
            letter-spacing: 0.5px;
        }

        /* 4. 选项卡 Tab 的等距修复（分段控制器风格） */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #1C1C1E;
            padding: 4px;
            border-radius: 14px;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px; 
            padding: 8px 20px; 
            border: none !important;
            color: #8E8E93 !important;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #3A3A3C !important; 
            color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        /* 5. 按钮的交互感 */
        .stButton>button {
            border-radius: 12px !important;
            height: 44px !important;
            padding: 0 30px !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .stButton>button:active { transform: scale(0.96); }

        /* 6. 表格圆角与边框处理 */
        [data-testid="stDataFrame"] { 
            border-radius: 18px; 
            overflow: hidden; 
            border: 1px solid #2C2C2E;
            padding: 5px;
            background-color: #1C1C1E;
        }
        </style>
    """, unsafe_allow_html=True)

inject_apple_ui()

# ==========================================
# ☁️ 核心数据逻辑 (100% 保留)
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
    config = CAT_COLORS.get(val, {"bg": "#343A40", "text": "#FFFFFF"})
    return f"background-color: {config['bg']}; color: {config['text']}; font-weight: bold; border-radius: 4px;"

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
        st.error("同步至云端失败，请检查网络！")

if 'df' not in st.session_state:
    st.session_state.df = load_data_from_cloud()

# ==========================================
# 🔒 登录验证
# ==========================================
def login():
    st.markdown("<br><br><h2 style='text-align: center; color: #F5F5F7; font-weight: 600; letter-spacing: -1px;'>禹来环保记账系统</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("账号")
        password = st.text_input("密码", type="password")
        if st.button("登录", use_container_width=True, type="primary"):
            creds = st.secrets.get("credentials", {})
            if username in creds and creds[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = creds[username]["role"]
                st.rerun()
            else:
                st.error("账号或密码不匹配")

if not st.session_state.get("logged_in", False):
    login()
    st.stop()

with st.sidebar:
    role_name = "最高权限管理员" if st.session_state["role"] == "admin" else "股东 / 业务员"
    st.markdown(f"### {st.session_state['username']}")
    st.markdown(f"<span style='color: #8E8E93; font-size: 13px;'>{role_name}</span>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 同步云端数据", use_container_width=True):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("退出登录", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体界面渲染
# ==========================================
st.title("企业财务核心看板")
tab1, tab2, tab3 = st.tabs(["录入账目", "审计与修改", "BI 洞察"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("发生时间", datetime.date.today())
            main_cat = st.selectbox("总类别", ["接待", "餐旅", "经营管理", "办公费用", "人员薪酬", "其他"])
            sub_cat = st.text_input("子类别")
            amount = st.number_input("金额 (元)", min_value=0.0, step=0.01)
        with col2:
            summary = st.text_input("摘要", placeholder="事由简述")
            people = st.text_input("相关人员")
            num_people = st.number_input("人数", min_value=1, value=1)
            applicant = st.text_input("申请人", value=st.session_state["username"])
        with col3:
            location = st.text_input("地点/行程")
            status = st.selectbox("申报状态", ["未申报", "已申报", "审批中"])
            remarks = st.text_area("备注信息")
            
        if st.form_submit_button("确认提交入账", use_container_width=True):
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
            with st.spinner("同步至云端..."): save_data_to_cloud(st.session_state.df)
            st.success(f"入账成功！单号: {serial}")

with tab2:
    st.markdown("<h4 style='font-weight: 600;'>数据阅览表</h4>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: 
        display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=300)
    
    st.markdown("---")
    st.markdown("<h4 style='font-weight: 600;'>授权修改区</h4>", unsafe_allow_html=True)
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
        st.warning("暂无修改权限内的账目")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
        if st.button("保存修改", type="primary"):
            if st.session_state["role"] == "admin":
                st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df.copy()
                main_df = main_df[~main_df['序号'].isin(edited_subset['序号'])]
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            with st.spinner("更新云端数据..."): save_data_to_cloud(st.session_state.df)
            st.success("同步成功")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        total = temp_df['金额'].sum()
        
        # 苹果风毛玻璃指标卡
        st.markdown(f"""
        <div style='background: rgba(28, 28, 30, 0.8); backdrop-filter: blur(20px); border: 1px solid #2C2C2E; 
        padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3); margin-bottom: 30px;'>
            <span style='color: #8E8E93; font-size: 15px; font-weight: 500; letter-spacing: 1px;'>ANNUAL EXPENDITURE</span><br>
            <span style='color: #F5F5F7; font-size: 42px; font-weight: 700; letter-spacing: -1px;'>{total:.2f} <span style='font-size: 18px; color: #8E8E93;'>CNY</span></span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h5 style='font-weight: 600; margin-bottom: 15px;'>支出分类占比</h5>", unsafe_allow_html=True)
            pie_data = temp_df.groupby('总类别')['金额'].sum().reset_index()
            fig = px.pie(pie_data, values='金额', names='总类别', hole=0.6, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig.update_traces(textinfo='percent', marker=dict(line=dict(color='#000000', width=2)))
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font_color='#F5F5F7', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("<h5 style='font-weight: 600; margin-bottom: 15px;'>月度开支趋势</h5>", unsafe_allow_html=True)
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            fig_bar = px.bar(monthly, x='月份', y='金额', text_auto='.2f', color_discrete_sequence=['#0A84FF'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#F5F5F7')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        m1, m2 = st.columns(2)
        with m1:
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            st.dataframe(apply_color_style(cat_sum.rename(columns={'金额': '小计'})), use_container_width=True)
        with m2:
            monthly_table = monthly.copy()
            monthly_table['金额'] = monthly_table['金额'].map("{:.2f}".format)
            st.dataframe(monthly_table.rename(columns={'金额': '月总额'}), use_container_width=True)
    else:
        st.info("尚无数据录入")
