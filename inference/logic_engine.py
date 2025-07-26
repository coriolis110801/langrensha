from constraint import Problem, ExactSumConstraint
from collections import defaultdict

ROLES = {
    "police": 1,
    "mafia": 4,
    "villager": 7,
}

def apply_chain_reasoning_constraints(problem, judgments, police_a_number, police_b_number):
    """
    应用连锁推理约束
    处理主观判断警察身份相关玩家后的连锁推理
    """
    # 检查是否有警察身份相关的主观判断
    police_a_judged_good = any(j["player"] == police_a_number and j["label"] == "good" for j in judgments)
    police_b_judged_good = any(j["player"] == police_b_number and j["label"] == "good" for j in judgments)
    
    # 连锁推理：如果警察A被判断为好人，那么警察B必须是匪徒
    if police_a_judged_good:
        problem.addConstraint(lambda role: role == "mafia", [police_b_number])
        print(f"连锁推理：{police_a_number}号（警察A）被判断为好人 → {police_b_number}号（警察B）必须是匪徒")
    
    # 连锁推理：如果警察B被判断为好人，那么警察A必须是匪徒
    if police_b_judged_good:
        problem.addConstraint(lambda role: role == "mafia", [police_a_number])
        print(f"连锁推理：{police_b_number}号（警察B）被判断为好人 → {police_a_number}号（警察A）必须是匪徒")

def solve_scenario_with_police_identity(checks, deaths, judgments, police_a_number, police_b_number=None, assume_police_a_is_real=True):
    """
    参数：
      checks: List of dicts: {"checker": 'A' or 'B', "target": int, "result": 'good'/'bad'}
      deaths: List of dicts: {"player": int, "type": 'kill'/'vote'}
      judgments: List of dicts: {"player": int, "label": 'good'/'bad'}
      police_a_number: int, 警察A的玩家编号
      police_b_number: int or None, 警察B的玩家编号，如果为None则表示只设置了一个警察
      assume_police_a_is_real: bool, True表示假设警察A是真警察，False表示假设警察B是真警察
    返回：
      所有满足约束的角色分配列表
    """
    problem = Problem()
    players = list(range(1, 13))
    
    # 每个玩家的变量，其取值域为三种角色
    for p in players:
        problem.addVariable(p, ["police", "mafia", "villager"])
    
    # 总数约束
    def count_police(*roles):
        return roles.count("police") == 1
    
    def count_mafia(*roles):
        return roles.count("mafia") == 4
    
    def count_villager(*roles):
        return roles.count("villager") == 7
    
    problem.addConstraint(count_police, players)
    problem.addConstraint(count_mafia, players)
    problem.addConstraint(count_villager, players)

    # 警察身份约束
    if assume_police_a_is_real:
        # 假设警察A是真警察
        problem.addConstraint(lambda role: role == "police", [police_a_number])
        if police_b_number is not None:
            # 警察B必须是匪徒（假警察）
            problem.addConstraint(lambda role: role == "mafia", [police_b_number])
            print(f"警察身份约束：{police_a_number}号（警察A）是真警察，{police_b_number}号（警察B）是假警察（匪徒）")
        else:
            print(f"警察身份约束：{police_a_number}号（警察A）是真警察，暂未设置警察B")
    else:
        # 假设警察B是真警察
        if police_b_number is not None:
            problem.addConstraint(lambda role: role == "police", [police_b_number])
            # 警察A必须是匪徒（假警察）
            problem.addConstraint(lambda role: role == "mafia", [police_a_number])
            print(f"警察身份约束：{police_b_number}号（警察B）是真警察，{police_a_number}号（警察A）是假警察（匪徒）")
        else:
            # 如果没有设置警察B，则假设B无解
            return []

    # 死亡约束：被杀/处决的人只能是villager或police，绝不能是mafia
    if deaths:
        death_players = [e["player"] for e in deaths]
        for player in death_players:
            problem.addConstraint(lambda role: role != "mafia", [player])

    # 主观判断约束
    for j in judgments:
        if j["label"] == "good":
            # 判断为好人：不能是匪徒，但可以是警察或好人
            problem.addConstraint(lambda role, player=j["player"]: role != "mafia", [j["player"]])
        else:
            # 判断为匪徒：必须是匪徒，不能是警察或好人
            problem.addConstraint(lambda role, player=j["player"]: role == "mafia", [j["player"]])

    # 应用连锁推理约束
    if police_b_number is not None:
        apply_chain_reasoning_constraints(problem, judgments, police_a_number, police_b_number)

    # 查验约束：真警察的检查结果直接用，假警察的检查结果不可信
    for c in checks:
        is_true_check = False
        if assume_police_a_is_real and c["checker"] == "A":
            is_true_check = True
        elif not assume_police_a_is_real and c["checker"] == "B" and police_b_number is not None:
            is_true_check = True
        
        if is_true_check:
            # 真警察的查验结果：直接使用，100%真实
            if c["result"] == "good":
                # 真警察查验为好人：该玩家必须是好人（不能是警察或匪徒）
                problem.addConstraint(lambda role: role == "villager", [c["target"]])
                print(f"连锁推理：真警察查验{c['target']}号为好人 → {c['target']}号必须是好人")
            else:
                # 真警察查验为坏人：该玩家必须是匪徒
                problem.addConstraint(lambda role: role == "mafia", [c["target"]])
                print(f"连锁推理：真警察查验{c['target']}号为坏人 → {c['target']}号必须是匪徒")
        else:
            # 假警察的查验结果：不可信，不添加约束
            # 假警察可能会说谎，也可能不会说谎，不能简单取反
            print(f"忽略假警察查验：{c['checker']}查验{c['target']}号为{c['result']}（不可信）")

    # 求解
    try:
        solutions = problem.getSolutions()
        return solutions
    except Exception as e:
        print(f"求解出错: {e}")
        return []

