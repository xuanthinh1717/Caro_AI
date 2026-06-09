# 🏗️ Architecture Guide - Caro AI Framework

*Hiểu cách game hoạt động và cách AI tích hợp vào hệ thống.*

---

## 📋 Mục Lục

1. [High-Level Architecture](#high-level-architecture)
2. [Game Flow](#game-flow)
3. [Module Breakdown](#module-breakdown)
4. [Class Relationships](#class-relationships)
5. [Data Flow](#data-flow)
6. [AI Integration Points](#ai-integration-points)
7. [State Management](#state-management)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Game Loop)                   │
│  - Event handling (mouse, keyboard)                      │
│  - Update logic                                          │
│  - Rendering                                             │
└─────────┬───────────────────────────────────────┬────────┘
          │                                       │
    ┌─────▼──────────┐                  ┌────────▼────────┐
    │   MenuScreen   │                  │  GameManager    │
    │  (UI Layer)    │                  │ (Coordinator)   │
    └────────────────┘                  └────────┬────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────┐
                    │                            │                        │
            ┌───────▼──────┐          ┌─────────▼─────┐        ┌────────▼────────┐
            │ Player X     │          │  GameEngine   │        │  Player O       │
            │ (Human/AI)   │          │  (Rules)      │        │  (Human/AI)     │
            └───────┬──────┘          └────────┬──────┘        └────────┬────────┘
                    │                         │                        │
                    │      choose_move()      │      choose_move()      │
                    │                         │                        │
            ┌───────▼─────────────────────────▼─────────────────────────▼────┐
            │              GameState (State Management)                       │
            │  - board (Board object)                                        │
            │  - current_player (PLAYER_X / PLAYER_O)                       │
            │  - winner (player / None)                                     │
            │  - game_over (bool)                                           │
            └───────┬──────────────────────────────────────────────────────┘
                    │
                    │ clone() / simulate_move()
                    │
            ┌───────▼────────────────────────────────┐
            │   Helper Classes (AI Support)          │
            │  - PatternAnalyzer                     │
            │  - BoardAnalyzer                       │
            │  - GameHistory                         │
            └────────────────────────────────────────┘
```

---

## Game Flow

### 1️⃣ **Initialization (main.py)**

```
Start Game
    ↓
Initialize Pygame
    ↓
Show Menu
    ↓
Select Players (X and O)
    ↓
Create GameManager with player names
    ↓
Game State: MENU → GAME
```

### 2️⃣ **Game Loop (Every Frame)**

```
┌─────────────────────────────────┐
│  while running:                 │
│    ┌──────────────────────────┐ │
│    │ EVENT HANDLING           │ │
│    │ - Mouse clicks (Human)   │ │
│    │ - Keyboard (R/M)         │ │
│    └──────────────────────────┘ │
│              │                  │
│    ┌─────────▼──────────────────┐ │
│    │ GAME UPDATE               │ │
│    │ if not game_over:         │ │
│    │   if current is AI:       │ │
│    │     move = AI.choose()    │ │
│    │     apply move            │ │
│    └──────────────────────────┘ │
│              │                  │
│    ┌─────────▼──────────────────┐ │
│    │ RENDER                    │ │
│    │ - Draw board              │ │
│    │ - Draw pieces             │ │
│    │ - Draw info               │ │
│    └──────────────────────────┘ │
│              │                  │
│    tick(60) - 60 FPS            │
└─────────────────────────────────┘
```

### 3️⃣ **Move Execution**

```
Player chooses Move(row, col)
    ↓
GameEngine.make_move(move)
    ↓
Board.place_piece(row, col, player)
    ↓
Check Winner:
  - Check_winner(state, row, col, player)
    - Count 4 directions: horizontal, vertical, 2 diagonals
    - If count >= 5: winner found!
    ↓
Switch Player or End Game
    ↓
Update GameState
```

---

## Module Breakdown

### 🎮 **Game Logic (`src/game/`)**

| File | Purpose | Key Classes |
|------|---------|-------------|
| `constants.py` | Game rules | BOARD_SIZE, WIN_LENGTH, PLAYER_X/O, EMPTY |
| `move.py` | Move definition | Move(row, col) - immutable dataclass |
| `board.py` | Board state | Board - grid management, place pieces |
| `game_state.py` | Game state snapshot | GameState - immutable state + queries |
| `game_engine.py` | Move validation & winner check | GameEngine - apply_move, check_winner |
| `game_manager.py` | Game coordinator | GameManager - holds players + engine |
| `pattern.py` | **Pattern detection (NEW)** | PatternAnalyzer, PatternType, LineInfo |
| `board_analyzer.py` | **Board analysis (NEW)** | BoardAnalyzer, CellAnalysis |
| `history.py` | **Game history (NEW)** | GameHistory, MoveRecord, GameStats |

### 👤 **AI System (`src/ai/`)**

| File | Purpose | Key Classes |
|------|---------|-------------|
| `base.py` | AI base class | AIPlayer - abstract base |
| `human_player.py` | Human player wrapper | HumanPlayer |
| `player_factory.py` | Create player by name | create_player(name) |
| `loader.py` | Load plugins | load_ai_players() |

### 🔌 **Plugins (`src/plugins/`)**

| File | Purpose | Example |
|------|---------|---------|
| `random_ai.py` | Random move picker | RandomAI |
| `greedy_ai.py` | Win/Block/Candidate strategy | GreedyAI |
| `your_ai.py` | Your implementation | YourAI |

### 🎨 **UI (`src/ui/`)**

| File | Purpose |
|------|---------|
| `menu_screen.py` | Menu UI - select players |
| `board_view.py` | Board rendering |

---

## Class Relationships

### **GameState & GameEngine**

```python
# GameState: Snapshot of current game
class GameState:
    board: Board
    current_player: int          # PLAYER_X or PLAYER_O
    winner: int | None
    game_over: bool
    last_move: Move | None
    
    # Queries (non-destructive)
    get_valid_moves()
    get_candidate_moves(distance)
    get_opponent()
    piece_count()
    is_terminal()
    clone()                       # Deep copy
    simulate_move(move)           # Returns new GameState

# GameEngine: Applies rules, validates moves
class GameEngine:
    state: GameState
    
    # Modifies state
    make_move(move) -> bool
    @staticmethod
    apply_move(state, move) -> bool
    check_winner(state, row, col, player) -> bool
    switch_player(state) -> None
```

**Usage Pattern**:
```python
# Don't modify state directly
# Instead: create copy and simulate
new_state = state.simulate_move(move)  # Returns new GameState
```

### **AIPlayer Hierarchy**

```python
# Base class (abstract)
class AIPlayer:
    @property
    is_human -> bool              # False for AI
    
    @property
    @abstractmethod
    name -> str                   # "My AI Name"
    
    @abstractmethod
    choose_move(state) -> Move    # Main AI logic
    
    # Note: state is GameState clone
    # Don't modify it!

# Your AI
class MyAI(AIPlayer):
    @property
    def name(self):
        return "My AI"
    
    def choose_move(self, state):
        # Implement logic here
        return Move(7, 7)
```

---

## Data Flow

### **AI Turn Execution**

```
main.py (update phase)
    │
    ├─→ Get current_player
    │
    ├─→ If AI:
    │   │
    │   ├─→ AI.choose_move(state.clone())
    │   │   │
    │   │   ├─→ PatternAnalyzer.analyze_move()
    │   │   │
    │   │   ├─→ BoardAnalyzer.get_candidate_analysis()
    │   │   │
    │   │   └─→ Return Move(row, col)
    │   │
    │   ├─→ GameEngine.make_move(move)
    │   │   │
    │   │   ├─→ Board.place_piece()
    │   │   │
    │   │   ├─→ GameEngine.check_winner()
    │   │   │
    │   │   └─→ Update GameState
    │   │
    │   └─→ Render board
    │
    └─→ If Human:
        └─→ Wait for mouse click
```

### **Helper Functions Calling**

```
AI.choose_move(state)
    │
    ├─→ PatternAnalyzer.find_winning_moves()
    │   │
    │   └─→ For each move:
    │       └─→ PatternAnalyzer.get_line_info()
    │
    ├─→ PatternAnalyzer.find_threats()
    │   │
    │   └─→ Group moves by threat level
    │
    └─→ BoardAnalyzer.get_candidate_analysis()
        │
        └─→ For each candidate:
            └─→ BoardAnalyzer.analyze_cell()
                └─→ PatternAnalyzer.analyze_move()
                    (2 calls: X pattern + O pattern)
```

---

## AI Integration Points

### **Where AI Plugs In**

```python
# 1. AI files created in src/plugins/
src/plugins/my_ai.py

# 2. Inherit AIPlayer
from ai.base import AIPlayer

class MyAI(AIPlayer):
    ...

# 3. Main entry point: choose_move()
def choose_move(self, state):
    # state = GameState (clone, safe to query)
    # Use helpers: PatternAnalyzer, BoardAnalyzer
    # Return: Move(row, col)
    return Move(7, 7)

# 4. Game automatically:
#    a) Loads AI from plugins/ folder (loader.py)
#    b) Shows in menu (MenuScreen)
#    c) Calls choose_move() each turn (main.py)
#    d) Applies move (GameEngine)
#    e) Updates UI (BoardView)
```

### **APIs Available to AI**

```python
# Query game state
state.get_valid_moves()          # All empty cells
state.get_candidate_moves(2)     # Optimized: near pieces
state.get_opponent()             # Get opponent player
state.current_player             # Current player (PLAYER_X/O)
state.board                       # Board object

# Analyze board
PatternAnalyzer.analyze_move(board, move, player)
PatternAnalyzer.find_winning_moves(board, moves, player)
PatternAnalyzer.find_threats(board, moves, opponent)

BoardAnalyzer.analyze_cell(board, move)
BoardAnalyzer.get_candidate_analysis(board, top_n=10)
BoardAnalyzer.get_critical_cells(board, player)

# Simulate (non-destructive)
new_state = state.clone()
new_state = state.simulate_move(move)

# Pattern detection
from game.pattern import PatternType
# PatternType.WINNING, OPEN_4, DEAD_4, LIVE_3, LIVE_2, ...
```

---

## State Management

### **Immutability Strategy**

```python
# ✅ SAFE: state is clone + snapshot
def choose_move(self, state):
    # state is GameState.clone()
    # Modifying state doesn't affect game
    temp_state = state.clone()
    temp_state.board.place_piece(7, 7, PLAYER_X)
    # Game state untouched
    
    return Move(7, 7)

# ✅ SAFE: simulate doesn't modify
new_state = state.simulate_move(move)
# state is unchanged

# ❌ UNSAFE: Don't do this
engine.state.board.place_piece(...)  # Modifies game directly!
```

### **State Lifecycle**

```
GameEngine.__init__()
    │
    └─→ state = GameState.create_new()
            - board = empty 15x15
            - current_player = PLAYER_X
            - winner = None
            - game_over = False
            
During game:
    make_move(move)
        │
        └─→ apply_move(state, move)
            ├─→ board.place_piece()
            ├─→ check_winner()
            ├─→ switch_player() or set game_over = True
            └─→ state modified in-place

AI queries:
    state.clone()
    state.simulate_move()
    │
    └─→ Creates new GameState snapshot
        Original untouched
```

---

## Execution Timeline

### **First Move of Game**

```
Time 0ms:   Game starts
            state: empty board, current=X, game_over=False

Time 100ms: Render board
            show "X's turn"

Time 300ms: X (AI) thinks
            choose_move(state.clone())
            ├─→ get_candidate_moves()
            ├─→ analyze_move() x N candidates
            └─→ return Move(7, 7)

Time 600ms: Apply move
            engine.make_move(Move(7, 7))
            state updated:
            - board[7][7] = PLAYER_X
            - current_player = PLAYER_O
            - last_move = Move(7, 7)

Time 700ms: Render
            show board with X at (7,7)
            show "O's turn"

Time 900ms: O (Human) waits for click...
```

---

## Performance Considerations

### **Optimization Points**

```python
# ❌ Slow: Check all 225 cells
valid_moves = state.get_valid_moves()
for move in valid_moves:
    analyze(move)  # O(225 * expensive_op)

# ✅ Fast: Check only ~20 candidates
candidates = state.get_candidate_moves(distance=2)
for move in candidates:
    analyze(move)  # O(20 * expensive_op)

# ❌ Slow: Evaluate each candidate independently
scores = [evaluate(move) for move in all_moves]

# ✅ Fast: Get pre-ranked candidates
candidates = BoardAnalyzer.get_candidate_analysis(board, top_n=10)
best = candidates[0].move
```

### **Time Budget**

```
Per move: ~1 second (AI_MOVE_DELAY = 0.3s in main.py)

Minimax depth: ~4-5 levels reasonable
MCTS iterations: ~500-1000 simulations

Rule of thumb: 
- If move takes > 1 second: game freezes (bad UX)
- If move takes < 100ms: feels instant
```

---

## Testing & Debugging

### **How to Verify Architecture**

```python
# 1. Test GameState immutability
state1 = GameState.create_new()
state2 = state1.clone()
state2.board.place_piece(7, 7, PLAYER_X)
assert state1.board.get_cell(7, 7) == EMPTY  # ✓

# 2. Test AI loading
from ai.loader import load_ai_players
players = load_ai_players()
assert len(players) >= 1  # ✓

# 3. Test pattern detection
lines = PatternAnalyzer.analyze_move(board, move, PLAYER_X)
assert lines[0].piece_count >= 1  # ✓

# 4. Test game flow
engine = GameEngine()
engine.make_move(Move(7, 7))
assert engine.state.current_player == PLAYER_O  # ✓
```

---

## Quick Reference

### **Key Files & Their Roles**

| Component | File | Responsibility |
|-----------|------|-----------------|
| **Entry** | `main.py` | Game loop, events, rendering |
| **State** | `game_state.py` | Immutable game snapshot |
| **Rules** | `game_engine.py` | Validate moves, check winner |
| **AI Base** | `ai/base.py` | AIPlayer interface |
| **AI Loading** | `ai/loader.py` | Auto-discover AI plugins |
| **Patterns** | `game/pattern.py` | Detect patterns (OPEN_4, etc.) |
| **Board Analysis** | `game/board_analyzer.py` | Priority scoring |
| **History** | `game/history.py` | Track game record |

### **Critical Methods**

| Method | Class | Returns | Use Case |
|--------|-------|---------|----------|
| `choose_move(state)` | AIPlayer | Move | Main AI entry point |
| `make_move(move)` | GameEngine | bool | Apply move to game |
| `get_candidate_moves(dist)` | GameState | list[Move] | Optimize AI search |
| `simulate_move(move)` | GameState | GameState | Test move safely |
| `analyze_move(board, move, player)` | PatternAnalyzer | list[LineInfo] | Detect patterns |
| `get_candidate_analysis(board, top_n)` | BoardAnalyzer | list[CellAnalysis] | Ranked candidates |

---

**Next Step**: Read **AI_DEVELOPMENT_GUIDE.md** to understand how to implement AI!
