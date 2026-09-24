# ============================================================
# TASK 1 - AUTOMATED DATA PIPELINE
# Automated Stock Analytics Platform
# ============================================================

import os
import zipfile
import pandas as pd


# ============================================================
# 1. THIẾT LẬP ĐƯỜNG DẪN
# ============================================================

# Lấy đường dẫn thư mục gốc của project
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Thư mục dữ liệu gốc
RAW_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw"
)

# Thư mục dữ liệu đã xử lý
PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

# Tự động tạo thư mục nếu chưa tồn tại
os.makedirs(
    RAW_DIR,
    exist_ok=True
)

os.makedirs(
    PROCESSED_DIR,
    exist_ok=True
)


# ============================================================
# 2. GIẢI NÉN FILE ZIP
# ============================================================

def extract_zip_files():

    print("\n=== BƯỚC 1: GIẢI NÉN DỮ LIỆU ===")

    # Tìm tất cả file ZIP
    zip_files = [
        file_name
        for file_name in os.listdir(RAW_DIR)
        if file_name.lower().endswith(".zip")
    ]

    # Nếu không có file ZIP
    if not zip_files:
        print("Không tìm thấy file ZIP trong data/raw.")
        return

    # Giải nén từng file
    for file_name in zip_files:

        zip_path = os.path.join(
            RAW_DIR,
            file_name
        )

        print("Tìm thấy:", file_name)

        try:

            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as zip_ref:

                zip_ref.extractall(
                    RAW_DIR
                )

            print(
                "Giải nén thành công:",
                file_name
            )

        except zipfile.BadZipFile:

            print(
                "File ZIP không hợp lệ:",
                file_name
            )


# ============================================================
# 3. CLEAN & VALIDATE DATA
# ============================================================

