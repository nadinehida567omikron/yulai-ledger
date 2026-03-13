import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="禹来企业级财务系统", layout="wide", page_icon="🍎")

# ==========================================
# 🍎 注入 Apple Dark Mode (苹果深色模式) UI 引擎
# ==========================================
def inject_apple_ui():
    st.markdown("""
        <style>
        /* 强制全局调用苹果系统字体 SF Pro */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }
        
        /* 纯粹的深色背景，贴近 iOS 质感 */
        .stApp { background-color: #000000; }
        [data-testid="stSidebar"] { background-color: #1C1C1E !important; }

        /* 顶部 Tab 标签页圆角化，模仿 iOS 分段控制器 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px; background-color: #1C1C1E; padding: 6px; border-radius: 14px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px; padding: 8px 16px; border: none !important;
        }
        .stTabs [aria-selected="true"] { background-color: #3A3A3C !important; }

        /* 输入框、下拉菜单的苹果风大圆角和底色 */
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input, .stTextArea textarea {
            border-radius: 12px !important; background-color: #1C1C1E !important; 
            border: 1px solid #2C2C2E !important; color: #FFFFFF !important;
        }
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
            border-color: #0A84FF !important; box-shadow: 0 0 0 1px #0A84FF !important;
        }

        /* 按钮的大圆角与果味交互动画 */
        .stButton>button {
            border-radius: 14px !important; font-weight: 600 !important; 
            border: none !important; transition: all 0.2s ease;
            background-color: #1C1C1E !important; color: #0A84FF !important;
        }
        .stButton>button[kind="primary"] {
            background-color: #0A84FF !important; color: white !important;
        }
        .stButton>button:hover { transform: scale(0.98); opacity: 0.9; }

        /* DataFrame 表格圆角化 */
        [data-testid="stDataFrame"] { border-radius: 16px; overflow: hidden; border: 1px solid #2C2C2E;}
        </style>
    """, unsafe_allow_html=True)

inject_apple_ui()

# ==========================================
# ☁️ JSONBin 云端数据库引擎 & 专属深色配置
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
    config = CAT_COLORS.get(val, {"bg": "#343A40", "text": "#FFFFFF"})
    return f"background-color: {config['bg']}; color: {config['text']}; font-weight: bold;"

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
                    if col not in df.columns:
                        df[col] = ""
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
        st.error("同步网络发生异常！")

if 'df' not in st.session_state:
    st.session_state.df = load_data_from_cloud()

# ==========================================
# 🔒 RBAC 多角色登录验证
# ==========================================
def login():
    st.markdown("<br><br><h2 style='text-align: center; color: #F5F5F7; font-weight: 600;'>禹来环保记账系统</h2>", unsafe_allow_html=True)
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
                st.error("账号或密码错误")

if not st.session_state.get("logged_in", False):
    login()
    st.stop()

