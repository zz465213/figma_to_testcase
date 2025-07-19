import google.generativeai as genai
import json


class AIGenerator:
    def __init__(self, api_key, rag_service=None):
        self.model = genai.GenerativeModel('gemma-3-27b-it')
        self.setting_ai(api_key)
        self.rag_service = rag_service

    @staticmethod
    def setting_ai(api_key):
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            print(f"錯誤：設定 Google AI 時發生問題: {e}")

    @staticmethod
    def _create_rag_query(processed_data: dict) -> str:
        """根據 Figma 資料建立 RAG 服務的查詢字串。"""
        print("正在建立 RAG 查詢...")
        return f"基於以下Figma資訊，生成相關測試案例: {json.dumps(processed_data, indent=2)}"

    @staticmethod
    def _create_llm_prompt(processed_data: dict, retrieved_docs: list[str]) -> str:
        """組合所有資訊，建立最終給 LLM 的完整 Prompt。"""
        print("正在建立最終的 LLM Prompt...")
        knowledge_base_prompt = ""
        if retrieved_docs:
            knowledge_base_prompt = "\n\n**參考知識庫:**\n"
            for doc in retrieved_docs:
                knowledge_base_prompt += f"- {doc}\n"

        prompt = f"""
        你是一位資深的軟體測試工程師。
        你的任務是根據我提供的 Figma 設計稿的結構化資訊，並參考可能的知識庫，撰寫一份專業的整合性測試案例。

        **Figma 設計稿結構化資訊:**
        ```json
        {json.dumps(processed_data, indent=2)}
        ```
        {knowledge_base_prompt}

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
        立即開始分析並生成10筆左右功能性測試的測試案例，中文回答。
        """
        return prompt

    def generate_test_cases(self, processed_data: dict) -> list | None:
        """
        使用 Google AI 分析處理過的 Figma 資料並生成測試案例。
        協調 RAG 查詢、Prompt 生成和 AI 呼叫的流程。
        """
        print("正在準備 AI 生成流程...")

        # 1. (如果可用) 透過 RAG 服務獲取相關知識
        retrieved_docs = []
        if self.rag_service:
            query_text = self._create_rag_query(processed_data)
            retrieved_docs = self.rag_service.query(query_text)

        # 2. 建立最終的 Prompt
        prompt = self._create_llm_prompt(processed_data, retrieved_docs)

        # 3. 呼叫 AI 模型並處理回應
        print("正在呼叫 Google AI 模型...")
        try:
            response = self.model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            test_cases = json.loads(cleaned_response)
            print(f"成功從 AI 模型獲取並解析了 {len(test_cases)} 個測試案例。")
            return test_cases
        except Exception as e:
            print(f"錯誤：呼叫 AI 模型或解析其回應時發生問題: {e}")
            # 試圖從回應中獲取更多資訊
            if 'response' in locals() and hasattr(response, 'text'):
                print("--- AI 模型原始回應 ---")
                print(response.text)
                print("--------------------")
            return None
