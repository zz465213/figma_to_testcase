import google.generativeai as genai
import json


class AIGenerator:
    def __init__(self, api_key):
        self.model = genai.GenerativeModel('gemma-3-27b-it')
        self.setting_ai(api_key)

    @staticmethod
    def setting_ai(api_key):
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            print(f"錯誤：設定 Google AI 時發生問題: {e}")

    def generate_test_cases(self, processed_data):
        """
        使用 Google AI 分析處理過的 Figma 資料並生成測試案例。
        """
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
        response = self.model.generate_content(prompt)
        try:
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            test_cases = json.loads(cleaned_response)
            print(f"成功從 AI 模型獲取並解析了 {len(test_cases)} 個測試案例。")
            return test_cases
        except Exception as e:
            print(f"錯誤：呼叫 AI 模型或解析其回應時發生問題: {e}")
            print("--- AI 模型原始回應 ---")
            print(response.text)
            print("--------------------")
