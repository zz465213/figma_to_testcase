import pandas as pd
import os


class ExcelWriter:
    def __init__(self, test_cases):
        self.test_cases = test_cases

    def save_to_excel(self, filename="output_test_cases.xlsx"):
        """
        將測試案例儲存到 Excel 檔案中。
        """
        print(f"正在將測試案例儲存至 {filename}...")
        try:
            df = pd.DataFrame(self.test_cases)
            column_order = [
                "Test Case ID", "Test Suite", "Test Section", "Priority",
                "Test Categery", "Precondition", "Test Step", "Expect Result"
            ]
            df = df.reindex(columns=column_order)

            df.to_excel(filename, index=False, engine='openpyxl')

            absolute_path = os.path.abspath(filename)
            print(f"✅ 成功！測試案例已儲存至: {absolute_path}")
            return True
        except Exception as e:
            print(f"錯誤：儲存 Excel 檔案時發生問題: {e}")
            return False
