# 📚 Tài Liệu Phát Triển AI - Caro Game

## Tóm Tắt

Dự án Caro AI cung cấp một framework hoàn chỉnh để phát triển AI players. Tài liệu này tóm tắt các resources có sẵn:

### 📖 Tài Liệu Chính

| Tài Liệu | Mục Đích | Đọc Khi |
|---------|---------|--------|
| **AI_DEVELOPMENT_GUIDE.md** | Hướng dẫn chi tiết phát triển AI | Muốn tạo AI mới |
| **HELPERS.md** | API reference cho helper functions | Cần biết có function nào hỗ trợ |
| **README_ARCHITECTURE.md** | Cấu trúc game & project | Muốn hiểu codebase |

---

## 🚀 Quick Start (3 Bước)

### 1. Tạo File AI

Tạo file `src/plugins/my_ai.py`:

```python
from ai.base import AIPlayer
from game.move import Move

class MyAI(AIPlayer):
    @property
    def name(self):
        return "My AI"
    
    def choose_move(self, state):
        return state.get_valid_moves()[0]
```

### 2. Game Tự Load

Run `main.py` → AI xuất hiện trong menu!

### 3. Test

Chọn "My AI" từ menu → Play!

---

## 📁 Cấu Trúc Project

```
Caro_AI/
├── src/
│   ├── game/
│   │   ├── board.py           # Board logic
│   │   ├── game_state.py      # Game state + state queries
│   │   ├── game_engine.py     # Move validation, winner check
│   │   ├── game_manager.py    # Game coordinator
│   │   ├── move.py            # Move dataclass
│   │   ├── constants.py       # Constants (BOARD_SIZE, etc.)
│   │   ├── pattern.py         # ✨ NEW: Pattern detection
│   │   ├── board_analyzer.py  # ✨ NEW: Board analysis
│   │   └── history.py         # ✨ NEW: Game history tracking
│   ├── ai/
│   │   ├── base.py            # AIPlayer base class
│   │   ├── human_player.py    # Human player
│   │   ├── player_factory.py  # Create player by name
│   │   └── loader.py          # ✅ FIXED: Load plugins
│   ├── plugins/
│   │   ├── random_ai.py       # Random AI example
│   │   ├── greedy_ai.py       # ✨ NEW: Greedy AI example
│   │   └── __init__.py        # ✨ NEW: Package marker
│   ├── ui/
│   │   ├── board_view.py      # Board rendering
│   │   └── menu_screen.py     # Menu UI
│   └── main.py                # Game entry point
├── AI_DEVELOPMENT_GUIDE.md    # ✨ NEW: Full AI dev guide
├── HELPERS.md                 # ✨ NEW: Helper API reference
└── requirements.txt
```

---

## 🎯 Các Loại AI Có Thể Tạo

| Loại | Độ Khó | Thời Gian | Lợi Thế |
|------|--------|----------|--------|
| **Random** | ⭐ | 5 min | Đơn giản, base line |
| **Greedy** | ⭐⭐ | 30 min | Detect win/threat, prioritize |
| **Minimax** | ⭐⭐⭐ | 2h | Optimal search, alpha-beta |
| **MCTS** | ⭐⭐⭐⭐ | 4h | Strong play, flexible |
| **Deep Learning** | ⭐⭐⭐⭐⭐ | 1d+ | Powerful, complex |

---

## 🔧 API Cheat Sheet

### Game State

```python
state.get_valid_moves()           # list[Move]
state.get_candidate_moves(dist=2) # list[Move] (optimized)
state.get_opponent()              # int (PLAYER_X/O)
state.clone()                     # GameState copy
state.simulate_move(move)         # GameState after move
state.piece_count()               # int
state.is_terminal()               # bool
```

### Pattern Detection

```python
PatternAnalyzer.analyze_move(board, move, player)
# → list[LineInfo] (4 directions)

PatternAnalyzer.find_winning_moves(board, moves, player)
# → list[Move]

PatternAnalyzer.find_threats(board, moves, opponent)
# → dict[PatternType, list[Move]]
```

### Board Analysis

```python
BoardAnalyzer.analyze_cell(board, move)
# → CellAnalysis (x_pattern, o_pattern, priority_score)

BoardAnalyzer.get_candidate_analysis(board, top_n=10)
# → list[CellAnalysis] (sorted by priority)

BoardAnalyzer.get_critical_cells(board, player)
# → list[Move] (need to block/attack)
```

---

