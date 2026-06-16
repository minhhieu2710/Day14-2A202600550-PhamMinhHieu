import asyncio
import json
import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv() # Nạp API Key từ file .env
from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.retrieval_eval import RetrievalEvaluator # Import RetrievalEvaluator
from engine.llm_judge import LLMJudge

# Giả lập các components Expert
class ExpertEvaluator:
    def __init__(self):
        self.retrieval_evaluator = RetrievalEvaluator()
        # TODO: Khởi tạo các evaluator khác như RAGAS (Faithfulness, Relevancy) ở đây

    async def score(self, case: Dict, agent_response: Dict) -> Dict: 
        """
        Đánh giá câu trả lời của agent dựa trên nhiều tiêu chí.
        """
        # 1. Đánh giá Retrieval
        expected_retrieval_ids = case.get("expected_retrieval_ids", [])
        retrieved_ids = agent_response.get("metadata", {}).get("retrieved_ids", [])
        
        hit_rate = self.retrieval_evaluator.calculate_hit_rate(expected_retrieval_ids, retrieved_ids)
        mrr = self.retrieval_evaluator.calculate_mrr(expected_retrieval_ids, retrieved_ids)

        # TODO: Tích hợp RAGAS hoặc các thư viện đánh giá khác
        # Ví dụ:
        # faithfulness_score = await self.ragas_evaluator.evaluate_faithfulness(agent_response["answer"], agent_response["contexts"])
        # relevancy_score = await self.ragas_evaluator.evaluate_relevancy(agent_response["answer"], case["question"])
        
        # Giả lập các điểm số RAGAS cho đến khi bạn tích hợp thực tế
        return {
            "faithfulness": 0.92, # Giả lập điểm Faithfulness
            "relevancy": 0.88,   # Giả lập điểm Relevancy
            "retrieval": {
                "hit_rate": hit_rate,
                "mrr": mrr
            }
        }


async def run_benchmark_with_results(agent_version: str, agent_instance: Any):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    # Khởi tạo các evaluator thực tế
    expert_evaluator = ExpertEvaluator()
    multi_model_judge = LLMJudge() 

    runner = BenchmarkRunner(agent_instance, expert_evaluator, multi_model_judge)
    results = await runner.run_all(dataset)

    total = len(results)
    if total == 0:
        print("Không có kết quả nào được tạo ra.")
        return None, None

    # Tính toán Token và Cost (Expert Feature)
    # Đảm bảo runner.py trả về đúng cấu trúc này trong kết quả từng test
    total_tokens = sum(r.get("metadata", {}).get("tokens_used", 0) for r in results)
    # Giá GPT-4o-mini: ~0.15$ per 1M tokens input
    total_cost = (total_tokens / 1000000) * 0.15 

    # Tính toán Inter-rater Reliability (Cohen's Kappa giả lập)
    gpt_scores = [r["judge"]["individual_scores"]["gpt-4o"] for r in results]
    claude_scores = [r["judge"]["individual_scores"]["claude-3-5"] for r in results]
    kappa = multi_model_judge.calculate_cohens_kappa(gpt_scores, claude_scores)

    summary = {
        "metadata": {"version": agent_version, "total": total, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        "metrics": {
            "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
            "hit_rate": sum(r["expert_eval"]["retrieval"]["hit_rate"] for r in results) / total, # Đổi từ "ragas" sang "expert_eval"
            "agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
            "avg_faithfulness": sum(r["expert_eval"]["faithfulness"] for r in results) / total,
            "avg_relevancy": sum(r["expert_eval"]["relevancy"] for r in results) / total,
            "cohens_kappa": kappa,
            "total_tokens": total_tokens,
            "estimated_cost_usd": total_cost
        }
    }
    return results, summary

async def main():
    # Chạy benchmark cho Agent V1
    v1_agent = MainAgent(version="v1") # Instance của Agent V1
    _, v1_summary = await run_benchmark_with_results("Agent_V1_Base", v1_agent)
    
    # Giả lập V2 có cải tiến (để test logic)
    v2_agent = MainAgent(version="v2") # Bây giờ V2 đã khác biệt
    v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized", v2_agent)
    
    if not v1_summary or not v2_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại data/golden_set.jsonl.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    print(f"V1 Score: {v1_summary['metrics']['avg_score']}")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    if delta > 0:
        print("✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        print("❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE)")

if __name__ == "__main__":
    asyncio.run(main())
