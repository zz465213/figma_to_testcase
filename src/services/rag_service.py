import chromadb
import google.generativeai as genai
from pathlib import Path

# --- 常數設定 ---
KNOWLEDGE_BASE_DIR = "src/rag_knowledge_base"
PERSIST_DIRECTORY = "src/rag_db"
COLLECTION_NAME = "figma_test_cases"
EMBEDDING_MODEL = "models/text-embedding-004"


class RAGService:
    """
    一個封裝了 RAG (Retrieval-Augmented Generation) 相關操作的服務。
    負責建立、載入和查詢向量知識庫。
    """

    def __init__(self, google_api_key: str):
        if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
            raise ValueError("未提供有效的 GOOGLE_API_KEY。")

        genai.configure(api_key=google_api_key)
        print(f"初始化 RAGService. 持久化目錄: {PERSIST_DIRECTORY}")
        self.client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        print(f"ChromaDB Collection '{COLLECTION_NAME}' 初始化完成。目前文件數: {self.collection.count()}")

    def build_or_load_index(self):
        documents, metadatas, ids = [], [], []
        doc_id_counter = 1

        for md_file in Path(KNOWLEDGE_BASE_DIR).rglob('*.md'):
            print(f"讀取 RAG 文件: {md_file}")
            try:
                content = md_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"[ERROR] 讀取 RAG 文件 {md_file} 失敗: {e}")
                continue

            documents.append(content)
            metadatas.append({'source': str(md_file)})
            ids.append(str(doc_id_counter))
            doc_id_counter += 1

        if not documents:
            print(f"[WARNING] 在 {KNOWLEDGE_BASE_DIR} 中未找到任何 .md 檔案。請確認路徑和文件是否存在。")
            return

        print(f"找到 {len(documents)} 個 RAG 文件，正在生成向量 (Embeddings)...")
        try:
            embeddings = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=documents,
                task_type="retrieval_document"
            )["embedding"]
            print(f"向量生成完畢。")
        except Exception as e:
            print(f"[ERROR] 生成 Embedding 失敗: {e}")
            print("請檢查您的 GOOGLE_API_KEY 是否有效，以及網路連線是否正常。")
            return

        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"索引建立完畢！共 {self.collection.count()} 個文件已加入資料庫。")
        except Exception as e:
            print(f"[ERROR] 將資料加入 ChromaDB 失敗: {e}")
            return

    def query(self, query_text: str, n_results: int = 3) -> list[str]:
        try:
            query_embedding = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query_text,
                task_type="retrieval_query"
            )["embedding"]
        except Exception as e:
            print(f"[ERROR] 生成查詢 Embedding 失敗: {e}")
            print("請檢查您的 GOOGLE_API_KEY 是否有效，以及網路連線是否正常。")
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        else:
            print("[DEBUG] 未檢索到任何文件。")
            return []
