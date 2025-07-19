import requests
import re


class FigmaClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.figma.com/v1"

    def get_figma_file(self, figma_url):
        """
        使用 Figma API 獲取檔案內容。
        """
        match = re.search(r"figma\.com/(?:design|proto)/([^/]+)", figma_url)
        if not match:
            print("錯誤：無效的 Figma URL 格式。")
            return None
        file_id = match.group(1)

        api_url = f"{self.base_url}/files/{file_id}"
        headers = {"X-Figma-Token": self.api_key}

        try:
            print("正在向 Figma API 發送請求...")
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            print("成功從 Figma API 獲取資料。")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"錯誤：呼叫 Figma API 時發生問題: {e}")
            return None
