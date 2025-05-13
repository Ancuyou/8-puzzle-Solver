# Áp dụng các thuật toán tìm kiếm và tối ưu để giải bài toán 8 puzzle

Dự án này cài đặt một số thuật toán tìm kiếm Trí tuệ nhân tạo để giải bài toán 8 puzzle, bao gồm Tìm kiếm không có thông tin (Uninformed Search), Tìm kiếm có thông tin (Informed Search), Tìm kiếm cục bộ (Local Search), Tìm kiếm trong môi trường phức tạp (Complex Environments), Tìm kiếm có ràng buộc (CSPs), và Học tăng cường (Reinforcement Learning - Đang trong quá trình hoàn thiện). Mỗi phần bao gồm các hình ảnh trực quan (GIF) và biểu đồ hiệu suất để giúp hiểu rõ hành vi của các thuật toán, trong điều kiện môi trường tĩnh và xác định của trò chơi 8 puzzle.

## Cấu trúc Thư mục

- `__pycache__`: Thư mục chứa các file bộ nhớ đệm của Python (tự động tạo).
- `assets/`: Chứa các file GIF và biểu đồ để trực quan hóa.
- `logic.py`: Chứa mã nguồn chính để triển khai các thuật toán tìm kiếm.
- `visualization.py`: Xử lý giao diện.
- `results.csv`: Kết quả đầu ra từ việc chạy các thuật toán.

## Tổng quan về bài toán 8 puzzle

Bài toán 8 puzzle là một trò chơi trượt số trên lưới 3x3, gồm 8 ô số (từ 1 đến 8) và 1 ô trống. Mục tiêu là di chuyển các ô số từ trạng thái ban đầu đến trạng thái mục tiêu (thường là 1-2-3, 4-5-6, 7-8-trống) bằng cách trượt ô trống lên, xuống, trái, hoặc phải.

### Không gian trạng thái

- Tổng số cấu hình có thể: \(9! = 362,880\), nhưng chỉ một nửa (181,440) là khả thi do tính chất hoán vị chẵn/lẻ của bài toán.
- Mỗi trạng thái có tối đa 4 hành động (di chuyển ô trống), dẫn đến một đồ thị trạng thái với độ sâu tối đa khoảng 31 bước trong trường hợp xấu nhất.

### Độ phức tạp

- **Thời gian**: Phụ thuộc vào thuật toán, từ \(O(b^d)\) (với \(b\) là độ nhánh, \(d\) là độ sâu) cho tìm kiếm mù đến \(O(n)\) cho các phương pháp heuristic tối ưu.
- **Không gian**: Từ \(O(d)\) cho các phương pháp tiết kiệm bộ nhớ đến \(O(b^d)\) cho các thuật toán lưu toàn bộ trạng thái.

### Tính chất

- **Tĩnh**: Môi trường không thay đổi trong quá trình giải.
- **Xác định**: Mỗi hành động dẫn đến một kết quả duy nhất.
- **Rời rạc**: Không gian trạng thái và hành động là hữu hạn.
- **Khả thi**: Không phải mọi cấu hình ban đầu đều có thể đạt được mọi cấu hình mục tiêu (phụ thuộc vào tính chẵn/lẻ của hoán vị).

---

## Tìm kiếm không có thông tin (Uninformed Search)

Uninformed Search bao gồm các thuật toán như BFS, DFS, UCS, và IDDFS. Dưới đây là các hình ảnh trực quan cho từng thuật toán, cùng với biểu đồ hiệu suất.

### Hình ảnh Trực quan

| Tên thuật toán | Hình ảnh                   |
| -------------- | -------------------------- |
| BFS            | ![BFS](assets/BFS_2.gif)   |
| DFS            | ![DFS](assets/DFS.gif)     |
| UCS            | ![UCS](assets/UCS.gif)     |
| IDDFS          | ![IDDFS](assets/IDDFS.gif) |

### Biểu đồ Hiệu suất

![Biểu đồ Tìm kiếm Không Thông Tin](assets/uninformed.png)

### Phân tích

