import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="2026财务库", layout="wide", page_icon="📊")

# ==========================================
# 🎨 专属低纯度/低明度色系配置 (全局统一)
# ==========================================
# 分类色盘
CAT_COLORS = {
    "接待": {"bg": "#1A2433", "text": "#FFFFFF"},       # 深海蓝
    "餐旅": {"bg": "#1A3324", "text": "#FFFFFF"},       # 深松绿
    "经营管理": {"bg": "#33241A", "text": "#FFFFFF"},   # 深焦褐
    "办公费用": {"bg": "#2B1A33", "text": "#FFFFFF"},   # 深暗紫
    "人员薪酬": {"bg": "#331A24", "text": "#FFFFFF"},   # 深酒红
    "其他": {"bg": "#262626", "text": "#FFFFFF"}        # 深炭灰
}
# 状态色盘
STATUS_COLORS = {
    "已申报": "#1A3324", # 对应绿色系 (低明度)
    "未申报": "#33241A", # 对应橙色系 (低明度)
    "审批中": "#1A2433"  # 对应蓝色系 (低明度)
}
PLOTLY_COLORS = {k: v["bg"] for k, v in CAT_COLORS.items()}

# ==========================================
# ⬛ 注入极致暗黑扁平风 UI 引擎
# ==========================================
def inject_flat_dark_ui():
    st.markdown("""
        <style>
        /* 1. 全局字体与高级杂点深灰背景 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        .stApp { 
            background-color: #1A1A1C !important;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E") !important;
        }
        [data-testid="stSidebar"] { background-color: #151516 !important; border-right: 1px solid #2C2C2E !important; }

        /* 2. 输入组件彻底扁平化 + 强制垂直水平居中 + 严格圆角对齐 */
        .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
            background-color: #242426 !important;
            border: 1px solid #333336 !important;
            border-radius: 4px !important;
            color: #FFFFFF !important;
            text-align: center !important;
            font-size: 15px !important;
            height: 42px !important;
            line-height: 42px !important;
            padding: 0 10px !important;
            box-shadow: none !important;
        }
        /* 文本域靠左对齐以保证阅读性，边框严格等距 */
        .stTextArea textarea { text-align: left !important; padding: 10px !important; height: 80px !important; line-height: 1.5 !important; }

        /* 💥 下拉框全局基础扁平化 */
        div[data-baseweb="select"] {
            border: 1px solid #333336 !important;
            border-radius: 4px !important;
            box-shadow: none !important;
            transition: background-color 0.3s ease !important; /* 颜色切换丝滑过渡 */
        }
        div[data-baseweb="select"] > div { background-color: transparent !important; border: none !important; }
        /* 框内文字强制居中，高反差白色 */
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
            text-align: center !important; width: 100% !important; font-size: 15px !important; margin: 0 !important; color: #FFFFFF !important;
        }
        div[data-baseweb="select"] span { text-align: center !important; }
        .stSelectbox div[data-baseweb="select"] span[data-baseweb="icon"] { margin-right: 8px !important; color: #8E8E93 !important; }

        /* 下拉菜单面板扁平化 */
        div[data-baseweb="menu"] { background-color: #1E1E20 !important; border: 1px solid #333336 !important; border-radius: 4px !important; padding: 4px !important; }
        div[data-baseweb="menu"] div { text-align: center !important; font-size: 14px !important; color: #A0A0A5 !important; padding: 8px !important; }

        /* 3. 标签排版 */
        .stMarkdown label, p, .stWidgetLabel { font-size: 13px !important; font-weight: 500 !important; color: #8E8E93 !important; margin-bottom: 6px !important; }

        /* 4. 选项卡(Tab)极致去边框 */
        .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #2C2C2E !important; gap: 20px; padding: 0 !important; }
        .stTabs [data-baseweb="tab"] { background-color: transparent !important; border: none !important; color: #8E8E93 !important; font-size: 15px !important; padding: 10px 4px !important; }
        .stTabs [aria-selected="true"] { color: #FFFFFF !important; border-bottom: 2px solid #8E8E93 !important; }

        /* 5. 💥 按钮致敬 33号文件：通栏、暗色、上下边框、文字靠右 */
        .stButton>button {
            background-color: #151516 !important; /* 极暗背景融入底层 */
            color: #A0A0A5 !important;            /* 高级灰文字 */
            border: none !important;
            border-top: 1px solid #2C2C2E !important;    /* 仅保留顶部边线 */
            border-bottom: 1px solid #2C2C2E !important; /* 仅保留底部边线 */
            border-radius: 0 !important;                 /* 彻底砍掉圆角 */
            
            height: 54px !important;
            font-weight: 400 !important;
            font-size: 15px !important;
            
            display: flex !important;
            justify-content: flex-end !important; /* 💥 文字强制靠右对齐 */
            align-items: center !important;
            padding-right: 24px !important;       /* 右侧留白呼吸感 */
            box-shadow: none !important;
            width: 100% !important;
        }
        /* 强制内部元素跟随靠右 */
        .stButton > button span { width: auto !important; display: inline-block !important; text-align: right !important; }
        .stButton>button:hover { background-color: #1E1E20 !important; color: #FFFFFF !important; }

        /* 6. 表格极致扁平 */
        [data-testid="stDataFrame"] { border: none !important; background-color: transparent !important; padding: 0 !important; }
        [data-testid="stDataFrame"] > div { border: none !important; }
        th { border-bottom: 1px solid #333336 !important; background-color: #1A1A1C !important; font-weight: 500;}
        td { border-bottom: 1px solid #2C2C2E !important; border-right: none !important; }
        </style>
    """, unsafe_allow_html=True)

