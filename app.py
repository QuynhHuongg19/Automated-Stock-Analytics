import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


# ============================================================
# 1. CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Automated Stock Analytics",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Automated Stock Analytics Platform")
st.caption(
    "Phân tích và sàng lọc cổ phiếu dựa trên các chỉ báo kỹ thuật"
)


# ============================================================
# 2. ĐƯỜNG DẪN DỮ LIỆU
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

INDICATOR_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_data_indicators.csv"
)

SCREENER_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_screener.csv"
)


# ============================================================
# 3. ĐỌC DỮ LIỆU
# ============================================================

@st.cache_data
def load_stock_data():

    df = pd.read_csv(
        INDICATOR_FILE,
        parse_dates=["Date"]
    )

    return df


@st.cache_data
def load_screener():

    df = pd.read_csv(
        SCREENER_FILE,
        parse_dates=["Date"]
    )

    return df


try:

    stock_data = load_stock_data()
    screener = load_screener()

except Exception as e:

    st.error(
        f"Không thể đọc dữ liệu: {e}"
    )

    st.stop()


# ============================================================
# 4. SIDEBAR
# ============================================================

st.sidebar.header("Bộ lọc phân tích")


# ------------------------------------------------------------
# Chọn sàn
# ------------------------------------------------------------

exchange_list = sorted(
    stock_data["Exchange"]
    .dropna()
    .unique()
)

selected_exchange = st.sidebar.selectbox(
    "Chọn sàn giao dịch",
    exchange_list
)


# ------------------------------------------------------------
# Chọn mã cổ phiếu
# ------------------------------------------------------------

# Chỉ lấy các mã hiện hành đã có trong Screener
ticker_list = sorted(
    screener.loc[
        screener["Exchange"] == selected_exchange,
        "Ticker"
    ]
    .dropna()
    .unique()
)

selected_ticker = st.sidebar.selectbox(
    "Chọn mã cổ phiếu",
    ticker_list
)


# ------------------------------------------------------------
# Chọn khoảng thời gian
# ------------------------------------------------------------

period = st.sidebar.selectbox(
    "Khoảng thời gian",
    [
        "3 tháng",
        "6 tháng",
        "1 năm",
        "3 năm",
        "Toàn bộ"
    ],
    index=2
)


# ============================================================
# 5. LỌC DỮ LIỆU CỔ PHIẾU
# ============================================================

ticker_data = stock_data[
    (
        stock_data["Exchange"]
        == selected_exchange
    )
    &
    (
        stock_data["Ticker"]
        == selected_ticker
    )
].copy()

ticker_data = ticker_data.sort_values(
    "Date"
)


if ticker_data.empty:

    st.warning(
        "Không có dữ liệu cho mã cổ phiếu này."
    )

    st.stop()


latest_date = ticker_data["Date"].max()


if period == "3 tháng":

    start_date = (
        latest_date
        - pd.DateOffset(months=3)
    )

elif period == "6 tháng":

    start_date = (
        latest_date
        - pd.DateOffset(months=6)
    )

elif period == "1 năm":

    start_date = (
        latest_date
        - pd.DateOffset(years=1)
    )

elif period == "3 năm":

    start_date = (
        latest_date
        - pd.DateOffset(years=3)
    )

else:

    start_date = ticker_data["Date"].min()


chart_data = ticker_data[
    ticker_data["Date"] >= start_date
].copy()


# ============================================================
# 6. THÔNG TIN PHIÊN MỚI NHẤT
# ============================================================

latest = ticker_data.iloc[-1]


st.subheader(
    f"{selected_ticker} - {selected_exchange}"
)

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Giá đóng cửa",
    f"{latest['Close']:,.2f}"
)


col2.metric(
    "RSI14",
    (
        f"{latest['RSI14']:.2f}"
        if pd.notna(latest["RSI14"])
        else "N/A"
    )
)


col3.metric(
    "MA20",
    (
        f"{latest['MA20']:,.2f}"
        if pd.notna(latest["MA20"])
        else "N/A"
    )
)


col4.metric(
    "MA50",
    (
        f"{latest['MA50']:,.2f}"
        if pd.notna(latest["MA50"])
        else "N/A"
    )
)


st.caption(
    f"Phiên dữ liệu mới nhất: "
    f"{latest['Date'].strftime('%d/%m/%Y')}"
)


# ============================================================
# 7. BIỂU ĐỒ GIÁ + MA + VOLUME
# ============================================================

st.subheader(
    "Biểu đồ giá và khối lượng"
)

fig_price = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[
        0.75,
        0.25
    ]
)


# Candlestick
fig_price.add_trace(

    go.Candlestick(
        x=chart_data["Date"],
        open=chart_data["Open"],
        high=chart_data["High"],
        low=chart_data["Low"],
        close=chart_data["Close"],
        name="OHLC"
    ),

    row=1,
    col=1
)


# MA20
fig_price.add_trace(

    go.Scatter(
        x=chart_data["Date"],
        y=chart_data["MA20"],
        name="MA20",
        mode="lines"
    ),

    row=1,
    col=1
)


# MA50
fig_price.add_trace(

    go.Scatter(
        x=chart_data["Date"],
        y=chart_data["MA50"],
        name="MA50",
        mode="lines"
    ),

    row=1,
    col=1
)


