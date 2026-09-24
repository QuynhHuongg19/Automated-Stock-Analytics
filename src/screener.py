# ============================================================
# TASK 3 - TECHNICAL SCREENER
# Automated Stock Analytics Platform
# ============================================================

import os
import pandas as pd


# ============================================================
# 1. THIẾT LẬP ĐƯỜNG DẪN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

INPUT_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_data_indicators.csv"
)

OUTPUT_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_screener.csv"
)


# ============================================================
# 2. ĐỌC DỮ LIỆU CHỈ BÁO
# ============================================================

def load_data():

    print(
        "\n=== BƯỚC 1: ĐỌC DỮ LIỆU CHỈ BÁO ==="
    )

    if not os.path.exists(INPUT_FILE):

        print(
            "Không tìm thấy file:"
        )

        print(
            INPUT_FILE
        )

        return None

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["Date"]
    )

    print(
        "Đọc dữ liệu thành công."
    )

    print(
        "Số dòng:",
        len(df)
    )

    print(
        "Số mã cổ phiếu:",
        df["Ticker"].nunique()
    )

    return df


# ============================================================
# 3. LẤY PHIÊN MỚI NHẤT CỦA TỪNG MÃ
# ============================================================

def get_latest_data(df):

    print(
        "\n=== BƯỚC 2: LẤY PHIÊN MỚI NHẤT ==="
    )

    # Xác định ngày mới nhất của toàn bộ dữ liệu
    market_latest_date = df["Date"].max()

    print(
        "Ngày dữ liệu mới nhất:",
        market_latest_date.date()
    )

    # Chỉ giữ các mã có dữ liệu trong 30 ngày gần nhất
    cutoff_date = (
        market_latest_date
        - pd.Timedelta(days=30)
    )

    print(
        "Chỉ giữ mã có dữ liệu từ:",
        cutoff_date.date()
    )

    # Sắp xếp theo mã và ngày
    df = df.sort_values(
        by=[
            "Ticker",
            "Date"
        ]
    )

    # Lấy phiên giao dịch mới nhất của từng mã
    latest = (
        df.groupby(
            "Ticker",
            as_index=False
        )
        .tail(1)
        .copy()
    )

    # Loại các mã không còn dữ liệu gần đây
    latest = latest[
        latest["Date"] >= cutoff_date
    ].copy()

    # Loại các mã dài hơn 3 ký tự
    # nhằm loại chứng quyền trong dataset hiện tại
    latest = latest[
        latest["Ticker"].str.len() <= 3
    ].copy()

    latest = latest.reset_index(
        drop=True
    )

    print(
        "Số mã sau khi lọc dữ liệu hiện hành:",
        len(latest)
    )

    return latest


# ============================================================
# 4. TẠO CÁC ĐIỀU KIỆN KỸ THUẬT
# ============================================================

def create_conditions(df):

    print(
        "\n=== BƯỚC 3: KIỂM TRA ĐIỀU KIỆN KỸ THUẬT ==="
    )

    # --------------------------------------------------------
    # Điều kiện 1:
    # Giá đóng cửa nằm trên MA20
    # --------------------------------------------------------

    df["Above_MA20"] = (
        df["Close"] > df["MA20"]
    )

    # --------------------------------------------------------
    # Điều kiện 2:
    # MA20 nằm trên MA50
    # --------------------------------------------------------

    df["MA20_Above_MA50"] = (
        df["MA20"] > df["MA50"]
    )

    # --------------------------------------------------------
    # Điều kiện 3:
    # RSI nằm trong vùng 50 - 70
    # --------------------------------------------------------

    df["RSI_50_70"] = (
        (df["RSI14"] >= 50)
        &
        (df["RSI14"] <= 70)
    )

    # --------------------------------------------------------
    # Điều kiện 4:
    # MACD nằm trên Signal
    # --------------------------------------------------------

    df["MACD_Bullish"] = (
        df["MACD"] > df["MACD_Signal"]
    )

    # --------------------------------------------------------
    # Điều kiện 5:
    # Volume lớn hơn trung bình Volume 20 phiên
    # --------------------------------------------------------

    df["Volume_Above_MA20"] = (
        df["Volume"] > df["Volume_MA20"]
    )

    # --------------------------------------------------------
    # Đếm số điều kiện đạt được
    # --------------------------------------------------------

    condition_columns = [
        "Above_MA20",
        "MA20_Above_MA50",
        "RSI_50_70",
        "MACD_Bullish",
        "Volume_Above_MA20"
    ]

    df["Conditions_Met"] = (
        df[condition_columns]
        .sum(axis=1)
    )

    # --------------------------------------------------------
    # Phân loại kết quả
    #
    # Đây là phân loại kỹ thuật theo quy tắc của hệ thống,
    # không phải khuyến nghị mua/bán.
    # --------------------------------------------------------

    df["Technical_Status"] = "Không đạt"

    df.loc[
        df["Conditions_Met"] >= 3,
        "Technical_Status"
    ] = "Theo dõi"

    df.loc[
        df["Conditions_Met"] >= 4,
        "Technical_Status"
    ] = "Đạt bộ lọc"

    print(
        "Đã kiểm tra các điều kiện kỹ thuật."
    )

    return df


# ============================================================
# 5. TẠO BẢNG SCREENER
# ============================================================

def create_screener(df):

    print(
        "\n=== BƯỚC 4: TẠO BẢNG SCREENER ==="
    )

    screener_columns = [
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
        "Above_MA20",
        "MA20_Above_MA50",
        "RSI_50_70",
        "MACD_Bullish",
        "Volume_Above_MA20",
        "Conditions_Met",
        "Technical_Status"
    ]

    screener = df[
        screener_columns
    ].copy()

    # Sắp xếp theo số điều kiện đạt được
    screener = screener.sort_values(
        by=[
            "Conditions_Met",
            "RSI14"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(
        drop=True
    )

    print(
        "Tạo Screener thành công."
    )

    return screener


# ============================================================
# 6. LƯU KẾT QUẢ
# ============================================================

def save_screener(df):

    print(
        "\n=== BƯỚC 5: LƯU KẾT QUẢ SCREENER ==="
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "Đã lưu tại:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "Số cổ phiếu:",
        len(df)
    )


# ============================================================
# 7. THỐNG KÊ KẾT QUẢ
# ============================================================

def show_summary(df):

    print(
        "\n=== THỐNG KÊ SCREENER ==="
    )

    print(
        df["Technical_Status"]
        .value_counts()
    )

    print(
        "\n10 mã có số điều kiện đạt cao:"
    )

    display_columns = [
        "Ticker",
        "Exchange",
        "Date",
        "Close",
        "RSI14",
        "Conditions_Met",
        "Technical_Status"
    ]

    print(
        df[
            display_columns
        ]
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# 8. CHƯƠNG TRÌNH CHÍNH
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "TECHNICAL STOCK SCREENER"
    )

    print(
        "=" * 60
    )

    # Đọc dữ liệu
    df = load_data()

    if df is None:
        return

    # Lấy phiên mới nhất
    latest = get_latest_data(
        df
    )

    # Tạo điều kiện kỹ thuật
    latest = create_conditions(
        latest
    )

    # Tạo bảng Screener
    screener = create_screener(
        latest
    )

    # Lưu kết quả
    save_screener(
        screener
    )

    # Hiển thị thống kê
    show_summary(
        screener
    )

    print(
        "\nHoàn thành Technical Screener!"
    )


# ============================================================
# 9. KHỞI CHẠY
# ============================================================

if __name__ == "__main__":

    main()