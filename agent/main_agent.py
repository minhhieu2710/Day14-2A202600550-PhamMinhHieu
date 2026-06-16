import asyncio
from typing import List, Dict

class MainAgent:
    """
    Đây là Agent mẫu sử dụng kiến trúc RAG đơn giản.
    Sinh viên nên thay thế phần này bằng Agent thực tế đã phát triển ở các buổi trước.
    """
    def __init__(self, version: str = "v1"):
        self.version = version
        self.name = f"SupportAgent-{version}"

    async def query(self, question: str) -> Dict:
        """
        Mô phỏng quy trình RAG:
        1. Retrieval: Tìm kiếm context liên quan.
        2. Generation: Gọi LLM để sinh câu trả lời.
        """
        # Giả lập V2 nhanh hơn V1
        latency = 0.5 if self.version == "v1" else 0.3
        await asyncio.sleep(latency) 

        # TODO: Thay thế phần này bằng logic RAG thực tế của bạn.

        # Giả lập nội dung câu trả lời tốt hơn cho V2
        answer_prefix = "[V1 Baseline]" if self.version == "v1" else "[V2 Optimized]"
        answer = f"{answer_prefix} Dựa trên tài liệu hệ thống, tôi xin trả lời câu hỏi '{question}'..."
        
        # Giả lập Retrieval ID (V2 có thể retrieve chính xác hơn)
        retrieved_ids = ["doc_id_1"] if self.version == "v1" else ["doc_ai_eval_intro_1", "doc_quote_1"]

        return {
            "answer": answer,
            "contexts": [
                "Đoạn văn bản trích dẫn 1 dùng để trả lời...", # Nội dung từ các tài liệu retrieve được
                "Đoạn văn bản trích dẫn 2 dùng để trả lời..."
            ],
            "metadata": {
                "model": "gpt-4o-mini",
                "tokens_used": 150,
                "sources": ["policy_handbook.pdf"],
                "retrieved_ids": retrieved_ids # Rất quan trọng cho Retrieval Evaluation
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    async def test():
        resp = await agent.query("Làm thế nào để đổi mật khẩu?")
        print(resp)
    asyncio.run(test())
