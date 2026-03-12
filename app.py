import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="禹来日常记账系统", layout="wide", page_icon="📊")

DATA_FILE = "yulai_cloud_ledger.csv"
COLUMNS = ['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '人数', '出发地/目的地', '金额', '申请人', '申报状态', '备注']

# 颜色配置字典 (用于渲染分类汇总的颜色)
CAT_COLORS = {
    "接待": "#e3f2fd", "餐旅": "#e8f5e9", "经营管理": "#fff3e0",
    "办公费用": "#f3e5f5", "人员薪酬": "#ffebee", "其他": "#f5f5f5"
}

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

# 顶部分类标签卡 (完美复现了之前的三个页面切换)
st.title("📊 禹来日常记账系统 (云端永久免费版)")
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
            
            # 自动计算流水号
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
    st.info("💡 **超级功能（类似Excel）**：双击下方表格的任意单元格可**直接修改**内容！选中左侧的复选框，按键盘 `Delete` 键可**删除**整行！修改完记得点击底部的绿色保存按钮。")
    
    # 核心：调用可编辑的云端数据表
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        use_container_width=True,
        height=400,
        column_config={"金额": st.column_config.NumberColumn("金额 (元)", format="%.2f")}
    )
    
    col_save, col_exp = st.columns([1, 4])
    if col_save.button("🔄 保存修改到云端", type="primary"):
        st.session_state.df = edited_df
        save_data(edited_df)
        st.success("✅ 修改与删除操作已成功同步至云端！")
        
    csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    col_exp.download_button("📥 导出财务月报 (CSV)", data=csv, file_name="禹来云端台账.csv", mime="text/csv")

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
            st.dataframe(monthly, use_container_width=True)
            
        with col_c:
            st.markdown("#### 🏷️ 各类别支出明细")
            cat_sum = temp_df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
            
            # 为分类表格加上柔和的底色
            def color_cat(val):
                color = CAT_COLORS.get(val, "#ffffff")
                return f'background-color: {color}; color: #333;'
                
            styled_cat_sum = cat_sum.style.map(color_cat, subset=['总类别'])
            st.dataframe(styled_cat_sum, use_container_width=True)
