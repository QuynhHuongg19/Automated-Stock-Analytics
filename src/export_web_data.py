import os
import pandas as pd


# ============================================================
# TẠO DATASET NHẸ DÙNG CHO STREAMLIT PUBLIC
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

SCREENER_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_screener.csv"
)

OUTPUT_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_data_web.csv"
)


def main():

    print("=" * 60)
    print("EXPORT WEB DATA")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Đọc Screener để lấy các mã hiện hành
    # --------------------------------------------------------

    print("\n=== BƯỚC 1: ĐỌC SCREENER ===")

    screener = pd.read_csv(
        SCREENER_FILE
    )

    active_tickers = (
        screener["Ticker"]
        .dropna()
        .astype(str)
        .unique()
    )

    print(
        "Số mã hiện hành:",
        len(active_tickers)
    )

    # --------------------------------------------------------
    # 2. Đọc dữ liệu Indicators
    # --------------------------------------------------------

    print("\n=== BƯỚC 2: ĐỌC DỮ LIỆU INDICATORS ===")

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["Date"]
    )

    print(
        "Số dòng ban đầu:",
        len(df)
    )

    # --------------------------------------------------------
    # 3. Chỉ giữ mã hiện hành
    # --------------------------------------------------------

    df = df[
        df["Ticker"].isin(active_tickers)
    ].copy()

    print(
        "Sau khi lọc mã hiện hành:",
        len(df)
    )

    # --------------------------------------------------------
    # 4. Chỉ giữ khoảng 1 năm dữ liệu gần nhất
    # --------------------------------------------------------

    latest_date = df["Date"].max()

    start_date = (
        latest_date
        - pd.DateOffset(years=1)
    )

    df = df[
        df["Date"] >= start_date
    ].copy()

    print(
        "Ngày bắt đầu:",
        start_date.date()
    )

    print(
        "Ngày kết thúc:",
        latest_date.date()
    )

    print(
        "Số dòng dữ liệu Web:",
        len(df)
    )

    # --------------------------------------------------------
    # 5. Sắp xếp
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "Exchange",
            "Ticker",
            "Date"
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # 6. Lưu file
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    file_size_mb = (
        os.path.getsize(OUTPUT_FILE)
        / 1024
        / 1024
    )

    print("\n=== HOÀN THÀNH ===")

    print(
        "Đã tạo:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        f"Dung lượng: {file_size_mb:.2f} MB"
    )


if __name__ == "__main__":

    main()
    