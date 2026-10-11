from search import SearchProblem

class PositionSearchProblem(SearchProblem):
    """
    Bài toán tìm đường: Pacman từ vị trí xuất phát tìm đường đến 1 điểm đích cố định.
    Trạng thái (state) ở đây đơn giản là một tuple tọa độ: (x, y)
    """

    def __init__(self, start_pos, goal_pos, walls, cost_fn=lambda x: 1):
        """
        - start_pos: Tọa độ bắt đầu của Pacman, ví dụ (1, 1)
        - goal_pos: Tọa độ đích (thức ăn), ví dụ (5, 5)
        - walls: Tập hợp set chứa các tọa độ tường, ví dụ set([(0,0), (0,1), ...])
        - cost_fn: Hàm tính chi phí bước đi (mặc định mỗi bước tốn chi phí là 1)
        """
        self.start_state = start_pos
        self.goal_state = goal_pos
        self.walls = walls
        self.cost_fn = cost_fn

    def get_start_state(self):
        """Trả về trạng thái bắt đầu (x, y)"""
        return self.start_state

    def is_goal_state(self, state):
        """Kiểm tra xem tọa độ hiện tại đã trùng với tọa độ đích chưa"""
        return state == self.goal_state

    def get_successors(self, state):
        """
        Từ tọa độ hiện tại (x, y), thử đi sang 4 hướng:
        North (lên), South (xuống), East (phải), West (trái).
        Ô nào không phải là tường thì coi là kế tiếp hợp lệ.
        """
        successors = []
        x, y = state

        # Thống nhất 4 hành động và sự thay đổi tọa độ tương ứng (dx, dy)
        # Giả sử: x tăng sang phải, y tăng đi xuống dưới (theo chỉ số dòng/cột)
        actions = [
            ('North', (x, y - 1)),
            ('South', (x, y + 1)),
            ('East',  (x + 1, y)),
            ('West',  (x - 1, y))
        ]

        for action, next_pos in actions:
            # Nếu vị trí kế tiếp không nằm trong tập các ô tường
            if next_pos not in self.walls:
                cost = self.cost_fn(next_pos)
                successors.append((next_pos, action, cost))

        return successors

    def get_cost_of_actions(self, actions):
        """Tính tổng chi phí của một danh sách các hành động"""
        # Nếu chi phí đồng nhất = 1 thì tổng chi phí chính bằng số bước đi
        return len(actions)
def manhattan_heuristic(state, problem=None):
    """
    Hàm Heuristic tính khoảng cách Manhattan từ vị trí hiện tại đến đích.
    Thỏa mãn cả tính Admissible (không đánh giá quá cao) và Consistent (nhất quán).
    """
    if problem is not None and hasattr(problem, 'goal_state'):
        goal = problem.goal_state
        # state ở dạng tọa độ (x, y)
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    return 0

class FoodSearchProblem(SearchProblem):
    """
    Bài toán tìm đường để Pacman ăn hết toàn bộ thức ăn trên bản đồ.
    Trạng thái: (pacman_pos, remaining_foods)
      - pacman_pos: (x, y)
      - remaining_foods: frozenset chứa các tọa độ (x, y) của thức ăn chưa ăn
    """

    def __init__(self, start_pos, foods_set, walls):
        """
        - start_pos: tọa độ bắt đầu của Pacman (x, y)
        - foods_set: tập hợp (set/frozenset) chứa tọa độ các hạt thức ăn
        - walls: tập hợp set chứa tọa độ các ô tường
        """
        self.start_pos = start_pos
        self.start_foods = frozenset(foods_set)
        self.walls = walls

    def get_start_state(self):
        # Trạng thái xuất phát gồm: vị trí Pacman và toàn bộ thức ăn ban đầu
        return (self.start_pos, self.start_foods)

    def is_goal_state(self, state):
        # Đích đạt được khi tập thức ăn còn lại rỗng (đã ăn hết)
        pacman_pos, remaining_foods = state
        return len(remaining_foods) == 0

    def get_successors(self, state):
        successors = []
        pacman_pos, remaining_foods = state
        x, y = pacman_pos

        directions = [
            ('North', (x, y - 1)),
            ('South', (x, y + 1)),
            ('East',  (x + 1, y)),
            ('West',  (x - 1, y))
        ]

        for action, next_pos in directions:
            # Nếu không đi vào tường
            if next_pos not in self.walls:
                # Nếu ô tiếp theo có thức ăn, loại hạt đó ra khỏi tập còn lại
                if next_pos in remaining_foods:
                    next_foods = remaining_foods - {next_pos}
                else:
                    next_foods = remaining_foods

                next_state = (next_pos, next_foods)
                step_cost = 1
                successors.append((next_state, action, step_cost))

        return successors

    def get_cost_of_actions(self, actions):
        return len(actions)
def food_heuristic(state, problem=None):
    """
    Heuristic cho FoodSearchProblem:
    Lấy khoảng cách Manhattan từ vị trí hiện tại của Pacman tới hạt thức ăn xa nhất.
    Đảm bảo tính Admissible vì để ăn hết thức ăn, Pacman tối thiểu phải đi tới hạt xa nhất.
    """
    pacman_pos, remaining_foods = state
    
    if not remaining_foods:
        return 0

    px, py = pacman_pos
    # Tìm khoảng cách Manhattan lớn nhất tới một hạt thức ăn bất kỳ còn lại
    max_distance = max(abs(px - fx) + abs(py - fy) for fx, fy in remaining_foods)
    return max_distance