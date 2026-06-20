# Helper Functions & Classes cho Phát Triển AI

Dự án Caro AI cung cấp các helper classes để hỗ trợ viết AI: đọc board, phân tích pattern, tìm nước thắng, tìm threat, xếp hạng candidate moves và debug heuristic.

Tài liệu này giữ format ngắn gọn của `HELPERS.md`, nhưng cập nhật theo logic hiện tại trong `src/game/pattern.py` và `src/game/board_analyzer.py`.

---

## 1. PatternAnalyzer (`game/pattern.py`)

Phát hiện và phân loại pattern nếu một player đặt quân vào một ô trống.

`PatternAnalyzer` không chấm điểm tổng thể board. Nó chỉ trả về pattern theo từng hướng và các helper tìm threat/thắng ngay.

### PatternType (Enum)

Thứ tự enum cũng là thứ tự ưu tiên pattern:

- **WINNING**: Có chuỗi 5 quân liên tiếp thật sự (`XXXXX`).
- **OPEN_4**: 4 quân liên tiếp, mở 2 đầu (`_XXXX_`).
- **THREAT_4**: 4 threat đang gay, có thể tạo áp lực 4/5 nhưng không phải 4 liên tiếp mở 2 đầu (`XX_XX`, `X_XXX`, `XXX_X`).
- **DEAD_4**: 4 quân liên tiếp, bị chặn 1 đầu (`OXXXX_` hoặc `_XXXXO`).
- **LIVE_3**: 3 quân liên tiếp, mở 2 đầu (`_XXX_`).
- **THREAT_3**: 3 threat đang gay (`_XX_X_`, `_X_XX_`, `X_X` trong vùng có thể phát triển).
- **BLOCKED_3**: 3 quân liên tiếp, bị chặn 1 đầu.
- **LIVE_2**: 2 quân liên tiếp, mở 2 đầu.
- **NONE**: Không có threat đáng kể.

### Điểm quan trọng

`WINNING` chỉ được tính khi có 5 quân liên tiếp:

```text
XXXXX   -> WINNING
XXXX_X  -> không phải WINNING
```

4 quân bị chặn cả 2 đầu không còn được tính là `DEAD_4`:

```text
XOOO_X  -> O đánh vào gap thành XOOOOX -> NONE
XOOO__  -> O đánh vào gap thành XOOOO_ -> DEAD_4
_OOO__  -> O đánh vào gap thành _OOOO_ -> OPEN_4
```

### LineInfo (Dataclass)

```python
@dataclass
class LineInfo:
    direction: tuple        # (dr, dc)
    piece_count: int        # Số quân liên tiếp quanh move sau khi đặt
    empty_left: int         # 1 nếu đầu âm còn trống, ngược lại 0
    empty_right: int        # 1 nếu đầu dương còn trống, ngược lại 0
    player: int             # PLAYER_X hoặc PLAYER_O
    pattern: PatternType    # Pattern tốt nhất của hướng đó
```

`piece_count`, `empty_left`, `empty_right` vẫn là thông tin dạng liên tiếp. `pattern` có thể được nâng lên bởi logic line-string để bắt pattern gay.

### Các phương thức

```python
# Lấy thông tin pattern theo 1 hướng.
line_info = PatternAnalyzer.get_line_info(
    board,
    row,
    col,
    direction,
    player
)

# Phân tích 1 nước đi theo 4 hướng.
lines = PatternAnalyzer.analyze_move(
    board,
    move,
    player
)

# Tìm tất cả nước thắng ngay.
winning_moves = PatternAnalyzer.find_winning_moves(
    board,
    valid_moves,
    player
)

# Nhóm các nước tạo threat theo PatternType tốt nhất.
threats = PatternAnalyzer.find_threats(
    board,
    valid_moves,
    player
)
```

### Lưu ý về `analyze_move`

- Chỉ phân tích ô hợp lệ và đang trống.
- Nếu move nằm ngoài bàn hoặc ô đã có quân, hàm trả về `[]`.
- Hàm clone board nội bộ, không làm thay đổi board gốc.
- Kết quả `lines` được sort giảm dần theo `(pattern, piece_count)`.

### Ví dụ

