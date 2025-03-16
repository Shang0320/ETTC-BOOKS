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
    .title-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
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
    @media (max-width: 600px) {
        .title {
            font-size: 2em;
        }
    }
    @media (max-width: 1024px) and (min-width: 601px) {
        .title {
            font-size: 2.2em;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 絕對置中 LOGO 與標題
st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.image("https://github.com/Shang0320/ETTC-BOOKS/blob/5fc5be38bc2139df7395a027679bd45248ba4b8f/ettclogo.png?raw=true", width=120)
st.markdown('<div class="title">海巡署教育訓練測考中心圖書查詢系統</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 三種瀏覽模式
view_mode = st.radio("選擇瀏覽模式:", ["電腦", "手機", "平板"], horizontal=True)

if view_mode == "手機":
    st.markdown("<style>body { font-size: 14px; }</style>", unsafe_allow_html=True)
elif view_mode == "平板":
    st.markdown("<style>body { font-size: 18px; }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>body { font-size: 20px; }</style>", unsafe_allow_html=True)

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