Uninformed Search là nhóm thuật toán tìm kiếm mù, tức không có sử dụng bất cứ thông tin đường đi nào khác ngoài cấu hình không gian trạng thái (cấu hình board) và tập hành động. Điều đó làm cho các thuật toán trong nhóm này phải duyệt qua toàn bộ không gian trạng thái (mở rộng tập tìm kiếm liên tục), thường đảm bảo tìm được giải pháp nếu tồn tại nhưng không chắc là giải pháp tối ưu nhất. Đặc biệt gặp vấn đề về hiệu suất trong không gian trạng thái 9! của bài toán 8 puzzle. Trong đó:

- `BFS`: luôn tìm được lời giải ngắn nhất, hiệu quả với bài toán độ sâu thấp như trên ảnh gif ví dụ. Tuy nhiên không gian trạng thái tìm kiếm tương đối lớn và gặp khó khăn khi lời giải quá sâu.
- `DFS`: tiết kiệm bộ nhớ hơn BFS do chỉ lưu trữ trạng thái của nhánh đang xét, đồng thời tìm được lời giải nhanh hơn BFS cho các nhánh sâu. Tuy nhiên thường không tìm ra được giải pháp tối ưu và phức tạp thời gian tăng cao nếu khám phá nhánh ở xa lời giải.
- `IDDFS`: kết hợp ưu điểm tìm lời giải tối ưu và tiết kiệm bộ nhớ của BFS và DFS. Phù hợp với bài toán 8 puzzle có độ sâu trong khoảng 15-25 bước. Tuy nhiên do lặp lại duyệt trên từng độ sâu liên tục nên hiệu suất bị giảm.
- `UCS`: sử dụng chi phí tích lũy từ trạng thái ban đầu để quyết định mở rộng trạng thái nào tiếp theo. Nhưng ở bài toán 8 puzzle khi chi phí các bước đi đều bằng nhau thì UCS sẽ cho kết quả tương tự BFS.

## Tìm kiếm Có Thông Tin (Informed Search)

Tìm kiếm Có Thông Tin bao gồm các thuật toán như A\*, Tìm kiếm Tốt Nhất Trước Hết theo Heuristic, và một phương pháp dựa trên heuristic khác. Dưới đây là các hình ảnh trực quan và biểu đồ hiệu suất.

### Hình ảnh Trực quan

| Tên thuật toán | Hình ảnh                |
| -------------- | ----------------------- |
| A\*            | ![A*](assets/A.gif)     |
| IDA\*          | ![IDA*](assets/IDA.gif) |
| GBFS           | ![GBFS](assets/GB.gif)  |

### Biểu đồ Hiệu suất

![Biểu đồ Tìm kiếm Có Thông Tin](assets/informed.png)

### Phân tích

Informed Search là nhóm thuật toán sử dụng thông tin heuristic để ưu tiên duyệt các trạng thái được cho là có "triển vọng". Heuristic được dùng ở đây là tổng khoảng cách Manhattan của các ô so với vị trí đúng. Nhóm thuật toán này thể hiện khả năng giảm đáng kể số trạng thái cần duyệt so với Uninformed Search. Trong đó:

- `A*`: với heuristic admissible (không vượt quá chi phí thực tế), A\* đảm bảo tìm được giải pháp tối ưu trong bài toán 8 puzzle với thời gian nhanh nhất. Tuy nhiên thuật toán cũng gặp vấn đề về không gian bộ nhớ do yêu cầu lưu toàn bộ trạng thái đã duyệt cùng với đó là giảm hiệu suất khi lời giải ở sâu.
- `IDA*`: Sử dụng ít bộ nhớ hơn A\* nhờ vào cơ chế duyệt sâu dần. Tuy nhiên tốn thời gian hơn vì phải duyệt lại nhiều lần nếu trạng thái ở sâu.
- `Greedy Best-First Search`: Nhanh hơn A\* vì chỉ tập trung vào giá trị heuristic h(n). Đặc biệt tốt khi cần lời giải nhanh và nhất thiết tối ưu. Và điểm yếu cũng là không đảm bảo tìm được lời giải tối ưu nhất.

## Tìm kiếm Cục Bộ (Local Search)