```python
from game.board import Board
from game.move import Move
from game.pattern import PatternAnalyzer, PatternType
from game.constants import PLAYER_X

board = Board()
board.place_piece(7, 7, PLAYER_X)
board.place_piece(7, 8, PLAYER_X)
board.place_piece(7, 9, PLAYER_X)

lines = PatternAnalyzer.analyze_move(
    board,
    Move(7, 10),
    PLAYER_X
)

print(lines[0].pattern == PatternType.OPEN_4)  # True
print(lines[0].piece_count)                    # 4
```

---

## 2. BoardAnalyzer (`game/board_analyzer.py`)

Phân tích các ô trống trên board: nếu X/O đặt vào đó sẽ tạo pattern nào, score bao nhiêu, và move nào nên được ưu tiên.

### CellAnalysis (Dataclass)

```python
@dataclass
class CellAnalysis:
    move: Move

    # Nếu X đánh vào đây
    x_lines: list[LineInfo]
    x_best_pattern: PatternType
    x_score: float

    # Nếu O đánh vào đây
    o_lines: list[LineInfo]
    o_best_pattern: PatternType
    o_score: float

    # Dùng để ranking candidate
    priority_score: float = 0.0
```

`priority_score = max(x_score, o_score)`, nên nó biểu diễn độ quan trọng tổng quát của ô đó cho cả attack và defense.

### Pattern score

```python
WINNING    = 1_000_000
OPEN_4     = 100_000
THREAT_4   = 80_000
DEAD_4     = 30_000
LIVE_3     = 10_000
THREAT_3   = 8_000
BLOCKED_3  = 3_000
LIVE_2     = 500
NONE       = 0
```

### Fork bonus

BoardAnalyzer cộng thêm điểm khi một move tạo nhiều threat:

```python
DOUBLE_OPEN4_BONUS   = 500_000
DOUBLE_THREAT4_BONUS = 300_000
DOUBLE_DEAD4_BONUS   = 100_000
DOUBLE_LIVE3_BONUS   = 50_000
MIXED_THREE_BONUS    = 40_000   # LIVE_3 + THREAT_3
DOUBLE_THREAT3_BONUS = 30_000
```

Mục tiêu là nhận diện fork:

```text
LIVE_3 + LIVE_3
LIVE_3 + THREAT_3
THREAT_3 + THREAT_3
OPEN_4 + OPEN_4
THREAT_4 + THREAT_4
```

### Các phương thức

```python
# Phân tích 1 ô.
analysis = BoardAnalyzer.analyze_cell(
    board,
    move
)

# Lấy danh sách candidate gần các quân đã đánh.
candidates = BoardAnalyzer.get_candidate_analysis(
    board,
    distance=2,
    top_n=10
)

# Lấy các ô chiến thuật cần xem xét.
critical = BoardAnalyzer.get_critical_cells(
    board,
    player
)

# Lấy heatmap score cho toàn board.
heatmap = BoardAnalyzer.get_board_heatmap(
    board,
    PLAYER_X
)
```

### Critical cells

`get_critical_cells()` hiện xem các pattern sau là critical cho cả X và O:

```python
PatternType.WINNING
PatternType.OPEN_4
PatternType.THREAT_4
PatternType.DEAD_4
PatternType.LIVE_3
PatternType.THREAT_3
```

Dùng cho:

- tactical search
- quiescence search
- ưu tiên block/attack
- debug các ô nguy hiểm

### Ví dụ

```python
from game.board import Board
from game.move import Move
from game.constants import PLAYER_X
from game.board_analyzer import BoardAnalyzer

board = Board()
board.place_piece(7, 4, PLAYER_X)
board.place_piece(7, 6, PLAYER_X)
board.place_piece(6, 7, PLAYER_X)
board.place_piece(8, 7, PLAYER_X)

analysis = BoardAnalyzer.analyze_cell(
    board,
    Move(7, 7)
)

print(analysis.x_best_pattern.name)
print(analysis.x_score)  # Có bonus LIVE_3 + THREAT_3
```

---

## 3. GameHistory & GameStats (`game/history.py`)

Track lịch sử game, replay, export/import.

### MoveRecord (Dataclass)

```python
@dataclass
class MoveRecord:
    move_number: int
    player: int
    move: Move
    timestamp: float = 0.0
    board_state: GameState | None = None
```

### GameHistory