def clean_data(df, exchange):

    """
    Chuẩn hóa và kiểm tra chất lượng
    dữ liệu chứng khoán CafeF.
    """

    # --------------------------------------------------------
    # 3.1. Đổi tên cột
    # --------------------------------------------------------

    df = df.rename(
        columns={
            "<Ticker>": "Ticker",
            "<DTYYYYMMDD>": "Date",
            "<Open>": "Open",
            "<High>": "High",
            "<Low>": "Low",
            "<Close>": "Close",
            "<Volume>": "Volume"
        }
    )

    # Thêm tên sàn
    df["Exchange"] = exchange

    # Danh sách cột cần sử dụng
    required_columns = [
        "Ticker",
        "Exchange",
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    # Chỉ giữ các cột cần thiết
    df = df[required_columns].copy()

    # Ghi nhận số dòng ban đầu
    rows_before = len(df)


    # --------------------------------------------------------
    # 3.2. Chuẩn hóa mã cổ phiếu
    # --------------------------------------------------------

    df["Ticker"] = (
        df["Ticker"]
        .astype("string")
        .str.strip()
        .str.upper()
    )


    # --------------------------------------------------------
    # 3.3. Chuẩn hóa ngày giao dịch
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"].astype("string"),
        format="%Y%m%d",
        errors="coerce"
    )


    # --------------------------------------------------------
    # 3.4. Chuyển dữ liệu giá và Volume sang numeric
    # --------------------------------------------------------

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    # --------------------------------------------------------
    # 3.5. Kiểm tra Missing Values
    # --------------------------------------------------------

    missing_before = (
        df[
            [
                "Ticker",
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]
        ]
        .isna()
        .sum()
        .sum()
    )

    # Loại các dòng thiếu trường dữ liệu bắt buộc
    df = df.dropna(
        subset=[
            "Ticker",
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    )


    # --------------------------------------------------------
    # 3.6. Kiểm tra Duplicate
    # --------------------------------------------------------

    duplicates = df.duplicated(
        subset=[
            "Ticker",
            "Exchange",
            "Date"
        ]
    ).sum()

    # Loại dữ liệu trùng
    df = df.drop_duplicates(
        subset=[
            "Ticker",
            "Exchange",
            "Date"
        ],
        keep="last"
    )


    # --------------------------------------------------------
    # 3.7. Kiểm tra dữ liệu OHLC và Volume
    # --------------------------------------------------------

    zero_open = (
        df["Open"] <= 0
    ).sum()

    zero_high = (
        df["High"] <= 0
    ).sum()

    zero_low = (
        df["Low"] <= 0
    ).sum()

    zero_close = (
        df["Close"] <= 0
    ).sum()

    negative_volume = (
        df["Volume"] < 0
    ).sum()


    # High phải lớn hơn hoặc bằng
    # Open, Low và Close
    invalid_high_mask = (
        (df["High"] < df["Open"])
        |
        (df["High"] < df["Close"])
        |
        (df["High"] < df["Low"])
    )

    invalid_high = (
        invalid_high_mask.sum()
    )


    # Low phải nhỏ hơn hoặc bằng
    # Open, High và Close
    invalid_low_mask = (
        (df["Low"] > df["Open"])
        |
        (df["Low"] > df["Close"])
        |
        (df["Low"] > df["High"])
    )

    invalid_low = (
        invalid_low_mask.sum()
    )


    # --------------------------------------------------------
    # 3.8. In mẫu dữ liệu High không hợp lệ
    # --------------------------------------------------------

    invalid_high_rows = df[
        invalid_high_mask
    ]

    print(
        "\n5 dòng High không hợp lệ đầu tiên:"
    )

    if len(invalid_high_rows) > 0:

        print(
            invalid_high_rows[
                [
                    "Ticker",
                    "Date",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ]
            ]
            .head()
            .to_string(index=False)
        )

    else:

        print(
            "Không phát hiện High không hợp lệ."
        )


    # --------------------------------------------------------
    # 3.9. In báo cáo kiểm tra dữ liệu
    # --------------------------------------------------------

    print(
        "\n--- KIỂM TRA DỮ LIỆU KHÔNG HỢP LỆ ---"
    )

    print(
        "Open <= 0:",
        zero_open
    )

    print(
        "High <= 0:",
        zero_high
    )

    print(
        "Low <= 0:",
        zero_low
    )

    print(
        "Close <= 0:",
        zero_close
    )

    print(
        "Volume < 0:",
        negative_volume
    )

    print(
        "High không hợp lệ:",
        invalid_high
    )

    print(
        "Low không hợp lệ:",
        invalid_low
    )


    # --------------------------------------------------------
    # QUAN TRỌNG
    # --------------------------------------------------------
    # Hiện tại CHƯA xóa các dòng OHLC bất thường.
    #
    # Lý do:
    # Số lượng dòng bị đánh dấu High không hợp lệ
    # đang rất lớn.
    #
    # Cần kiểm tra dữ liệu thực tế trước khi quyết định
    # quy tắc xử lý để tránh mất dữ liệu lịch sử.
    # --------------------------------------------------------


    # --------------------------------------------------------
    # 3.10. Sắp xếp dữ liệu
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "Ticker",
            "Date"
        ]
    ).reset_index(
        drop=True
    )

    rows_after = len(df)


    # --------------------------------------------------------
    # 3.11. Báo cáo kết quả Clean & Validate
    # --------------------------------------------------------

    print(
        "\n--- KẾT QUẢ CLEAN & VALIDATE ---"
    )

    print(
        "Missing values phát hiện:",
        missing_before
    )

    print(
        "Duplicate phát hiện:",
        duplicates
    )

    print(
        "Số dòng trước làm sạch:",
        rows_before
    )

    print(
        "Số dòng sau xử lý Missing/Duplicate:",
        rows_after
    )

    print(
        "Số dòng đã loại:",
        rows_before - rows_after
    )

    return df


# ============================================================
# 4. ĐỌC DỮ LIỆU CAFEF
# ============================================================

