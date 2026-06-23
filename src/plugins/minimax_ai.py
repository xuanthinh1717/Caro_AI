import math
import time

from ai.base import AIPlayer
from game.constants import BOARD_SIZE, EMPTY, PLAYER_X, PLAYER_O
from game.move import Move
from game.pattern import PatternAnalyzer
from game.board_analyzer import BoardAnalyzer


class MinimaxAlphaBetaAI(AIPlayer):
    """
    AI sử dụng MiniMax kết hợp Alpha-Beta pruning.
    - MiniMax: mô phỏng nước đi của AI và đối thủ.
    - Alpha-Beta: cắt bỏ các nhánh không cần xét.
    - Heuristic: đánh giá trạng thái bàn cờ khi đạt độ sâu giới hạn.
    - Threat Detection: phát hiện và chặn các thế nguy hiểm trước khi gọi MiniMax.
    """

    def __init__(self):
        self.max_depth = 3
        self.max_candidates = 8
        self.nodes_searched = 0

    @property
    def name(self):
        return "MiniMax AB"

    def choose_move(self, state):
        """
        Hàm chính được game gọi khi đến lượt AI.
        Trả về nước đi tốt nhất.
        Đồng thời in thời gian AI đưa ra quyết định cho một nước đi.
        """

        self.nodes_searched = 0
        start_time = time.perf_counter()

        ai_player = state.current_player
        opponent = self.get_opponent(ai_player)

        # Nếu bàn cờ đang rỗng, đi vào giữa bàn.
        if state.piece_count() == 0:
            center = BOARD_SIZE // 2
            move = Move(center, center)

            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=move,
                score=None
            )

            return move

        valid_moves = state.get_valid_moves()

        if not valid_moves:
            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=None,
                score=None
            )

            return None

        # 1. Nếu AI có thể thắng ngay, đi luôn.
        winning_moves = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            ai_player
        )

        if winning_moves:
            move = winning_moves[0]

            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=move,
                score="WIN"
            )

            return move

        # 2. Nếu đối thủ có thể thắng ngay, chặn ngay.
        opponent_winning_moves = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            opponent
        )

        if opponent_winning_moves:
            move = opponent_winning_moves[0]

            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=move,
                score="BLOCK"
            )

            return move

        # 3. Nếu đối thủ có thế 3 mở hai đầu, chặn ngay.
        open_three_blocks = self.find_open_three_blocks(
            state,
            opponent
        )

        if open_three_blocks:
            move = open_three_blocks[0]

            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=move,
                score="BLOCK_OPEN_THREE"
            )

            return move
        
        # 4. Nếu đối thủ có thế 3 gãy, chặn ngay.
        broken_three_blocks = self.find_broken_three_blocks(
            state,
            opponent
        )

        if broken_three_blocks:
            move = broken_three_blocks[0]

            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=move,
                score="BLOCK_BROKEN_THREE"
            )

            return move

        # 5. Lấy các nước đi ứng viên thay vì xét toàn bộ bàn cờ.
        candidate_moves = self.get_ordered_candidate_moves(
            state,
            ai_player
        )

        if not candidate_moves:
            self.print_decision_info(
                start_time=start_time,
                ai_player=ai_player,
                move=None,
                score=None
            )

            return None

        best_score = -math.inf
        best_move = candidate_moves[0]

        alpha = -math.inf
        beta = math.inf

        for move in candidate_moves:
            new_state = state.simulate_move(move)

            score = self.minimax(
                new_state,
                self.max_depth - 1,
                alpha,
                beta,
                False,
                ai_player
            )

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        self.print_decision_info(
            start_time=start_time,
            ai_player=ai_player,
            move=best_move,
            score=best_score
        )

        return best_move

    def minimax(
        self,
        state,
        depth,
        alpha,
        beta,
        maximizing,
        ai_player
    ):
        """
        MiniMax kết hợp Alpha-Beta pruning.
        maximizing = True  -> lượt AI, chọn điểm lớn nhất.
        maximizing = False -> lượt đối thủ, chọn điểm nhỏ nhất.
        """

        # Đếm số node mà MiniMax đã duyệt.
        self.nodes_searched += 1

        if depth == 0 or state.is_terminal():
            return self.evaluate(state, ai_player)

        candidate_moves = self.get_ordered_candidate_moves(
            state,
            ai_player
        )

        if not candidate_moves:
            return self.evaluate(state, ai_player)

        if maximizing:
            value = -math.inf

            for move in candidate_moves:
                new_state = state.simulate_move(move)

                value = max(
                    value,
                    self.minimax(
                        new_state,
                        depth - 1,
                        alpha,
                        beta,
                        False,
                        ai_player
                    )
                )

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value

        else:
            value = math.inf

            for move in candidate_moves:
                new_state = state.simulate_move(move)

                value = min(
                    value,
                    self.minimax(
                        new_state,
                        depth - 1,
                        alpha,
                        beta,
                        True,
                        ai_player
                    )
                )

                beta = min(beta, value)

                if alpha >= beta:
                    break

            return value

    def evaluate(self, state, ai_player):
        """
        Hàm Heuristic đánh giá trạng thái bàn cờ.
        score(state) = AI_score(state) - Opponent_score(state)
        """
        opponent = self.get_opponent(ai_player)

        if state.winner == ai_player:
            return 1_000_000_000

        if state.winner == opponent:
            return -1_000_000_000

        ai_score = self.evaluate_player(state, ai_player)
        opponent_score = self.evaluate_player(state, opponent)

        # Nhân điểm đối thủ lớn hơn một chút để AI ưu tiên phòng thủ.
        return ai_score - opponent_score * 1.15

    def evaluate_player(self, state, player):
        """
        Chấm điểm các thế cờ của một người chơi.
        Cách làm: duyệt các đoạn 5 ô theo 4 hướng.
        Nếu đoạn 5 ô chỉ có quân của player và ô trống, cộng điểm.
        Nếu đoạn có cả quân player và đối thủ thì bỏ qua.
        """
        score = 0
        board = state.board

        directions = [
            (0, 1),    # ngang
            (1, 0),    # dọc
            (1, 1),    # chéo xuống phải
            (1, -1),   # chéo xuống trái
        ]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                for dr, dc in directions:
                    cells = []

                    for i in range(5):
                        r = row + dr * i
                        c = col + dc * i

                        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                            break

                        cells.append(board.get_cell(r, c))

                    if len(cells) == 5:
                        score += self.score_window(cells, player)

        return score

    def score_window(self, cells, player):
        """
        Chấm điểm một đoạn 5 ô.
        """
        opponent = self.get_opponent(player)

        player_count = cells.count(player)
        opponent_count = cells.count(opponent)
        empty_count = cells.count(EMPTY)

        # Nếu đoạn có cả quân mình và quân đối thủ thì không tạo được chuỗi thắng.
        if player_count > 0 and opponent_count > 0:
            return 0

        if player_count == 5:
            return 1_000_000

        if player_count == 4 and empty_count == 1:
            return 100_000

        if player_count == 3 and empty_count == 2:
            return 10_000

        if player_count == 2 and empty_count == 3:
            return 1_000

        if player_count == 1 and empty_count == 4:
            return 10

        return 0

    def find_open_three_blocks(self, state, player):
        """
        Tìm các ô cần chặn khi player có thế 3 quân mở hai đầu.

        Mẫu được phát hiện:
            . X X X .

        Hàm trả về danh sách các nước đi có thể dùng để chặn hai đầu.
        """
        board = state.board
        blocks = []

        directions = [
            (0, 1),    # ngang
            (1, 0),    # dọc
            (1, 1),    # chéo xuống phải
            (1, -1),   # chéo xuống trái
        ]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                for dr, dc in directions:
                    cells = []
                    positions = []

                    for i in range(5):
                        r = row + dr * i
                        c = col + dc * i

                        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                            break

                        cells.append(board.get_cell(r, c))
                        positions.append((r, c))

                    if len(cells) != 5:
                        continue

                    # Mẫu: . X X X .
                    if (
                        cells[0] == EMPTY and
                        cells[1] == player and
                        cells[2] == player and
                        cells[3] == player and
                        cells[4] == EMPTY
                    ):
                        left_r, left_c = positions[0]
                        right_r, right_c = positions[4]

                        blocks.append(Move(left_r, left_c))
                        blocks.append(Move(right_r, right_c))

        return blocks
    
    def find_broken_three_blocks(self, state, player):
        """
        Tìm các ô cần chặn khi player có thế 3 gãy nguy hiểm.

        Các mẫu được phát hiện:
            . X X . X .
            . X . X X .

        Hàm trả về danh sách Move cần chặn.
        """
        board = state.board
        blocks = []

        directions = [
            (0, 1),    # ngang
            (1, 0),    # dọc
            (1, 1),    # chéo xuống phải
            (1, -1),   # chéo xuống trái
        ]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                for dr, dc in directions:
                    cells = []
                    positions = []

                    for i in range(6):
                        r = row + dr * i
                        c = col + dc * i

                        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                            break

                        cells.append(board.get_cell(r, c))
                        positions.append((r, c))

                    if len(cells) != 6:
                        continue

                    # Mẫu: . X X . X .
                    if (
                        cells[0] == EMPTY and
                        cells[1] == player and
                        cells[2] == player and
                        cells[3] == EMPTY and
                        cells[4] == player and
                        cells[5] == EMPTY
                    ):
                        block_r, block_c = positions[3]
                        blocks.append(Move(block_r, block_c))

                    # Mẫu: . X . X X .
                    if (
                        cells[0] == EMPTY and
                        cells[1] == player and
                        cells[2] == EMPTY and
                        cells[3] == player and
                        cells[4] == player and
                        cells[5] == EMPTY
                    ):
                        block_r, block_c = positions[2]
                        blocks.append(Move(block_r, block_c))

        return blocks

    def get_ordered_candidate_moves(self, state, ai_player):
        """
        Lấy và sắp xếp các nước đi ứng viên bằng BoardAnalyzer.

        BoardAnalyzer đã phân tích mức độ nguy hiểm/tốt của từng ô,
        bao gồm cả khả năng tấn công và phòng thủ.
        Việc sắp xếp nước đi tốt lên trước giúp Alpha-Beta cắt nhánh hiệu quả hơn.
        """

        analyses = BoardAnalyzer.get_candidate_analysis(
            state.board,
            distance=2,
            top_n=self.max_candidates
        )

        if not analyses:
            moves = state.get_valid_moves()
            return moves[:self.max_candidates]

        scored_moves = []

        for analysis in analyses:
            if ai_player == PLAYER_X:
                attack_score = analysis.x_score
                defense_score = analysis.o_score
            else:
                attack_score = analysis.o_score
                defense_score = analysis.x_score

            # Ưu tiên cả tấn công và phòng thủ.
            # Defense nhân nhẹ 1.15 để AI không bỏ qua threat của đối thủ.
            priority = attack_score + defense_score * 1.15

            scored_moves.append(
                (
                    priority,
                    analysis.move
                )
            )

        scored_moves.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            move
            for _, move in scored_moves[:self.max_candidates]
        ]

    def get_opponent(self, player):
        if player == PLAYER_X:
            return PLAYER_O

        return PLAYER_X

    def print_decision_info(
        self,
        start_time,
        ai_player,
        move,
        score
    ):
        """
        In thông tin thời gian AI đưa ra quyết định cho một nước đi.
        Thông tin này hiển thị ở terminal/console.
        """

        elapsed_time = time.perf_counter() - start_time

        if move is None:
            move_text = "None"
        else:
            move_text = f"({move.row}, {move.col})"

        print(
            f"[{self.name}] "
            f"Player: {ai_player} | "
            f"Move: {move_text} | "
            f"Score: {score} | "
            f"Depth: {self.max_depth} | "
            f"Candidates: {self.max_candidates} | "
            f"Nodes: {self.nodes_searched} | "
            f"Time: {elapsed_time:.4f}s"
        )