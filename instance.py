import random
import matplotlib.pyplot as plt
from typing import List, Dict, Set
import graphviz

class Graph:
    def __init__(self):
        self.nodes: Set[int] = set()
        self.edges = []

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, start, end):
        self.edges.append((start, end))

    def visualize(self, seed, qtde_tarefas):
        #* Usar graphviz para visualizar o grafo
        dot = graphviz.Digraph(comment='Grafo de precedência')
        for node in self.nodes:
            dot.node(str(node))
        for start, end in self.edges:
            dot.edge(str(start), str(end))
        
        import os
        if not os.path.exists('graphs'):
            os.mkdir('graphs')
        
        path = dot.render(filename=f"{seed}-{qtde_tarefas}", directory='graphs', format='png', view=True, cleanup=True)
        print(f"Visualização do grafo salva em {path}")

class Mode:
    def __init__(self, _id: int, duracao: int, qtde_recurso_renovavel: List[int], qtde_recurso_nao_renovavel: List[int]):
        self.id = _id
        self.duracao: int = duracao
        self.qtde_recurso_renovavel: List[int] = qtde_recurso_renovavel
        self.qtde_recurso_nao_renovavel: List[int] = qtde_recurso_nao_renovavel

class Task:
    def __init__(self, _id: int, sucessores: Set[int], modos: List[Mode]):
        self.id: int = _id
        self.sucessores: Set[int] = sucessores
        self.antecessores: Set[int] = set()
        self.qtde_recurso: List[int] = []
        self.modos: List[Mode] = modos

    def add_sucessor(self, sucessor: int):
        self.sucessores.add(sucessor)

    def add_antecessor(self, antecessor: int):
        self.antecessores.add(antecessor)

    def __str__(self):
        out = f"Tarefa {self.id} - Sucessores: ["
        for sucessor in self.sucessores:
            out += f"{sucessor}, "
        out += "]"
        out += " \nModos:\n"
        for modo in self.modos:
            out += f"Modo {modo.id} - Duração: {modo.duracao} - Uso de recurso renovavel: {modo.qtde_recurso_renovavel} - Uso de recurso nao renovavel: {modo.qtde_recurso_nao_renovavel}\n"
        return out
