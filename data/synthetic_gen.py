import json
import asyncio
import os
from typing import List, Dict, Any

# Giả lập thư viện OpenAI/Anthropic client
class MockLLMClient:
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        # Giả lập phản hồi từ LLM
        # Trong thực tế, bạn sẽ gọi API của OpenAI/Anthropic ở đây
        print("MockLLMClient: Generating QA pairs...")
        await asyncio.sleep(0.1) # Giả lập độ trễ
        return {
            "choices": [{
                "message": {
                    "content": json.dumps([
                        {
                            "question": "AI Evaluation là gì?",
                            "expected_answer": "AI Evaluation là quy trình đo lường chất lượng của các mô hình AI.",
                            "context": "AI Evaluation là một quy trình kỹ thuật nhằm đo lường chất lượng của các mô hình AI, đảm bảo chúng hoạt động hiệu quả và đáng tin cậy.",
                            "expected_retrieval_ids": ["doc_ai_eval_intro_1"], # ID của tài liệu gốc chứa thông tin này
                            "metadata": {"difficulty": "easy", "type": "fact-check"}
                        },
                        {
                            "question": "Làm thế nào để cải thiện AI nếu không đo lường được nó?",
                            "expected_answer": "Theo nguyên tắc chung, nếu không thể đo lường một thứ, bạn không thể cải thiện nó. Do đó, việc đánh giá là cần thiết để xác định điểm mạnh và điểm yếu của AI.",
                            "context": "Nếu bạn không thể đo lường nó, bạn không thể cải thiện nó.",
                            "expected_retrieval_ids": ["doc_quote_1"], # ID của tài liệu gốc chứa thông tin này
                            "metadata": {"difficulty": "medium", "type": "inference"}
                        }
                    ], ensure_ascii=False)
                }
            }]
        }

# Giả lập việc gọi LLM để tạo dữ liệu (Students will implement this)
async def generate_qa_from_text(text: str, num_pairs: int = 5, llm_client: Any = None) -> List[Dict]:
    """
    Sử dụng OpenAI/Anthropic API để tạo các cặp (Question, Expected Answer, Context, Expected Retrieval IDs)
    từ đoạn văn bản cho trước.
    Yêu cầu: Tạo ít nhất 1 câu hỏi 'lừa' (adversarial) hoặc cực khó.
    """
    if llm_client is None:
        llm_client = MockLLMClient() # Sử dụng mock client nếu không có client thực

    # Trong thực tế, bạn sẽ gửi `text` đến LLM và yêu cầu nó tạo ra `num_pairs` QA.
    # Bạn cần hướng dẫn LLM tạo ra `expected_retrieval_ids` dựa trên các đoạn văn bản nguồn.
    # Đây là một ví dụ đơn giản, bạn cần mở rộng prompt để LLM hiểu rõ yêu cầu.
    messages = [
        {"role": "system", "content": "Bạn là một chuyên gia tạo câu hỏi và câu trả lời từ văn bản. Hãy tạo các cặp (câu hỏi, câu trả lời kỳ vọng, ngữ cảnh, ID tài liệu gốc) từ văn bản sau. Đảm bảo mỗi câu hỏi có ít nhất một ID tài liệu gốc liên quan. Tạo ít nhất 1 câu hỏi khó hoặc adversarial."},
        {"role": "user", "content": f"Văn bản: {text}\n\nĐịnh dạng đầu ra JSON: [{{\"question\": \"...\", \"expected_answer\": \"...\", \"context\": \"...\", \"expected_retrieval_ids\": [\"doc_id_1\", ...], \"metadata\": {{}} }}]"}
    ]
    
    try:
        response = await llm_client.chat_completion(
            messages=messages,
            model="gpt-4o-mini", # Hoặc model bạn đang sử dụng
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        content = response["choices"][0]["message"]["content"]
        qa_pairs = json.loads(content)
        # Đảm bảo có ít nhất 50 cases như yêu cầu trong README
        if len(qa_pairs) < num_pairs:
            print(f"Cảnh báo: LLM chỉ tạo ra {len(qa_pairs)} cặp QA, cần ít nhất {num_pairs}.")
        return qa_pairs
    except Exception as e:
        print(f"Lỗi khi gọi LLM để tạo QA: {e}")
        # Trả về dữ liệu mẫu nếu có lỗi
        return [
            {
                "question": "Câu hỏi mẫu từ tài liệu?",
                "expected_answer": "Câu trả lời kỳ vọng mẫu.",
                "context": text[:200],
                "expected_retrieval_ids": ["mock_doc_id_1"],
                "metadata": {"difficulty": "easy", "type": "fact-check"}
            } for _ in range(num_pairs) # Tạo đủ số lượng mẫu
        ]

async def main():
    raw_text = "AI Evaluation là một quy trình kỹ thuật nhằm đo lường chất lượng..."
    # Để tạo 50+ cases, bạn có thể cần một đoạn văn bản dài hơn hoặc gọi hàm này nhiều lần
    # hoặc điều chỉnh `num_pairs` và prompt cho LLM.
    
    all_qa_pairs = []
    # Giả lập việc lặp lại để tạo đủ 50 cases
    for i in range(25):
        pairs = await generate_qa_from_text(f"{raw_text} - Part {i}", num_pairs=2)
        all_qa_pairs.extend(pairs)

    # Xử lý đường dẫn linh hoạt: nếu đang ở trong folder 'data' thì không cần thêm 'data/' vào path
    current_dir = os.path.basename(os.getcwd())
    file_path = "golden_set.jsonl" if current_dir == "data" else "data/golden_set.jsonl"
    
    # Đảm bảo thư mục tồn tại nếu chạy từ root
    if "/" in file_path:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        for pair in all_qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print(f"Done! Generated {len(all_qa_pairs)} cases and saved to {file_path}")

if __name__ == "__main__":
    asyncio.run(main())
