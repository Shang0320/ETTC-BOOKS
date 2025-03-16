import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# 設定頁面標題和版面
st.set_page_config(page_title="教測中心圖書查詢系統", layout="wide")

# 自訂 CSS 讓 LOGO 和標題形成 BANNER 並置中
st.markdown(
    """
    <style>
    .banner {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #2c3e50;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .banner img {
        height: 80px;
        margin-right: 15px;
    }
    .banner-text {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .banner h1 {
        color: white;
        font-size: 2em;
        margin: 0;
    }
    .banner h4 {
        color: white;
        font-size: 1em;
        margin-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# BANNER 標題與 LOGO
st.markdown(
    """
    <div class="banner">
        <img src="https://raw.githubusercontent.com/Shang0320/ETTC-BOOKS/5fc5be38bc2139df7395a027679bd45248ba4b8f/ettclogo.png">
        <div class="banner-text">
            <h1>海巡署教育訓練測考中心圖書查詢系統</h1>
            <h4>Coast Guard Administration Education and Training Testing Center Library Query System</h4>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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

# 顯示載入提示
with st.spinner("正在從 Google Drive 讀取資料..."):
    df = load_data()

if df.empty:
    st.error("無法獲取資料，請檢查連接和權限設定。")
else:
    st.success(f"已成功讀取 {len(df)} 筆資料")
