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
    .icon {
        font-size: 20px;
        margin-right: 10px;
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
    
    # 添加可愛的 ICON
    st.markdown("""
    <div style="display: flex; align-items: center;">
        <span class="icon">📖</span>
        <h3>請選擇搜尋條件：</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 搜尋選項
    search_method = st.radio("選擇搜尋方式:", ["📚 論文名稱", "🧑‍🎓 研究生", "👨‍🏫 指導教授"])
    
    search_input = ""
    if search_method == "📚 論文名稱":
        search_input = st.text_input("輸入論文名稱關鍵字 📖:")
    elif search_method == "🧑‍🎓 研究生":
        search_input = st.text_input("輸入研究生姓名關鍵字 🧑‍🎓:")
    else:
        search_input = st.text_input("輸入指導教授姓名關鍵字 👨‍🏫:")
    
    if search_input:
        column_name = search_method.split()[1]  # 取得對應的欄位名稱
        filtered_df = df[df[column_name].str.contains(search_input, case=False, na=False)]
        st.write(f"搜尋結果: {len(filtered_df)} 筆")
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.warning("沒有符合的搜尋結果")
    
    # 進階篩選功能
    with st.expander("進階篩選", expanded=True):
        df_filtered = df.copy()
        col1, col2 = st.columns(2)
        with col1:
            if "校院名稱" in df.columns:
                schools = sorted(df["校院名稱"].dropna().unique().tolist())
                selected_schools = st.multiselect("選擇校院名稱:", schools)
                if selected_schools:
                    df_filtered = df_filtered[df_filtered["校院名稱"].isin(selected_schools)]
        with col2:
            if "論文出版年" in df.columns:
                min_year = int(df["論文出版年"].min())
                max_year = int(df["論文出版年"].max())
                year_range = st.slider("論文出版年範圍:", min_year, max_year, (min_year, max_year))
                df_filtered = df_filtered[(df_filtered["論文出版年"] >= year_range[0]) & (df_filtered["論文出版年"] <= year_range[1])]
        st.write(f"進階篩選後，共有 {len(df_filtered)} 筆論文")
        st.dataframe(df_filtered)
    
    # 顯示資料概覽
    if st.checkbox("顯示資料概覽"):
        st.subheader("資料統計")
        if "系所名稱" in df.columns:
            dept_counts = df["系所名稱"].value_counts()
            st.bar_chart(dept_counts)
        if "論文出版年" in df.columns:
            year_counts = df["論文出版年"].value_counts().sort_index()
            st.line_chart(year_counts)
