
from typing import List
from queue import Queue

def dfs(graph: List[List[int]], start:int, end:int, visited: dict[int,bool], path_length: int):
    if start == end:
        return path_length >= 2
    
    visited[start] = True
    for neighbor in graph[start]:
        if not visited[neighbor]:
            if dfs(graph, neighbor, end, visited, path_length + 1):
                return True
    
    visited[start] = False
    return False

def is_redundant_arc(graph:List[List[int]], h:int, j:int):
    visited = {node: False for node in range(len(graph))}
    return dfs(graph, h, j, visited, 0)

def find_redundant_arcs(graph:List[set[int]]):
    redundant_arcs = []
    graph_to_list = [list(h) for h in graph]
    for h, i in enumerate(graph_to_list):
        for j in i:
            if is_redundant_arc(graph_to_list, h, j):
                redundant_arcs.append((h, j))
    return redundant_arcs


def indiretos(graph: List[set[int]], v: int) -> list[int]:
    indiretos = []
    queue = Queue()
    queue.put(v)
    visited = {node: False for node in range(len(graph))}
    visited[v] = True
    while not queue.empty():
        v = queue.get()
        for w in graph[v]:
            if not visited[w]:
                indiretos.append(w)
                visited[w] = True
                queue.put(w)
    return indiretos


if __name__ == "__main__":
    dag = [
        {2,6,7},
        {8,9,4},
        {11},
        {5,8,1},
        {11},
        {11},
        {10,3,8},
        {10,1},
        {5,9,4},
        {4},
        {3,5},
        {},
    ]
    total_arcs = []
    for idx,i in enumerate(dag):
        for j in i:
            # print(f"{idx} -> {j}")
            total_arcs.append((idx,j))
    num_atividades = len(dag) - 2
    redundantes = find_redundant_arcs(dag)
    non_redundant_arcs = [arc for arc in total_arcs if arc not in redundantes]
    maximal_non_redundant_arcs = num_atividades - 2 + ((num_atividades-2)/2)**2
    complexidade = len(non_redundant_arcs) / len(dag)

    print(f"Numero de atividades: {num_atividades}")
    print(f"Numero maximo de arcos nao redundantes: {maximal_non_redundant_arcs}")
    print(f"Arcos totais: {len(total_arcs)}")
    print(f"Arcos nao redundantes: {len(non_redundant_arcs)}")
    print(f"Arcos redundantes: {len(redundantes)}")
    print(f"Complexidade: {complexidade}")
    