# HELPERS.md

## Mục đích

Tài liệu này mô tả các helper, utility và API hỗ trợ phát triển AI trong dự án Caro AI.

Mục tiêu:

* Giúp AI developer không cần đọc toàn bộ codebase.
* Chuẩn hóa cách truy cập board và game state.
* Tận dụng lại PatternAnalyzer và BoardAnalyzer.
* Hỗ trợ phát triển Minimax, Alpha-Beta, MCTS, Heuristic AI và các AI khác.

---

# Tổng quan kiến trúc

```text
GameState
│
├── Board
│
├── PatternAnalyzer
│     └── Phân tích pattern
│
├── BoardAnalyzer
│     └── Đánh giá candidate moves
│
└── AIPlayer
      └── choose_move(state)
```

---

# AIPlayer

Tất cả AI phải kế thừa:

```python
from ai.base import AIPlayer
```

Interface:

```python
class AIPlayer(ABC):

    @property
    def name(self):
        pass

    def choose_move(self, state):
        pass
```

Ví dụ:

```python
class MyAI(AIPlayer):

    @property
    def name(self):
        return "My AI"

    def choose_move(self, state):
        return state.get_valid_moves()[0]
```

---

# GameState

AI luôn nhận:

```python
state
```

trong:

```python
choose_move(state)
```

Các API quan trọng:

## Lấy người chơi hiện tại

```python
state.current_player
```

## Lấy đối thủ

```python
state.get_opponent()
```

## Lấy tất cả nước đi hợp lệ

```python
moves = state.get_valid_moves()
```

## Candidate moves gần quân đã đánh

```python
moves = state.get_candidate_moves(
    distance=2
)
```

Khuyến nghị:

* Không nên dùng toàn bộ valid_moves.
* Nên dùng candidate_moves để giảm branching factor.

---

# Board

Truy cập:

```python
board = state.board
```

## Đọc ô

```python
cell = board.get_cell(row, col)
```

Trả về:

```python
EMPTY
PLAYER_X
PLAYER_O
```

## Clone board

```python
new_board = board.clone()
```

## Đặt quân

```python
success = board.place_piece(
    row,
    col,
    player
)
```

---

# Simulate Move

Tạo state mới sau khi đánh:

```python
new_state = state.simulate_move(
    move
)
```

Rất hữu ích cho:

* Minimax
* Alpha-Beta
* MCTS

---

# PatternAnalyzer

Import:

```python
from game.pattern import (
    PatternAnalyzer,
    PatternType
)
```

Mục đích:

* Nhận diện pattern.
* Tìm nước thắng.
* Tìm threat.

PatternAnalyzer KHÔNG thực hiện heuristic scoring.

---

# PatternType

Các pattern hiện hỗ trợ:

```python
PatternType.WINNING
PatternType.OPEN_4
PatternType.DEAD_4
PatternType.THREAT_4
PatternType.LIVE_3
PatternType.THREAT_3
PatternType.BLOCKED_3
PatternType.LIVE_2
```

---

# Giới hạn hiện tại

PatternAnalyzer hiện dựa trên:

```python
piece_count
empty_left
empty_right
```

Nó hoạt động tốt với:

```text
XXXXX
_XXXX_
_XXX_
_XX_
```

Nhưng KHÔNG nhận diện chính xác:

```text
XX_XX
X_XXX
XXX_X
XX_X
OXXX_O
```

Các broken pattern này hiện chưa được hỗ trợ.

Nếu cần AI mạnh hơn trong tương lai có thể phát triển PatternAnalyzer V2 bằng pattern matching trên chuỗi.

---

# Analyze Move

Phân tích một nước đi:

```python
lines = PatternAnalyzer.analyze_move(
    board,
    move,
    player
)
```

Trả về:

```python
list[LineInfo]
```

Mỗi direction có:

```python
line.pattern
line.piece_count
line.empty_left
line.empty_right
```

Ví dụ:

```python
best_pattern = lines[0].pattern
```

---

# Tìm nước thắng

```python
winning_moves = (
    PatternAnalyzer.find_winning_moves(
        board,
        valid_moves,
        player
    )
)
```

Nếu danh sách không rỗng:

```python
winning_moves[0]
```

là nước thắng ngay.

---

# Tìm Threat

```python
threats = (
    PatternAnalyzer.find_threats(
        board,
        valid_moves,
        player
    )
)
```

Trả về:

```python
{
    PatternType.OPEN_4: [...],
    PatternType.LIVE_3: [...],
}
```

Dùng để:

* block đối thủ
* tactical search

---

# BoardAnalyzer

Import:

```python
from game.board_analyzer import (
    BoardAnalyzer
)
```

Mục đích:

* Candidate ordering
* Heuristic ranking
* Fork detection
* Tactical move selection

---

# Candidate Analysis

```python
candidates = (
    BoardAnalyzer.get_candidate_analysis(
        board,
        distance=2
    )
)
```

Kết quả:

```python
list[CellAnalysis]
```

Đã được sắp xếp:

```python
priority_score giảm dần
```

---

# CellAnalysis

```python
analysis.move

analysis.x_lines
analysis.o_lines

analysis.x_best_pattern
analysis.o_best_pattern

analysis.priority_score
```

---

# Priority Score

BoardAnalyzer sử dụng heuristic:

```python
WINNING    = 1_000_000
OPEN_4     = 100_000
THREAT_4   = 80_000
DEAD_4     = 30_000
LIVE_3     = 10_000
THREAT_3   = 8_000
BLOCKED_3  = 3_000
LIVE_2     = 500
```

Ngoài ra còn có bonus cho:

## Double LIVE_3

```text
LIVE_3 + LIVE_3
```

## Double OPEN_4

```text
OPEN_4 + OPEN_4
```

## Double DEAD_4

```text
DEAD_4 + DEAD_4
```

Mục đích:

* nhận diện fork
* ưu tiên multi-threat

---

# Critical Cells

Lấy các nước chiến thuật quan trọng:

```python
moves = (
    BoardAnalyzer.get_critical_cells(
        board,
        player
    )
)
```

Thường dùng cho:

* Quiescence Search
* Tactical Search
* Threat Search

---

# Heatmap

Debug heuristic:

```python
heatmap = (
    BoardAnalyzer.get_board_heatmap(
        board
    )
)
```

Mỗi ô:

```python
heatmap[row][col]
```

chứa priority score.

---

# Tournament Notes

Tournament hiện sử dụng:

```text
2 random opening moves
```

trong vùng trung tâm bàn cờ.

Mục đích:

* Tránh mọi trận đấu giống hệt nhau.
* Tăng tính đa dạng khi benchmark AI.

---

# Khuyến nghị cho AI Developer

## Greedy AI

Nên sử dụng:

```python
BoardAnalyzer.get_candidate_analysis()
```

để chọn nước ưu tiên cao nhất.

---

## Minimax / Alpha-Beta

Nên:

```python
BoardAnalyzer.get_candidate_analysis()
```

để move ordering.

Điều này giúp Alpha-Beta pruning hiệu quả hơn.

---

## MCTS

Có thể sử dụng:

```python
priority_score
```

để bias rollout hoặc expansion.

---

# Lưu ý

BoardAnalyzer hiện là heuristic hỗ trợ.

Nó không thay thế evaluation function riêng của từng AI.

Các AI mạnh hơn nên xây dựng evaluation function riêng dựa trên:

* PatternAnalyzer
* BoardAnalyzer
* hoặc heuristic tùy chỉnh.