## 📊 Constants & Enums

```python
# Players
PLAYER_X = 1
PLAYER_O = 2
EMPTY = 0

# Board
BOARD_SIZE = 15
WIN_LENGTH = 5

# Patterns (from PatternAnalyzer)
PatternType.WINNING     # 5 liên tiếp
PatternType.OPEN_4      # 4 mở 2 mặt (44)
PatternType.DEAD_4      # 4 bị chặn (444)
PatternType.LIVE_3      # 3 mở 2 mặt (33)
PatternType.LIVE_2      # 2 mở 2 mặt (22)
PatternType.BLOCKED_3   # 3 bị chặn
PatternType.THREAT_4    # 2 cách tạo 4
PatternType.THREAT_3    # 2 cách tạo 3
```

---

## 💡 Ví Dụ Nhanh

### Ví Dụ 1: Check Win & Block

```python
def choose_move(self, state):
    # Win if possible
    winning = PatternAnalyzer.find_winning_moves(
        state.board,
        state.get_valid_moves(),
        state.current_player
    )
    if winning:
        return winning[0]
    
    # Block opponent
    opponent_threats = PatternAnalyzer.find_threats(
        state.board,
        state.get_valid_moves(),
        state.get_opponent()
    )
    if opponent_threats:
        return next(iter(opponent_threats.values()))[0]
    
    # Play best
    return state.get_valid_moves()[0]
```

### Ví Dụ 2: Ranked Candidates

```python
def choose_move(self, state):
    candidates = BoardAnalyzer.get_candidate_analysis(
        state.board,
        distance=2,
        top_n=5
    )
    
    # Candidates sorted by priority_score
    best = candidates[0].move if candidates else state.get_valid_moves()[0]
    return best
```

---

## ⚙️ Bug Fixes & Improvements

### ✅ Fixed
- ❌ Loader không load plugins → ✅ Fixed path logic
- ❌ Plugins folder không là package → ✅ Added `__init__.py`

### ✨ New Features
- Pattern detection (PatternAnalyzer)
- Board analysis (BoardAnalyzer)
- Game history tracking (GameHistory)
- GreedyAI example
- Comprehensive dev guide

---

## 📋 Checklist Khi Tạo AI

- [ ] Tạo file trong `src/plugins/`
- [ ] Inherit từ `AIPlayer`
- [ ] Implement `name` property
- [ ] Implement `choose_move()` method
- [ ] Return `Move` object (không phải tuple)
- [ ] Return valid move (ô trống)
- [ ] Test bằng cách run game

---

## 🔗 Linked Documentation

| Link | Purpose |
|------|---------|
| `AI_DEVELOPMENT_GUIDE.md` | Full guide with GreedyAI example |
| `README_ARCHITECTURE.md` | Game architecture & flow |
| `HELPERS.md` | Helper functions API reference |
| `src/game/pattern.py` | Pattern detection source |
| `src/game/board_analyzer.py` | Board analysis source |
| `src/plugins/greedy_ai.py` | Example AI implementation (template) |

---

## ❓ FAQs

**Q: Cách nào để AI load được?**
A: File trong `src/plugins/`, inherit `AIPlayer`, implement `name` & `choose_move()`

**Q: Làm sao optimize AI?**
A: Dùng `get_candidate_moves()` thay vì `get_valid_moves()`

**Q: Pattern type nào quan trọng nhất?**
A: OPEN_4 (4 liên tiếp mở 2 mặt) = rất nguy hiểm, nên block ngay

**Q: Có thể modify state trong choose_move()?**
A: Không, nó là clone. Modify không ảnh hưởng game.

**Q: Performance limit?**
A: ~1 second per move (có delay để user thấy)

---

## 🎓 Learning Path

1. **First**: Read `README_ARCHITECTURE.md` để hiểu game hoạt động
2. **Second**: Read `AI_DEVELOPMENT_GUIDE.md` (Quick Start + API sections)
3. **Third**: Copy `GreedyAI` từ `src/plugins/greedy_ai.py` làm template
4. **Then**: Implement AI của bạn!
5. **Next Level**: Read HELPERS.md chi tiết, implement Minimax/MCTS

---

## 🚀 Next Steps

1. Đọc **AI_DEVELOPMENT_GUIDE.md** cho full details
2. Xem **HELPERS.md** cho API reference
3. Copy GreedyAI từ `src/plugins/greedy_ai.py` làm template
4. Implement AI của bạn!

**Good luck! 🎯**
