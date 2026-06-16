from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Tính toán xem ít nhất 1 trong expected_ids có nằm trong top_k của retrieved_ids không.
        Nếu có, trả về 1.0, ngược lại 0.0.
        """
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Tính Mean Reciprocal Rank (MRR).
        Tìm vị trí đầu tiên của một expected_id trong retrieved_ids.
        MRR = 1 / position (vị trí 1-indexed). Nếu không thấy thì là 0.
        """
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def evaluate_batch(self, dataset: List[Dict], agent_results: List[Dict]) -> Dict:
        """
        Chạy eval cho toàn bộ bộ dữ liệu.
        Dataset cần có trường 'expected_retrieval_ids'.
        Agent results cần có trường 'retrieved_ids' (từ metadata của agent).
        """
        total_hit_rate = 0.0
        total_mrr = 0.0
        num_cases = len(dataset)

        if num_cases == 0:
            return {"avg_hit_rate": 0.0, "avg_mrr": 0.0}

        for i in range(num_cases):
            case = dataset[i]
            agent_res = agent_results[i]

            expected_ids = case.get("expected_retrieval_ids", [])
            # Giả định agent_res["metadata"]["retrieved_ids"] chứa các ID tài liệu mà agent đã retrieve
            retrieved_ids = agent_res.get("metadata", {}).get("retrieved_ids", [])

            total_hit_rate += self.calculate_hit_rate(expected_ids, retrieved_ids)
            total_mrr += self.calculate_mrr(expected_ids, retrieved_ids)

        avg_hit_rate = total_hit_rate / num_cases
        avg_mrr = total_mrr / num_cases

        return {"avg_hit_rate": avg_hit_rate, "avg_mrr": avg_mrr}
