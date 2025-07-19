class FigmaParser:
    def __init__(self, figma_file):
        self.figma_file = figma_file

    def process_figma_data(self):
        """
        遞迴解析 Figma 資料，提取頁面、框架和互動元件的簡化資訊。
        """
        print("正在處理 Figma 資料...")
        simplified_data = {
            "fileName": self.figma_file.get("name"),
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

        for page in self.figma_file["document"]["children"]:
            if page["type"] == "CANVAS":
                page_info = extract_node_info(page)
                if page_info:
                    simplified_data["pages"].append(page_info)

        print("Figma 資料處理完成。")
        return simplified_data