class Instance:
    def __init__(self, seed, qtde_tarefas) -> None:
        if qtde_tarefas < 7:
            raise ValueError("Quantidade de tarefas deve ser maior ou igual a 7")
        # constantes
        self.max_duracao = 120
        self.min_duracao = 10
        self.max_recursos = 5
        self.min_recursos = 2
        self.max_uso_recurso = 100
        self.min_uso_recurso = 10
        self.min_modos = 1
        self.max_modos = 4
        self.max_sucessores = int(3)
        self.resource_factor = 0.5 # O que vai decidir se o recurso r é usado ou não pela atividade
        
        # Use a seed para inicializar o gerador de números aleatórios
        self.seed: int = seed
        random.seed(seed)
        
        # Defina a quantidade inicial de projetos
        self.qtde_projetos = 1
        self.tarefas: Dict[int, Task] = {}

        # Recursos
        self.qtde_recursos_renovavel: int = random.randint(self.min_recursos, self.max_recursos) 
        self.qtde_recursos_nao_renovavel: int = random.randint(self.min_recursos, self.max_recursos) 
        self.recursos_renovaveis: List[int] = []
        self.recursos_nao_renovaveis: List[int] = []

        # Gere a quantidade de tarefas com base na seed
        self.qtde_tarefas: int = qtde_tarefas

        self.start()
    
    def __str__(self):
        out = f"Seed: {self.seed} - Quantidade de tarefas: {self.qtde_tarefas} - Quantidade de recursos: {self.qtde_recursos_renovavel} - Quantidade de recursos nao renovaveis: {self.qtde_recursos_nao_renovavel}\n"
        out += f"Recursos renováveis {self.recursos_renovaveis}\n"
        out += f"Recursos nao renovaveis {self.recursos_nao_renovaveis}\n"
        for i in range(self.qtde_tarefas + 2):
            out += f"{self.tarefas[i]}\n"
        return out
    
    def calculate_resource_factor_for_type(self, renovavel: bool):
        soma = 0
        for tarefa in self.tarefas.values():
            soma_tarefa = 0
            for modos in tarefa.modos:
                if renovavel:
                    for recurso in modos.qtde_recurso_renovavel:
                        if recurso > 0:
                            soma_tarefa += 1
                else:
                    for recurso in modos.qtde_recurso_nao_renovavel:
                        if recurso > 0:
                            soma_tarefa += 1
            soma += soma_tarefa/len(tarefa.modos)
        
        if renovavel:
            soma = soma/self.qtde_recursos_renovavel
        else:
            soma = soma/self.qtde_recursos_nao_renovavel

        return soma / self.qtde_tarefas

    def start(self):
        self.gerar_tarefas()
        self.gerar_relacao_precedencia_2()
        self.gerar_recursos()

    def gerar_recursos(self):
        for _ in range(self.qtde_recursos_renovavel):
            self.recursos_renovaveis.append(random.randint(10,100)) # min e max que pode ser usado por uma atividade
        for _ in range(self.qtde_recursos_nao_renovavel):
            self.recursos_nao_renovaveis.append(random.randint(100,350))

    def gerar_tarefas(self):
        self.tarefas[0] = Task(0, set(random.sample(range(1, self.qtde_tarefas + 1), random.randint(1, (self.qtde_tarefas % 10) + 1))), [Mode(0, 0, [0 for _ in range(self.qtde_recursos_renovavel)],[0 for _ in range(self.qtde_recursos_nao_renovavel)])] )
        self.tarefas[self.qtde_tarefas + 1] = Task(self.qtde_tarefas + 1, set(), [Mode(0, 0, [0 for _ in range(self.qtde_recursos_renovavel)], [0 for _ in range(self.qtde_recursos_nao_renovavel)])])

        for i in range(1, self.qtde_tarefas + 1):
            qtde_modos = random.randint(self.min_modos, self.max_modos)
            modos = []
            for j in range(qtde_modos):
                duracao = random.randint(self.min_duracao, self.max_duracao)
                fator_uso = duracao/self.max_duracao
                uso_recurso_renovavel = []
                for k in range(self.qtde_recursos_renovavel):
                    vai_usar_o_recurso = random.random() < self.resource_factor
                    recurso = 0
                    if vai_usar_o_recurso:
                        recurso = random.randint(self.min_uso_recurso, self.max_uso_recurso)
                        recurso = int(recurso/fator_uso)
                    uso_recurso_renovavel.append(recurso)
                uso_recurso_nao_renovavel = []
                for k in range(self.qtde_recursos_nao_renovavel):
                    vai_usar_o_recurso = random.random() < self.resource_factor
                    recurso = 0
                    if vai_usar_o_recurso:
                        recurso = random.randint(self.min_uso_recurso, self.max_uso_recurso)
                        recurso = int(recurso/fator_uso)
                    uso_recurso_nao_renovavel.append(recurso)
                modos.append(Mode(j, duracao, uso_recurso_renovavel,uso_recurso_nao_renovavel))
            self.tarefas[i] = Task(i, set(), modos)
        

    def gerar_relacao_precedencia(self):
        for i in range(1, self.qtde_tarefas):
            sucessores = random.sample(range(i + 1, self.qtde_tarefas + 1), random.randint(0, (self.qtde_tarefas - i) % self.max_sucessores))
            for sucessor in sucessores:
                self.tarefas[i].add_sucessor(sucessor)
                self.tarefas[sucessor].add_antecessor(i)
        
        for i in range(1, self.qtde_tarefas + 1):
            if len(self.tarefas[i].sucessores) == 0:
                self.tarefas[i].add_sucessor(self.qtde_tarefas + 1)
            if len(self.tarefas[i].antecessores) == 0:
                self.tarefas[0].add_sucessor(i)


    
    def gerar_relacao_precedencia_2(self):
        num_start = [3, 3]
        num_finish = [3, 3]
        empty_list: set[int] = set()
        sucessores: List[set[int]] = [empty_list.copy() for _ in range(self.qtde_tarefas + 2)]
        predecessores: List[set[int]] = [empty_list.copy() for _ in range(self.qtde_tarefas + 2)]
        total_arcs = []
        activities = list(range(1, self.qtde_tarefas + 1))

        start_activities = random.sample(activities, random.choice(num_start))
        # finish activities precisam ser diferentes de start activities
        sucessores[0] = set(start_activities)
        for start in start_activities:
            activities.remove(start)
            predecessores[start] = {0}
            total_arcs.append((0, start))
        finish_activities = random.sample(activities, random.choice(num_finish))
        predecessores[self.qtde_tarefas + 1] = set(finish_activities)
        for finish in finish_activities:
            activities.remove(finish)
            sucessores[finish] = {self.qtde_tarefas + 1}
            total_arcs.append((finish, self.qtde_tarefas + 1))
        maximal_non_redundant_arcs = 0
        if self.qtde_tarefas % 2 == 0:
            maximal_non_redundant_arcs = self.qtde_tarefas - 2 + ((self.qtde_tarefas-2)/2)**2
            pass
        else:
            maximal_non_redundant_arcs = self.qtde_tarefas - 2 + ((self.qtde_tarefas-1)/2) * ((self.qtde_tarefas-3)/2)
            pass

        # media dos arcos nao redundantes por nodo
        c = 0
        non_start_activities = activities.copy() + finish_activities.copy()
        non_start_activities = sorted(non_start_activities)
        

        def has_path(graph, start, end, visited):
            if start == end:
                return True
            visited.add(start)
            for neighbor in graph[start]:
                if neighbor not in visited and has_path(graph, neighbor, end, visited):
                    return True
            visited.remove(start)
            return False

        
        non_redundant_arcs = []

        for ac in non_start_activities:
            pred = random.choice(start_activities + activities)
            while pred == ac or len(sucessores[pred]) >= self.max_sucessores or has_path(sucessores, ac, pred, set()):
                pred = random.choice(start_activities + activities)
            
            predecessores[ac].add(pred)
            sucessores[pred].add(ac)
            total_arcs.append((pred, ac))

        for ac in sorted(start_activities + activities):
            if len(sucessores[ac]) == 0:
                # print(f"Colocando sucessor para {ac}")
                suc = random.choice(non_start_activities)  
                while suc == ac or has_path(sucessores, suc, ac, set()):
                    suc = random.choice(non_start_activities)
                sucessores[ac].add(suc)
                predecessores[suc].add(ac)
                total_arcs.append((ac, suc))
        
        redundant_arcs = find_redundant_arcs(sucessores)
        non_redundant_arcs = [arc for arc in total_arcs if arc not in redundant_arcs]
        c = len(non_redundant_arcs)/len(sucessores)
        

        # for i in range(100):
        while c < 1.5 and len(non_redundant_arcs) < maximal_non_redundant_arcs:
            for ac in sorted(activities + finish_activities):
                pred = random.choice(activities + start_activities)
                while pred == ac:
                    pred = random.choice(activities + start_activities)
                if  len(sucessores[pred]) < self.max_sucessores and not has_path(sucessores, ac, pred, set()): # and pred not in sucessores[ac]
                    predecessores[ac].add(pred)
                    sucessores[pred].add(ac)
                    total_arcs.append((pred, ac))
                    total_arcs = list(set(total_arcs))

            # se todos possuem o maximo de sucessores, parar de adicionar arcos
            if all([len(sucessores[ac]) == self.max_sucessores for ac in (activities )]):
                # print("All activities have the maximum number of successors")
                break

            redundant_arcs = find_redundant_arcs(sucessores)
            non_redundant_arcs = [arc for arc in total_arcs if arc not in redundant_arcs]
            c = len(non_redundant_arcs)/len(sucessores)


        # for i in range(self.qtde_tarefas + 2):
        #     print(f"{i}: {predecessores[i]} - {sucessores[i]}")

        for i in range(self.qtde_tarefas + 2):
            self.tarefas[i].sucessores = sucessores[i]
            self.tarefas[i].antecessores = predecessores[i]

        
    def visualizar_grafo(self):
        grafo = Graph()
        for tarefa in self.tarefas.values():
            for sucessor in tarefa.sucessores:
                grafo.add_edge(tarefa.id, sucessor)
            grafo.add_node(tarefa.id)
        grafo.visualize(self.seed, self.qtde_tarefas)


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


if __name__ == "__main__":
    instance = Instance(seed=19, qtde_tarefas=10)
    instance.visualizar_grafo()
    # with open('instance.txt', 'w') as f:
    #     f.write(f"RF renovavel: {instance.calculate_resource_factor_for_type(renovavel=True)}\n")
    #     f.write(f"RF nao renovavel: {instance.calculate_resource_factor_for_type(renovavel=False)}\n")
    #     f.write(str(instance))
    