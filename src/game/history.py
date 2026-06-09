"""Quản lý lịch sử nước đi và replay game"""

from dataclasses import dataclass, field
from typing import Optional, List

from game.move import Move
from game.game_state import GameState
from game.game_engine import GameEngine
from game.constants import PLAYER_X, PLAYER_O


@dataclass
class MoveRecord:
    """Record của một nước đi"""
    move_number: int        # 1, 2, 3, ... (1-indexed)
    player: int             # PLAYER_X hoặc PLAYER_O
    move: Move
    timestamp: float = 0.0  # Optional: khi nước đi được make (unix time)
    
    # State sau khi move này
    board_state: Optional[GameState] = None
    
    def __str__(self):
        player_name = "X" if self.player == PLAYER_X else "O"
        return f"{self.move_number}. {player_name}{self.move}"


class GameHistory:
    """Quản lý lịch sử game"""
    
    def __init__(self):
        self.moves: List[MoveRecord] = []
        self.initial_state: Optional[GameState] = None
    
    def record_move(
        self,
        player: int,
        move: Move,
        board_state: GameState,
        timestamp: float = 0.0
    ) -> None:
        """
        Ghi lại một nước đi
        
        Args:
            player: PLAYER_X hoặc PLAYER_O
            move: Move object
            board_state: State sau khi make move
            timestamp: Thời điểm move (optional)
        """
        move_number = len(self.moves) + 1
        
        record = MoveRecord(
            move_number=move_number,
            player=player,
            move=move,
            timestamp=timestamp,
            board_state=board_state.clone()
        )
        
        self.moves.append(record)
    
    def set_initial_state(self, state: GameState) -> None:
        """Lưu state ban đầu (dùng cho replay)"""
        self.initial_state = state.clone()
    
    def get_move_count(self) -> int:
        """Số nước đi đã make"""
        return len(self.moves)
    
    def get_move(self, index: int) -> Optional[MoveRecord]:
        """Lấy nước đi thứ index (0-indexed)"""
        if 0 <= index < len(self.moves):
            return self.moves[index]
        return None
    
    def get_last_move(self) -> Optional[MoveRecord]:
        """Lấy nước đi cuối cùng"""
        if self.moves:
            return self.moves[-1]
        return None
    
    def get_moves_by_player(self, player: int) -> List[MoveRecord]:
        """Lấy tất cả nước đi của một player"""
        return [m for m in self.moves if m.player == player]
    
    def clear(self) -> None:
        """Xóa lịch sử"""
        self.moves.clear()
        self.initial_state = None
    
    def to_pgn_string(self) -> str:
        """
        Xuất lịch sử dưới dạng PGN-like string.
        Format: 1. X(row,col) O(row,col) 2. X(row,col) O(row,col) ...
        """
        pgn = []
        
        for i, record in enumerate(self.moves):
            # Mỗi nước đó được format: X(row,col) hoặc O(row,col)
            player_name = "X" if record.player == PLAYER_X else "O"
            move_str = f"{player_name}({record.move.row},{record.move.col})"
            
            # Mỗi 2 nước là 1 round
            if len(pgn) % 2 == 0:
                pgn.append(f"{len(pgn) // 2 + 1}.")
            
            pgn.append(move_str)
        
        return " ".join(pgn)
    
    def from_pgn_string(self, pgn_string: str, engine: 'GameEngine') -> bool:
        """
        Parse PGN-like string và replay game.
        Format: 1. X(7,7) O(7,8) 2. X(8,7) ...
        
        Returns:
            True nếu replay thành công, False nếu invalid
        """
        self.clear()
        
        # Reset engine
        engine.state = GameState.create_new()
        self.set_initial_state(engine.state)
        
        # Parse moves
        tokens = pgn_string.split()
        
        for token in tokens:
            # Skip move numbers (e.g., "1.", "2.")
            if token.endswith("."):
                continue
            
            # Parse move: X(row,col) hoặc O(row,col)
            try:
                if not (token[0] in ['X', 'O'] and '(' in token and ')' in token):
                    continue
                
                player_char = token[0]
                player = PLAYER_X if player_char == 'X' else PLAYER_O
                
                # Extract row, col
                coords = token.split('(')[1].split(')')[0]
                row, col = map(int, coords.split(','))
                move = Move(row, col)
                
                # Make move
                if not engine.make_move(move):
                    return False
                
                # Record
                self.record_move(player, move, engine.state)
                
            except (IndexError, ValueError):
                return False
        
        return True
    
    def replay_to_move(
        self,
        move_index: int,
        engine: 'GameEngine'
    ) -> bool:
        """
        Replay game đến move thứ move_index (0-indexed).
        Reset engine và apply moves từ đầu.
        
        Returns:
            True nếu thành công
        """
        if not self.initial_state:
            return False
        
        if move_index < 0 or move_index >= len(self.moves):
            return False
        
        # Reset engine
        engine.state = self.initial_state.clone()
        
        # Apply moves đến move_index (inclusive)
        for i in range(move_index + 1):
            record = self.moves[i]
            if not engine.make_move(record.move):
                return False
        
        return True
    
    def __str__(self) -> str:
        """String representation"""
        return self.to_pgn_string()
    
    def __repr__(self) -> str:
        return f"GameHistory(moves={len(self.moves)})"


@dataclass
class GameStats:
    """Thống kê game"""
    total_moves: int = 0
    player_x_moves: int = 0
    player_o_moves: int = 0
    winner: Optional[int] = None
    game_duration: float = 0.0  # seconds
    
    def update(self, history: GameHistory, duration: float = 0.0):
        """Update stats từ history"""
        self.total_moves = history.get_move_count()
        self.player_x_moves = len(history.get_moves_by_player(PLAYER_X))
        self.player_o_moves = len(history.get_moves_by_player(PLAYER_O))
        self.game_duration = duration
    
    def __str__(self) -> str:
        return (
            f"Total moves: {self.total_moves}, "
            f"X: {self.player_x_moves}, "
            f"O: {self.player_o_moves}, "
            f"Duration: {self.game_duration:.2f}s"
        )
