import os

# ==== 目錄相關 ====
# -- 根目錄 --
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# -- log相關 --
LOG_DIR = os.path.join(SRC_DIR, "logs")
# -- 測案相關 --
TESTCASES_DIR = os.path.join(SRC_DIR, "testcases")
# -- 配置相關 --
CONFIGS_DIR = os.path.join(SRC_DIR, "configs")
ENV_FILE = os.path.join(CONFIGS_DIR, ".env")

# ==== 目錄設定 ====
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(TESTCASES_DIR, exist_ok=True)
os.makedirs(CONFIGS_DIR, exist_ok=True)

if __name__ == "__main__":
    pass