def compare_scenarios_with_police_identity(checks, deaths, judgments, police_a_number, police_b_number=None):
    """
    比较两种假设（警察A是真警察 vs 警察B是真警察）的可行性
    如果police_b_number为None，则只考虑警察A是真警察的情况
    """
    sols_A = solve_scenario_with_police_identity(checks, deaths, judgments, police_a_number, police_b_number, assume_police_a_is_real=True)
    
    if police_b_number is not None:
        sols_B = solve_scenario_with_police_identity(checks, deaths, judgments, police_a_number, police_b_number, assume_police_a_is_real=False)
    else:
        # 如果只设置了一个警察，则假设B无解
        sols_B = []
    
    return {"A": sols_A, "B": sols_B}

# 保留原来的函数以保持兼容性
def solve_scenario(checks, deaths, judgments, suspect_police_id):
    """
    参数：
      checks: List of dicts: {"checker": 'A' or 'B', "target": int, "result": 'good'/'bad'}
      deaths: List of dicts: {"player": int, "type": 'kill'/'vote'}
      judgments: List of dicts: {"player": int, "label": 'good'/'bad'}
      suspect_police_id: 'A' or 'B'
    返回：
      所有满足约束的角色分配列表，每个分配是 dict {player_id: 'police'|'mafia'|'villager', ...}
    """
    problem = Problem()
    players = list(range(1, 13))
    
    # 每个玩家的变量，其取值域为三种角色
    for p in players:
        problem.addVariable(p, ["police", "mafia", "villager"])
    
    # 总数约束 - 修复约束应用方式
    def count_police(*roles):
        return roles.count("police") == 1
    
    def count_mafia(*roles):
        return roles.count("mafia") == 4
    
    def count_villager(*roles):
        return roles.count("villager") == 7
    
    problem.addConstraint(count_police, players)
    problem.addConstraint(count_mafia, players)
    problem.addConstraint(count_villager, players)

    # 死亡约束：被杀/处决的人只能是villager或police，绝不能是mafia
    if deaths:
        death_players = [e["player"] for e in deaths]
        for player in death_players:
            problem.addConstraint(lambda role: role != "mafia", [player])

    # 主观判断约束
    for j in judgments:
        if j["label"] == "good":
            # 判断为好人：不能是匪徒，但可以是警察或好人
            problem.addConstraint(lambda role, player=j["player"]: role != "mafia", [j["player"]])
        else:
            # 判断为匪徒：必须是匪徒，不能是警察或好人
            problem.addConstraint(lambda role, player=j["player"]: role == "mafia", [j["player"]])

    # 查验约束：真警察的检查结果直接用，假警察的检查结果不可信
    for c in checks:
        is_true_check = (c["checker"] == suspect_police_id)
        
        if is_true_check:
            # 真警察的查验结果：直接使用，100%真实
            if c["result"] == "good":
                # 真警察查验为好人：该玩家必须是好人（不能是警察或匪徒）
                problem.addConstraint(lambda role: role == "villager", [c["target"]])
            else:
                # 真警察查验为坏人：该玩家必须是匪徒
                problem.addConstraint(lambda role: role == "mafia", [c["target"]])
        else:
            # 假警察的查验结果：不可信，不添加约束
            # 假警察可能会说谎，也可能不会说谎，不能简单取反
            pass

    # 求解
    try:
        solutions = problem.getSolutions()
        return solutions
    except Exception as e:
        print(f"求解出错: {e}")
        return []

