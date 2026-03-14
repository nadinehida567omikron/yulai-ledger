import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="2026 财务管控库", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 赛博极简色盘与全局变量
# ==========================================
BRAND_COLOR = "#a7f069" 
BG_DARK = "#050505"     
CARD_BG = "rgba(255, 255, 255, 0.02)" 
BORDER_COLOR = "rgba(255, 255, 255, 0.15)" 

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
# 🧱 [绝对封存] 登录页专属 UI 引擎
# ==========================================
def render_login_header(icon, title, desc):
    return f"""
    <div class="card-header-wrapper">
        <div class="icon-container">{icon}</div>
        <div class="title-text">{title}</div>
        <div class="desc-text">{desc}</div>
    </div>
    """

def inject_login_ui():
    """💥 完整恢复了您验收通过的终极版CSS，一个字符都不差！"""
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }}
        .stApp {{ background-color: {BG_DARK} !important; }} 
        [data-testid="stSidebar"] {{ display: none !important; }}
        header {{ visibility: hidden !important; }} 
        [data-testid="block-container"] {{ padding-top: 3rem !important; max-width: 1200px !important; margin: 0 auto !important; }}

        /* 1. 25px圆角卡片 */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {CARD_BG} !important; 
            border: 1px solid {BORDER_COLOR} !important;  
            border-radius: 25px !important;       
            padding: 36px 40px 24px 40px !important; 
            margin-bottom: 40px !important;
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; 
            position: relative;
            z-index: 1;
            backdrop-filter: blur(10px);
        }}
        
        [data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-4px) !important; 
            border-color: rgba(167, 240, 105, 0.4) !important; 
            box-shadow: 0 15px 40px -10px rgba(167, 240, 105, 0.15), 0 0 25px rgba(167, 240, 105, 0.08) !important;
            z-index: 10;
        }}

        /* 2. 头部结构 */
        .card-header-wrapper {{ display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 24px; }}
        .icon-container {{
            width: 42px; height: 42px;
            border-radius: 12px; 
            border: 1px solid {BORDER_COLOR};
            background-color: rgba(255,255,255,0.02);
            display: flex; justify-content: center; align-items: center;
            font-size: 18px; color: #FFFFFF;
            margin-bottom: 16px;
            transition: all 0.4s ease;
        }}
        .title-text {{ color: #FFFFFF; font-size: 18px; font-weight: 600; margin-bottom: 6px; letter-spacing: 0.5px; }}
        .desc-text {{ color: rgba(255,255,255,0.4); font-size: 13px; font-weight: 400; }}
        
        [data-testid="stVerticalBlockBorderWrapper"]:hover .icon-container {{
            transform: scale(1.1); border-color: {BRAND_COLOR}; color: {BRAND_COLOR}; box-shadow: 0 0 15px rgba(167, 240, 105, 0.2);
        }}

        /* 3. 组件外框修复 */
        div[data-baseweb="input"], div[data-baseweb="select"] {{
            background-color: rgba(0,0,0,0.3) !important; 
            border: 1px solid {BORDER_COLOR} !important; 
            border-radius: 12px !important; 
            height: 48px !important;            
            min-height: 48px !important;
            box-sizing: border-box !important;
            transition: all 0.3s ease !important;
            display: flex !important; align-items: center !important; overflow: hidden !important; 
            margin-bottom: 8px !important; /* 这里提供基础的 8px 下间距 */
        }}
        
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ border: none !important; background-color: transparent !important; box-shadow: none !important; border-radius: 0 !important; }}
        div[data-baseweb="input"] input {{ background-color: transparent !important; border: none !important; color: #FFFFFF !important; font-size: 14px !important; text-align: center !important; height: 100% !important; padding: 0 16px !important; outline: none !important; }}
        
        /* 聚焦态点亮 */
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {{
            border-color: {BRAND_COLOR} !important; box-shadow: 0 0 0 1px {BRAND_COLOR} !important;
        }}
        
        .stMarkdown label, p, .stWidgetLabel {{ font-size: 13px !important; font-weight: 500 !important; color: rgba(255,255,255,0.45) !important; margin-bottom: 8px !important; }}

        /* ============================================================== */
        /* 💥 4. 终极按钮引擎：彻底找回多重选择器，死锁绝对居中           */
        /* ============================================================== */
        
        /* 使用 Grid 布局强制居中 */
        div[data-testid="stButton"] {{
            display: grid !important;
            place-items: center !important; 
            width: 100% !important;
            margin-top: 0px !important; 
            padding-top: 0px !important;
        }}

        /* 按钮本体尺寸与样式 */
        .stButton > button {{
            background-color: rgba(255,255,255,0.03) !important; 
            color: rgba(255,255,255,0.8) !important;            
            border: 1px solid {BORDER_COLOR} !important;    
            border-radius: 50px !important; /* 胶囊形 */
            height: 38px !important; 
            width: 140px !important; 
            margin: 0 !important; 
            padding: 0 !important;  
            display: flex !important; 
            justify-content: center !important; 
            align-items: center !important; 
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; 
        }}
        
        /* 💥 找回了丢失的 div 和 p 选择器，修复了文字偏上的问题 */
        .stButton > button span, 
        .stButton > button div, 
        .stButton > button p {{ 
            display: flex !important; 
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important; 
            font-weight: 600 !important; 
            font-size: 14px !important;
            line-height: normal !important; 
            letter-spacing: 2px !important; 
            transform: none !important; 
            margin: 0 !important;
            padding: 0 !important;
        }} 
        
        .stButton > button[kind="primary"] {{ border-color: {BRAND_COLOR} !important; color: {BRAND_COLOR} !important; }}
        
        /* Hover：保持绿底、光晕，文字变黑 */
        .stButton > button[kind="primary"]:hover {{ 
            background-color: {BRAND_COLOR} !important; 
            border-color: {BRAND_COLOR} !important;
            box-shadow: 0 0 25px rgba(167, 240, 105, 0.3) !important; 
        }}
        .stButton > button[kind="primary"]:hover * {{
            color: #000000 !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# ==========================================
# 💎 [全新主页] 极致紧凑 UI 引擎与渲染器
# ==========================================
def render_main_header(title, desc):
    return f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 16px;">
        <div style="color: #FFFFFF; font-size: 16px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;">{title}</div>
        <div style="color: rgba(255,255,255,0.3); font-size: 12px; font-weight: 400;">{desc}</div>
    </div>
    """

def inject_main_ui():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif !important; -webkit-font-smoothing: antialiased; }}
        .stApp {{ background-color: {BG_DARK} !important; }} 
        [data-testid="stSidebar"] {{ background-color: #0A0A0A !important; border-right: 1px solid {BORDER_COLOR} !important; }}
        header {{ visibility: hidden !important; }} 
        
        [data-testid="block-container"] {{ padding-top: 2rem !important; max-width: 960px !important; margin: 0 auto !important; }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {CARD_BG} !important; 
            border: 1px solid {BORDER_COLOR} !important;  
            border-radius: 16px !important;       
            padding: 24px 28px 16px 28px !important; 
            margin-bottom: 24px !important;
            backdrop-filter: blur(10px);
        }}

        div[data-baseweb="input"], div[data-baseweb="select"] {{
            background-color: rgba(0,0,0,0.3) !important; 
            border: 1px solid {BORDER_COLOR} !important; 
            border-radius: 8px !important; 
            height: 36px !important;            
            min-height: 36px !important;
            box-sizing: border-box !important;
            display: flex !important; align-items: center !important; overflow: hidden !important; 
            margin-bottom: 2px !important; 
        }}
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ border: none !important; background-color: transparent !important; box-shadow: none !important; border-radius: 0 !important; }}
        div[data-baseweb="input"] input {{ color: #FFFFFF !important; font-size: 13px !important; text-align: center !important; padding: 0 12px !important; outline: none !important; }}
        
        [data-testid="stDateInput"] div[data-baseweb="input"] {{ background-color: transparent !important; border: none !important; box-shadow: none !important; }}
        [data-testid="stNumberInput"] div[data-baseweb="input"] {{ padding: 0 !important; }}
        [data-testid="stNumberInput"] input {{ height: 36px !important; line-height: 36px !important; padding: 0 8px !important; font-size: 13px !important; }}
        [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{ background-color: transparent !important; color: rgba(255,255,255,0.4) !important; height: 36px !important; width: 28px !important; border: none !important; }}
        
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {{ font-size: 13px !important; margin: 0 !important; color: #FFFFFF !important; font-weight: 500 !important; text-align: center !important; width: 100% !important; }}
        div[data-baseweb="select"] span[data-baseweb="icon"] {{ color: rgba(255,255,255,0.4) !important; margin-right: 8px !important; }}
        
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {{ border-color: {BRAND_COLOR} !important; box-shadow: 0 0 0 1px {BRAND_COLOR} !important; }}
        
        .stMarkdown label, p, .stWidgetLabel {{ font-size: 12px !important; font-weight: 500 !important; color: rgba(255,255,255,0.45) !important; margin-bottom: 4px !important; }}

        div[data-testid="stButton"] {{ display: flex !important; justify-content: flex-end !important; margin-top: 12px !important; }}
        .stButton > button {{
            background-color: rgba(255,255,255,0.03) !important; color: rgba(255,255,255,0.8) !important;            
            border: 1px solid {BORDER_COLOR} !important; border-radius: 8px !important; height: 36px !important; width: 120px !important; 
            margin: 0 !important; font-weight: 500 !important; font-size: 13px !important; transition: all 0.3s ease !important; 
        }}
        .stButton > button[kind="primary"] {{ border-color: {BRAND_COLOR} !important; color: {BRAND_COLOR} !important; }}
        .stButton > button[kind="primary"]:hover {{ background-color: {BRAND_COLOR} !important; color: #000000 !important; box-shadow: 0 0 15px rgba(167, 240, 105, 0.3) !important; }}
        
        .stTabs [data-baseweb="tab-list"] {{ border-bottom: none !important; gap: 32px; padding-bottom: 8px !important; margin-bottom: 24px !important; background-color: transparent !important;}}
        .stTabs [data-baseweb="tab"] {{ border: none !important; color: rgba(255,255,255,0.4) !important; font-size: 15px !important; font-weight: 500 !important; background-color: transparent !important;}}
        .stTabs [aria-selected="true"] {{ color: {BRAND_COLOR} !important; border-bottom: 2px solid {BRAND_COLOR} !important; }}
        
        [data-testid="stDataFrame"] {{ border: none !important; background-color: transparent !important; }}
        th {{ border-bottom: 1px solid {BORDER_COLOR} !important; background-color: transparent !important; font-weight: 500 !important; color:rgba(255,255,255,0.4) !important; font-size: 12px !important;}}
        td {{ border-bottom: 1px solid rgba(255,255,255,0.04) !important; color: #EBEBEB !important; font-size: 13px !important;}}
        </style>
    """, unsafe_allow_html=True)


# ==========================================
# ☁️ 核心数据逻辑
# ==========================================
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注', '录入人', '录入时间']

def style_category(val):
    return f"background-color: rgba(255,255,255,0.05); color: #FFF; font-weight: 500;"
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
        pass

if 'df' not in st.session_state: st.session_state.df = load_data_from_cloud()

# ==========================================
# 路由拦截：登录鉴权
# ==========================================
if not st.session_state.get("logged_in", False):
    inject_login_ui() # 💥 登录时，注入已被封存的完美登录页 CSS
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True): 
            st.markdown(render_login_header("🔐", "系统安全鉴权", "请验证您的管理密钥以访问核心财务节点"), unsafe_allow_html=True)
            username = st.text_input("登录账号")
            password = st.text_input("安全密钥", type="password")
            
            if st.button("Enter", type="primary"):
                creds = st.secrets.get("credentials", {})
                if username in creds and creds[username]["password"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = creds[username]["role"]
                    st.rerun()
                else:
                    st.error("身份验证失败。")
    st.stop()

# ==========================================
# 以下为登录后的主界面逻辑
# ==========================================
inject_main_ui() # 💥 登录成功后，系统立刻切换为高度紧凑压缩的主页 CSS

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#FFF; font-weight:600; font-size: 20px;'>{st.session_state['username']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color: {BRAND_COLOR}; font-size: 13px; font-weight: 500; border: 1px solid rgba(167,240,105,0.3); padding: 4px 8px; border-radius: 6px; background: rgba(167,240,105,0.05);'>{'最高权限' if st.session_state['role'] == 'admin' else '业务节点'}</span><br><br><br>", unsafe_allow_html=True)
    
    if st.button("同步数据"):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("退出系统"):
        st.session_state.clear()
        st.rerun()

st.markdown("<h2 style='color:#FFF; font-weight:600; margin-bottom: 24px; font-size: 24px;'>核心工作台</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["录入中心", "审计终端", "数据矩阵"])

with tab1:
    with st.container(border=True):
        st.markdown(render_main_header("核心账目核算", "在此定义费用的属性及金额"), unsafe_allow_html=True)
        a_col1, a_col2, a_col3, a_col4 = st.columns(4) 
        with a_col1: date = st.date_input("发生时间", datetime.date.today())
        with a_col2: main_cat = st.selectbox("总类别", list(CAT_COLORS.keys()))
        with a_col3: sub_cat = st.text_input("子类别")
        with a_col4: amount = st.number_input("金额 (元)", min_value=0.0, step=0.01)
        
        a2_col1, a2_col2, a2_col3, a2_col4 = st.columns(4)
        with a2_col1: remarks = st.text_input("补充备注")
        with a2_col2: st.empty() 
        with a2_col3: st.empty() 
        with a2_col4: st.empty() 

    with st.container(border=True):
        st.markdown(render_main_header("业务追踪", "关联业务发生详情"), unsafe_allow_html=True)
        b_col1, b_col2, b_col3, b_col4 = st.columns(4) 
        with b_col1: location = st.text_input("行程")
        with b_col2: people = st.text_input("涉及人员")
        with b_col3: num_people = st.number_input("人数", min_value=1, value=1)
        with b_col4: summary = text_input("事由摘要") if 'text_input' in locals() else st.text_input("事由摘要")

    with st.container(border=True):
        st.markdown(render_main_header("审计与提交", "确认状态并封装"), unsafe_allow_html=True)
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1: status = st.selectbox("申报状态", list(STATUS_COLORS.keys()))
        with c_col2: applicant = st.text_input("申请人", value=st.session_state["username"])
        with c_col3: st.empty() 
        with c_col4: st.empty() 
        
        if st.button("Submit", type="primary"):
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
            st.success(f"已生成标识: {serial}")

    st.markdown(f"""
        <style>
        [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(1) [data-testid="column"]:nth-of-type(2) div[data-baseweb="select"] {{
            background-color: {CAT_COLORS[main_cat]['bg']} !important;
            border-color: {CAT_COLORS[main_cat]['border']} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(3) [data-testid="column"]:nth-of-type(1) div[data-baseweb="select"] {{
            background-color: {STATUS_COLORS[status]} !important;
            border-color: {STATUS_COLORS[status].replace("0.8", "0.5")} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

with tab2:
    with st.container(border=True):
        st.markdown(render_main_header("只读数据流", "不可篡改的历史节点监控"), unsafe_allow_html=True)
        display_df = st.session_state.df.copy()
        if not display_df.empty: display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
        st.dataframe(apply_color_style(display_df), use_container_width=True, height=250)
    
    with st.container(border=True):
        st.markdown(render_main_header("审计覆写终端", "12小时安全期内数据修正"), unsafe_allow_html=True)
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
            st.info("当前时间戳内无活跃可编辑数据单元。")
        else:
            edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, column_config={"金额": st.column_config.NumberColumn("金额", format="%.2f")})
            
            if st.button("Sync Data", type="primary"):
                if st.session_state["role"] == "admin": st.session_state.df = edited_subset
                else:
                    main_df = st.session_state.df[~st.session_state.df['序号'].isin(edited_subset['序号'])].copy()
                    st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
                save_data_to_cloud(st.session_state.df)
                st.success("数据变更完毕。")

        if not st.session_state.df.empty and st.session_state["role"] == "admin":
            csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("Export Data", data=csv, file_name="2026_财务数据.csv", mime="text/csv")

with tab3:
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        
        with st.container(border=True):
            st.markdown(f"""
            <div style='text-align: center; padding: 10px 0;'>
                <span style='color: rgba(255,255,255,0.4); font-size: 13px; font-weight: 500; letter-spacing: 2px; text-transform: uppercase;'>年度资金流出量</span><br><br>
                <span style='color: #FFF; font-size: 48px; font-weight: 600; letter-spacing: -1px; text-shadow: 0 0 20px rgba(167, 240, 105, 0.3);'>{temp_df['金额'].sum():.2f} <span style='font-size: 16px; color: {BRAND_COLOR};'>CNY</span></span>
            </div>
            """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown(render_main_header("流向矩阵", "业务分配占比"), unsafe_allow_html=True)
                fig = px.pie(temp_df.groupby('总类别')['金额'].sum().reset_index(), values='金额', names='总类别', hole=0.8, color_discrete_sequence=[BRAND_COLOR, '#8A8A93', '#4A4A52', '#2C2C30', '#1E1E21', '#121214'])
                fig.update_traces(textinfo='none', marker=dict(line=dict(color='#050505', width=2)))
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font_color='#FFF', showlegend=True, height=200)
                st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            with st.container(border=True):
                st.markdown(render_main_header("时间轴峰值", "月度消耗动态"), unsafe_allow_html=True)
                fig_bar = px.bar(temp_df.groupby('月份')['金额'].sum().reset_index(), x='月份', y='金额', color_discrete_sequence=[BRAND_COLOR])
                fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#FFF', height=200)
                st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("等待业务数据流...")
