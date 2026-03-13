import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="2026 财务管控库", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 专业级色盘配置 (严格保持深色调不同色相)
# ==========================================
CAT_COLORS = {
    "接待": {"bg": "#101D2B", "text": "#E6F0FA", "border": "#1A2E44"},       
    "餐旅": {"bg": "#12261E", "text": "#E2F2EB", "border": "#1D3A2F"},       
    "经营管理": {"bg": "#2A1E16", "text": "#F5EBE1", "border": "#3D2B20"},   
    "办公费用": {"bg": "#22152E", "text": "#EFE6F7", "border": "#332044"},   
    "人员薪酬": {"bg": "#291419", "text": "#F7E6EB", "border": "#3F1E26"},   
    "其他": {"bg": "#1A1A1C", "text": "#EBEBEB", "border": "#2C2C2E"}        
}
STATUS_COLORS = { "已申报": "#12261E", "未申报": "#2A1E16", "审批中": "#101D2B" }
PLOTLY_COLORS = {k: v["bg"] for k, v in CAT_COLORS.items()}

# ==========================================
# ⬛ 模块化内容矩阵 CSS 引擎
# ==========================================
def inject_matrix_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        .stApp { background-color: #0D0D0F !important; } 
        [data-testid="stSidebar"] { background-color: #121214 !important; border-right: 1px solid #232326 !important; }
        header { visibility: hidden !important; } 
        [data-testid="block-container"] { padding-top: 2rem !important; }

        /* 💥 区块外轮廓配置：定义独立大内容区块的样式，保证宏观对齐 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161618 !important; 
            border: 1px solid #232326 !important; 
            border-radius: 12px !important;       
            padding: 28px 32px 16px 32px !important; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important; 
            margin-bottom: 24px !important;
        }

        /* 💥 区块内小标题排版 */
        .block-title {
            color: #EBEBEB;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid #2C2C2E;
            letter-spacing: 1px;
        }

        /* 统一输入组件的内部栅格高度，剔除冗余边距 */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            background-color: #0D0D0F !important; 
            border: 1px solid #232326 !important;
            border-radius: 8px !important;
            color: #EDEDED !important;
            font-size: 14px !important;
            height: 48px !important;              
            line-height: 48px !important;
            padding: 0 16px !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
            margin-bottom: 8px !important;
        }

        div[data-baseweb="select"] {
            border: 1px solid #232326 !important;
            border-radius: 8px !important;
            height: 48px !important;
            margin-bottom: 8px !important;
            transition: all 0.3s ease !important; 
        }
        div[data-baseweb="select"] > div { background-color: transparent !important; border: none !important; }
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
            font-size: 14px !important; margin: 0 !important; color: #EDEDED !important; font-weight: 500 !important;
            padding-left: 8px !important;
        }
        div[data-baseweb="select"] span[data-baseweb="icon"] { color: #8A8A93 !important; }
        div[data-baseweb="menu"] { background-color: #1E1E20 !important; border: 1px solid #333336 !important; border-radius: 4px !important; padding: 4px !important; }
        div[data-baseweb="menu"] div { font-size: 14px !important; color: #A0A0A5 !important; padding: 8px 12px !important; }

        .stTextInput input:focus, div[data-baseweb="select"]:focus-within {
            border-color: #4A4A52 !important;
            background-color: #121214 !important;
        }

        /* 标签排版对齐 */
        .stMarkdown label, p, .stWidgetLabel { 
            font-size: 13px !important; 
            font-weight: 500 !important; 
            color: #8A8A93 !important; 
            margin-bottom: 8px !important; 
            letter-spacing: 0.5px !important;
        }

        /* 通栏操作区按钮 */
        .stButton>button {
            background-color: #1A1A1D !important; 
            color: #A0A0A5 !important;            
            border: 1px solid #2C2C2E !important;    
            border-radius: 8px !important;                 
            height: 54px !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            display: flex !important;
            justify-content: center !important; 
            align-items: center !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button[kind="primary"] {
            background-color: #12261E !important; /* 主提交按钮采用低明度深绿 */
            border-color: #1D3A2F !important;
            color: #E2F2EB !important;
        }
        .stButton>button:hover { filter: brightness(1.2); color: #FFFFFF !important; }

        /* 表格与选项卡 */
        [data-testid="stDataFrame"] { border: none !important; background-color: transparent !important; }
        th { border-bottom: 1px solid #2C2C30 !important; background-color: #161618 !important; font-weight: 600 !important; color:#8A8A93 !important;}
        td { border-bottom: 1px solid #1E1E21 !important; border-right: none !important; color: #D4D4D8 !important; font-size: 14px !important;}
        
        .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #232326 !important; gap: 32px; padding-bottom: 8px !important; margin-bottom: 32px !important; background-color: transparent !important;}
        .stTabs [data-baseweb="tab"] { border: none !important; color: #66666E !important; font-size: 16px !important; font-weight: 500 !important; background-color: transparent !important;}
        .stTabs [aria-selected="true"] { color: #EDEDED !important; border-bottom: 2px solid #EDEDED !important; }
        </style>
    """, unsafe_allow_html=True)

inject_matrix_ui()

# ==========================================
# ☁️ 核心数据逻辑 (保留自动序号、2位小数)
# ==========================================
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注', '录入人', '录入时间']

def style_category(val):
    config = CAT_COLORS.get(val, {"bg": "#1A1A1C", "text": "#EBEBEB"})
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
        st.error("网络异常，无法同步至云端")

if 'df' not in st.session_state: st.session_state.df = load_data_from_cloud()

# ==========================================
# 🔒 登录系统
# ==========================================
def login():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #EDEDED; font-weight: 600; letter-spacing: 1px;'>系统安全鉴权</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8A8A93; margin-bottom: 30px;'>禹来环保 2026 核心财务数据节点</p>", unsafe_allow_html=True)
        
        username = st.text_input("登录账号")
        password = st.text_input("安全密钥", type="password")
        
        if st.button("验证登录", type="primary"):
            creds = st.secrets.get("credentials", {})
            if username in creds and creds[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = creds[username]["role"]
                st.rerun()
            else:
                st.error("身份验证失败，账号或密码不匹配。")
if not st.session_state.get("logged_in", False):
    login()
    st.stop()

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#EDEDED; font-weight:600; font-size: 20px;'>{st.session_state['username']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color: #8A8A93; font-size: 13px; font-weight: 500; padding: 4px 8px; background: #1C1C1E; border-radius: 4px;'>{'最高权限管理员' if st.session_state['role'] == 'admin' else '业务节点操作员'}</span><br><br><br>", unsafe_allow_html=True)
    
    if st.button("同步底层数据"):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("安全退出系统"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体界面渲染
# ==========================================
st.markdown("<h2 style='color:#EDEDED; font-weight:600; margin-bottom: 24px; font-size: 28px;'>核心工作台</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["录入中心", "审计终端", "数据矩阵"])

with tab1:
    
    # 💥 区块 A：核心账目区块 (带有独立容器轮廓)
    with st.container(border=True):
        st.markdown("<div class='block-title'>核心账目核算维度</div>", unsafe_allow_html=True)
        a_col1, a_col2, a_col3 = st.columns(3) # 内部严谨 3 列栅格
        with a_col1: date = st.date_input("发生时间", datetime.date.today())
        with a_col2: main_cat = st.selectbox("总类别", list(CAT_COLORS.keys()))
        with a_col3: sub_cat = st.text_input("子类别")
        
        a2_col1, a2_col2, a2_col3 = st.columns(3)
        with a2_col1: amount = st.number_input("报销金额 (元)", min_value=0.0, step=0.01)
        with a2_col2: st.empty() # 留白维持矩阵对齐
        with a2_col3: st.empty()

    # 💥 区块 B：业务执行区块 (高度对齐的独立轮廓)
    with st.container(border=True):
        st.markdown("<div class='block-title'>业务执行细节追踪</div>", unsafe_allow_html=True)
        b_col1, b_col2, b_col3 = st.columns(3) # 完全一致的 3 列栅格，贯穿上下
        with b_col1: location = st.text_input("目的地 / 行程")
        with b_col2: people = st.text_input("涉及人员")
        with b_col3: num_people = st.number_input("参与人数", min_value=1, value=1)
        
        b2_col1, b2_col2, b2_col3 = st.columns(3)
        with b2_col1: summary = st.text_input("事由摘要", placeholder="精确描述业务动向")
        with b2_col2: st.empty()
        with b2_col3: st.empty()

    # 💥 区块 C：审计与控制区块
    with st.container(border=True):
        st.markdown("<div class='block-title'>审计控制与提交流</div>", unsafe_allow_html=True)
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1: status = st.selectbox("当前申报状态", list(STATUS_COLORS.keys()))
        with c_col2: applicant = st.text_input("提交申请人", value=st.session_state["username"])
        with c_col3: remarks = st.text_input("补充备注信息", placeholder="选填")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("封装记录并写入底层数据库", type="primary"):
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
            st.success(f"审计日志链已生成。数据节点防伪标识: {serial}")
        
    # 动态 CSS 引擎，精准定位特定区块内的下拉框以实现低明度色彩反馈
    st.markdown(f"""
        <style>
        /* 区块A内的总类别背景反馈 */
        [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(1) [data-testid="column"]:nth-of-type(2) div[data-baseweb="select"] {{
            background-color: {CAT_COLORS[main_cat]['bg']} !important;
            border-color: {CAT_COLORS[main_cat]['border']} !important;
        }}
        /* 区块C内的申报状态背景反馈 */
        [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(3) [data-testid="column"]:nth-of-type(1) div[data-baseweb="select"] {{
            background-color: {STATUS_COLORS[status]} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("<p style='color:#8A8A93; font-size:14px; margin-bottom:12px; font-weight:500;'>全局数据流 (只读节点)</p>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 16px; margin-bottom:32px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=250)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#8A8A93; font-size:14px; margin-bottom:12px; font-weight:500;'>审计与日志覆写终端</p>", unsafe_allow_html=True)
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

    st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 16px; margin-bottom:16px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
    if editable_df.empty and st.session_state["role"] != "admin":
        st.info("当前时间戳内暂无活跃的可编辑数据单元。")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("同步覆写指令至云端数据库", type="primary"):
            if st.session_state["role"] == "admin": st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df[~st.session_state.df['序号'].isin(edited_subset['序号'])].copy()
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            save_data_to_cloud(st.session_state.df)
            st.success("底层数据变更完毕，日志链同步正常。")

    if not st.session_state.df.empty and st.session_state["role"] == "admin":
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("抽取底层全量数据切片 (CSV格式)", data=csv, file_name="2026_财务核心数据.csv", mime="text/csv")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        
        st.markdown(f"""
        <div style='background: #161618; border: 1px solid #232326; border-radius: 12px; padding: 40px; text-align: center; margin-bottom: 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'>
            <span style='color: #8A8A93; font-size: 14px; font-weight: 500; letter-spacing: 2px; text-transform: uppercase;'>年度全域资金净流出量</span><br><br>
            <span style='color: #EDEDED; font-size: 48px; font-weight: 600; letter-spacing: -1px;'>{temp_df['金额'].sum():.2f} <span style='font-size: 18px; color: #66666E;'>CNY</span></span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#8A8A93; font-size:13px; font-weight:500;'>核心资产流向矩阵建模</p>", unsafe_allow_html=True)
            fig = px.pie(temp_df.groupby('总类别')['金额'].sum().reset_index(), values='金额', names='总类别', hole=0.8, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig.update_traces(textinfo='none', marker=dict(line=dict(color='#161618', width=4)))
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font_color='#EDEDED', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#8A8A93; font-size:13px; font-weight:500;'>月度时间轴消耗峰值监测</p>", unsafe_allow_html=True)
            fig_bar = px.bar(temp_df.groupby('月份')['金额'].sum().reset_index(), x='月份', y='金额', color_discrete_sequence=['#4A4A52'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#EDEDED')
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("系统心跳正常，正在等待业务数据流的初始注入...")