def read_cafef_files():

    print(
        "\n=== BƯỚC 2: ĐỌC DỮ LIỆU CAFEF ==="
    )

    # Danh sách chứa dữ liệu 3 sàn
    all_data = []

    # Tìm file CSV
    csv_files = [
        file_name
        for file_name in os.listdir(RAW_DIR)
        if file_name.lower().endswith(".csv")
    ]

    if not csv_files:

        print(
            "Không tìm thấy file CSV."
        )

        return None


    # --------------------------------------------------------
    # Đọc từng file CSV
    # --------------------------------------------------------

    for file_name in csv_files:

        file_path = os.path.join(
            RAW_DIR,
            file_name
        )

        upper_name = (
            file_name.upper()
        )


        # ----------------------------------------------------
        # Nhận diện sàn giao dịch
        # ----------------------------------------------------

        if ".HSX." in upper_name:

            exchange = "HOSE"

        elif ".HNX." in upper_name:

            exchange = "HNX"

        elif ".UPCOM." in upper_name:

            exchange = "UPCOM"

        else:

            print(
                "Không xác định được sàn:",
                file_name
            )

            continue


        print(
            "\n=================================================="
        )

        print(
            "Đang đọc:",
            file_name
        )

        print(
            "Sàn:",
            exchange
        )


        # ----------------------------------------------------
        # Đọc CSV
        # ----------------------------------------------------

        try:

            df = pd.read_csv(
                file_path
            )

            print(
                "Số dòng ban đầu:",
                len(df)
            )


            # Clean & Validate
            df = clean_data(
                df,
                exchange
            )


            print(
                "\nTên cột sau chuẩn hóa:"
            )

            print(
                df.columns.tolist()
            )


            print(
                "\n5 dòng đầu sau xử lý:"
            )

            print(
                df.head().to_string(
                    index=False
                )
            )


            # Thêm vào danh sách
            all_data.append(
                df
            )


        except Exception as e:

            print(
                "Lỗi khi đọc:",
                file_name
            )

            print(
                "Chi tiết:",
                e
            )


    # --------------------------------------------------------
    # Kiểm tra dữ liệu
    # --------------------------------------------------------

    if not all_data:

        return None


    # --------------------------------------------------------
    # Gộp dữ liệu 3 sàn
    # --------------------------------------------------------

    combined_df = pd.concat(
        all_data,
        ignore_index=True
    )


    print(
        "\n=================================================="
    )

    print(
        "=== GỘP DỮ LIỆU 3 SÀN ==="
    )

    print(
        "Tổng số dòng:",
        len(combined_df)
    )

    print(
        "Tổng số cột:",
        len(combined_df.columns)
    )


    return combined_df


# ============================================================
# 5. CHƯƠNG TRÌNH CHÍNH
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "AUTOMATED STOCK ANALYTICS PLATFORM"
    )

    print(
        "=" * 60
    )


    print(
        "\nRaw directory:"
    )

    print(
        RAW_DIR
    )


    print(
        "\nProcessed directory:"
    )

    print(
        PROCESSED_DIR
    )


    # --------------------------------------------------------
    # Bước 1: Giải nén dữ liệu
    # --------------------------------------------------------

    extract_zip_files()


    # --------------------------------------------------------
    # Bước 2: Đọc + Clean + Validate + Gộp
    # --------------------------------------------------------

    df = read_cafef_files()


    if df is None:

        print(
            "\nKhông có dữ liệu để xử lý."
        )

        return
    # --------------------------------------------------------
    # Bước 3: Lưu dữ liệu đã xử lý
    # --------------------------------------------------------

    output_file = os.path.join(
        PROCESSED_DIR,
        "stock_data_clean.csv"
    )

    print(
        "\n=== BƯỚC 3: LƯU DỮ LIỆU ĐÃ XỬ LÝ ==="
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        "Đã lưu dữ liệu tại:"
    )

    print(
        output_file
    )

    print(
        "Số dòng đã lưu:",
        len(df)
    )

    # --------------------------------------------------------
    # Kết quả
    # --------------------------------------------------------

    print(
        "\n=================================================="
    )

    print(
        "=== KẾT QUẢ PIPELINE ==="
    )

    print(
        "Kích thước dataset:",
        df.shape
    )


    print(
        "\nCác cột:"
    )

    print(
        df.columns.tolist()
    )


    print(
        "\n5 dòng dữ liệu đầu:"
    )

    print(
        df.head().to_string(
            index=False
        )
    )


    print(
        "\nPipeline chạy thành công!"
    )


# ============================================================
# 6. KHỞI CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":

    main()