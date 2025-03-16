import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# 設定頁面標題和版面，採用深色主題
st.set_page_config(page_title="教測中心圖書查詢系統", layout="wide")

# 自定義 CSS，呈現高對比度、華麗的介面，以及置中 banner
st.markdown("""
    <style>
    /* 整體背景與文字 */
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    
    /* Banner 樣式 */
    .banner-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #1E3A8A 0%, #0D253F 100%);
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        border: 1px solid #3B82F6;
    }
    
    .banner-title {
        color: #FFEB3B;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .banner-subtitle {
        color: #E0E0E0;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* 按鈕樣式 */
    .stButton>button {
        background: linear-gradient(135deg, #FF5722 0%, #E64A19 100%);
        color: #FFFFFF;
        border: none;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #E64A19 0%, #BF360C 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.4);
    }
    
    /* 標題樣式 */
    h1, h2, h3 {
        color: #FFEB3B;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* 資料表樣式 */
    .css-1oe6wy3 {
        background-color: #1E1E1E !important;
    }
    
    .stDataFrame {
        border: 1px solid #3B82F6;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    table {
        background-color: #1E1E1E;
        border: 1px solid #424242;
    }
    
    th {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: #000000;
        font-weight: bold;
        padding: 12px 8px !important;
    }
    
    td {
        border: 1px solid #424242;
        padding: 10px 8px !important;
    }
    
    tr:nth-child(even) {
        background-color: #2C2C2C;
    }
    
    tr:hover {
        background-color: #424242;
    }
    
    /* 搜尋區塊樣式 */
    .search-container {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3B82F6;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border: 1px solid #424242;
        border-radius: 8px;
        padding: 10px 15px;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
    }
    
    /* 展開區樣式 */
    .stExpander {
        border: 1px solid #3B82F6;
        border-radius: 10px;
        background-color: #1E1E1E;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 成功提示訊息 */
    .stSuccess {
        background-color: #1B5E20;
        color: #FFFFFF;
        padding: 16px;
        border-radius: 8px;
        border-left: 8px solid #4CAF50;
    }
    
    /* 警告提示訊息 */
    .stWarning {
        background-color: #E65100;
        color: #FFFFFF;
        padding: 16px;
        border-radius: 8px;
        border-left: 8px solid #FF9800;
    }
    </style>
    """, unsafe_allow_html=True)

# 置中 Banner 設計
st.markdown("""
    <div class="banner-container">
        <img src="https://th.bing.com/th/id/OIP.9jKbLb2tJQxAcb_7avTrdAHaHa?rs=1" width="150">
        <h1 class="banner-title">海巡署教育訓練測考中心圖書查詢系統</h1>
        <p class="banner-subtitle">Coast Guard Academy Training & Testing Center Library Search System</p>
    </div>
""", unsafe_allow_html=True)

# 定義函數從 Google Sheets 讀取資料
@st.cache_data(ttl=600)  # 快取 10 分鐘
def load_data():
    try:
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )
        client = gspread.authorize(credentials)
        # 直接硬編碼 Google Sheets URL
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1R6OM-Mp9KES7FOKOgxlSseK9tfgPbBt3_moINKF8DAQ/edit?usp=sharing"
        sheet = client.open_by_url(spreadsheet_url).worksheet("Sheet1")
        df = get_as_dataframe(sheet, evaluate_formulas=True, skiprows=0)
        df = df.dropna(how='all')
        if '畢業年度' in df.columns:
            df['畢業年度'] = pd.to_numeric(df['畢業年度'], errors='coerce')
        if '論文出版年' in df.columns:
            df['論文出版年'] = pd.to_numeric(df['論文出版年'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"讀取數據時發生錯誤: {e}")
        return pd.DataFrame()

# 載入資料
with st.spinner("正在從 Google Drive 讀取資料..."):
    df = load_data()

if df.empty:
    st.error("無法獲取資料，請檢查連接和權限設定。")
else:
    st.success(f"已成功讀取 {len(df)} 筆資料")
    
    # 使用容器美化搜尋區塊
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.subheader("📚 論文搜尋")
    
    # 單一查詢方式
    search_method = st.radio("選擇搜尋方式:", ["論文名稱", "研究生", "指導教授"], horizontal=True)
    
    if search_method == "論文名稱":
        search_input = st.text_input("📝 輸入論文名稱關鍵字:")
        if search_input:
            filtered_df = df[df["論文名稱"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df, height=400)
            else:
                st.warning("沒有符合的搜尋結果")
    elif search_method == "研究生":
        search_input = st.text_input("👨‍🎓 輸入研究生姓名關鍵字:")
        if search_input:
            filtered_df = df[df["研究生"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df, height=400)
            else:
                st.warning("沒有符合的搜尋結果")
    else:  # 指導教授
        search_input = st.text_input("👨‍🏫 輸入指導教授姓名關鍵字:")
        if search_input:
            filtered_df = df[df["指導教授"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df, height=400)
            else:
                st.warning("沒有符合的搜尋結果")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 進階篩選，預設展開
    with st.expander("🔍 進階篩選", expanded=True):
        df_filtered = df.copy()
        col1, col2 = st.columns(2)
        with col1:
            if "校院名稱" in df.columns:
                schools = sorted(df["校院名稱"].dropna().unique().tolist())
                selected_schools = st.multiselect("選擇校院名稱:", schools)
                if selected_schools:
                    df_filtered = df_filtered[df_filtered["校院名稱"].isin(selected_schools)]
            if "系所名稱" in df.columns:
                departments = sorted(df["系所名稱"].dropna().unique().tolist())
                selected_departments = st.multiselect("選擇系所名稱:", departments)
                if selected_departments:
                    df_filtered = df_filtered[df_filtered["系所名稱"].isin(selected_departments)]
        with col2:
            if "學位類別" in df.columns:
                degrees = sorted(df["學位類別"].dropna().unique().tolist())
                selected_degrees = st.multiselect("選擇學位類別:", degrees)
                if selected_degrees:
                    df_filtered = df_filtered[df_filtered["學位類別"].isin(selected_degrees)]
            if "論文出版年" in df.columns:
                min_year = int(df["論文出版年"].min())
                max_year = int(df["論文出版年"].max())
                year_range = st.slider("論文出版年範圍:", min_year, max_year, (min_year, max_year))
                df_filtered = df_filtered[(df_filtered["論文出版年"] >= year_range[0]) & (df_filtered["論文出版年"] <= year_range[1])]
        
        st.write(f"進階篩選後，共有 {len(df_filtered)} 筆論文")
        st.dataframe(df_filtered, height=400)
    
    # 資料概覽與統計圖表
    if st.checkbox("📊 顯示資料概覽"):
        st.subheader("資料統計")
        
        # 以兩欄方式並排顯示統計資料
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if "系所名稱" in df.columns:
                st.subheader("各系所論文數量分布")
                dept_counts = df["系所名稱"].value_counts().head(10)  # 取前10筆以免太雜亂
                st.bar_chart(dept_counts)
                
        with chart_col2:
            if "論文出版年" in df.columns:
                st.subheader("歷年論文出版數量趨勢")
                year_counts = df["論文出版年"].value_counts().sort_index()
                st.line_chart(year_counts)