```python
history = GameHistory()

# Lưu state ban đầu để replay.
history.set_initial_state(engine.state)

# Ghi lại move sau khi engine đã apply move.
history.record_move(
    player=PLAYER_X,
    move=Move(7, 7),
    board_state=engine.state,
    timestamp=123.45
)

count = history.get_move_count()
last_move = history.get_last_move()
x_moves = history.get_moves_by_player(PLAYER_X)

pgn_string = history.to_pgn_string()

ok = history.from_pgn_string(
    pgn_string,
    engine
)

ok = history.replay_to_move(
    move_index=5,
    engine=engine
)
```

### GameStats

```python
stats = GameStats()
stats.update(history, duration=45.3)

print(stats)
```

---

## 4. Cách Sử Dụng Cho AI

### Greedy-style AI

```python
from ai.base import AIPlayer
from game.pattern import PatternAnalyzer
from game.board_analyzer import BoardAnalyzer

class SmartAI(AIPlayer):
    @property
    def name(self):
        return "Smart AI"

    def choose_move(self, state):
        valid_moves = state.get_valid_moves()
        current_player = state.current_player
        opponent = state.get_opponent()

        # 1. Thắng ngay nếu có.
        winning = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            current_player
        )
        if winning:
            return winning[0]

        # 2. Chặn đối thủ thắng ngay.
        opponent_wins = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            opponent
        )
        if opponent_wins:
            return opponent_wins[0]

        # 3. Chọn candidate có score cao nhất.
        candidates = BoardAnalyzer.get_candidate_analysis(
            state.board,
            distance=2,
            top_n=10
        )

        return candidates[0].move if candidates else valid_moves[0]
```

### Minimax / Alpha-Beta

Nên dùng helper theo 2 cách:

- `PatternAnalyzer.find_winning_moves()` trước khi search để bắt win/block ngay.
- `BoardAnalyzer.get_candidate_analysis()` để move ordering và cắt bớt branch factor.

Nếu AI có evaluation riêng, có thể dùng:

```python
analysis = BoardAnalyzer.analyze_cell(board, move)
score = analysis.x_score - analysis.o_score
```

---

## API Summary

| Class/Function | Purpose | Returns |
|---|---|---|
| `PatternAnalyzer.get_line_info()` | Phân tích 1 hướng tại 1 vị trí | `LineInfo` |
| `PatternAnalyzer.analyze_move()` | Phân tích 1 move theo 4 hướng | `list[LineInfo]` |
| `PatternAnalyzer.find_winning_moves()` | Tìm các move thắng ngay | `list[Move]` |
| `PatternAnalyzer.find_threats()` | Nhóm threat theo pattern tốt nhất | `dict[PatternType, list[Move]]` |
| `BoardAnalyzer.analyze_cell()` | Phân tích X/O nếu đánh vào 1 ô | `CellAnalysis` |
| `BoardAnalyzer.get_candidate_analysis()` | Candidate moves đã sort theo priority | `list[CellAnalysis]` |
| `BoardAnalyzer.get_critical_cells()` | Các ô chiến thuật cần xem xét | `list[Move]` |
| `BoardAnalyzer.get_board_heatmap()` | Heatmap priority score | `list[list[float]]` |
| `GameHistory.record_move()` | Ghi lại 1 move | `None` |
| `GameHistory.to_pgn_string()` | Export lịch sử | `str` |
| `GameHistory.from_pgn_string()` | Import và replay | `bool` |
| `GameHistory.replay_to_move()` | Replay đến move index | `bool` |

---

## Notes

- Helper functions không sửa board/state gốc.
- `analyze_move()` trả `[]` nếu move không hợp lệ hoặc ô không trống.
- `DEAD_4` chỉ có nghĩa là 4 liên tiếp bị chặn 1 đầu. Bị chặn 2 đầu là `NONE`.
- `WINNING` yêu cầu 5 quân liên tiếp thật sự.
- `BoardAnalyzer.get_board_heatmap(board, player)` hiện vẫn tính priority tổng quát bằng `max(x_score, o_score)`; tham số `player` chưa làm thay đổi cách chấm điểm.
- `PatternAnalyzer` đã hỗ trợ một số broken pattern, nhưng không thay thế evaluation function riêng cho AI mạnh.
