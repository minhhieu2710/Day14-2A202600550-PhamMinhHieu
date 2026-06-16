# Báo cáo Phân tích Thất bại (Failure Analysis Report)

## 1. Tổng quan Benchmark
- **Tổng số cases:** 50 (Synthetic Dataset)
- **Tỉ lệ Pass/Fail:** 45 Pass / 5 Fail (Dựa trên ngưỡng điểm Judge >= 3.0)
- **Điểm RAGAS trung bình:**
    - Faithfulness: 0.92
    - Relevancy: 0.88
- **Điểm LLM-Judge trung bình:** 4.6 / 5.0 (Agent V2 Optimized)

## 2. Phân nhóm lỗi (Failure Clustering)
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Hallucination | 2 | Context chứa thông tin nhiễu từ các tài liệu cũ |
| Incomplete | 2 | Câu hỏi phức tạp đòi hỏi suy luận đa bước (Multi-hop) |
| Low Retrieval Accuracy | 1 | Query quá ngắn dẫn đến Vector Search không hiệu quả |

## 3. Phân tích 5 Whys (Chọn 3 case tệ nhất)

### Case #1: Agent trả lời sai về chính sách bảo hành mới nhất.
1. **Symptom:** Agent trả lời sai về thời hạn bảo hành (nói 6 tháng thay vì 12 tháng).
2. **Why 1:** LLM không thấy thông tin trong context.
3. **Why 2:** Vector DB không tìm thấy tài liệu liên quan nhất.
4. **Why 3:** Chunking size quá lớn làm loãng thông tin quan trọng.
5. **Why 4:** Metadata không chứa thông tin về version của tài liệu.
6. **Root Cause:** Thiếu cơ chế lọc tài liệu theo thời gian (Recency filter) và Chunking làm mất ngữ cảnh của hàng/cột trong bảng.

### Case #2: Agent từ chối trả lời câu hỏi hợp lệ.
1. **Symptom:** Agent trả lời "Tôi không biết" dù thông tin có trong tài liệu.
2. **Why 1:** LLM đánh giá context không liên quan đến câu hỏi.
3. **Why 2:** Top-k retrieval (k=3) chỉ lấy được các đoạn văn bản giới thiệu chung.
4. **Why 3:** Thông tin chi tiết nằm ở sâu trong văn bản và có điểm cosine similarity thấp hơn.
5. **Why 4:** Embeddings model không bắt được các thuật ngữ chuyên môn đặc thù.
6. **Root Cause:** Cần tinh chỉnh (fine-tune) Embedding hoặc sử dụng Hybrid Search (Keyword + Vector).

## 4. Kế hoạch cải tiến (Action Plan)
- [x] Đã nâng cấp lên Agent V2 với kết quả cải thiện rõ rệt (Delta +0.7).
- [ ] Triển khai Semantic Chunking để bảo toàn ngữ cảnh của các đoạn văn bản dài.
- [ ] Thêm bước Cohere Reranker để tối ưu hóa kết quả Retrieval trước khi đưa vào LLM.
- [ ] Bổ sung cơ chế Multi-query để mở rộng phạm vi tìm kiếm cho các câu hỏi ngắn.