def compare_scenarios(checks, deaths, judgments):
    """
    比较两种假设（A是警察 vs B是警察）的可行性
    """
    sols_A = solve_scenario(checks, deaths, judgments, suspect_police_id="A")
    sols_B = solve_scenario(checks, deaths, judgments, suspect_police_id="B")
    
    return {"A": sols_A, "B": sols_B}

def analyze_solutions(solutions):
    """
    分析解决方案，统计每个玩家被标记为匪徒的频率
    """
    if not solutions:
        return {}
    
    mafia_counts = defaultdict(int)
    police_counts = defaultdict(int)
    villager_counts = defaultdict(int)
    
    for solution in solutions:
        for player, role in solution.items():
            if role == "mafia":
                mafia_counts[player] += 1
            elif role == "police":
                police_counts[player] += 1
            elif role == "villager":
                villager_counts[player] += 1
    
    total_solutions = len(solutions)
    
    return {
        "mafia_probability": {player: round((count/total_solutions) * 100) for player, count in mafia_counts.items()},
        "police_probability": {player: round((count/total_solutions) * 100) for player, count in police_counts.items()},
        "villager_probability": {player: round((count/total_solutions) * 100) for player, count in villager_counts.items()},
        "total_solutions": total_solutions
    }

def get_recommendations(results):
    """
    根据推理结果给出建议
    """
    recommendations = []
    
    if not results["A"] and not results["B"]:
        recommendations.append("两种假设都无解，请检查输入数据是否有误")
        return recommendations
    
    if not results["A"]:
        recommendations.append("A假设无解 → A肯定是假警察，B为真警察")
        analysis = analyze_solutions(results["B"])
        if analysis["mafia_probability"]:
            most_likely_mafia = max(analysis["mafia_probability"].items(), key=lambda x: x[1])
            recommendations.append(f"最可能的匪徒是{most_likely_mafia[0]}号玩家（概率{most_likely_mafia[1]:.1%}）")
    
    elif not results["B"]:
        recommendations.append("B假设无解 → B肯定是假警察，A为真警察")
        analysis = analyze_solutions(results["A"])
        if analysis["mafia_probability"]:
            most_likely_mafia = max(analysis["mafia_probability"].items(), key=lambda x: x[1])
            recommendations.append(f"最可能的匪徒是{most_likely_mafia[0]}号玩家（概率{most_likely_mafia[1]:.1%}）")
    
    else:
        recommendations.append("两种假设都还有可行解，需要更多事件来排除")
        
        # 分析两种假设下的匪徒概率
        analysis_A = analyze_solutions(results["A"])
        analysis_B = analyze_solutions(results["B"])
        
        # 找出在两种假设下都被高度怀疑的玩家
        high_suspect_A = {p: prob for p, prob in analysis_A["mafia_probability"].items() if prob > 0.5}
        high_suspect_B = {p: prob for p, prob in analysis_B["mafia_probability"].items() if prob > 0.5}
        
        common_suspects = set(high_suspect_A.keys()) & set(high_suspect_B.keys())
        if common_suspects:
            recommendations.append(f"无论谁是警察，以下玩家都很可疑: {sorted(common_suspects)}")
    
    return recommendations 

def apply_werewolf_probability_adjustments(analysis_result, werewolf_adjustments):
    """
    应用匪徒概率调整到分析结果中
    
    参数：
      analysis_result: dict, 包含mafia_probability等分析结果
      werewolf_adjustments: List of dicts: {"player": int, "probability_increase": float, "reason": str}
    
    返回：
      调整后的分析结果
    """
    if not werewolf_adjustments or 'mafia_probability' not in analysis_result:
        return analysis_result
    
    adjusted_result = analysis_result.copy()
    adjusted_probabilities = adjusted_result['mafia_probability'].copy()
    
    for adjustment in werewolf_adjustments:
        player = adjustment["player"]
        increase = adjustment["probability_increase"]
        
        if player in adjusted_probabilities:
            # 增加匪徒概率，但不超过100%
            current_prob = adjusted_probabilities[player]
            new_prob = min(100.0, current_prob + increase)
            adjusted_probabilities[player] = new_prob
            print(f"匪徒概率调整：{player}号从{current_prob}%增加到{new_prob}% (+{increase}%)")
        else:
            # 如果该玩家之前没有匪徒概率，设置为调整值
            adjusted_probabilities[player] = min(100.0, increase)
            print(f"匪徒概率调整：{player}号设置为{min(100.0, increase)}%")
    
    adjusted_result['mafia_probability'] = adjusted_probabilities
    return adjusted_result 

