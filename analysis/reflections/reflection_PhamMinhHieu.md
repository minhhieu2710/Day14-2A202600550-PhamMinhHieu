# Bài thu hoạch cá nhân - Lab Day 14

**Họ và tên:** Phạm Minh Hiếu
**Vai trò trong nhóm:** AI Engineer / Backend Developer

## 1. Công việc đã thực hiện
- Triển khai hệ thống đánh giá tự động (Evaluation Factory) sử dụng kiến trúc Async để tối ưu hiệu năng.
- Xây dựng module `RetrievalEvaluator` để tính toán các chỉ số kỹ thuật quan trọng như Hit Rate và MRR.
- Thiết kế logic `Multi-Judge Consensus` giúp hệ thống đánh giá khách quan hơn bằng cách kết hợp kết quả từ nhiều model LLM khác nhau.
- Thực hiện SDG (Synthetic Data Generation) để tạo ra bộ Golden Dataset 50 cases chất lượng cao.
- Phát triển logic `Regression Release Gate` để tự động so sánh phiên bản Agent V1 và V2, đưa ra quyết định APPROVE/BLOCK dựa trên dữ liệu.
- Triển khai cơ chế theo dõi Token usage và ước tính chi phí Eval thực tế.

## 2. Bài học kinh nghiệm
- **Tầm quan trọng của Retrieval:** Qua bài lab, em nhận ra rằng chất lượng câu trả lời phụ thuộc cực kỳ lớn vào giai đoạn Retrieval. Nếu Hit Rate thấp, dù LLM có mạnh đến đâu cũng sẽ dẫn đến Hallucination.
- **Kiểm soát Bias:** Em đã học được cách triển khai Swap Test để phát hiện **Position Bias** - hiện tượng LLM Judge ưu tiên câu trả lời đứng ở vị trí đầu tiên.
- **Độ tin cậy của Judge:** Việc sử dụng hệ số đồng thuận giúp em hiểu về **Cohen's Kappa**, đo lường sự nhất quán giữa GPT-4o và Claude, tránh việc đánh giá phiến diện từ một mô hình.
- **Chỉ số MRR:** Em hiểu sâu hơn về MRR giúp đánh giá không chỉ việc tìm thấy (Hit) mà còn là vị trí (Rank) của tài liệu, giúp tối ưu hóa ngữ cảnh đưa vào Prompt.
- **Tư duy dựa trên dữ liệu & Trade-off:** Thay vì cảm tính rằng "V2 có vẻ tốt hơn", việc có một hệ thống Benchmark giúp đội ngũ kỹ thuật có con số cụ thể (Delta +0.7) để tự tin triển khai sản phẩm. Đồng thời, việc theo dõi chi phí và hiệu năng giúp em hiểu về sự đánh đổi giữa chất lượng đánh giá (dùng LLM Judge mạnh) và chi phí vận hành.

## 3. Khó khăn và cách giải quyết
- **Vấn đề:** Gặp lỗi Rate Limit khi gọi API LLM liên tục cho 50 test cases.
- **Giải quyết:** Triển khai cơ chế Batching trong `BenchmarkRunner` sử dụng `asyncio.gather` với giới hạn số lượng request đồng thời.
- **Vấn đề:** Lỗi định dạng JSON khi SDG tạo dữ liệu không đồng nhất.
- **Giải quyết:** Sử dụng `response_format={"type": "json_object"}` và viết lại Prompt hướng dẫn cấu trúc metadata rõ ràng.
- **Vấn đề:** Tối ưu chi phí cho việc đánh giá bằng LLM Judge.
- **Giải quyết:** Em đề xuất chiến lược sử dụng mô hình nhỏ (GPT-4o-mini) cho các câu hỏi Fact-check đơn giản và chỉ dùng mô hình lớn (GPT-4o/Claude) cho các câu hỏi Reasoning phức tạp, giúp giảm khoảng 30% chi phí mà vẫn giữ được độ chính xác cần thiết.

## 4. Hướng phát triển tiếp theo
- Tích hợp thư viện RAGAS thật thay vì các điểm số giả lập để có cái nhìn sâu hơn về Faithfulness và Answer Relevancy.
- Xây dựng Dashboard trực quan hóa kết quả Benchmark để các bên liên quan (Stakeholders) dễ dàng theo dõi quá trình cải thiện của Agent.
- Thử nghiệm các chiến lược Reranking để đẩy MRR lên mức tối đa.

---
*Phạm Minh Hiếu - 16/06/2026*