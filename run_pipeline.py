import subprocess
import sys
from datetime import datetime


def run_script(script_path, description):
    """Chạy một bước trong pipeline và dừng nếu bước đó xảy ra lỗi."""

    print("\n" + "=" * 60)
    print(f"ĐANG CHẠY: {description}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_path],
        check=False
    )

    if result.returncode != 0:
        print(f"\nLỖI: {description}")
        print("Pipeline đã dừng.")
        sys.exit(result.returncode)

    print(f"\nHOÀN THÀNH: {description}")


def main():
    start_time = datetime.now()

    print("=" * 60)
    print("AUTOMATED STOCK ANALYTICS PIPELINE")
    print(f"Bắt đầu: {start_time:%d/%m/%Y %H:%M:%S}")
    print("=" * 60)

    steps = [
        ("src/data_pipeline.py", "Cập nhật và làm sạch dữ liệu"),
        ("src/indicators.py", "Tính chỉ báo kỹ thuật"),
        ("src/screener.py", "Chạy bộ lọc cổ phiếu"),
        ("src/export_web_data.py", "Tạo dữ liệu cho Web Dashboard"),
    ]

    for script_path, description in steps:
        run_script(script_path, description)

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 60)
    print("PIPELINE HOÀN THÀNH")
    print(f"Kết thúc: {end_time:%d/%m/%Y %H:%M:%S}")
    print(f"Thời gian chạy: {duration}")
    print("=" * 60)


if __name__ == "__main__":
    main()