# ==========================================
# ⬛ 霓虹悬浮 CSS 引擎 (彻底修复登录框细边框)
# ==========================================
def inject_neon_ui():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }}
        .stApp {{ background-color: {BG_DARK} !important; }} 
        [data-testid="stSidebar"] {{ background-color: #0A0A0A !important; border-right: 1px solid {BORDER_COLOR} !important; }}
        header {{ visibility: hidden !important; }} 
        [data-testid="block-container"] {{ padding-top: 3rem !important; max-width: 1200px !important; margin: 0 auto !important; }}

        /* 1. 25px圆角卡片与交互动效 */
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
            transform: scale(1.1);
            border-color: {BRAND_COLOR};
            color: {BRAND_COLOR};
            box-shadow: 0 0 15px rgba(167, 240, 105, 0.2);
        }}

        /* ============================================================== */
        /* 💥 3. 组件底座归一化 (精准重构：确保外边框 100% 显示)          */
        /* ============================================================== */
        
        /* 针对最外层的 Wrapper 强制施加物理边框和背景 */
        div[data-baseweb="input"], div[data-baseweb="select"] {{
            background-color: rgba(0,0,0,0.2) !important;
            border: 1px solid {BORDER_COLOR} !important; /* 💥 边框复活点 */
            border-radius: 12px !important; 
            height: 48px !important;            
            min-height: 48px !important;
            box-sizing: border-box !important;
            transition: all 0.3s ease !important;
            display: flex !important; align-items: center !important; overflow: hidden !important; margin-bottom: 8px !important;
        }}

        /* 剥去第二层自带的透明壳，防止双层阴影 */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ 
            border: none !important; 
            background-color: transparent !important; 
            box-shadow: none !important; 
            border-radius: 0 !important; 
        }}

        /* 剥去最内层输入区域的背景，让文字直接浮在 Wrapper 的背景上 */
        div[data-baseweb="input"] input {{ 
            background-color: transparent !important; 
            border: none !important; 
            color: #FFFFFF !important; 
            font-size: 14px !important; 
            text-align: center !important; 
            height: 100% !important; 
            padding: 0 16px !important; 
        }}
        
        /* 文本域(事由摘要)修复 */
        .stTextArea textarea {{ 
            background-color: rgba(0,0,0,0.2) !important; 
            border: 1px solid {BORDER_COLOR} !important; 
            border-radius: 12px !important;
            color: #FFFFFF !important; font-size: 14px !important; height: 140px !important; line-height: 1.6 !important; padding: 16px !important; 
            transition: all 0.3s ease !important;
        }}
        [data-testid="stTextArea"] {{ margin-bottom: 2px !important; }}

        /* 数字控件修复 */
        [data-testid="stNumberInput"] div[data-baseweb="input"] {{ padding: 0 !important; }}
        [data-testid="stNumberInput"] input {{ height: 48px !important; line-height: 48px !important; padding: 0 12px !important; }}
        [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{ background-color: transparent !important; color: rgba(255,255,255,0.4) !important; height: 48px !important; width: 36px !important; border: none !important; }}
        
        /* 下拉框文字居中 */
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {{ font-size: 14px !important; margin: 0 !important; color: #FFFFFF !important; font-weight: 500 !important; text-align: center !important; width: 100% !important; }}
        div[data-baseweb="select"] span[data-baseweb="icon"] {{ color: rgba(255,255,255,0.4) !important; margin-right: 12px !important; }}
        
        /* 聚焦态点亮 */
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within, .stTextArea textarea:focus {{
            border-color: {BRAND_COLOR} !important; 
            box-shadow: 0 0 0 1px {BRAND_COLOR} !important;
        }}
        
        /* 下拉面板 */
        div[data-baseweb="menu"] {{ background-color: #1E1E20 !important; border: 1px solid #333336 !important; border-radius: 4px !important; padding: 4px !important; margin-top: 4px !important;}}
        div[data-baseweb="menu"] div {{ font-size: 14px !important; color: #A0A0A5 !important; padding: 8px 12px !important; text-align: center !important; }}

        /* 标签对齐与透灰色 */
        .stMarkdown label, p, .stWidgetLabel {{ font-size: 13px !important; font-weight: 500 !important; color: rgba(255,255,255,0.45) !important; margin-bottom: 8px !important; }}

        /* 4. 按钮引擎：暗色底 + 荧光色边框反差 */
        .stButton>button {{
            background-color: rgba(255,255,255,0.03) !important; 
            color: rgba(255,255,255,0.8) !important;            
            border: 1px solid {BORDER_COLOR} !important;    
            border-radius: 12px !important;                 
            height: 54px !important; font-weight: 500 !important; font-size: 15px !important;
            display: flex !important; justify-content: center !important; align-items: center !important; width: 100% !important;
            transition: all 0.4s ease !important; margin-top: 12px !important;
        }}
        .stButton>button span {{ display: block !important; text-align: center !important; width: 100% !important; }}
        .stButton>button[kind="primary"] {{ border-color: {BRAND_COLOR} !important; color: {BRAND_COLOR} !important; }}
        .stButton>button[kind="primary"]:hover {{ background-color: {BRAND_COLOR} !important; color: #000000 !important; box-shadow: 0 0 20px rgba(167, 240, 105, 0.4) !important; }}

        /* 表格与选项卡 */
        [data-testid="stDataFrame"] {{ border: none !important; background-color: transparent !important; }}
        th {{ border-bottom: 1px solid {BORDER_COLOR} !important; background-color: rgba(255,255,255,0.02) !important; font-weight: 500 !important; color:rgba(255,255,255,0.5) !important;}}
        td {{ border-bottom: 1px solid rgba(255,255,255,0.04) !important; border-right: none !important; color: #EBEBEB !important; font-size: 14px !important;}}
        
        .stTabs [data-baseweb="tab-list"] {{ border-bottom: 1px solid {BORDER_COLOR} !important; gap: 32px; padding-bottom: 8px !important; margin-bottom: 40px !important; background-color: transparent !important;}}
        .stTabs [data-baseweb="tab"] {{ border: none !important; color: rgba(255,255,255,0.4) !important; font-size: 16px !important; font-weight: 500 !important; background-color: transparent !important;}}
        .stTabs [aria-selected="true"] {{ color: {BRAND_COLOR} !important; border-bottom: 2px solid {BRAND_COLOR} !important; }}
        </style>
    """, unsafe_allow_html=True)