Tìm kiếm Cục Bộ bao gồm các thuật toán như Leo Đồi (Hill Climbing), Ủ Nhiệt Mô Phỏng (Simulated Annealing), Thuật toán Di truyền (Genetic Algorithms), và các thuật toán khác. Dưới đây là các hình ảnh trực quan và biểu đồ hiệu suất.

### Hình ảnh Trực quan

| Tên thuật toán          | Hình ảnh                      |
| ----------------------- | ----------------------------- |
| HillClimbing(Simple)    | ![BFS](assets/hill_simp.gif)  |
| HillClimbing(Steepest)  | ![DFS](assets/Hill_steep.gif) |
| HillClimbing(Stochatic) | ![UCS](assets/hill_stor.gif)  |
| Simulated Annealing     | ![IDDFS](assets/SA.gif)       |
| Genetic Algorithm       | ![IDDFS](assets/Genertic.gif) |

### Biểu đồ Hiệu suất

![Biểu đồ Tìm kiếm Cục Bộ](assets/local.png)

### Phân tích

Local Search không duyệt toàn bộ không gian trạng thái vì vậy độ phức tạp không gian giảm mạnh so với hai thuật toán trước, chỉ tập trung cải thiện lời giải cục bộ và hiệu quả với không gian trạng thái quá lớn. Tuy nhiên vấn đề của nhóm này chính là lời giải thường không tối ưu toàn cục và dễ bị mắc kẹt ở cực trị cục bộ. Trong đó:

- `SA`: Có khả năng vượt qua cực trị cục bộ bằng việc "làm nguội" và chọn các ước đi tạm thời kém hơn. Tuy nhiên hiện đang là thuật toán kém hiệu quả nhất với 8 puzzle, đặc biệt khi lời giải ở độ sâu cao.
- `GA`: Thử nghiệm nhiều trạng thái cùng lúc, tăng khả năng tìm ra lời giải. Tuy nhiên mất nhiều thời gian trong việc thử nghiệm và tối ưu tham số. Ngoài ra thời gian hội tụ của thuật toán cũng có thể rất lâu.
- `Nhóm thuật toán HillClimbing`: Nhanh và dễ triển khai. HillClimbing cơ bản dễ bị mắc kẹt ở cực trị địa phương. HillClimbing Steepest xem xét các trạng thái lân cân và tìm trạng thái tốt nhất tuy nhiên cũng dễ mắc kẹt trong bẫy cực trị cục bộ. HillClimbing Storchastic đem lại một tỉ lệ chọn các trạng thái không tốt bằng để tránh bẫy cực trị tuy nhiên đòi hỏi việc điều chỉnh tỉ lệ phù hợp. Vấn đề chung của nhóm trên là dù nhanh nhưng rất dễ bị mắc kẹt.

## Tìm kiếm Phức Tạp (Complex Environments)

Tìm kiếm Phức Tạp bao gồm ba thuật toán nâng cao cùng với các hình ảnh trực quan và biểu đồ hiệu suất.

### Hình ảnh Trực quan

| Tên thuật toán          | Hình ảnh                       |
| ----------------------- | ------------------------------ |
| Search with no obs      | ![A*](assets/belief.gif)       |
| Search with partial obs | ![IDA*](assets/partbelief.gif) |
| And or search           | ![GBFS](assets/AndOr.gif)      |

### Biểu đồ Hiệu suất

![Biểu đồ Tìm kiếm Phức Tạp](assets/complex.png)

### Phân tích

Search in Complex Environment là nhóm thuật toán xử lý các điều kiện thực tế như môi trường mù hoàn toàn hay môi trường có thông tin một phần. 8 puzzle là bài toán tĩnh, ít phù hợp hơn với nhóm này. Tuy nhiên chúng ta cũng có thể cài đặt một số biến thể để xem xét cách hoạt động. Trong đó:

