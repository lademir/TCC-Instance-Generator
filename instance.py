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
    def __init__(self, _id: int, duracao: int, qtde_recurso: List[int]):
        self.id = _id
        self.duracao: int = duracao
        self.qtde_recurso: List[int] = qtde_recurso

class Task:
    def __init__(self, _id: int, duracao: int, sucessores: Set[int], modos: List[Mode]):
        self.id: int = _id
        self.duracao: int = duracao
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
            out += f"Modo {modo.id} - Duração: {modo.duracao} - Uso de recurso: {modo.qtde_recurso}\n"
        return out
class Instance:
    def __init__(self, seed, qtde_tarefas) -> None:
        # constantes
        self.max_duracao = 120
        self.min_duracao = 10
        self.max_recursos = 8
        self.min_recursos = 2
        self.max_uso_recurso = 100
        self.min_uso_recurso = 10
        self.max_sucessores = 5
        
        # Use a seed para inicializar o gerador de números aleatórios
        self.seed: int = seed
        random.seed(seed)
        
        # Defina a quantidade inicial de projetos
        self.qtde_projetos = 1
        self.tarefas: Dict[int, Task] = {}

        # Recursos
        self.qtde_recursos: int = random.randint(self.min_recursos, self.max_recursos) 
        self.recursos: List[int] = []
        
        # Gere a quantidade de tarefas com base na seed
        self.qtde_tarefas: int = qtde_tarefas

        self.start()
    
    def __str__(self):
        out = f"Seed: {self.seed} - Quantidade de tarefas: {self.qtde_tarefas} - Quantidade de recursos: {self.qtde_recursos}\n"
        out += f"Recursos renováveis {self.recursos}\n"
        for i in range(self.qtde_tarefas + 2):
            out += f"{self.tarefas[i]}\n"
        return out

    def start(self):
        self.gerar_recursos()
        self.gerar_tarefas()
        self.gerar_relacao_precedencia()

    def gerar_recursos(self):
        for _ in range(self.qtde_recursos):
            self.recursos.append(random.randint(100,1000))

    def gerar_tarefas(self):
        self.tarefas[0] = Task(0, 0, set(random.sample(range(1, self.qtde_tarefas + 1), random.randint(1, (self.qtde_tarefas % 10) + 1))), [Mode(0, 0, [0 for _ in range(self.qtde_recursos)])] )
        self.tarefas[self.qtde_tarefas + 1] = Task(self.qtde_tarefas + 1, 0, set(), [Mode(0, 0, [0 for _ in range(self.qtde_recursos)])] )

        for i in range(1, self.qtde_tarefas + 1):
            qtde_modos = random.randint(1, 4)
            modos = []
            for j in range(qtde_modos):
                duracao = random.randint(self.min_duracao, self.max_duracao)
                fator_uso = duracao/self.max_duracao
                uso_recurso = []
                for k in range(self.qtde_recursos):
                    recurso = random.randint(self.min_uso_recurso, self.max_uso_recurso)
                    recurso = int(recurso/fator_uso)
                    uso_recurso.append(recurso)
                modos.append(Mode(j, duracao, uso_recurso))
            self.tarefas[i] = Task(i, random.randint(self.min_duracao, self.max_duracao), set(), modos)
        

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


    def visualizar_grafo(self):
        grafo = Graph()
        for tarefa in self.tarefas.values():
            for sucessor in tarefa.sucessores:
                grafo.add_edge(tarefa.id, sucessor)
            grafo.add_node(tarefa.id)
        grafo.visualize(self.seed, self.qtde_tarefas)


if __name__ == "__main__":
    instance = Instance(seed=1916069400, qtde_tarefas=10)
    instance.visualizar_grafo()