def check_bipartite_opposition(opposition_groups):
    """
    检查对立组合是否可以构成二分图（即玩家可以分成两个阵营）
    
    参数：
      opposition_groups: List of dicts: {"player_a": int, "player_b": int, "reason": str}
    
    返回：
      dict: {
        "is_bipartite": bool,  # 是否可以分成两个阵营
        "coloring": dict,      # 染色结果 {player: "A" or "B"}
        "conflict": tuple,     # 冲突的玩家对 (player1, player2) 或 None
        "message": str         # 结果说明
      }
    """
    if not opposition_groups:
        return {
            "is_bipartite": True,
            "coloring": {},
            "conflict": None,
            "message": "暂无对立组合，无法进行阵营分析"
        }
    
    # 构建图（邻接表）
    graph = {}
    for opposition in opposition_groups:
        player_a = opposition["player_a"]
        player_b = opposition["player_b"]
        
        if player_a not in graph:
            graph[player_a] = []
        if player_b not in graph:
            graph[player_b] = []
        
        graph[player_a].append(player_b)
        graph[player_b].append(player_a)
    
    # 二分图染色
    coloring = {}
    visited = set()
    
    def dfs_coloring(node, color):
        """DFS染色函数"""
        if node in coloring:
            return coloring[node] == color
        
        coloring[node] = color
        visited.add(node)
        
        for neighbor in graph.get(node, []):
            if not dfs_coloring(neighbor, "B" if color == "A" else "A"):
                return False
        
        return True
    
    # 尝试染色所有连通分量
    for node in graph:
        if node not in visited:
            if not dfs_coloring(node, "A"):
                # 找到冲突
                conflict_node = None
                for n in graph:
                    if n in coloring:
                        for neighbor in graph[n]:
                            if neighbor in coloring and coloring[n] == coloring[neighbor]:
                                conflict_node = (n, neighbor)
                                break
                        if conflict_node:
                            break
                
                return {
                    "is_bipartite": False,
                    "coloring": coloring,
                    "conflict": conflict_node,
                    "message": f"无法分成两个阵营！存在冲突：{conflict_node[0]}号和{conflict_node[1]}号既对立又可能同阵营"
                }
    
    # 检查是否所有玩家都被染色
    all_players = set()
    for opposition in opposition_groups:
        all_players.add(opposition["player_a"])
        all_players.add(opposition["player_b"])
    
    uncolored = all_players - set(coloring.keys())
    
    if uncolored:
        return {
            "is_bipartite": True,
            "coloring": coloring,
            "conflict": None,
            "message": f"可以分成两个阵营，但{len(uncolored)}个玩家未参与对立关系"
        }
    
    # 统计各阵营人数
    team_a = [p for p, c in coloring.items() if c == "A"]
    team_b = [p for p, c in coloring.items() if c == "B"]
    
    return {
        "is_bipartite": True,
        "coloring": coloring,
        "conflict": None,
        "message": f"可以分成两个阵营！阵营A({len(team_a)}人): {sorted(team_a)}号, 阵营B({len(team_b)}人): {sorted(team_b)}号"
    }

def analyze_opposition_camp_analysis(opposition_groups):
    """
    分析对立组合的阵营分布
    
    参数：
      opposition_groups: List of dicts: {"player_a": int, "player_b": int, "reason": str}
    
    返回：
      dict: 包含阵营分析结果
    """
    bipartite_result = check_bipartite_opposition(opposition_groups)
    
    # 构建对立关系图
    opposition_edges = []
    for opposition in opposition_groups:
        opposition_edges.append((opposition["player_a"], opposition["player_b"]))
    
    return {
        "bipartite_result": bipartite_result,
        "opposition_edges": opposition_edges,
        "total_oppositions": len(opposition_groups)
    } 