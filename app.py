import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

st.set_page_config(page_title="禹来企业级财务系统", layout="wide", page_icon="📊")

# ==========================================
# ☁️ JSONBin 云端数据库引擎 & 专属深色配置
# ==========================================
# 严格保留原有字段，新增'录入人'和'录入时间'用于权限审计
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注', '录入人', '录入时间']

# 按照深色调不同色相区分，保持全局颜色联动一致
CAT_COLORS = {
    "接待": {"bg": "#1A237E", "text": "#FFFFFF"},       # 深宝蓝
    "餐旅": {"bg": "#004D40", "text": "#FFFFFF"},       # 深墨绿
    "经营管理": {"bg": "#3E2723", "text": "#FFFFFF"},   # 深咖啡
    "办公费用": {"bg": "#4A148C", "text": "#FFFFFF"},   # 深紫罗兰
    "人员薪酬": {"bg": "#880E4F", "text": "#FFFFFF"},   # 深酒红
    "其他": {"bg": "#263238", "text": "#FFFFFF"}        # 深蓝灰
}
# 提取给 Plotly 图表用的色板，保证图表和表格颜色完全一致
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
                # 兼容老数据，如果没有审计列就补上空值
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
    st.markdown("<br><br><h2 style='text-align: center; color: #333;'>🔒 禹来环保记账系统</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("账号")
        password = st.text_input("密码", type="password")
        if st.button("登录", use_container_width=True):
            creds = st.secrets.get("credentials", {})
            if username in creds and creds[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = creds[username]["role"]
                st.rerun()
            else:
                st.error("❌ 账号或密码错误！")

if not st.session_state.get("logged_in", False):
    login()
    st.stop()

# 侧边栏用户信息
with st.sidebar:
    role_name = "👑 最高权限管理员" if st.session_state["role"] == "admin" else "👤 股东/业务员"
    st.markdown(f"### 当前用户: {st.session_state['username']}")
    st.markdown(f"**身份**: {role_name}")
    st.markdown("---")
    if st.button("🔄 拉取云端最新数据", use_container_width=True):
        load_data_from_cloud.clear()
        st.session_state.df = load_data_from_cloud()
        st.rerun()
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🖥️ 主体功能区 
# ==========================================
st.title("📊 禹来企业级财务系统")
tab1, tab2, tab3 = st.tabs(["💰 录入新账目", "📋 台账与审计修改", "📈 沉浸式 BI 看板"])

with tab1:
    st.markdown("### ✏️ 新增开支申报")
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
            
        if st.form_submit_button("💾 确认提交入账", use_container_width=True):
            month_str = f"{date.month:02d}"
            year_month = f"{date.year % 100:02d}{month_str}"
            current_month_df = st.session_state.df[st.session_state.df['月份'] == month_str]
            # 严格保留自动生成完整序号的功能，绝不删减
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
            with st.spinner("正在安全封存至云端数据库..."):
                save_data_to_cloud(st.session_state.df)
            st.success(f"✅ 提交成功！单号自动生成为: {serial}。您有12小时的时间可进行修改。")

with tab2:
    st.markdown("### 📋 历史台账与权限修改")
    
    # 视图区分：展示全部数据的只读视图（保留彩色）
    st.markdown("##### 👁️ 全局数据阅览 (只读)")
    display_df = st.session_state.df.copy()
    if not display_df.empty: 
        display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
    st.dataframe(apply_color_style(display_df), use_container_width=True, height=250)
    
    st.markdown("---")
    # 权限修改区：Admin 修改所有，Shareholder 修改 12h 内的自己数据
    st.markdown("##### ✍️ 授权修改区")
    if st.session_state["role"] == "admin":
        st.info("👑 管理员权限：您可以双击修改或选中删除下方【所有】历史数据。")
        editable_df = st.session_state.df.copy()
    else:
        st.info("👤 股东权限：您只能修改或删除下方【您自己录入且在 12 小时内】的账目。")
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
        st.warning("您当前没有处于 12 小时修改期内的账目。")
    else:
        edited_subset = st.data_editor(editable_df, num_rows="dynamic", use_container_width=True, height=250, column_config={"金额": st.column_config.NumberColumn("金额 (元)", format="%.2f")})
        if st.button("🔄 保存上述修改至云端", type="primary"):
            if st.session_state["role"] == "admin":
                st.session_state.df = edited_subset
            else:
                # 将股东修改后的小表格合并回大表格
                main_df = st.session_state.df.copy()
                # 剔除原来的老记录
                main_df = main_df[~main_df['序号'].isin(edited_subset['序号'])]
                # 拼接入修改后的新记录
                st.session_state.df = pd.concat([main_df, edited_subset], ignore_index=True)
            
            with st.spinner("正在覆盖更新云端数据..."):
                save_data_to_cloud(st.session_state.df)
            st.success("✅ 修改已完成双向同步！")

    if not st.session_state.df.empty and st.session_state["role"] == "admin":
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 管理员导出全部台账 (CSV)", data=csv, file_name="禹来全量台账.csv", mime="text/csv")

with tab3:
    st.markdown("### 📈 沉浸式财务洞察 BI 看板")
    if not st.session_state.df.empty:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        total = temp_df['金额'].sum()
        
        # 核心指标卡 (严格保留两位小数)
        st.markdown(f"<div style='background-color: #212529; color: #f8f9fa; padding: 20px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>企业年度总开支累计: <span style='color:#e53935'>{total:.2f}</span> 元</div><br>", unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### 🍩 各类别开支占比")
            pie_data = temp_df.groupby('总类别')['金额'].sum().reset_index()
            # 使用 Plotly 画出高级交互式环形图，颜色完美继承深色色板
            fig_pie = px.pie(pie_data, values='金额', names='总类别', hole=0.4, color='总类别', color_discrete_map=PLOTLY_COLORS)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("#### 🏷️ 支出明细穿透表")
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            # 明细汇总严格保留两位小数
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            st.dataframe(apply_color_style(cat_sum.rename(columns={'金额': '累计金额 (元)'})), use_container_width=True)

        with col_chart2:
            st.markdown("#### 📊 月度开支趋势")
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            # 使用 Plotly 画出柱状图
            fig_bar = px.bar(monthly, x='月份', y='金额', text_auto='.2f', color_discrete_sequence=['#455A64'])
            fig_bar.update_layout(xaxis_type='category', margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("#### 📅 月度汇总表")
            # 月度汇总严格保留两位小数
            monthly['金额'] = monthly['金额'].map("{:.2f}".format)
            st.dataframe(monthly.rename(columns={'金额': '当月总支出 (元)'}), use_container_width=True)
    else:
        st.info("数据仓库中暂无记录，赶快去记下第一笔开支吧！")
