import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# 設定頁面標題和版面
st.set_page_config(page_title="教測中心圖書查詢系統", layout="wide")

# 自訂 CSS 樣式以提升美觀度
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f0f2f6, #cfd8e3);
    }
    .title {
        font-size: 2.5em;
        color: #2c3e50;
        font-weight: bold;
        text-align: center;
    }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 利用 st.columns 將 LOGO 與標題並排
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://github.com/Shang0320/ETTC-BOOKS/blob/5fc5be38bc2139df7395a027679bd45248ba4b8f/ettclogo.png", width=120)
with col2:
    st.markdown('<div class="title">海巡署教育訓練測考中心圖書查詢系統</div>', unsafe_allow_html=True)

# 定義函數從 Google Sheets 讀取資料
@st.cache_data(ttl=600)  # 快取 10 分鐘
def load_data():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
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
    st.header("搜尋功能")
    search_method = st.radio("選擇搜尋方式:", ["論文名稱", "研究生", "指導教授"])
    search_input = st.text_input(f"輸入 {search_method} 關鍵字:")
    
    if search_input:
        filtered_df = df[df[search_method].str.contains(search_input, case=False, na=False)]
        st.write(f"搜尋結果: {len(filtered_df)} 筆")
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.warning("沒有符合的搜尋結果")

    # 進階篩選 - 預設展開
    with st.expander("進階篩選", expanded=True):
        df_filtered = df.copy()
        col1, col2 = st.columns(2)
        with col1:
            if "校院名稱" in df.columns:
                selected_schools = st.multiselect("選擇校院名稱:", sorted(df["校院名稱"].dropna().unique().tolist()))
                if selected_schools:
                    df_filtered = df_filtered[df_filtered["校院名稱"].isin(selected_schools)]
            if "系所名稱" in df.columns:
                selected_departments = st.multiselect("選擇系所名稱:", sorted(df["系所名稱"].dropna().unique().tolist()))
                if selected_departments:
                    df_filtered = df_filtered[df_filtered["系所名稱"].isin(selected_departments)]
        with col2:
            if "學位類別" in df.columns:
                selected_degrees = st.multiselect("選擇學位類別:", sorted(df["學位類別"].dropna().unique().tolist()))
                if selected_degrees:
                    df_filtered = df_filtered[df_filtered["學位類別"].isin(selected_degrees)]
            if "論文出版年" in df.columns:
                year_range = st.slider("論文出版年範圍:", int(df["論文出版年"].min()), int(df["論文出版年"].max()),
                                      (int(df["論文出版年"].min()), int(df["論文出版年"].max())))
                df_filtered = df_filtered[(df_filtered["論文出版年"] >= year_range[0]) &
                                          (df_filtered["論文出版年"] <= year_range[1])]
        st.write(f"進階篩選後，共有 {len(df_filtered)} 筆論文")
        st.dataframe(df_filtered)
    
    # 統計圖表
    if st.checkbox("顯示資料概覽"):
        st.subheader("資料統計")
        if "系所名稱" in df.columns:
            st.bar_chart(df["系所名稱"].value_counts())
        if "論文出版年" in df.columns:
            st.line_chart(df["論文出版年"].value_counts().sort_index())
