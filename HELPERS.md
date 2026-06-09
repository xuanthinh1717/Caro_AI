# Helper Functions & Classes cho Phát Triển AI

Dự án Caro AI bổ sung các helper classes để hỗ trợ phát triển AI strategies. Những components này cung cấp thông tin chi tiết về board state, patterns, và move analysis mà AI có thể sử dụng.

## 1. PatternAnalyzer (`game/pattern.py`)

Phát hiện và phân loại patterns trên board.

### PatternType (Enum)

Các loại pattern được hỗ trợ:

- **WINNING** (5): 5 quân liên tiếp - chiến thắng!
- **OPEN_4** (44): 4 quân liên tiếp, mở 2 mặt - rất nguy hiểm
- **DEAD_4** (444): 4 quân liên tiếp, bị chặn 1 mặt
- **LIVE_3** (33): 3 quân liên tiếp, mở 2 mặt
- **LIVE_2** (22): 2 quân liên tiếp, mở 2 mặt
- **BLOCKED_3** (333): 3 quân liên tiếp, bị chặn 1 mặt
- **THREAT_4** (434): Có 2 cách tạo 4 liên tiếp
- **THREAT_3** (233): Có 2 cách tạo 3 liên tiếp mở

### LineInfo (Dataclass)

```python
@dataclass
class LineInfo:
    direction: tuple        # (dr, dc)
    piece_count: int        # Số quân liên tiếp
    empty_left: int         # Số ô trống trước (hướng âm)
    empty_right: int        # Số ô trống sau (hướng dương)
    player: int             # PLAYER_X (1) hoặc PLAYER_O (2)
    pattern: PatternType    # Loại pattern
```

### Các phương thức

```python
# Lấy thông tin line tại vị trí (row, col) theo hướng
line_info = PatternAnalyzer.get_line_info(board, row, col, direction, player)

# Phân tích nước đi: lấy info 4 directions
lines = PatternAnalyzer.analyze_move(board, move, player)
# Returns: list[LineInfo] sắp xếp theo piece_count (giảm dần)

# Tìm nước đi chiến thắng
winning_moves = PatternAnalyzer.find_winning_moves(board, valid_moves, player)

# Nhóm nước đi theo threat level
threats = PatternAnalyzer.find_threats(board, valid_moves, player)
# Returns: dict[PatternType, List[Move]]
```

### Ví dụ

```python
from game.board import Board
from game.move import Move
from game.pattern import PatternAnalyzer
from game.constants import PLAYER_X

board = Board()
board.place_piece(7, 7, PLAYER_X)
board.place_piece(7, 8, PLAYER_X)
board.place_piece(7, 9, PLAYER_X)

# Phân tích nước đi tiếp theo
move = Move(7, 10)
lines = PatternAnalyzer.analyze_move(board, move, PLAYER_X)

print(f"Best pattern: {lines[0].pattern.name}")  # Output: DEAD_4
print(f"Piece count: {lines[0].piece_count}")    # Output: 4
```

---

## 2. BoardAnalyzer (`game/board_analyzer.py`)

Phân tích board toàn cục - priority scoring, threat detection, candidate moves.

### CellAnalysis (Dataclass)

```python
@dataclass
class CellAnalysis:
    move: Move
    
    # Nếu X đặt ở đây
    x_lines: list[LineInfo]
    x_best_pattern: PatternType
    
    # Nếu O đặt ở đây
    o_lines: list[LineInfo]
    o_best_pattern: PatternType
    
    # Priority score (cao hơn = quan trọng hơn)
    priority_score: float = 0.0
```

### Các phương thức

```python
# Phân tích 1 ô: nếu X/O đặt ở đây sẽ tạo patterns gì?
analysis = BoardAnalyzer.analyze_cell(board, move, depth=1)

# Lấy danh sách candidate moves (gần các quân đã đi)
# Sắp xếp theo priority_score (cao nhất trước)
candidates = BoardAnalyzer.get_candidate_analysis(
    board,
    distance=2,      # Chỉ lấy ô cách quân ≤ 2 ô
    top_n=10         # Top 10 candidates
)

# Lấy ô quan trọng nhất (cần block hoặc attack)
# Chỉ lấy những nước tạo OPEN_4, DEAD_4, hay LIVE_3
critical = BoardAnalyzer.get_critical_cells(board, player)

# Heatmap priority: lấy score cho mỗi ô
# Dùng để visualize hoặc debug
heatmap = BoardAnalyzer.get_board_heatmap(board, PLAYER_X)
```

