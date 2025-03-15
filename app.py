import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# 設定頁面
st.set_page_config(page_title="海事論文查詢系統", layout="wide")
st.title("海事論文查詢系統")

# 創建一個函數來讀取 Google Sheets 資料
@st.cache_data(ttl=600)  # 快取資料 10 分鐘，確保不會頻繁請求
def load_data():
    try:
        # 定義需要的權限範圍
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 讀取憑證資訊
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],  # 從 Streamlit 的 secrets 管理中獲取
            scopes=scope
        )
        
        # 認證並建立客戶端
        client = gspread.authorize(credentials)
        
        # 打開工作表 - 使用工作表 URL 或名稱
        spreadsheet_url = st.secrets["spreadsheet_url"]  # 從 Streamlit 的 secrets 管理中獲取
        sheet = client.open_by_url(spreadsheet_url).worksheet("Sheet1")  # 假設你的數據在 "Sheet1" 工作表
        
        # 讀取資料為 DataFrame
        df = get_as_dataframe(sheet, evaluate_formulas=True, skiprows=0)
        
        # 清理資料 - 移除空白列
        df = df.dropna(how='all')
        
        # 確保數值列為正確的數值類型
        if '畢業年度' in df.columns:
            df['畢業年度'] = pd.to_numeric(df['畢業年度'], errors='coerce')
        if '論文出版年' in df.columns:
            df['論文出版年'] = pd.to_numeric(df['論文出版年'], errors='coerce')
            
        return df
    
    except Exception as e:
        st.error(f"讀取數據時發生錯誤: {e}")
        return pd.DataFrame()  # 返回空的 DataFrame

# 顯示加載中提示
with st.spinner("正在從 Google Drive 讀取資料..."):
    df = load_data()

# 檢查是否成功獲取了資料
if df.empty:
    st.error("無法獲取資料，請檢查連接和權限設定。")
else:
    # 顯示總資料筆數
    st.success(f"已成功讀取 {len(df)} 筆資料")
    
    # 創建搜尋功能
    st.header("搜尋功能")
    
    # 創建三個搜尋選項
    search_method = st.radio("選擇搜尋方式:", ["論文名稱", "研究生", "指導教授"])
    
    # 根據選擇的搜尋方式顯示相應的搜尋框
    if search_method == "論文名稱":
        # 取得所有論文名稱
        titles = df["論文名稱"].dropna().unique().tolist()
        titles.sort()  # 按字母順序排序
        
        # 創建關鍵字搜尋框
        search_input = st.text_input("輸入論文名稱關鍵字:")
        if search_input:
            filtered_df = df[df["論文名稱"].str.contains(search_input, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
        
        # 提供論文名稱的下拉選單
        selected_title = st.selectbox("或選擇論文名稱:", [""] + titles)
        if selected_title:
            filtered_df = df[df["論文名稱"] == selected_title]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            st.dataframe(filtered_df)
    
    elif search_method == "研究生":
        # 取得所有研究生
        students = df["研究生"].dropna().unique().tolist()
        students.sort()  # 按字母順序排序
        
        # 創建關鍵字搜尋框
        search_input = st.text_input("輸入研究生姓名關鍵字:")
        if search_input:
            filtered_df = df[df["研究生"].str.contains(search_input, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
        
        # 提供研究生的下拉選單
        selected_student = st.selectbox("或選擇研究生:", [""] + students)
        if selected_student:
            filtered_df = df[df["研究生"] == selected_student]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            st.dataframe(filtered_df)
    
    else:  # 指導教授
        # 取得所有指導教授
        professors = df["指導教授"].dropna().unique().tolist()
        professors.sort()  # 按字母順序排序
        
        # 創建關鍵字搜尋框
        search_input = st.text_input("輸入指導教授姓名關鍵字:")
        if search_input:
            filtered_df = df[df["指導教授"].str.contains(search_input, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
        
        # 提供指導教授的下拉選單
        selected_professor = st.selectbox("或選擇指導教授:", [""] + professors)
        if selected_professor:
            filtered_df = df[df["指導教授"] == selected_professor]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            st.dataframe(filtered_df)
    
    # 添加進階篩選功能
    with st.expander("進階篩選"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 篩選學校
            if "校院名稱" in df.columns:
                schools = df["校院名稱"].dropna().unique().tolist()
                schools.sort()
                selected_school = st.multiselect("選擇學校:", schools)
                if selected_school:
                    df = df[df["校院名稱"].isin(selected_school)]
            
            # 篩選系所
            if "系所名稱" in df.columns:
                departments = df["系所名稱"].dropna().unique().tolist()
                departments.sort()
                selected_department = st.multiselect("選擇系所:", departments)
                if selected_department:
                    df = df[df["系所名稱"].isin(selected_department)]
        
        with col2:
            # 篩選學位類別
            if "學位類別" in df.columns:
                degrees = df["學位類別"].dropna().unique().tolist()
                selected_degree = st.multiselect("選擇學位類別:", degrees)
                if selected_degree:
                    df = df[df["學位類別"].isin(selected_degree)]
            
            # 篩選年份範圍
            if "論文出版年" in df.columns:
                min_year = int(df["論文出版年"].min()) if not df.empty else 2000
                max_year = int(df["論文出版年"].max()) if not df.empty else 2025
                year_range = st.slider("論文出版年範圍:", min_year, max_year, (min_year, max_year))
                df = df[(df["論文出版年"] >= year_range[0]) & (df["論文出版年"] <= year_range[1])]
        
        # 顯示經過篩選的結果
        st.write(f"符合條件的論文數量: {len(df)} 筆")
        
    # 顯示資料概覽
    if st.checkbox("顯示資料概覽"):
        st.subheader("資料統計")
        
        # 繪製圖表
        st.subheader("各系所論文數量分布")
        if "系所名稱" in df.columns:
            dept_counts = df["系所名稱"].value_counts()
            st.bar_chart(dept_counts)
        
        st.subheader("論文出版年份分布")
        if "論文出版年" in df.columns:
            year_counts = df["論文出版年"].value_counts().sort_index()
            st.line_chart(year_counts)