inject_flat_dark_ui()

# ==========================================
# ☁️ 核心数据逻辑
# ==========================================
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注', '录入人', '录入时间']

def style_category(val):
    config = CAT_COLORS.get(val, {"bg": "#242426", "text": "#FFFFFF"})
    return f"background-color: {config['bg']}; color: {config['text']}; font-weight: 500;"
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
        st.error("网络异常")

if 'df' not in st.session_state: st.session_state.df = load_data_from_cloud()

# ==========================================
# 🔒 登录验证
# ==========================================
def login():
    st.markdown("<br><br><br><h2 style='text-align: center; color: #FFFFFF; font-weight: 400; letter-spacing: 2px;'>禹来环保</h2><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("账号")
        password = st.text_input("密码", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("登 录"):
            creds = st.secrets.get("credentials", {})
            if username in creds and creds[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = creds[username]["role"]
                st.rerun()
            else:
                st.error("权限不匹配")
if not st.session_state.get("logged_in", False):
    login()
    st.stop()

with st.sidebar:
    st.markdown(f"<h3 style='color:#FFF;'>{st.session_state['username']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color: #8E8E93; font-size: 12px;'>{'最高权限' if st.session_state['role'] == 'admin' else '业务节点'}</span><br><br>", unsafe_allow_html=True)
    if st.button("同步云端"):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("退出系统"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体界面渲染
# ==========================================
st.title("2026财务库")
tab1, tab2, tab3 = st.tabs(["录入中心", "审计终端", "数据矩阵"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 💥 废弃 st.form 机制，换取下拉框颜色的绝对实时渲染
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("发生时间", datetime.date.today())
        main_cat = st.selectbox("总类别", list(CAT_COLORS.keys()))
        sub_cat = st.text_input("子类别")
        amount = st.number_input("金额", min_value=0.0, step=0.01)
    with col2:
        summary = st.text_area("摘要")
        people = st.text_input("相关人员")
        num_people = st.number_input("人数", min_value=1, value=1)
        applicant = st.text_input("申请人", value=st.session_state["username"])
    with col3:
        location = st.text_input("地点/行程")
        status = st.selectbox("申报状态", list(STATUS_COLORS.keys()))
        remarks = st.text_area("备注信息")
        
    st.markdown("<br>", unsafe_allow_html=True)
    # 💥 极简右对齐操作条按钮 (致敬33图)
    if st.button("提交写入库"):
        month_str = f"{date.month:02d}"
        year_month = f"{date.year % 100:02d}{month_str}"
        current_month_df = st.session_state.df[st.session_state.df['月份'] == month_str]
        serial = f"CL{year_month}{len(current_month_df) + 1:03d}"
        
        new_row = {
            '月份': month_str, '序号': serial, '时间': date.strftime("%Y.%m.%d"),
            '总类别': main_cat, '子类别': sub_cat, '摘要': summary, '人员': people, '人数': num_people, '出发地/目的地': location,
            '金额': amount, '申请人': applicant, '申报状态': status, '备注': remarks,
            '录入人': st.session_state["username"], '录入时间': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        save_data_to_cloud(st.session_state.df)
        st.success(f"已归档 [单号: {serial}]")
        
    # 💥 核心魔法：根据变量动态注入特定的 CSS，实现框体颜色实时变换
    st.markdown(f"""
        <style>
        /* 第一列的下拉框 (总类别) 实时变色 */
        [data-testid="column"]:nth-of-type(1) div[data-baseweb="select"] {{
            background-color: {CAT_COLORS[main_cat]['bg']} !important;
        }}
        /* 第三列的下拉框 (申报状态) 实时变色 */
        [data-testid="column"]:nth-of-type(3) div[data-baseweb="select"] {{
            background-color: {STATUS_COLORS[status]} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("<br><p style='color:#8E8E93; font-size:14px; margin-bottom:5px;'>全局流阅览</p>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=280)
    
    st.markdown("<br><p style='color:#8E8E93; font-size:14px; margin-bottom:5px;'>授权终端</p>", unsafe_allow_html=True)
    if st.session_state["role"] == "admin":
        editable_df = st.session_state.df.copy()
    else:
        now = datetime.datetime.now()
        editable_indices = []
        for idx, row in st.session_state.df.iterrows():
            if row['录入人'] == st.session_state["username"] and row['录入时间'] != "":
                try:
                    if (now - datetime.datetime.strptime(row['录入时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() <= 12 * 3600: editable_indices.append(idx)
                except: pass
        editable_df = st.session_state.df.loc[editable_indices].copy()

    if editable_df.empty and st.session_state["role"] != "admin":
        st.info("当前无编辑权限")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
        if st.button("覆盖更新"):
            if st.session_state["role"] == "admin": st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df[~st.session_state.df['序号'].isin(edited_subset['序号'])].copy()
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            save_data_to_cloud(st.session_state.df)
            st.success("节点同步完成")

    if not st.session_state.df.empty and st.session_state["role"] == "admin":
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("导出矩阵", data=csv, file_name="2026财务库.csv", mime="text/csv")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        
        st.markdown(f"""
        <div style='background: #1A1A1C; border-top: 1px solid #2C2C2E; border-bottom: 1px solid #2C2C2E; padding: 30px; text-align: right; margin-bottom: 30px;'>
            <span style='color: #8E8E93; font-size: 13px; letter-spacing: 2px;'>ANNUAL EXPENDITURE</span><br>
            <span style='color: #FFFFFF; font-size: 32px; font-weight: 300;'>{temp_df['金额'].sum():.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<p style='color:#8E8E93; font-size:13px;'>资产流向</p>", unsafe_allow_html=True)
            fig = px.pie(temp_df.groupby('总类别')['金额'].sum().reset_index(), values='金额', names='总类别', hole=0.75, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig.update_traces(textinfo='none', marker=dict(line=dict(color='#1A1A1C', width=2)))
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("<p style='color:#8E8E93; font-size:13px;'>月度峰值</p>", unsafe_allow_html=True)
            fig_bar = px.bar(temp_df.groupby('月份')['金额'].sum().reset_index(), x='月份', y='金额', color_discrete_sequence=['#2C2C2E'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
            st.plotly_chart(fig_bar, use_container_width=True)

        m1, m2 = st.columns(2)
        with m1:
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            st.dataframe(apply_color_style(cat_sum), use_container_width=True)
        with m2:
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            monthly['金额'] = monthly['金额'].map("{:.2f}".format)
            st.dataframe(monthly, use_container_width=True)
    else:
        st.info("数据载入中")
