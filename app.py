import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="禹来日常记账系统", layout="wide", page_icon="📊")

# ==========================================
# 🔒 密码验证模块
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["pwd_input"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["pwd_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br><h2 style='text-align: center; color: #333;'>🔒 禹来环保记账系统</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.text_input("请输入访问密码：", type="password", on_change=password_entered, key="pwd_input")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<br><br><h2 style='text-align: center; color: #333;'>🔒 禹来环保记账系统</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.text_input("请输入访问密码：", type="password", on_change=password_entered, key="pwd_input")
            st.error("❌ 密码错误，请重新输入！")
        return False
    else:
        return True

if not check_password():
    st.stop()

with st.sidebar:
    st.markdown("### 👤 用户中心")
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

# ==========================================
# 🎨 色彩与核心数据引擎
# ==========================================
DATA_FILE = "yulai_cloud_ledger.csv"
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注']

# --- 高级深色调色板 (基于用户上传图片采样) ---
# 背景色为深色，字体统一强制为纯白(#FFFFFF)
CAT_COLORS = {
    "接待": {"bg": "#1D3E6E", "text": "#FFFFFF"},      # 深宝蓝
    "餐旅": {"bg": "#195458", "text": "#FFFFFF"},      # 深孔雀绿
    "经营管理": {"bg": "#A63A24", "text": "#FFFFFF"},  # 铁锈红
    "办公费用": {"bg": "#4D2B5D", "text": "#FFFFFF"},  # 深紫罗兰
    "人员薪酬": {"bg": "#9E234A", "text": "#FFFFFF"},  # 复古绛红
    "其他": {"bg": "#9B6B1E", "text": "#FFFFFF"}       # 深芥末棕
}

# --- 核心：跨组件颜色渲染器 ---
def style_category(val):
    """用于 Pandas Styler 的单元格颜色渲染"""
    config = CAT_COLORS.get(val, {"bg": "#6c757d", "text": "#FFFFFF"})
    return f"background-color: {config['bg']}; color: {config['text']}; font-weight: bold;"

def apply_color_style(df_to_style):
    """统一为明细表和汇总表穿上'彩色衣服'"""
    # 兼容 pandas 新老版本
    if hasattr(df_to_style.style, 'map'):
        return df_to_style.style.map(style_category, subset=['总类别'])
    else:
        return df_to_style.style.applymap(style_category, subset=['总类别'])

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0.0)
        return df
    return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# ==========================================
# 🖥️ 界面渲染
# ==========================================
st.title("📊 禹来日常记账系统")
tab1, tab2, tab3 = st.tabs(["💰 新增账目", "📋 台账明细与修改", "📈 月度报表汇总"])

# --- 页面 1: 录入新账目 ---
with tab1:
    st.markdown("### ✏️ 录入新账目")
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("时间", datetime.date.today())
            main_cat = st.selectbox("总类别", ["接待", "餐旅", "经营管理", "办公费用", "人员薪酬", "其他"])
            sub_cat = st.text_input("子类别 (如：会餐/交通)")
            amount = st.number_input("金额 (元)", min_value=0.0, step=10.0)
        with col2:
            summary = st.text_input("摘要", placeholder="如：东北菜馆")
            people = st.text_input("人员", placeholder="如：罗一维、郑磊")
            num_people = st.number_input("人数", min_value=1, value=1)
            applicant = st.text_input("申请人")
        with col3:
            location = st.text_input("出发地/目的地", placeholder="如：郑州-上海")
            status = st.selectbox("申报状态", ["未申报", "已申报", "审批中"])
            remarks = st.text_area("备注")
            
        submit = st.form_submit_button("💾 保存记录", use_container_width=True)
        
        if submit:
            month_str = f"{date.month:02d}"
            year_month = f"{date.year % 100:02d}{month_str}"
            current_month_df = st.session_state.df[st.session_state.df['月份'] == month_str]
            count = len(current_month_df) + 1
            serial = f"CL{year_month}{count:03d}"
            
            new_row = {
                '月份': month_str, '序号': serial, '时间': date.strftime("%Y.%m.%d"),
                '总类别': main_cat, '子类别': sub_cat, '摘要': summary,
                '人员': people, '人数': num_people, '出发地/目的地': location,
                '金额': amount, '申请人': applicant, '申报状态': status, '备注': remarks
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"✅ 保存成功！单号自动生成为: {serial}")

# --- 页面 2: 台账明细与超级修改 ---
with tab2:
    st.markdown("### 📋 日常台账明细")
    st.info("💡 双击单元格直接修改内容！修改完务必点击底部的【🔄 保存修改到云端】。导出CSV时格式不受颜色影响。")
    
    if st.session_state.df.empty:
        st.warning("暂无记录。")
    else:
        # 为了让台账明细也有颜色，我们渲染一个带颜色的视图供查看
        # 考虑到 Streamlit 的可编辑表格 (data_editor) 暂时不支持带颜色的 Pandas Styler
        # 我们用一个巧妙的折中办法：不可编辑但带颜色的展示表 + 可编辑但不带颜色的操作表
        
        view_mode = st.toggle("🔍 开启彩色只读阅览模式 (关闭则进入可修改模式)", value=True)
        
        if view_mode:
            # 开启阅览模式：完美彩色渲染，格式化金额为两位小数
            display_df = st.session_state.df.copy()
            display_df['金额'] = pd.to_numeric(display_df['金额']).map("{:.2f}".format)
            st.dataframe(apply_color_style(display_df), use_container_width=True, height=450)
        else:
            # 修改模式：原生编辑器
            st.warning("⚠️ 现处于修改模式，双击修改或按Delete删除。完成后请点击下方保存按钮！")
            edited_df = st.data_editor(
                st.session_state.df,
                num_rows="dynamic",
                use_container_width=True,
                height=450,
                column_config={"金额": st.column_config.NumberColumn("金额 (元)", format="%.2f")}
            )
            col_save, col_exp = st.columns([1, 4])
            if col_save.button("🔄 保存修改到云端", type="primary"):
                st.session_state.df = edited_df
                save_data(edited_df)
                st.success("✅ 修改已保存！请开启上方阅览模式查看彩色效果。")
                
        # 导出按钮
        st.markdown("<br>", unsafe_allow_html=True)
        csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出财务月报 (CSV)", data=csv, file_name="禹来云端台账.csv", mime="text/csv")

# --- 页面 3: 月度与分类报表 ---
with tab3:
    st.markdown("### 📈 财务数据汇总")
    if st.session_state.df.empty:
        st.warning("暂无数据。")
    else:
        temp_df = st.session_state.df.copy()
        temp_df['金额'] = pd.to_numeric(temp_df['金额'], errors='coerce').fillna(0.0)
        total = temp_df['金额'].sum()
        
        st.markdown(f"<div style='background-color: #e9ecef; padding: 15px; border-radius: 5px; font-size: 20px; font-weight: bold; color: #333;'>年度总支出累计: <span style='color:#d32f2f'>{total:.2f}</span> 元</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_m, col_c = st.columns(2)
        with col_m:
            st.markdown("#### 📅 月度总支出汇总")
            monthly = temp_df.groupby('月份')['金额'].sum().reset_index()
            # 强制保留两位小数
            monthly['金额'] = monthly['金额'].map("{:.2f}".format)
            monthly = monthly.rename(columns={'金额': '当月总支出 (元)'})
            st.dataframe(monthly, use_container_width=True)
            
        with col_c:
            st.markdown("#### 🏷️ 各类别支出明细")
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            # 强制保留两位小数
            cat_sum['金额'] = cat_sum['金额'].map("{:.2f}".format)
            cat_sum = cat_sum.rename(columns={'金额': '累计金额 (元)'})
            
            # 使用前面定义的跨组件渲染器，确保和明细表颜色 100% 联动！
            styled_cat_sum = apply_color_style(cat_sum)
            st.dataframe(styled_cat_sum, use_container_width=True)
