import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="禹来记账系统", layout="wide")
DATA_FILE = "yulai_cloud_ledger.csv"

# --- 核心数据处理 ---
@st.cache_data(ttl=0) # 确保数据实时刷新
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['月份', '序号', '时间', '总类别', '子类别', '摘要', '人员', '金额', '申请人', '备注'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

df = load_data()

# --- 侧边栏导航 ---
st.sidebar.title("📊 禹来环保云端账本")
menu = st.sidebar.radio("导航菜单", ["💰 新增账目", "📋 台账明细", "📈 月度汇总"])

# --- 功能 1: 新增账目录入 ---
if menu == "💰 新增账目":
    st.header("✏️ 录入新账目")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("时间", datetime.date.today())
            main_category = st.selectbox("总类别", ["接待", "餐旅", "经营管理", "办公费用", "人员薪酬", "其他"])
            amount = st.number_input("金额 (元)", min_value=0.0, step=10.0, format="%.2f")
        with col2:
            sub_category = st.text_input("子类别 (如: 会餐, 交通)")
            people = st.text_input("人员 (如: 罗一维、郑磊)")
            applicant = st.text_input("申请人")
        with col3:
            summary = st.text_input("摘要 (消费说明)")
            remarks = st.text_input("备注")
            
        if st.form_submit_button("💾 保存记录"):
            month = f"{date.month:02d}"
            year_month = f"{date.year % 100:02d}{month}"
            
            # 生成序号
            monthly_records = df[df['月份'] == int(month)] if not df.empty and '月份' in df.columns else []
            count = len(monthly_records) + 1
            serial_no = f"CL{year_month}{count:03d}"
            
            new_record = pd.DataFrame([{
                '月份': month, '序号': serial_no, '时间': date.strftime("%Y.%m.%d"),
                '总类别': main_category, '子类别': sub_category, '摘要': summary,
                '人员': people, '金额': amount, '申请人': applicant, '备注': remarks
            }])
            df = pd.concat([df, new_record], ignore_index=True)
            save_data(df)
            st.success(f"✅ 保存成功！云端流水号: {serial_no}")

# --- 功能 2: 台账明细 ---
elif menu == "📋 台账明细":
    st.header("📋 日常台账明细")
    if df.empty:
        st.info("云端暂无数据。")
    else:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出财务月报 (CSV)", data=csv, file_name="禹来云端台账.csv", mime="text/csv")

# --- 功能 3: 月度汇总 ---
elif menu == "📈 月度汇总":
    st.header("📈 财务数据汇总")
    if df.empty:
        st.info("暂无数据。")
    else:
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
        summary = df.groupby(['总类别', '子类别'])['金额'].sum().reset_index()
        st.dataframe(summary, use_container_width=True)
        st.bar_chart(summary, x='子类别', y='金额', color='总类别')
