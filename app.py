import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# 設定頁面標題和版面
st.set_page_config(page_title="海事論文查詢系統", layout="wide")
st.title("海事論文查詢系統")

# 定義函數從 Google Sheets 讀取資料
@st.cache_data(ttl=600)  # 快取 10 分鐘
def load_data():
    try:
        # 定義需要的權限範圍
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        # 從 st.secrets 中讀取憑證資訊（請在 secrets.toml 中設定 gcp_service_account）
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )
        # 認證並建立 gspread 客戶端
        client = gspread.authorize(credentials)
        
        # 直接硬編碼 Google Sheets URL（請根據您的試算表調整 URL）
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1us_b4A3kGt6Vx8ZEstvDvReUEb-2Yd-7tAS7NBj5LVU/edit?usp=sharing"
        # 打開工作表（假設數據存放在 "sheet1" 工作表中）
        sheet = client.open_by_url(spreadsheet_url).worksheet("sheet1")
        
        # 讀取資料到 DataFrame
        df = get_as_dataframe(sheet, evaluate_formulas=True, skiprows=0)
        df = df.dropna(how='all')
        
        # 將數值欄位轉換為數值類型（如畢業年度、論文出版年）
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

# 檢查是否成功獲取資料
if df.empty:
    st.error("無法獲取資料，請檢查連接和權限設定。")
else:
    st.success(f"已成功讀取 {len(df)} 筆資料")
    
    st.header("搜尋功能")
    
    # 提供單一查詢方式：論文名稱、研究生、指導教授
    search_method = st.radio("選擇搜尋方式:", ["論文名稱", "研究生", "指導教授"])
    
    if search_method == "論文名稱":
        search_input = st.text_input("輸入論文名稱關鍵字:")
        if search_input:
            filtered_df = df[df["論文名稱"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
    elif search_method == "研究生":
        search_input = st.text_input("輸入研究生姓名關鍵字:")
        if search_input:
            filtered_df = df[df["研究生"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
    else:  # 指導教授
        search_input = st.text_input("輸入指導教授姓名關鍵字:")
        if search_input:
            filtered_df = df[df["指導教授"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
    
    # 進階篩選功能（例如校院名稱、系所名稱、學位類別、論文出版年）
    with st.expander("進階篩選"):
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
        st.dataframe(df_filtered)
    
    # 顯示其他資訊（例如統計圖表）
    if st.checkbox("顯示資料概覽"):
        st.subheader("資料統計")
        if "系所名稱" in df.columns:
            dept_counts = df["系所名稱"].value_counts()
            st.bar_chart(dept_counts)
        if "論文出版年" in df.columns:
            year_counts = df["論文出版年"].value_counts().sort_index()
            st.line_chart(year_counts)
