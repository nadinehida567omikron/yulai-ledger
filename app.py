import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="禹来企业级财务系统", layout="wide", page_icon="📊")

# ==========================================
# ⬛ 注入极致暗黑扁平风 (Dark Flat + Noise) UI 引擎
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
            background-color: #1A1A1C !important; /* 深灰底色 */
            /* 注入微弱的噪点/杂点 SVG 纹理 */
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E") !important;
        }
        [data-testid="stSidebar"] { 
            background-color: #151516 !important; 
            border-right: 1px solid #2C2C2E !important;
        }

        /* 2. 输入组件彻底扁平化 + 强制垂直水平居中 */
        .stTextInput input, 
        .stNumberInput input, 
        .stDateInput input, 
        .stTextArea textarea {
            background-color: #242426 !important; /* 扁平填充色 */
            border: 1px solid #333336 !important; /* 极弱边框 */
            border-radius: 6px !important;        /* 收敛圆角，更显专业 */
            color: #FFFFFF !important;
            
            text-align: center !important;        /* 💥 强制文字居中对齐 */
            font-size: 15px !important;           /* 舒适字号 */
            height: 42px !important;
            line-height: 42px !important;
            padding: 0 10px !important;
            box-shadow: none !important;          /* 剔除多余底框/阴影 */
        }

        /* 💥 下拉框专属扁平化调整：深蓝底 + 白字 */
        div[data-baseweb="select"] {
            background-color: #1C355E !important; /* 深空蓝填充色 */
            border: 1px solid #333336 !important;
            border-radius: 6px !important;
            box-shadow: none !important;
        }
        div[data-baseweb="select"] > div {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        /* 强制下拉框选中文字居中，箭头置于右下角附近 */
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
            text-align: center !important;
            width: 100% !important;
            font-size: 15px !important;
            margin: 0 !important;
            color: #FFFFFF !important; /* 下拉文字纯白，拉开反差 */
        }
        /* 箭头对齐修正 */
        div[data-baseweb="select"] span { text-align: center !important; }
        .stSelectbox div[data-baseweb="select"] span[data-baseweb="icon"] { margin-right: 5px !important; }

        /* 3. 标签(Label)排版美化 */
        .stMarkdown label, p, .stWidgetLabel {
            font-size: 13px !important;
            font-weight: 500 !important;
            color: #8E8E93 !important; 
            margin-bottom: 6px !important;
        }

        /* 4. 选项卡 Tab 的极致扁平化去套框 */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important; /* 去除大背景框 */
            border-bottom: 1px solid #2C2C2E !important; /* 仅保留底部分割线 */
            gap: 20px;
            padding: 0 !important;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            border: none !important;
            color: #8E8E93 !important;
            font-size: 15px !important;
            padding: 10px 4px !important;
        }
        .stTabs [aria-selected="true"] { 
            color: #FFFFFF !important;
            border-bottom: 2px solid #0A84FF !important; /* 底部指示蓝条 */
        }

        /* 5. 按钮：文字强制居中、纯白 */
        .stButton>button {
            border-radius: 6px !important;
            height: 44px !important;
            font-weight: 500 !important;
            font-size: 16px !important;
            border: none !important;
            
            display: flex !important;             /* 💥 强制布局居中 */
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
            box-shadow: none !important;          /* 扁平化无阴影 */
            width: 100% !important;
        }
        /* 登录按钮特定样式 (确保居中和反差) */
        .stButton>button[kind="primary"] {
            background-color: #0A84FF !important; 
            color: #FFFFFF !important;            /* 💥 字体颜色强制纯白 */
        }
        /* 扁平按钮样式 */
        .stButton>button[kind="secondary"] {
            background-color: #242426 !important;
            color: #0A84FF !important;
        }
        .stButton>button:hover { opacity: 0.9; }

        /* 6. 表格：彻底删除外部大框，极致扁平 */
        [data-testid="stDataFrame"] { 
            border: none !important;              /* 💥 彻底删除外框 */
            background-color: transparent !important;
            padding: 0 !important;
        }
        [data-testid="stDataFrame"] > div { border: none !important; }
        /* 内部弱分割线 */
        th { border-bottom: 1px solid #333336 !important; background-color: #1E1E20 !important; font-weight: 500;}
        td { border-bottom: 1px solid #2C2C2E !important; border-right: none !important; }
        </style>
    """, unsafe_allow_html=True)

inject_flat_dark_ui()

# ==========================================
# ☁️ 核心数据逻辑 (100% 保持严密防篡改机制)
# ==========================================
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注', '录入人', '录入时间']

# 按照深色调不同色相区分，保持全局颜色联动一致
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
    config = CAT_COLORS.get(val, {"bg": "#242426", "text": "#FFFFFF"})
    return f"background-color: {config['bg']}; color: {config['text']}; font-weight: 500; border-radius: 4px;"

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
# 🔒 登录验证 (登录按钮已完美居中纯白)
# ==========================================
def login():
    st.markdown("<br><br><h2 style='text-align: center; color: #FFFFFF; font-weight: 500; letter-spacing: 1px;'>禹来环保</h2>", unsafe_allow_html=True)
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
    role_name = "最高权限管理员" if st.session_state["role"] == "admin" else "股东/业务员"
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
st.title("2026财务库")
tab1, tab2, tab3 = st.tabs(["💰 录入中心", "📋 审计与修改", "📈 数据矩阵看板"])

with tab1:
    st.markdown("<h4 style='font-weight: 600; font-size:18px; color:#F5F5F7;'>✏️ 新增开支录入</h4>", unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("发生时间", datetime.date.today())
            main_cat = st.selectbox("总类别", ["接待", "餐旅", "经营管理", "办公费用", "人员薪酬", "其他"])
            sub_cat = st.text_input("子类别")
            amount = st.number_input("金额 (元)", min_value=0.0, step=0.01)
        with col2:
            summary = st.text_input("摘要", placeholder="事由简述")
            people = st.text_input("相关人员", placeholder="如：张三")
            num_people = st.number_input("人数", min_value=1, value=1)
            applicant = st.text_input("申请人", value=st.session_state["username"])
        with col3:
            location = st.text_input("地点/行程")
            status = st.selectbox("申报状态", ["未申报", "已申报", "审批中"])
            remarks = st.text_area("备注信息")
            
        if st.form_submit_button("💾 提交写入库", use_container_width=True):
            month_str = f"{date.month:02d}"
            year_month = f"{date.year % 100:02d}{month_str}"
            current_month_df = st.session_state.df[st.session_state.df['月份'] == month_str]
            # 自动单号生成功能严格保持，单号自动加1
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
            st.success(f"写入成功！系统单号自动生成为: {serial}")

with tab2:
    st.markdown("<h4 style='font-weight: 600; font-size:16px; margin-bottom:10px;'>📋 全局数据流阅览 (扁平视图)</h4>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: 
        display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    # 表格外框已被CSS完全消除
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=300)
    
    st.markdown("---")
    st.markdown("<h4 style='font-weight: 600; font-size:16px; margin-bottom:10px;'>✍️ 授权审计修改区</h4>", unsafe_allow_html=True)
    if st.session_state["role"] == "admin":
        st.info("管理员权限：您可以双击修改或选中删除下方表格内的【所有】历史数据。")
        editable_df = st.session_state.df.copy()
    else:
        st.info("股东权限：您只能修改或删除下方表格中【由您本人录入且在 12 小时内】的账目。")
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
        st.warning("您当前没有处于 12 小时修改期内的账目。以前的账目对您来说是只读的铁案。")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
        if st.button("🔄 保存上述修改至库", type="primary"):
            if st.session_state["role"] == "admin":
                st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df.copy()
                main_df = main_df[~main_df['序号'].isin(edited_subset['序号'])]
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            with st.spinner("同步库内数据..."): save_data_to_cloud(st.session_state.df)
            st.success("审计终端已同步成功。")

    if not st.session_state.df.empty and st.session_state["role"] == "admin":
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出全量台账CSV", data=csv, file_name="禹来财务全量台账.csv", mime="text/csv")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        total = temp_df['金额'].sum()
        
        # 极简扁平的数据指标卡
        st.markdown(f"""
        <div style='background: #242426; border: 1px solid #333336; padding: 25px; border-radius: 8px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 30px;'>
            <span style='color: #8E8E93; font-size: 14px; font-weight: 500; letter-spacing: 1px;'>年度累计核算开支</span><br>
            <span style='color: #FFFFFF; font-size: 38px; font-weight: 600; letter-spacing: -1px;'>{total:.2f} <span style='font-size: 16px; color: #8E8E93;'>元 (CNY)</span></span>
        </div>
        """, unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("<h5 style='font-weight: 600; font-size:16px; color:#F5F5F7; margin-bottom:15px;'>🍩 各类别占比</h5>", unsafe_allow_html=True)
            pie_data = temp_df.groupby('总类别')['金额'].sum().reset_index()
            # 图表颜色完美联动深色分类色板
            fig = px.pie(pie_data, values='金额', names='总类别', hole=0.6, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig.update_traces(textinfo='percent', marker=dict(line=dict(color='#1A1A1C', width=3)))
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            st.markdown("<h5 style='font-weight: 600; font-size:16px; color:#F5F5F7; margin-bottom:15px;'>📊 月度开支趋势</h5>", unsafe_allow_html=True)
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            # 柱状图采用苹果标志蓝
            fig_bar = px.bar(monthly, x='月份', y='金额', text_auto='.2f', color_discrete_sequence=['#0A84FF'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            # 明细严格保留两位小数
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            st.dataframe(apply_color_style(cat_sum.rename(columns={'金额': '累计金额'})), use_container_width=True)
        with col_m2:
            monthly_table = monthly.copy()
            monthly_table['金额'] = monthly_table['金额'].map("{:.2f}".format)
            st.dataframe(monthly_table.rename(columns={'金额': '当月总支出'}), use_container_width=True)
    else:
        st.info("等待数据节点接入...")
