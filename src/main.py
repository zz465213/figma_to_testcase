import argparse
import os
import re
import requests
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()


def get_figma_file(figma_url, api_key):
    """
    使用 Figma API 獲取檔案內容。
    """
    # match = re.search(r"figma\.com/design/([^/]+)", figma_url)
    match = re.search(r"figma\.com/proto/([^/]+)", figma_url)
    # match = re.search(r"figma\.com/design/([^/]+)", figma_url)
    if not match:
        print("錯誤：無效的 Figma URL 格式。")
        return None
    file_id = match.group(1)

    api_url = f"https://api.figma.com/v1/files/{file_id}"
    headers = {"X-Figma-Token": api_key}

    try:
        print("正在向 Figma API 發送請求...")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        print("成功從 Figma API 獲取資料。")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"錯誤：呼叫 Figma API 時發生問題: {e}")
        return None


def process_figma_data(figma_file):
    """
    遞迴解析 Figma 資料，提取頁面、框架和互動元件的簡化資訊。
    """
    print("正在處理 Figma 資料...")
    simplified_data = {
        "fileName": figma_file.get("name"),
        "pages": []
    }

    def extract_node_info(node):
        """遞迴提取節點資訊"""
        info = {
            "id": node.get("id"),
            "name": node.get("name"),
            "type": node.get("type"),
            "children": []
        }
        relevant_types = ['CANVAS', 'FRAME', 'COMPONENT', 'INSTANCE', 'TEXT', 'RECTANGLE']
        if node.get("type") not in relevant_types:
            return None

        if "children" in node:
            for child in node["children"]:
                child_info = extract_node_info(child)
                if child_info:
                    info["children"].append(child_info)

        if not info["children"]:
            del info["children"]

        return info

    for page in figma_file["document"]["children"]:
        if page["type"] == "CANVAS":
            page_info = extract_node_info(page)
            if page_info:
                simplified_data["pages"].append(page_info)

    print("Figma 資料處理完成。")
    return simplified_data


def generate_test_cases_with_ai(processed_data, api_key):
    """
    使用 Google AI 分析處理過的 Figma 資料並生成測試案例。
    """
    print("正在設定 Google AI...")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"錯誤：設定 Google AI 時發生問題: {e}")
        return None

    print("正在生成 AI Prompt...")
    prompt = f"""
    你是一位資深的軟體測試工程師。
    你的任務是根據我提供的 Figma 設計稿的結構化資訊，撰寫一份專業的整合性測試案例。

    **Figma 設計稿結構化資訊:**
    ```json
    {json.dumps(processed_data, indent=2)}
    ```

    **你的任務與要求:**
    1.  **理解設計**: 請先仔細分析以上 JSON 內容，理解各個頁面 (CANVAS/FRAME) 的功能以及其中包含的元件 (COMPONENT, INSTANCE, TEXT)。
    2.  **推斷流程**: 根據頁面和元件的名稱，推斷使用者可能的操作流程。例如，一個名為 "Login Page" 的頁面上有 "Username"、"Password" 輸入框和 "Login" 按鈕，這顯然是一個登入流程。
    3.  **撰寫測試案例**: 根據你的分析，生成一份完整的測試案例列表。
    4.  **輸出格式**: 你必須嚴格按照以下 JSON 格式輸出你的結果，不要有任何額外的文字或解釋。輸出必須是一個 JSON 陣列，其中每個物件代表一個測試案例。

    **JSON 輸出格式範例:**
    ```json
    [
      {{
        "Test Case ID": "TC-001",
        "Test Suite": "使用者登入",
        "Test Section": "成功登入",
        "Priority": "P1",
        "Test Categery": "功能性測試",
        "Precondition": "使用者已進入登入頁面，並擁有有效的帳號密碼。",
        "Test Step": "1. 在 'Username' 輸入框中輸入有效的使用者名稱.\n2. 在 'Password' 輸入框中輸入對應的密碼.\n3. 點擊 'Login' 按鈕。",
        "Expect Result": "系統驗證成功，頁面跳轉至使用者主頁。"
      }}
    ]
    ```
    請立即開始分析並生成10筆左右功能性測試的測試案例，中文回答。
    """

    print("正在呼叫 Google AI 模型...")
    model = genai.GenerativeModel('gemma-3-27b-it')
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        test_cases = json.loads(cleaned_response)
        print(f"成功從 AI 模型獲取並解析了 {len(test_cases)} 個測試案例。")
        return test_cases
    except Exception as e:
        print(f"錯誤：呼叫 AI 模型或解析其回應時發生問題: {e}")
        # 嘗試從 Gemini 的回應中提取可能存在的 JSON 內容
        try:
            print("--- AI 模型原始回應 ---")
            print(response.text)
            print("--------------------")
        except Exception:
            pass  # 如果 response.text 也不存在，就忽略
        return None


def save_to_excel(test_cases, filename="output_test_cases.xlsx"):
    """
    將測試案例儲存到 Excel 檔案中。
    """
    print(f"正在將測試案例儲存至 {filename}...")
    try:
        df = pd.DataFrame(test_cases)
        column_order = [
            "Test Case ID", "Test Suite", "Test Section", "Priority",
            "Test Categery", "Precondition", "Test Step", "Expect Result"
        ]
        # 重新排列欄位，並確保所有指定的欄位都存在
        df = df.reindex(columns=column_order)

        df.to_excel(filename, index=False, engine='openpyxl')

        # 提供完整絕對路徑
        absolute_path = os.path.abspath(filename)
        print(f"✅ 成功！測試案例已儲存至: {absolute_path}")
        return True
    except Exception as e:
        print(f"錯誤：儲存 Excel 檔案時發生問題: {e}")
        return False


def main():
    # API_KEY 撈取
    figma_api_key = os.getenv("FIGMA_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not figma_api_key or figma_api_key == "YOUR_FIGMA_API_KEY":
        print("錯誤：請在 .env 檔案中設定您的 FIGMA_API_KEY。")
        return
    if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
        print("錯誤：請在 .env 檔案中設定您的 GOOGLE_API_KEY。")
        return

    # cmd 接收參數
    parser = argparse.ArgumentParser(
        description="一個透過 AI 分析 Figma 設計稿並自動生成測試案例的工具。",
        epilog=f"使用範例: python src/main.py \"https://www.figma.com/file/your_file_id/your_file_name\""
    )
    parser.add_argument("figma_url", type=str, help="您想要分析的 Figma 檔案的完整 URL。")
    args = parser.parse_args()
    print(f"成功接收到 Figma URL: {args.figma_url}")

    figma_file = get_figma_file(args.figma_url, figma_api_key)
    if not figma_file:
        return
    print(f"成功獲取 Figma 檔案：{figma_file.get('name')}")

    processed_data = process_figma_data(figma_file)
    if not processed_data:
        return

    test_cases = generate_test_cases_with_ai(processed_data, google_api_key)

    if test_cases:
        # 使用 Figma 檔案的名稱來命名輸出的 Excel 檔
        file_name = re.sub(r'[\\/:*?"<>|]', '_', figma_file.get('name', 'figma_test_cases'))
        output_filename = f"{file_name}_test_cases.xlsx"

        save_to_excel(test_cases, output_filename)


if __name__ == "__main__":
    main()