- `Search with no observation`: giả định môi trường khi agent không có bất kỳ thông tin gì, ngay cả vị trí của bản thân. Thực hiện cài đặt belief states ban đầu và tìm kiếm theo BFS về tập goal states.
- `Search with partial observation`: tương tự như thuật toán trên nhưng có được thêm một phần thông tin về môi trường. Ở đây là thông tin số 1 nằm ở tọa độ (0,0), giúp giảm đáng kể không gian trạng thái cần xét.
- `And Or Search`: Được sử dụng trong bài toán có nhiều nhánh lựa chọn và các tình huống không xác định. Nút Or đại diện cho các lựa chọn khác nhau mà agent có thể thực hiện, nút And đại diện cho điều kiện con phải đượ thỏa để đạt mục tiêu. Phù hợp cho bài toán lên kế hoạch phức tạp, tuy nhiên 8 puzzle là không gian tĩnh nên thuật toán không thể hiện được nhiều.

## Bài toán Hài Hòa Ràng Buộc (CSPs)

CSPs bao gồm các thuật toán như Quay lui (Backtracking), Kiểm tra Tính Hài Hòa Cung (Arc Consistency), và một phương pháp CSP khác. Dưới đây là các hình ảnh trực quan và biểu đồ hiệu suất.

### Hình ảnh Trực quan

| Tên thuật toán             | Hình ảnh                              |
| -------------------------- | ------------------------------------- |
| Backtracking (simple)      | ![Backtrack(Simple)](assets/back.gif) |
| Backtracking (constraints) | ![IDA*](assets/back_cons.gif)         |
| Backtracking (LCV)         | ![GBFS](assets/back_heus.gif)         |

### Biểu đồ Hiệu suất

![Biểu đồ CSP](assets/CSPs.png)

### Phân tích

CSPs là nhóm thuật toán dựa trên việc giải quyết ràng buộc giữa các biến. Ta biến đổi bài toán giải 8 puzzle thành dạng bài tô màu đồ thị với các ràng buộc để cài đặt nhóm thuật toán này. Trong đó:

- `Nhóm thuật toán Backtracking`: backtracking ngây thơ đạt hiệu quả rất tệ với 8 puzzle, mất rất nhiều thời gian tuy nhiên sẽ đảm bảo luôn tìm ra lời giải. Backtracking với contraints (ràng buộc) cho hiệu quả tốt hơn hẳn với ràng buộc các số tăng dần theo thứ tự ô. Trong khi Backtracking với lcv kết hợp contraints thì chưa đạt được hiệu quả cải tiến quá nhiều.

---

## Bảng So sánh Các Thuật Toán

| Thuật toán                 | Độ phức tạp thời gian | Độ phức tạp không gian | Hoàn thiện | Tối ưu |
| -------------------------- | --------------------- | ---------------------- | ---------- | ------ |
| BFS                        | \(O(b^d)\)            | \(O(b^d)\)             | Có         | Có     |
| DFS                        | \(O(b^m)\)            | \(O(bm)\)              | Không      | Không  |
| UCS                        | \(O(b^d)\)            | \(O(b^d)\)             | Có         | Có     |
| IDDFS                      | \(O(b^d)\)            | \(O(bd)\)              | Có         | Có     |
| A\*                        | \(O(b^d)\)            | \(O(b^d)\)             | Có         | Có     |
| IDA\*                      | \(O(b^d)\)            | \(O(bd)\)              | Có         | Có     |
| GBFS                       | \(O(b^m)\)            | \(O(bm)\)              | Không      | Không  |
| Hill Climbing (Simple)     | \(O(\infty)\)         | \(O(1)\)               | Không      | Không  |
| Simulated Annealing        | \(O(\infty)\)         | \(O(1)\)               | Không      | Không  |
| Genetic Algorithm          | \(O(g \cdot p)\)      | \(O(p)\)               | Không      | Không  |
| Search with no obs         | \(O(b^d)\)            | \(O(b^d)\)             | Có         | Không  |
| Search with partial obs    | \(O(b^d)\)            | \(O(b^d)\)             | Có         | Không  |
| And Or Search              | \(O(b^m)\)            | \(O(bm)\)              | Có         | Không  |
| Backtracking (Simple)      | \(O(n!)\)             | \(O(n)\)               | Có         | Có     |
| Backtracking (Constraints) | \(O(n!)\)             | \(O(n)\)               | Có         | Có     |