with st.sidebar:
    role_name = "最高权限管理员" if st.session_state["role"] == "admin" else "股东 / 业务员"
    st.markdown(f"### {st.session_state['username']}")
    st.markdown(f"<span style='color: #8E8E93; font-size: 14px;'>{role_name}</span>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 同步云端数据", use_container_width=True):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("退出登录", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体功能区 
# ==========================================
st.title("企业财务核心看板")
tab1, tab2, tab3 = st.tabs(["录入账目", "审计与修改", "BI 洞察"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("发生时间", datetime.date.today())
            main_cat = st.selectbox("总类别", ["接待", "餐旅", "经营管理", "办公费用", "人员薪酬", "其他"])
            sub_cat = st.text_input("子类别 (如：会餐/交通)")
            amount = st.number_input("金额 (元)", min_value=0.0, step=10.0)
        with col2:
            summary = st.text_input("摘要", placeholder="如：客户洽谈")
            people = st.text_input("人员", placeholder="如：张三")
            num_people = st.number_input("人数", min_value=1, value=1)
            applicant = st.text_input("申请人", value=st.session_state["username"])
        with col3:
            location = st.text_input("出发地/目的地")
            status = st.selectbox("申报状态", ["未申报", "已申报", "审批中"])
            remarks = st.text_area("备注")
            
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
            with st.spinner("正在同步至安全云端..."):
                save_data_to_cloud(st.session_state.df)
            st.success(f"入账成功。单号: {serial}。您有12小时的时间可进行修改。")

with tab2:
    st.markdown("<h4 style='font-weight: 600;'>全局数据阅览</h4>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: 
        display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=250)
    
    st.markdown("---")
    st.markdown("<h4 style='font-weight: 600;'>授权修改区</h4>", unsafe_allow_html=True)
    if st.session_state["role"] == "admin":
        st.info("管理员权限：您拥有完整的历史数据管理权。")
        editable_df = st.session_state.df.copy()
    else:
        st.info("股东权限：您可编辑 12 小时内由您提交的账目。")
        now = datetime.datetime.now()
        editable_indices = []
        for idx, row in st.session_state.df.iterrows():
            if row['录入人'] == st.session_state["username"] and row['录入时间'] != "":
                try:
                    record_time = datetime.datetime.strptime(row['录入时间'], "%Y-%m-%d %H:%M:%S")
                    if (now - record_time).total_seconds() <= 12 * 3600:
                        editable_indices.append(idx)
                except: pass
        editable_df = st.session_state.df.loc[editable_indices].copy()

    if editable_df.empty and st.session_state["role"] != "admin":
        st.warning("暂无可修改的数据。")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, height=250, column_config={"金额": st.column_config.NumberColumn("金额 (元)", format="%.2f")})
        if st.button("保存修改", type="primary"):
            if st.session_state["role"] == "admin":
                st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df.copy()
                main_df = main_df[~main_df['序号'].isin(edited_subset['序号'])]
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            
            with st.spinner("正在覆盖更新云端数据..."):
                save_data_to_cloud(st.session_state.df)
            st.success("修改已完成双向同步。")

    if not st.session_state.df.empty and st.session_state["role"] == "admin":
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("导出全量台账 (CSV)", data=csv, file_name="禹来全量台账.csv", mime="text/csv")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        total = temp_df['金额'].sum()
        
        # 苹果风毛玻璃指标卡
        st.markdown(f"""
        <div style='background: rgba(28, 28, 30, 0.8); backdrop-filter: blur(20px); border: 1px solid #2C2C2E; 
        padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3); margin-bottom: 20px;'>
            <span style='color: #8E8E93; font-size: 16px; font-weight: 500;'>企业年度总开支累计</span><br>
            <span style='color: #F5F5F7; font-size: 40px; font-weight: 700; letter-spacing: 1px;'>{total:.2f} <span style='font-size: 20px; color: #8E8E93;'>元</span></span>
        </div>
        """, unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("<h5 style='font-weight: 600;'>各类别开支占比</h5>", unsafe_allow_html=True)
            pie_data = temp_df.groupby('总类别')['金额'].sum().reset_index()
            fig_pie = px.pie(pie_data, values='金额', names='总类别', hole=0.5, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#F5F5F7')
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("<h5 style='font-weight: 600; margin-top: 20px;'>支出明细穿透表</h5>", unsafe_allow_html=True)
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            st.dataframe(apply_color_style(cat_sum.rename(columns={'金额': '累计金额 (元)'})), use_container_width=True)

        with col_chart2:
            st.markdown("<h5 style='font-weight: 600;'>月度开支趋势</h5>", unsafe_allow_html=True)
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            fig_bar = px.bar(monthly, x='月份', y='金额', text_auto='.2f', color_discrete_sequence=['#0A84FF'])
            fig_bar.update_traces(marker_line_radius=8)
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#F5F5F7')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("<h5 style='font-weight: 600; margin-top: 20px;'>月度汇总表</h5>", unsafe_allow_html=True)
            monthly['金额'] = monthly['金额'].map("{:.2f}".format)
            st.dataframe(monthly.rename(columns={'金额': '当月总支出 (元)'}), use_container_width=True)
    else:
        st.info("数据仓库中暂无记录，赶快去记下第一笔开支吧！")
