import time
from plugins.minimax_ai import MinimaxAI
from plugins.mcts_ai import MctsAI


def print_separator():
    print("-" * 60)

def run_heavy_benchmark():
    print("\n🚀 KHỞI ĐỘNG HỆ THỐNG BENCHMARK AI CARO 🚀")
    print("Trận đấu: MINIMAX (Alpha-Beta) vs MCTS (Pro + VCF)\n")
    
    ai_minimax = MinimaxAI(max_depth=4) 
    ai_mcts = MctsAI(time_limit=3.0)    
    
    games_to_play = 10
    results = {'Minimax': 0, 'MCTS': 0, 'Draws': 0}
    time_stats = {'Minimax': [], 'MCTS': []}

    for i in range(games_to_play):
        print_separator()
        print(f"BẮT ĐẦU VÁN {i + 1}/{games_to_play}")
        
        if i % 2 == 0:
            player_x, name_x = ai_minimax, "Minimax"
            player_o, name_o = ai_mcts, "MCTS"
        else:
            player_x, name_x = ai_mcts, "MCTS"
            player_o, name_o = ai_minimax, "Minimax"
            
        print(f"X (Đi trước): {name_x} | O (Đi sau): {name_o}")        
        time.sleep(0.5) 

    print_separator()
    print("📊 BÁO CÁO KẾT QUẢ BENCHMARK M4 📊")
    print(f"Tổng số ván: {games_to_play}")
    print(f"🏆 Minimax Thắng: {results['Minimax']} ván")
    print(f"🏆 MCTS Thắng: {results['MCTS']} ván")
    print(f"🤝 Hòa: {results['Draws']} ván")
    print_separator()

if __name__ == "__main__":
    run_heavy_benchmark()