- \(b\): Độ nhánh, \(d\): Độ sâu lời giải, \(m\): Độ sâu tối đa, \(g\): Số thế hệ, \(p\): Kích thước quần thể, \(n\): Số biến.

---

## Học Tăng Cường

Học Tăng Cường (Reinforcement Learning - RL) áp dụng agent học qua thử nghiệm và phần thưởng.

### Hình ảnh Trực quan

| Tên thuật toán | Hình ảnh                            |
| -------------- | ----------------------------------- |
| Q-Learning     | ![Q-Learning](assets/Qlearning.gif) |

### Biểu đồ Hiệu suất

![Biểu đồ Học Tăng Cường](assets/qlearning.png)

### Phân tích

RL huấn luyện agent qua phần thưởng, phù hợp với bài toán động hơn 8 puzzle tĩnh, cập nhật Q theo công thức:

![CT](assets/ct.png)

`Q-Learning`: Học bảng Q qua thử nghiệm, hiệu quả với không gian nhỏ. Với 8 puzzle, tốc độ học chậm do không gian trạng thái lớn (181,440 trạng thái khả thi), cần nhiều lần lặp. Không đảm bảo tối ưu như A\*, nhưng linh hoạt với môi trường thay đổi. Biểu đồ ở trên nêu lên so sánh trực quan về Q-learning-first với 2000 episode ban đầu và Q-learning nâng cao hơn với:
- Sử dụng epsilon giảm dần theo từng episode với các tham số: EPSILON_START, EPSILON_END, và EPSILON_DECAY. Điều này khuyến khích việc thăm dò nhiều hơn ở giai đoạn đầu và tập trung khai thác (exploit) ở giai đoạn cuối.
- Chạy 50,000 episode, mỗi episode có tối đa 1,000 bước so với 2,000 episode, mỗi episode có tối đa 200 bước của Q-learning-first
- Sử dụng trạng thái ban đầu hoặc một trạng thái nhiễu với tối đa 50 bước so với 5 bước của Q-learning-first
Các thay đổi trên nhìn chung đã giúp cho kết quả của Q-learning tốt hơn, tuy nhiên vẫn có thể tối ưu thêm được nữa trong thời gian tới. 

## Hướng dẫn Cài đặt và Sử dụng

### Yêu cầu Cần Thiết

- Python 3.8 hoặc cao hơn
- pip (trình quản lý gói của Python)

### Các Bước Cài đặt

1. Tải mã nguồn về máy:
   ```bash
   git clone https://github.com/Ancuyou/8-puzzle-Solver.git
   cd 8-puzzle-Solver
   ```
2. Tạo môi trường ảo (khuyến khích nhưng không bắt buộc):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   ```
3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
   _Lưu ý_: Nếu không có file `requirements.txt`, bạn có thể cần cài đặt thủ công các thư viện như `pandas`, `matplotlib`, và các thư viện khác được sử dụng trong dự án.

### Chạy Dự án

1. Chạy file trực quan hóa chính:
   ```bash
   python visualization.py
   ```
2. File sẽ tạo ra các GIF và biểu đồ trong thư mục `assets/` và lưu kết quả vào `results.csv`.

### Tùy chỉnh Dữ liệu

- Sửa file `data.csv` để thay đổi dữ liệu đầu vào cho các thuật toán.
- Cập nhật file `logic.py` để điều chỉnh cách triển khai thuật toán nếu cần.

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng làm theo các bước sau:

1. Fork kho lưu trữ.
2. Tạo một nhánh mới (`git checkout -b feature/tinh-nang-cua-ban`).
3. Thực hiện thay đổi và commit (`git commit -m "Thêm mô tả thay đổi"`).
4. Đẩy lên nhánh của bạn (`git push origin feature/tinh-nang-cua-ban`).
5. Mở một Pull Request.

## Liên hệ

Nếu có câu hỏi hoặc phản hồi, vui lòng liên hệ qua [nguyenngocthaibaodetox@gmail.com](mailto:nguyenngocthaibaodetox@gmail.com) hoặc mở một issue trên GitHub.
