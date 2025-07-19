import argparse
import os.path
import re
from configs.common_paths import *
from dotenv import load_dotenv
from services.figma_client import FigmaClient
from services.figma_parser import FigmaParser
from services.ai_generator import AIGenerator
from services.excel_writer import ExcelWriter


def main():
    load_dotenv(ENV_FILE)
    figma_api_key = os.getenv("FIGMA_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not figma_api_key or figma_api_key == "YOUR_FIGMA_API_KEY":
        print("錯誤：請在 .env 檔案中設定您的 FIGMA_API_KEY。")
        return
    if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
        print("錯誤：請在 .env 檔案中設定您的 GOOGLE_API_KEY。")
        return

    parser = argparse.ArgumentParser(
        description="一個透過 AI 分析 Figma 設計稿並自動生成測試案例的工具。",
        epilog=f"使用範例: python src/main.py \"https://www.figma.com/file/your_file_id/your_file_name\""
    )
    parser.add_argument("figma_url", type=str, help="您想要分析的 Figma 檔案的完整 URL。")
    args = parser.parse_args()
    print(f"成功接收到 Figma URL: {args.figma_url}")

    figma_client = FigmaClient(figma_api_key)
    figma_file = figma_client.get_figma_file(args.figma_url)
    if not figma_file:
        return
    print(f"成功獲取 Figma 檔案：{figma_file.get('name')}")

    figma_parser = FigmaParser(figma_file)
    processed_data = figma_parser.process_figma_data()
    if not processed_data:
        return

    ai_generator = AIGenerator(google_api_key)
    test_cases = ai_generator.generate_test_cases(processed_data)

    if test_cases:
        file_name = re.sub(r'[\\/:*?"<>|]', '_', figma_file.get('name', 'figma_test_cases'))
        output_filename = f"{file_name}_test_cases.xlsx"
        excel_writer = ExcelWriter(test_cases)
        excel_writer.save_to_excel(os.path.join(TESTCASES_DIR, output_filename))


if __name__ == "__main__":
    main()