### Ví dụ

```python
board = Board()
board.place_piece(7, 7, PLAYER_X)
board.place_piece(8, 7, PLAYER_O)

# Lấy top 5 candidates
candidates = BoardAnalyzer.get_candidate_analysis(board, top_n=5)

for analysis in candidates:
    print(f"Move {analysis.move}: "
          f"X pattern={analysis.x_best_pattern.name}, "
          f"priority={analysis.priority_score}")
    
# Output:
# Move Move(row=9, col=7): X pattern=LIVE_2, priority=2.0
# Move Move(row=6, col=7): X pattern=LIVE_2, priority=2.0
# ...
```

---

## 3. GameHistory & GameStats (`game/history.py`)

Track lịch sử game, replay, export/import.

### MoveRecord (Dataclass)

```python
@dataclass
class MoveRecord:
    move_number: int        # 1, 2, 3, ...
    player: int             # PLAYER_X hoặc PLAYER_O
    move: Move
    timestamp: float = 0.0
    board_state: GameState = None  # State sau move
```

### GameHistory

```python
history = GameHistory()

# Ghi lại nước đi
history.record_move(PLAYER_X, Move(7, 7), engine.state, timestamp=123.45)

# Lấy thông tin
count = history.get_move_count()
last_move = history.get_last_move()
moves_x = history.get_moves_by_player(PLAYER_X)

# Export/Import game
pgn_string = history.to_pgn_string()
# Output: "1. X(7,7) O(7,8) 2. X(8,7) O(8,8) ..."

history.from_pgn_string(pgn_string, engine)

# Replay game đến move nào đó
history.replay_to_move(move_index=5, engine=engine)
```

### GameStats

```python
stats = GameStats()
stats.update(history, duration=45.3)

print(stats)
# Output: "Total moves: 20, X: 10, O: 10, Duration: 45.30s"
```

---

## 4. Cách Sử Dụng Cho AI

### Ví dụ: Simple Winning AI

```python
from ai.base import AIPlayer
from game.pattern import PatternAnalyzer
from game.board_analyzer import BoardAnalyzer
from game.constants import PLAYER_X

class SmartAI(AIPlayer):
    @property
    def name(self):
        return "Smart AI"
    
    def choose_move(self, state):
        valid_moves = state.get_valid_moves()
        
        # 1. Check winning move
        winning = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            PLAYER_X
        )
        if winning:
            return winning[0]
        
        # 2. Check opponent winning move & block
        threats = PatternAnalyzer.find_threats(
            state.board,
            valid_moves,
            PLAYER_O  # Opponent
        )
        if threats:
            return next(iter(threats.values()))[0]
        
        # 3. Otherwise play best candidate
        candidates = BoardAnalyzer.get_candidate_analysis(
            state.board,
            top_n=5
        )
        return candidates[0].move if candidates else valid_moves[0]
```

---

## API Summary

| Class/Function | Purpose | Returns |
|---|---|---|
| `PatternAnalyzer.analyze_move()` | Phân tích 1 nước → 4 directions | `list[LineInfo]` |
| `PatternAnalyzer.find_winning_moves()` | Tìm nước chiến thắng | `list[Move]` |
| `PatternAnalyzer.find_threats()` | Nhóm threats by level | `dict[PatternType, list[Move]]` |
| `BoardAnalyzer.analyze_cell()` | Chi tiết 1 ô | `CellAnalysis` |
| `BoardAnalyzer.get_candidate_analysis()` | Top candidates + scores | `list[CellAnalysis]` |
| `BoardAnalyzer.get_critical_cells()` | Ô cần block/attack | `list[Move]` |
| `BoardAnalyzer.get_board_heatmap()` | Priority heatmap | `list[list[float]]` |
| `GameHistory.record_move()` | Ghi lại nước đi | - |
| `GameHistory.to_pgn_string()` | Export lịch sử | `str` |
| `GameHistory.from_pgn_string()` | Import & replay | `bool` |

---

## Notes

- PatternAnalyzer chỉ phân loại patterns, không có heuristic scoring
- BoardAnalyzer có simple priority scoring (có thể override trong AI)
- Tất cả helper functions đều non-destructive (không thay đổi state)
- Dùng `board.clone()` & `state.clone()` để tạo copy riêng
