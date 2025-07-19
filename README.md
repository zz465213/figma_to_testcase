# Figma to Test Cases SPEC

## 核心目的

此工具的核心目標是利用 AI 自動化分析 Figma 設計稿，並產出結構化的測試案例。主要包含四個關鍵環節：

1.  **輸入 Figma 網址**：使用者提供一個 Figma 設計稿的公開網址作為輸入。
2.  **AI 分析頁面內容**：AI 會解析 Figma 檔案中每個畫面的具體內容，例如有哪些按鈕、表單、文字等元素。
3.  **AI 分析頁面關聯**：AI 會進一步分析不同頁面之間的流程關係與互動連結，例如點擊某個按鈕會跳轉到哪個頁面。
4.  **產出整合性測試案例**：基於對頁面內容和流程的理解，AI 會自動生成一份完整的整合測試案例。

## 安裝

1.  **複製專案**

    ```bash
    git clone https://github.com/your_username/figma_to_cases.git
    cd figma_to_cases
    ```

2.  **安裝依賴套件**

    建議在虛擬環境中安裝套件：

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## 設定

1.  **取得 API Keys**

    *   **Figma Personal Access Token**: 
        1.  登入您的 Figma 帳號。
        2.  前往 "Settings" > "Personal access tokens"。
        3.  點擊 "Create a new personal access token" 並給予權限。
        4.  複製您取得的 token。

    *   **Google AI API Key**:
        1.  前往 [Google AI Studio](https://aistudio.google.com/)。
        2.  點擊 "Get API key" > "Create API key in new project"。
        3.  複製您取得的 API key。

2.  **設定環境變數**

    專案根目錄下將 API keys 填入 `.env` 當中：

    ```
    FIGMA_API_KEY="YOUR_FIGMA_API_KEY"
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```

## 使用方式

透過 CLI (命令列介面) 來執行此工具，主要參數為 Figma 的檔案網址。

```bash
python src/main.py "<YOUR_FIGMA_FILE_URL>"
```

**範例:**

```bash
python src/main.py "https://www.figma.com/file/your_file_id/your_file_name"
```

執行成功後，工具會在專案根目錄下產出一個以 Figma 檔案名稱命名的 Excel 檔案 (`.xlsx`)，其中包含了所有生成出的測試案例。

## Excel 測試案例格式

輸出的 Excel 檔案包含以下欄位：

*   **Test Case ID**: 每個測試案例的唯一識別碼。
*   **Test Suite**: 測試案例所屬的主要功能模組或類別。
*   **Test Section**: 在主要功能模組下的次要分類。
*   **Priority**: 此測試案例的重要性，例如：P1, P2, P3。
*   **Test Categery**: 測試的種類，例如：功能測試、回歸測試、可用性測試等。
*   **Precondition**: 執行此測試前必須滿足的條件。
*   **Test Step**: 具體描述執行測試時需要操作的每一個步驟。
*   **Expect Result**: 執行完測試步驟後，預期應該看到的正確結果。
