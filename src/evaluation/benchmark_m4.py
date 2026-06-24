import time
from game.game_state import GameState
from game.game_engine import GameEngine
from plugins.mcts_ai import MctsAI
from plugins.greedy_ai import GreedyAI

def run_benchmark():
    print("\n🚀 BẮT ĐẦU BENCHMARK: MCTS vs GREEDY AI 🚀\n")
    
    mcts_player = MctsAI(time_limit=2.0)
    greedy_player = GreedyAI()
    
   
    state = GameState.create_new() 
    engine = GameEngine()
    engine.state = state

    moves_count = 0
    start_game_time = time.time()

    while not engine.state.game_over:
        current_player_ai = mcts_player if engine.state.current_player == 1 else greedy_player
        
        move_start = time.time()
        move = current_player_ai.choose_move(engine.state.clone())
        move_time = time.time() - move_start
        
        print(f"Lượt {moves_count + 1}: {current_player_ai.name} đánh {move} (Mất {move_time:.2f}s)")
        
        engine.make_move(move)
        moves_count += 1
        
        if moves_count > 100: 
            print("Hòa do quá số nước đi!")
            break

    total_time = time.time() - start_game_time
    print("\n" + "="*40)
    print("🏆 KẾT QUẢ VÁN ĐẤU")
    if engine.state.winner == 1:
        print(f"Chiến thắng: {mcts_player.name} (X)")
    elif engine.state.winner == 2:
        print(f"Chiến thắng: {greedy_player.name} (O)")
    else:
        print("Kết quả: HÒA")
    print(f"Tổng số nước đi: {moves_count}")
    print(f"Tổng thời gian: {total_time:.2f}s")
    print("="*40 + "\n")

if __name__ == "__main__":
    run_benchmark()