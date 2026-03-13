import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

# 隐藏 Streamlit 默认的顶部导航和汉堡菜单，打造纯净客户端体验
st.set_page_config(page_title="2026 财务管控库", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 专业级色盘：低纯度 / 低明度色系 (严格参考高级 UI)
# ==========================================
CAT_COLORS = {
    "接待": {"bg": "#101D2B", "text": "#E6F0FA", "border": "#1A2E44"},       # 深海蓝
    "餐旅": {"bg": "#12261E", "text": "#E2F2EB", "border": "#1D3A2F"},       # 深松绿
    "经营管理": {"bg": "#2A1E16", "text": "#F5EBE1", "border": "#3D2B20"},   # 深焦褐
    "办公费用": {"bg": "#22152E", "text": "#EFE6F7", "border": "#332044"},   # 深暗紫
    "人员薪酬": {"bg": "#291419", "text": "#F7E6EB", "border": "#3F1E26"},   # 深酒红
    "其他": {"bg": "#1A1A1C", "text": "#EBEBEB", "border": "#2C2C2E"}        # 深炭灰
}
STATUS_COLORS = {
    "已申报": "#12261E", "未申报": "#2A1E16", "审批中": "#101D2B"
}
PLOTLY_COLORS = {k: v["bg"] for k, v in CAT_COLORS.items()}

# ==========================================
# ⬛ 彻底推倒重来的前端 CSS 架构
# ==========================================
def inject_professional_ui():
    st.markdown("""
        <style>
        /* 引入高级无衬线字体，替代默认生硬字体 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        /* 1. 极致底层背景 */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        .stApp { background-color: #0D0D0F !important; } /* 极深渊黑背景 */
        [data-testid="stSidebar"] { background-color: #121214 !important; border-right: 1px solid #232326 !important; }
        header { visibility: hidden !important; } /* 隐藏顶部多余白条 */

        /* 2. 背景模块层次化 */
        [data-testid="block-container"] {
            padding-top: 2rem !important;
        }

        /* 3. 输入组件的“专业客户端”质感 */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            background-color: #0D0D0F !important; /* 输入框内嵌深色，产生层次 */
            border: 1px solid #232326 !important;
            border-radius: 8px !important;
            color: #EDEDED !important;
            font-size: 14px !important;
            height: 48px !important;              /* 💥 拉高控件，彻底摆脱拥挤感 */
            line-height: 48px !important;
            padding: 0 16px !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }

        /* 💥 像素级栅格补偿：修复“事由摘要”文本框与其他两行输入框的总高度对齐问题 */
        .stTextArea textarea { 
            background-color: #0D0D0F !important;
            border: 1px solid #232326 !important;
            border-radius: 8px !important;
            color: #EDEDED !important;
            font-size: 14px !important;
            height: 140px !important;       /* 精准高度拉伸 */
            line-height: 1.6 !important; 
            padding: 12px 16px !important; 
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stTextArea"] {
            margin-bottom: 2px !important;  /* 消除底部多余外边距，完美贴合 */
        }

        /* 下拉菜单扁平与颜色联动 */
        div[data-baseweb="select"] {
            border: 1px solid #232326 !important;
            border-radius: 8px !important;
            height: 48px !important;
            transition: all 0.3s ease !important; /* 颜色切换丝滑过渡 */
        }
        div[data-baseweb="select"] > div { background-color: transparent !important; border: none !important; }
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
            font-size: 14px !important; margin: 0 !important; color: #EDEDED !important; font-weight: 500 !important;
            padding-left: 8px !important;
        }
        div[data-baseweb="select"] span[data-baseweb="icon"] { color: #8A8A93 !important; }
        
        /* 下拉菜单面板扁平化 */
        div[data-baseweb="menu"] { background-color: #1E1E20 !important; border: 1px solid #333336 !important; border-radius: 4px !important; padding: 4px !important; }
        div[data-baseweb="menu"] div { font-size: 14px !important; color: #A0A0A5 !important; padding: 8px 12px !important; }

        /* 交互反馈 */
        .stTextInput input:focus, div[data-baseweb="select"]:focus-within, .stTextArea textarea:focus {
            border-color: #4A4A52 !important;
            background-color: #121214 !important;
        }

        /* 4. 标签文字 (精致副标题) */
        .stMarkdown label, p, .stWidgetLabel { 
            font-size: 13px !important; 
            font-weight: 500 !important; 
            color: #8A8A93 !important; 
            margin-bottom: 8px !important; 
            letter-spacing: 0.5px !important;
        }

        /* 5. 💥 按钮重构致敬参考图：通栏、极简、暗黑、靠右对齐 */
        .stButton>button {
            background-color: #151516 !important; 
            color: #A0A0A5 !important;            
            border: none !important;
            border-top: 1px solid #2C2C2E !important;    
            border-bottom: 1px solid #2C2C2E !important; 
            border-radius: 0 !important;                 /* 彻底砍掉圆角 */
            height: 54px !important;
            font-weight: 400 !important;
            font-size: 15px !important;
            margin-top: 12px !important;
            display: flex !important;
            justify-content: flex-end !important; /* 文字强制靠右对齐 */
            align-items: center !important;
            padding-right: 24px !important;       /* 右侧留白呼吸感 */
            box-shadow: none !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button span { width: auto !important; display: inline-block !important; text-align: right !important; }
        .stButton>button:hover { background-color: #1E1E20 !important; color: #FFFFFF !important; }

        /* 6. 表格与指标卡极致扁平 */
        [data-testid="stDataFrame"] { border: none !important; background-color: transparent !important; }
        th { border-bottom: 1px solid #2C2C30 !important; background-color: #161618 !important; font-weight: 600 !important; color:#8A8A93 !important;}
        td { border-bottom: 1px solid #1E1E21 !important; border-right: none !important; color: #D4D4D8 !important; font-size: 14px !important;}
        
        /* 选项卡 Tab 去线化，仅用亮色文字区分 */
        .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #232326 !important; gap: 32px; padding-bottom: 8px !important; margin-bottom: 32px !important; background-color: transparent !important;}
        .stTabs [data-baseweb="tab"] { border: none !important; color: #66666E !important; font-size: 16px !important; font-weight: 500 !important; background-color: transparent !important;}
        .stTabs [aria-selected="true"] { color: #EDEDED !important; border-bottom: 2px solid #EDEDED !important; }
        </style>
    """, unsafe_allow_html=True)

inject_professional_ui()

# ==========================================
# ☁️ 核心数据逻辑
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
# 🔒 登录验证模块 (纯中文系统鉴权)
# ==========================================
def login():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #EDEDED; font-weight: 600; letter-spacing: 1px;'>系统安全鉴权</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8A8A93; margin-bottom: 30px;'>禹来环保 2026 核心财务数据节点</p>", unsafe_allow_html=True)
        
        username = st.text_input("登录账号")
        password = st.text_input("安全密钥", type="password")
        
        if st.button("验证登录"):
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

# ==========================================
# 🎛️ 侧边栏 (极简信息板)
# ==========================================
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#EDEDED; font-weight:600; font-size: 20px;'>{st.session_state['username']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color: #8A8A93; font-size: 13px; font-weight: 500; padding: 4px 8px; background: #1C1C1E; border-radius: 4px;'>{'最高权限管理员' if st.session_state['role'] == 'admin' else '业务节点操作员'}</span><br><br><br>", unsafe_allow_html=True)
    
    if st.button("同步底层数据"):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("安全退出系统"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体界面渲染
# ==========================================
st.markdown("<h2 style='color:#EDEDED; font-weight:600; margin-bottom: 24px; font-size: 28px;'>核心工作台</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["录入中心", "审计终端", "数据矩阵"])

with tab1:
    st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 32px 32px 16px 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom:32px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-weight: 600; font-size:16px; color:#EDEDED; margin-bottom: 24px;'>创建台账记录</h4>", unsafe_allow_html=True)
    
    # 取消 st.form，实现下拉框实时渲染反馈
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("发生时间", datetime.date.today())
        main_cat = st.selectbox("总类别", list(CAT_COLORS.keys()))
        sub_cat = st.text_input("子类别")
        amount = st.number_input("报销金额 (元)", min_value=0.0, step=0.01)
    with col2:
        # 这里的文本框通过前面的 CSS 已被精确拉伸到 140px，完美对齐两边栅格
        summary = st.text_area("事由摘要")
        people = st.text_input("涉及人员")
        num_people = st.number_input("参与人数", min_value=1, value=1)
    with col3:
        location = st.text_input("目的地 / 行程")
        status = st.selectbox("当前申报状态", list(STATUS_COLORS.keys()))
        applicant = st.text_input("提交申请人", value=st.session_state["username"])
        remarks = st.text_input("补充备注信息")
        
    if st.button("确认并写入数据库"):
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
        st.success(f"数据记录生成成功。系统防伪单号: {serial}")
        
    st.markdown("</div>", unsafe_allow_html=True)
        
    # 💥 动态 CSS 注入：捕捉选项变化，赋予下拉框低纯度暗色背景
    st.markdown(f"""
        <style>
        [data-testid="column"]:nth-of-type(1) div[data-baseweb="select"] {{
            background-color: {CAT_COLORS[main_cat]['bg']} !important;
            border-color: {CAT_COLORS[main_cat]['border']} !important;
        }}
        [data-testid="column"]:nth-of-type(3) div[data-baseweb="select"] {{
            background-color: {STATUS_COLORS[status]} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("<p style='color:#8A8A93; font-size:14px; margin-bottom:12px; font-weight:500;'>全局数据流 (只读)</p>", unsafe_allow_html=True)
    display_df = st.session_state.df.copy()
    if not display_df.empty: display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 16px; margin-bottom:32px;'>", unsafe_allow_html=True)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=250)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#8A8A93; font-size:14px; margin-bottom:12px; font-weight:500;'>审计与覆写终端</p>", unsafe_allow_html=True)
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

    st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 16px; margin-bottom:16px;'>", unsafe_allow_html=True)
    if editable_df.empty and st.session_state["role"] != "admin":
        st.info("当前 12 小时内暂无您可编辑的活跃记录。")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("保存覆写记录至云端"):
            if st.session_state["role"] == "admin": st.session_state.df = edited_subset
            else:
                main_df = st.session_state.df[~st.session_state.df['序号'].isin(edited_subset['序号'])].copy()
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            save_data_to_cloud(st.session_state.df)
            st.success("审计日志已成功同步。")

    if not st.session_state.df.empty and st.session_state["role"] == "admin":
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("导出底层原始数据 (CSV)", data=csv, file_name="2026_财务核心数据.csv", mime="text/csv")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        
        st.markdown(f"""
        <div style='background: #161618; border: 1px solid #232326; border-radius: 12px; padding: 40px; text-align: center; margin-bottom: 32px;'>
            <span style='color: #8A8A93; font-size: 14px; font-weight: 500; letter-spacing: 2px;'>年度累计资金流出总额</span><br><br>
            <span style='color: #EDEDED; font-size: 48px; font-weight: 600; letter-spacing: -1px;'>{temp_df['金额'].sum():.2f} <span style='font-size: 18px; color: #66666E;'>元</span></span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 24px;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#8A8A93; font-size:13px; font-weight:500;'>核心资产流向矩阵</p>", unsafe_allow_html=True)
            fig = px.pie(temp_df.groupby('总类别')['金额'].sum().reset_index(), values='金额', names='总类别', hole=0.8, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig.update_traces(textinfo='none', marker=dict(line=dict(color='#161618', width=4)))
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font_color='#EDEDED', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div style='background-color:#161618; border:1px solid #232326; border-radius:12px; padding: 24px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#8A8A93; font-size:13px; font-weight:500;'>月度资金消耗峰值</p>", unsafe_allow_html=True)
            fig_bar = px.bar(temp_df.groupby('月份')['金额'].sum().reset_index(), x='月份', y='金额', color_discrete_sequence=['#4A4A52'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#EDEDED')
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("系统正等待数据节点接入...")
