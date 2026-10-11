import sys
import os

# Thêm thư mục src vào đường dẫn hệ thống để import module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
'''
Mặc định khi chạy 1 file trong python(ví dụ file test_search.py nằm trong thư mục tests/),python chỉ tìm kiếm các module và thư viện nằm 
ở 2 nơi:
-Các thư viện cài đặt sẵn của python(như math,time,collections)
-Ngay chính thư mục chứa file đang chạy(tức là thư mục tests/) 
Vì các file code thuật toán (search.py, searchAgents.py) nằm ở thư mục src/, chứ không nằm trong tests/
Python sẽ không tìm thấy và ném ra lỗi đỏ nếu ta import sang nodule ở thư mục src
'''

from search import depth_first_search, breadth_first_search, uniform_cost_search, a_star_search
from searchAgents import PositionSearchProblem, FoodSearchProblem, manhattan_heuristic, food_heuristic

def print_result(algo_name, result):
    print(f"--- {algo_name} ---")
    if result["actions"] is not None:
        print(f"  Trạng thái       : Thành công")
        print(f"  Số bước đi (Cost): {result['total_cost']}")
        print(f"  Số node mở rộng  : {result['nodes_expanded']}")
        print(f"  Thời gian chạy   : {result['execution_time']:.6f}s")
        print(f"  Hành động        : {' -> '.join(result['actions'])}")
    else:
        print("  Không tìm thấy đường đi!")
    print()

def test_single_goal():
    """
    Test Case 1: Tìm đường đến 1 đích (PositionSearchProblem)
    Mê cung 5x5:
      P: Xuất phát (1, 1)
      G: Đích (3, 3)
      %: Tường chắn
    """
    print("==================================================")
    print("KIỂM THỬ 1: POSITION SEARCH PROBLEM (TÌM 1 ĐÍCH)")
    print("==================================================")
    
    start_pos = (1, 1)
    goal_pos = (3, 3)
    
    # Đặt tường tạo mê cung buộc phải đi vòng
    walls = {
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
        (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
        (0, 1), (0, 2), (0, 3),
        (4, 1), (4, 2), (4, 3),
        (2, 1), (2, 2)  # Tường chắn ở giữa
    }

    problem = PositionSearchProblem(start_pos, goal_pos, walls)

    # 1. Depth-First Search
    res_dfs = depth_first_search(problem)
    print_result("DFS", res_dfs)

    # 2. Breadth-First Search
    res_bfs = breadth_first_search(problem)
    print_result("BFS", res_bfs)

    # 3. Uniform-Cost Search
    res_ucs = uniform_cost_search(problem)
    print_result("UCS", res_ucs)

    # 4. A* Search với Manhattan Heuristic
    res_astar = a_star_search(problem, manhattan_heuristic)
    print_result("A* (Manhattan)", res_astar)

    # Kiểm tra tính đúng đắn logic
    assert res_bfs["total_cost"] == res_ucs["total_cost"] == res_astar["total_cost"], \
        "Lỗi: BFS, UCS, và A* phải cho ra cùng chi phí tối ưu trên map phẳng!"
    assert res_astar["nodes_expanded"] <= res_bfs["nodes_expanded"], \
        "Lỗi: A* thông thường phải mở rộng số node ít hơn hoặc bằng BFS!"
    print(">> ĐẠT CHUẨN: Toàn bộ thuật toán tìm 1 đích hoạt động chính xác!\n")

def test_food_search():
    """
    Test Case 2: Ăn hết thức ăn (FoodSearchProblem)
    Pacman xuất phát ở (1, 1) và cần ăn 2 hạt thức ăn ở (1, 3) và (3, 1).
    """
    print("==================================================")
    print("KIỂM THỬ 2: FOOD SEARCH PROBLEM (ĂN HẾT THỨC ĂN)")
    print("==================================================")

    start_pos = (1, 1)
    foods = {(1, 3), (3, 1)}
    walls = {
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
        (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
        (0, 1), (0, 2), (0, 3),
        (4, 1), (4, 2), (4, 3)
    }

    problem = FoodSearchProblem(start_pos, foods, walls)

    # Chạy BFS
    res_bfs = breadth_first_search(problem)
    print_result("BFS (Food)", res_bfs)

    # Chạy A* với food_heuristic
    res_astar = a_star_search(problem, food_heuristic)
    print_result("A* (Food Heuristic)", res_astar)

    assert res_bfs["total_cost"] == res_astar["total_cost"], \
        "Lỗi: A* với food_heuristic phải tìm được số bước tối ưu như BFS!"
    print(">> ĐẠT CHUẨN: Bài toán FoodSearchProblem hoạt động chính xác!\n")

if __name__ == "__main__":
    test_single_goal()
    test_food_search()