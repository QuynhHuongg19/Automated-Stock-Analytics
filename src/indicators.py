# ============================================================
# TASK 2 - TECHNICAL INDICATORS
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
    "stock_data_clean.csv"
)

OUTPUT_FILE = os.path.join(
    PROCESSED_DIR,
    "stock_data_indicators.csv"
)


# ============================================================
# 2. HÀM TÍNH RSI
# ============================================================

def calculate_rsi(close, period=14):

    # Mức thay đổi giá đóng cửa
    delta = close.diff()

    # Phần tăng giá
    gain = delta.clip(lower=0)

    # Phần giảm giá
    loss = -delta.clip(upper=0)

    # Trung bình tăng và giảm theo Wilder
    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    # Relative Strength
    rs = avg_gain / avg_loss

    # RSI
    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ============================================================
# 3. HÀM TÍNH CÁC CHỈ BÁO CHO MỘT MÃ
# ============================================================

def calculate_indicators(group):

    # Sắp xếp đúng thứ tự thời gian
    group = group.sort_values(
        "Date"
    ).copy()

    # --------------------------------------------------------
    # MA20
    # --------------------------------------------------------

    group["MA20"] = (
        group["Close"]
        .rolling(window=20)
        .mean()
    )

    # --------------------------------------------------------
    # MA50
    # --------------------------------------------------------

    group["MA50"] = (
        group["Close"]
        .rolling(window=50)
        .mean()
    )

    # --------------------------------------------------------
    # RSI14
    # --------------------------------------------------------

    group["RSI14"] = calculate_rsi(
        group["Close"],
        period=14
    )

    # --------------------------------------------------------
    # MACD
    # EMA12 - EMA26
    # --------------------------------------------------------

    ema12 = (
        group["Close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        group["Close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    group["MACD"] = (
        ema12 - ema26
    )

    # Signal Line = EMA9 của MACD
    group["MACD_Signal"] = (
        group["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    # MACD Histogram
    group["MACD_Hist"] = (
        group["MACD"]
        - group["MACD_Signal"]
    )

    # --------------------------------------------------------
    # Volume MA20
    # --------------------------------------------------------

    group["Volume_MA20"] = (
        group["Volume"]
        .rolling(window=20)
        .mean()
    )

    return group


# ============================================================
# 4. ĐỌC DỮ LIỆU
# ============================================================

def load_data():

    print(
        "\n=== BƯỚC 1: ĐỌC DỮ LIỆU CLEAN ==="
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
# 5. TÍNH CHỈ BÁO CHO TOÀN BỘ CỔ PHIẾU
# ============================================================

def process_indicators(df):

    print(
        "\n=== BƯỚC 2: TÍNH CHỈ BÁO KỸ THUẬT ==="
    )

    # Sắp xếp dữ liệu theo sàn, mã và ngày
    df = df.sort_values(
        by=["Exchange", "Ticker", "Date"]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # MA20
    # --------------------------------------------------------

    df["MA20"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["Close"]
        .transform(
            lambda x: x.rolling(
                window=20
            ).mean()
        )
    )

    # --------------------------------------------------------
    # MA50
    # --------------------------------------------------------

    df["MA50"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["Close"]
        .transform(
            lambda x: x.rolling(
                window=50
            ).mean()
        )
    )

    # --------------------------------------------------------
    # RSI14
    # --------------------------------------------------------

    df["RSI14"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["Close"]
        .transform(
            lambda x: calculate_rsi(
                x,
                period=14
            )
        )
    )

    # --------------------------------------------------------
    # EMA12
    # --------------------------------------------------------

    df["EMA12"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["Close"]
        .transform(
            lambda x: x.ewm(
                span=12,
                adjust=False
            ).mean()
        )
    )

    # --------------------------------------------------------
    # EMA26
    # --------------------------------------------------------

    df["EMA26"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["Close"]
        .transform(
            lambda x: x.ewm(
                span=26,
                adjust=False
            ).mean()
        )
    )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    df["MACD"] = (
        df["EMA12"]
        - df["EMA26"]
    )

    # --------------------------------------------------------
    # MACD SIGNAL
    # --------------------------------------------------------

    df["MACD_Signal"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["MACD"]
        .transform(
            lambda x: x.ewm(
                span=9,
                adjust=False
            ).mean()
        )
    )

    # --------------------------------------------------------
    # MACD HISTOGRAM
    # --------------------------------------------------------

    df["MACD_Hist"] = (
        df["MACD"]
        - df["MACD_Signal"]
    )

    # --------------------------------------------------------
    # VOLUME MA20
    # --------------------------------------------------------

    df["Volume_MA20"] = (
        df.groupby(
            ["Exchange", "Ticker"]
        )["Volume"]
        .transform(
            lambda x: x.rolling(
                window=20
            ).mean()
        )
    )

    # Không cần lưu EMA12 và EMA26
    df = df.drop(
        columns=[
            "EMA12",
            "EMA26"
        ]
    )

    print(
        "Tính chỉ báo thành công."
    )

    print(
        "Số dòng sau tính toán:",
        len(df)
    )

    return df

# ============================================================
# 6. LƯU KẾT QUẢ
# ============================================================

def save_data(df):

    print(
        "\n=== BƯỚC 3: LƯU DỮ LIỆU CHỈ BÁO ==="
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
        "Số dòng:",
        len(df)
    )


# ============================================================
# 7. CHƯƠNG TRÌNH CHÍNH
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "TECHNICAL INDICATORS"
    )

    print(
        "=" * 60
    )

    df = load_data()

    if df is None:
        return

    df = process_indicators(
        df
    )

    save_data(
        df
    )

    print(
        "\nCác cột sau khi tính chỉ báo:"
    )

    print(
        df.columns.tolist()
    )

    print(
        "\n5 dòng cuối có dữ liệu chỉ báo:"
    )

    indicator_columns = [
        "Ticker",
        "Exchange",
        "Date",
        "Close",
        "MA20",
        "MA50",
        "RSI14",
        "MACD",
        "MACD_Signal",
        "MACD_Hist",
        "Volume",
        "Volume_MA20"
    ]

    print(
        df[
            indicator_columns
        ]
        .dropna()
        .tail()
        .to_string(index=False)
    )

    print(
        "\nHoàn thành tính chỉ báo kỹ thuật!"
    )


# ============================================================
# 8. KHỞI CHẠY
# ============================================================

if __name__ == "__main__":

    main()