# Volume
fig_price.add_trace(

    go.Bar(
        x=chart_data["Date"],
        y=chart_data["Volume"],
        name="Volume"
    ),

    row=2,
    col=1
)


# Volume MA20
fig_price.add_trace(

    go.Scatter(
        x=chart_data["Date"],
        y=chart_data["Volume_MA20"],
        name="Volume MA20",
        mode="lines"
    ),

    row=2,
    col=1
)


fig_price.update_layout(
    height=700,
    xaxis_rangeslider_visible=False,
    hovermode="x unified"
)


fig_price.update_yaxes(
    title_text="Giá",
    row=1,
    col=1
)

fig_price.update_yaxes(
    title_text="Volume",
    row=2,
    col=1
)


st.plotly_chart(
    fig_price,
    width="stretch"
)


# ============================================================
# 8. RSI
# ============================================================

st.subheader(
    "RSI (14)"
)


fig_rsi = go.Figure()


fig_rsi.add_trace(

    go.Scatter(
        x=chart_data["Date"],
        y=chart_data["RSI14"],
        name="RSI14",
        mode="lines"
    )
)


# Mốc RSI 70
fig_rsi.add_hline(
    y=70,
    line_dash="dash",
    annotation_text="70"
)


# Mốc RSI 30
fig_rsi.add_hline(
    y=30,
    line_dash="dash",
    annotation_text="30"
)


fig_rsi.update_layout(
    height=350,
    yaxis_title="RSI",
    hovermode="x unified"
)


fig_rsi.update_yaxes(
    range=[
        0,
        100
    ]
)


st.plotly_chart(
    fig_rsi,
    width="stretch"
)


# ============================================================
# 9. MACD
# ============================================================

st.subheader(
    "MACD"
)


fig_macd = go.Figure()


# MACD
fig_macd.add_trace(

    go.Scatter(
        x=chart_data["Date"],
        y=chart_data["MACD"],
        name="MACD",
        mode="lines"
    )
)


# Signal
fig_macd.add_trace(

    go.Scatter(
        x=chart_data["Date"],
        y=chart_data["MACD_Signal"],
        name="Signal",
        mode="lines"
    )
)


# Histogram
fig_macd.add_trace(

    go.Bar(
        x=chart_data["Date"],
        y=chart_data["MACD_Hist"],
        name="Histogram"
    )
)


fig_macd.update_layout(
    height=400,
    yaxis_title="MACD",
    hovermode="x unified"
)


st.plotly_chart(
    fig_macd,
    width="stretch"
)


# ============================================================
# 10. TECHNICAL SCREENER
# ============================================================

st.divider()

st.header(
    "Technical Screener"
)


# ------------------------------------------------------------
# Bộ lọc Screener
# ------------------------------------------------------------

screener_exchange = st.selectbox(
    "Lọc Screener theo sàn",
    [
        "Tất cả",
        "HOSE",
        "HNX",
        "UPCOM"
    ]
)


minimum_conditions = st.slider(
    "Số điều kiện kỹ thuật tối thiểu",
    min_value=0,
    max_value=5,
    value=4
)


filtered_screener = screener.copy()


if screener_exchange != "Tất cả":

    filtered_screener = filtered_screener[
        filtered_screener["Exchange"]
        == screener_exchange
    ]


filtered_screener = filtered_screener[
    filtered_screener["Conditions_Met"]
    >= minimum_conditions
]


# ------------------------------------------------------------
# Thống kê Screener
# ------------------------------------------------------------

s1, s2, s3 = st.columns(3)


s1.metric(
    "Số mã phù hợp",
    len(filtered_screener)
)


s2.metric(
    "Đạt 5/5 điều kiện",
    (
        filtered_screener[
            filtered_screener["Conditions_Met"]
            == 5
        ].shape[0]
    )
)


s3.metric(
    "Đạt từ 4 điều kiện",
    (
        filtered_screener[
            filtered_screener["Conditions_Met"]
            >= 4
        ].shape[0]
    )
)


# ------------------------------------------------------------
# Hiển thị bảng Screener
# ------------------------------------------------------------

display_columns = [
    "Ticker",
    "Exchange",
    "Date",
    "Close",
    "MA20",
    "MA50",
    "RSI14",
    "MACD",
    "MACD_Signal",
    "Volume",
    "Volume_MA20",
    "Conditions_Met",
    "Technical_Status"
]


st.dataframe(
    filtered_screener[
        display_columns
    ],
    width="stretch",
    hide_index=True
)


# ============================================================
# 11. GIẢI THÍCH ĐIỀU KIỆN
# ============================================================

with st.expander(
    "Xem các điều kiện của Technical Screener"
):

    st.write(
        """
        Hệ thống kiểm tra 5 điều kiện:

        1. Close > MA20
        2. MA20 > MA50
        3. RSI14 nằm trong khoảng 50 - 70
        4. MACD > MACD Signal
        5. Volume > Volume MA20

        Technical Screener được sử dụng để hỗ trợ
        sàng lọc dữ liệu theo các tiêu chí kỹ thuật.
        Kết quả không phải là khuyến nghị đầu tư.
        """
    )