# 📖 Hướng Dẫn Phát Triển AI cho Caro Game

*Tài liệu này dành cho các developer (hoặc AI agents) muốn tạo AI players cho game Caro.*

---

## 📋 Mục Lục

1. [Quick Start](#quick-start)
2. [Cấu Trúc Game](#cấu-trúc-game)
3. [Tạo AI - Base Class](#tạo-ai---base-class)
4. [Game State & API](#game-state--api)
5. [Helper Functions](#helper-functions)
6. [Ví Dụ Thực Tế](#ví-dụ-thực-tế)
7. [Best Practices & Tips](#best-practices--tips)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1️⃣ Tạo file AI mới

Tạo file trong `src/plugins/` folder:

```python
# src/plugins/my_first_ai.py

import random
from ai.base import AIPlayer
from game.move import Move

class MyFirstAI(AIPlayer):
    
    @property
    def name(self):
        return "My First AI"
    
    def choose_move(self, state):
        """AI logic: choose a move"""
        valid_moves = state.get_valid_moves()
        return random.choice(valid_moves)
```

### 2️⃣ Game sẽ tự load AI này!

AI sẽ tự động xuất hiện trong menu. Không cần thêm bất cứ gì nữa!

```
Why? → src/ai/loader.py tự động scan plugins/ folder
```

### 3️⃣ Test AI

Run game, chọn "My First AI" từ menu → Play!

---

## Cấu Trúc Game

### Board & Constants

```python
# src/game/constants.py
BOARD_SIZE = 15          # 15x15 board
WIN_LENGTH = 5           # 5 liên tiếp = win
EMPTY = 0
PLAYER_X = 1             # Human hoặc X AI
PLAYER_O = 2             # Human hoặc O AI
```

### Game Concepts

| Term | Meaning |
|------|---------|
| **Player** | PLAYER_X (1) hoặc PLAYER_O (2) |
| **Move** | Tuple (row, col) từ 0-14 |
| **Board** | 15x15 grid, mỗi ô = EMPTY/PLAYER_X/PLAYER_O |
| **Game State** | Snapshot: board, current player, winner, game_over |
| **Turn** | 1 player chọn 1 move → board update |

---

## Tạo AI - Base Class

### 1. Kế Thừa AIPlayer

```python
from ai.base import AIPlayer
from game.move import Move

class MyAI(AIPlayer):
    
    @property
    def name(self) -> str:
        """Tên AI hiển thị trong menu"""
        return "My Smart AI v1.0"
    
    def choose_move(self, state) -> Move:
        """
        Main AI logic.
        Input: GameState object
        Output: Move(row, col) object
        
        IMPORTANT: Hàm này được gọi với state.clone()
                   → Thay đổi state không ảnh hưởng game thực
        """
        pass
```

### 2. Properties (Tự động từ base class)

```python
@property
def is_human(self) -> bool:
    return False  # AI sẽ tự động return False
```

### 3. Quy Tắc

- **PHẢI** trả về `Move` object (không phải tuple)
- **PHẢI** return valid move (ô trống, valid position)
- **Có thể** raise exception nếu không có valid move
- **KHÔNG** được modify `state` (nó là clone)
- **Có thể** mất tối đa ~1 second per move (game có delay)

---

## Game State & API

### GameState Object

```python
class GameState:
    board: Board              # Board object
    current_player: int       # PLAYER_X hoặc PLAYER_O
    winner: int | None        # Người thắng (None nếu chưa end)
    game_over: bool           # Game đã kết thúc?
    last_move: Move | None    # Nước đi trước đó
```

### Các Methods Có Sẵn

#### 1. Board Access

```python
# Lấy giá trị ô (row, col)
cell_value = state.get_cell(row, col)
# Returns: EMPTY (0) / PLAYER_X (1) / PLAYER_O (2)

# Lấy toàn bộ board (copy)
grid = state.get_grid()  # list[list[int]]
```

#### 2. Move Generation

```python
# Tất cả ô trống
valid_moves = state.get_valid_moves()
# Returns: list[Move]

# Ô gần các quân đã đi (tối ưu cho minimax)
# distance=2 = tìm ô trong bán kính 2 từ quân
candidate_moves = state.get_candidate_moves(distance=2)
# Returns: list[Move] (ít hơn valid_moves, tối ưu hơn)
```

#### 3. Game Query

```python
# Opponent player
opponent = state.get_opponent()
# Returns: PLAYER_X hoặc PLAYER_O

# Số quân trên board
piece_count = state.piece_count()

# Kiểm tra game over?
if state.is_terminal():
    print("Game đã kết thúc")

# Clone state (tạo copy riêng để test)
new_state = state.clone()
```

#### 4. Simulation (Dự Phỏng Nước Đi)

```python
# Simulate move mà không modify state gốc
new_state = state.simulate_move(Move(7, 7))

# new_state = state sau khi move này được apply
# state gốc không thay đổi
```

### Board Object

```python
board = state.board

# Kiểm tra ô
is_empty = board.is_empty(row, col)  # True/False
is_valid = board.is_valid_position(row, col)  # True/False
cell = board.get_cell(row, col)  # EMPTY/PLAYER_X/PLAYER_O

# Place piece (thường không dùng - dùng GameEngine thay)
board.place_piece(row, col, player)

# Clone board
new_board = board.clone()
```

---

## Helper Functions

### 📊 PatternAnalyzer - Phát Hiện Patterns

```python
from game.pattern import PatternAnalyzer, PatternType

# ============================================================
# 1. ANALYZE MOVE - Phân tích 1 nước
# ============================================================

lines = PatternAnalyzer.analyze_move(board, Move(7, 7), PLAYER_X)
# Returns: list[LineInfo] - 4 directions (ngang/dọc/2 chéo)
# Sắp xếp theo piece_count (cao nhất trước)

for line in lines:
    print(f"Direction: {line.direction}")
    print(f"Pieces: {line.piece_count}")
    print(f"Empty left: {line.empty_left}")
    print(f"Empty right: {line.empty_right}")
    print(f"Pattern: {line.pattern.name}")
    # Pattern: WINNING / OPEN_4 / DEAD_4 / LIVE_3 / LIVE_2 / ...

# ============================================================
# 2. FIND WINNING MOVES - Tìm nước chiến thắng
# ============================================================

winning_moves = PatternAnalyzer.find_winning_moves(
    state.board,
    valid_moves,
    PLAYER_X
)

if winning_moves:
    return winning_moves[0]  # Play winning move!

# ============================================================
# 3. FIND THREATS - Phát hiện threat levels
# ============================================================

threats = PatternAnalyzer.find_threats(
    state.board,
    valid_moves,
    PLAYER_O  # Opponent
)

# Returns: dict[PatternType, list[Move]]
# {
#     PatternType.OPEN_4: [Move(...), ...],  # Opponent 4 mở 2 mặt
#     PatternType.LIVE_3: [Move(...), ...],  # Opponent 3 mở 2 mặt
# }

# Block most dangerous
if PatternType.OPEN_4 in threats:
    return threats[PatternType.OPEN_4][0]  # Block OPEN_4!
elif PatternType.LIVE_3 in threats:
    return threats[PatternType.LIVE_3][0]  # Block LIVE_3
```

### 🎯 BoardAnalyzer - Phân Tích Toàn Board

```python
from game.board_analyzer import BoardAnalyzer

# ============================================================
# 1. ANALYZE CELL - Chi tiết 1 ô
# ============================================================

analysis = BoardAnalyzer.analyze_cell(state.board, Move(7, 7))

# Returns: CellAnalysis
# - analysis.x_best_pattern = best pattern nếu X đặt ở đây
# - analysis.o_best_pattern = best pattern nếu O đặt ở đây
# - analysis.priority_score = mức độ ưu tiên (0-100)

print(f"Priority: {analysis.priority_score}")
print(f"If X plays: {analysis.x_best_pattern}")
print(f"If O plays: {analysis.o_best_pattern}")

# ============================================================
# 2. GET CANDIDATE ANALYSIS - Top candidates
# ============================================================

candidates = BoardAnalyzer.get_candidate_analysis(
    state.board,
    distance=2,    # Chỉ ô trong bán kính 2 từ quân
    top_n=10       # Top 10 candidates
)

# Returns: list[CellAnalysis] sắp xếp theo priority (cao → thấp)

for i, cand in enumerate(candidates):
    print(f"{i+1}. Move {cand.move}: priority={cand.priority_score}")

# Lấy best candidate
if candidates:
    best_move = candidates[0].move

# ============================================================
# 3. GET CRITICAL CELLS - Ô cần phải xem
# ============================================================

critical = BoardAnalyzer.get_critical_cells(state.board, PLAYER_X)

# Returns: list[Move] - những ô có HIGH-PRIORITY patterns
# (OPEN_4, DEAD_4, LIVE_3, THREAT_4)

# Hữu ích cho alpha-beta pruning hoặc iterative deepening

# ============================================================
# 4. GET BOARD HEATMAP - Visualize
# ============================================================

heatmap = BoardAnalyzer.get_board_heatmap(state.board, PLAYER_X)

# Returns: list[list[float]] (15x15)
# - Giá trị = priority score
# - -1.0 = ô đã có quân
# - Dùng để debug/visualize strategy
```

### 📜 GameHistory - Track Game

```python
from game.history import GameHistory, GameStats

history = GameHistory()

# Ghi lại move (khi AI play)
history.record_move(
    player=PLAYER_X,
    move=Move(7, 7),
    board_state=state,
    timestamp=time.time()
)

# Xem lịch sử
move_count = history.get_move_count()
last_move = history.get_last_move()
x_moves = history.get_moves_by_player(PLAYER_X)

# Export game
pgn = history.to_pgn_string()
# Output: "1. X(7,7) O(7,8) 2. X(8,7) ..."

# Replay game
history.from_pgn_string(pgn, engine)
history.replay_to_move(move_index=5, engine=engine)
```

---

## Ví Dụ Thực Tế

### ✅ Ví Dụ 1: Simple Greedy AI

```python
from ai.base import AIPlayer
from game.move import Move
from game.pattern import PatternAnalyzer, PatternType
from game.board_analyzer import BoardAnalyzer
from game.constants import PLAYER_X, PLAYER_O

class GreedyAI(AIPlayer):
    
    @property
    def name(self):
        return "Greedy AI"
    
    def choose_move(self, state):
        """
        Strategy:
        1. Win if possible
        2. Block opponent if needed
        3. Play best candidate
        """
        valid_moves = state.get_valid_moves()
        
        # 1. Check if we can win
        winning = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            state.current_player
        )
        if winning:
            return winning[0]
        
        # 2. Check if opponent can win next move
        threats = PatternAnalyzer.find_threats(
            state.board,
            valid_moves,
            state.get_opponent()
        )
        
        # Priority order: block OPEN_4 > DEAD_4 > LIVE_3
        if PatternType.OPEN_4 in threats:
            return threats[PatternType.OPEN_4][0]
        elif PatternType.DEAD_4 in threats:
            return threats[PatternType.DEAD_4][0]
        elif PatternType.LIVE_3 in threats:
            return threats[PatternType.LIVE_3][0]
        
        # 3. Play best candidate
        candidates = BoardAnalyzer.get_candidate_analysis(
            state.board,
            top_n=1
        )
        return candidates[0].move if candidates else valid_moves[0]
```

### 🎓 Ví Dụ 2+: Minimax & MCTS

Ngoài **Greedy AI**, bạn có thể implement các thuật toán advanced:

- **Minimax with Alpha-Beta Pruning**: Tìm best move bằng tree search
  - Implement: Recursively evaluate moves, prune branches
  - Use: `state.get_candidate_moves(distance=2)` để optimize
  - Evaluate: Heuristic scoring (win/threat/pattern value)

- **Monte Carlo Tree Search (MCTS)**: Playout-based search
  - Implement: Selection → Expansion → Simulation → Backup
  - Use: Time-limited iterations (0.5s per move)
  - Evaluate: Win/loss from playouts (random simulations)

- **Iterative Deepening**: Depth-first search with increasing depth
  - Implement: Loop with depth 1→2→3... until time limit
  - Use: `get_critical_cells()` để prioritize moves
  - Evaluate: Return best move found at time limit

**Tips**:
- Start with heuristic evaluation (pattern scoring)
- Use `get_candidate_moves()` để giảm branching factor
- Add time/depth limits để avoid timeout
- Test against GreedyAI để measure improvement

Xem HELPERS.md & game state API để code!

---

---

## Best Practices & Tips

### ✅ DO's

- ✅ **Use `state.clone()`** trước khi test moves
- ✅ **Use `get_candidate_moves()`** thay vì `get_valid_moves()` để tối ưu
- ✅ **Check winning moves** trước khi explore nodes
- ✅ **Use PatternAnalyzer** để phát hiện threats nhanh
- ✅ **Handle edge cases**: empty board, full board, near end
- ✅ **Test với print statements** khi debug
- ✅ **Return Move object** (không phải tuple)

### ❌ DON'Ts

- ❌ **Modify state** (nó là clone, nhưng không modify anyway)
- ❌ **Infinite loops** (check depth/time limit)
- ❌ **Return invalid moves** (game sẽ crash)
- ❌ **Assume pattern is already there** (check board state)
- ❌ **Hardcode player number** (dùng constants PLAYER_X/O)
- ❌ **Return tuple** - PHẢI là Move object

### 💡 Performance Tips

```python
# ❌ SLOW - Duyệt toàn 225 ô
for row in range(15):
    for col in range(15):
        if state.get_cell(row, col) == EMPTY:
            # ...

# ✅ FAST - Chỉ ~20 ô gần quân đã đi
candidate_moves = state.get_candidate_moves(distance=2)
for move in candidate_moves:
    # ...

# ❌ SLOW - Evaluate mỗi node riêng
for move in all_moves:
    score = expensive_evaluation(move)

# ✅ FAST - Sort candidates by priority
candidates = BoardAnalyzer.get_candidate_analysis(
    board,
    top_n=10  # Chỉ evaluate top 10
)
```

### 🔍 Debugging

```python
# Print board state
print(state.board.grid)

# Print candidate moves
candidates = BoardAnalyzer.get_candidate_analysis(state.board, top_n=5)
for cand in candidates:
    print(f"Move: {cand.move}, Priority: {cand.priority_score}")

# Check patterns
lines = PatternAnalyzer.analyze_move(state.board, move, player)
for line in lines:
    print(f"{line.direction}: {line.piece_count} pieces, pattern={line.pattern}")

# Track AI thinking
import time
start = time.time()
move = ai.choose_move(state)
elapsed = time.time() - start
print(f"AI thought for {elapsed:.3f}s")
```

---

## Troubleshooting

### ❓ "ModuleNotFoundError: No module named 'game'"

**Problem**: Import statement sai
```python
# ❌ WRONG
from src.game.move import Move

# ✅ CORRECT (run từ src/ folder)
from game.move import Move
```

### ❓ "AI không xuất hiện trong menu"

**Checklist**:
1. ✅ File trong `src/plugins/` folder?
2. ✅ Class inherit từ `AIPlayer`?
3. ✅ Implement `name` property?
4. ✅ Implement `choose_move()` method?

```python
# ✅ CORRECT FORMAT
from ai.base import AIPlayer

class MyAI(AIPlayer):
    @property
    def name(self):
        return "My AI"
    
    def choose_move(self, state):
        return state.get_valid_moves()[0]
```

### ❓ "Game freeze / infinite loop"

**Solution**: Add depth/time limit

```python
# Set depth limit for minimax
def _minimax(self, state, depth, ...):
    if depth == 0:  # <-- Add this!
        return self._evaluate(state), None
```

### ❓ "Move is not valid" / "Move already played"

**Problem**: Trả về move không valid

```python
# ❌ WRONG
move = Move(0, 0)  # Nếu ô (0,0) đã có quân → invalid!

# ✅ CORRECT
valid_moves = state.get_valid_moves()
move = valid_moves[0]  # Guaranteed valid
```

### ❓ "State modified unexpectedly"

**Problem**: Quên clone state

```python
# ❌ WRONG
new_state = state  # Shallow copy!
new_state.board.place_piece(...)  # Modifies original!

# ✅ CORRECT
new_state = state.clone()  # Deep copy
new_state = state.simulate_move(move)  # Already cloned
```

---

## 📚 Quick Reference

### Imports

```python
from ai.base import AIPlayer
from game.move import Move
from game.constants import PLAYER_X, PLAYER_O, EMPTY, BOARD_SIZE
from game.pattern import PatternAnalyzer, PatternType
from game.board_analyzer import BoardAnalyzer
from game.history import GameHistory
```

### Constants

```python
PLAYER_X = 1
PLAYER_O = 2
EMPTY = 0
BOARD_SIZE = 15
WIN_LENGTH = 5
```

### Key Methods

| Method | Input | Output | Use Case |
|--------|-------|--------|----------|
| `state.get_valid_moves()` | - | `list[Move]` | All empty cells |
| `state.get_candidate_moves(distance)` | int | `list[Move]` | Optimized search |
| `state.get_opponent()` | - | int | Get opponent player |
| `state.clone()` | - | GameState | Safe copy |
| `state.simulate_move(move)` | Move | GameState | Test move |
| `PatternAnalyzer.analyze_move()` | board, move, player | `list[LineInfo]` | Analyze move patterns |
| `PatternAnalyzer.find_winning_moves()` | board, moves, player | `list[Move]` | Find win moves |
| `PatternAnalyzer.find_threats()` | board, moves, player | `dict[PatternType, list[Move]]` | Find threats |
| `BoardAnalyzer.get_candidate_analysis()` | board, distance, top_n | `list[CellAnalysis]` | Ranked candidates |
| `BoardAnalyzer.get_critical_cells()` | board, player | `list[Move]` | Important moves |

---

## 🎯 Next Steps

1. **Start simple**: Implement Greedy AI (Example 1)
2. **Add evaluation**: Implement heuristic scoring
3. **Add search**: Implement minimax or MCTS
4. **Optimize**: Use alpha-beta pruning, iterative deepening
5. **Evaluate**: Play against other AIs, measure win rate

Good luck! 🚀
