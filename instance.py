import random
import matplotlib.pyplot as plt
from typing import List, Dict, Set, Any
import graphviz
import logging

from utils import find_redundant_arcs, indiretos

class Graph:
    def __init__(self):
        self.nodes: Set[int] = set()
        self.edges = []

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, start, end):
        self.edges.append((start, end))

    def visualize(self, seed, qtde_tarefas, save = False):
        dot = graphviz.Digraph(comment='Grafo de precedência', graph_attr={'rankdir':'LR'})
        for node in self.nodes:
            dot.node(str(node))
        for start, end in self.edges:
            dot.edge(str(start), str(end))
        
        import os
        if not os.path.exists('graphs'):
            os.mkdir('graphs')

        
        if save:
            path = dot.render(filename=f"{seed}-{qtde_tarefas}", directory='graphs', format='png', view=True, cleanup=True)
            print(f"Visualização do grafo salva em {path}")
        else:
            dot.render(format='png', view=True, cleanup=True)


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
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
        # constantes
        self.max_duracao = 50
        self.min_duracao = 10
        self.max_recursos = 5
        self.min_recursos = 2
        self.fator_max_uso_recurso = 100
        self.fator_min_uso_recurso = 10
        self.min_modos = 1
        self.max_modos = 4
        self.max_sucessores = int(3)
        self.resource_factor = 0.5 # O que vai decidir se o recurso r é usado ou não pela atividade
        self.resource_strength = 0.2 # O que vai influenciar na quantidade final de recurso renovavel
        self.complexidade_maxima = 1.5
        self.min_atividades_iniciais = 3
        self.max_atividades_iniciais = 3
        self.min_atividades_finais = 3
        self.max_atividades_finais = 3
        
        # Use a seed para inicializar o gerador de números aleatórios
        self.seed: int = seed
        random.seed(seed)

        self.horizon = 0
        
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

        self.possivel = True

        self.start()
    
    def print(self):
        out = f"Seed: {self.seed} - Quantidade de tarefas: {self.qtde_tarefas} - Quantidade de recursos renovaveis: {self.qtde_recursos_renovavel} - Quantidade de recursos nao renovaveis: {self.qtde_recursos_nao_renovavel}\n"
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
        try:
            self.gerar_tarefas()
            self.gerar_relacao_precedencia_2()
            self.gerar_recursos()
            print(f"Finalizou a geração da instância com seed {self.seed}.")
        except Exception as e:
            # print(f"Seed: {self.seed} não funciona, precisa recomeçar com outra seed.")
            logging.error(f"Seed: {self.seed} não funciona, precisa recomeçar com outra seed.")
            self.possivel = False
            
            

    def gerar_recursos(self):
        # for _ in range(self.qtde_recursos_renovavel):
        #     self.recursos_renovaveis.append(random.randint(10,100)) # min e max que pode ser usado por uma atividade
        # for _ in range(self.qtde_recursos_nao_renovavel):
        #     self.recursos_nao_renovaveis.append(random.randint(100,350))

        maximal_non_renewable = [0 for _ in range(self.qtde_recursos_nao_renovavel)]
        minimal_non_renewable = [999999 for _ in range(self.qtde_recursos_nao_renovavel)]
        maximal_renewable = [0 for _ in range(self.qtde_recursos_renovavel)]
        minimal_renewable = [999999 for _ in range(self.qtde_recursos_renovavel)]
        k_non_renewable_min = [0 for _ in range(self.qtde_recursos_nao_renovavel)]
        k_non_renewable_max = [0 for _ in range(self.qtde_recursos_nao_renovavel)]
        k_renewable_min = [0 for _ in range(self.qtde_recursos_renovavel)]
        horizon = 0

        for i, task in self.tarefas.items():
            if i == 0 or i == self.qtde_tarefas + 1:
                continue
            horizon_i = 0
            for modo in task.modos:
                horizon_i = max(horizon_i, modo.duracao)
                for j in range(self.qtde_recursos_renovavel):
                    maximal_renewable[j] = max(maximal_renewable[j], modo.qtde_recurso_renovavel[j])
                    minimal_renewable[j] = min(minimal_renewable[j], modo.qtde_recurso_renovavel[j])
                    

                for j in range(self.qtde_recursos_nao_renovavel):
                    maximal_non_renewable[j] = max(maximal_non_renewable[j], modo.qtde_recurso_nao_renovavel[j])
                    minimal_non_renewable[j] = min(minimal_non_renewable[j], modo.qtde_recurso_nao_renovavel[j])
                    k_non_renewable_min[j] += minimal_non_renewable[j]
                    k_non_renewable_max[j] += maximal_non_renewable[j]
            horizon += horizon_i

        min_usage_renw = [[999999 for _ in range(self.qtde_recursos_renovavel)] for _ in range(self.qtde_tarefas+2)]
        for i, task in self.tarefas.items():
            if i == 0 or i == self.qtde_tarefas + 1:
                continue
            for modo in task.modos:
                for j in range(self.qtde_recursos_renovavel):
                    min_usage_renw[i][j] = min(min_usage_renw[i][j], modo.qtde_recurso_renovavel[j])
            for j in range(self.qtde_recursos_renovavel):
                k_renewable_min[j] = max(k_renewable_min[j], min_usage_renw[i][j])
            pass
        # print(f"Min usage renw: {min_usage_renw}")
        # print(f"Max usage renw: {k_renewable_min}")
        kjr_ = [[0 for _ in range(self.qtde_recursos_renovavel)] for _ in range(self.qtde_tarefas + 2)]
        mjr_ = [[0 for _ in range(self.qtde_recursos_renovavel)] for _ in range(self.qtde_tarefas + 2)]
        for idx, task in self.tarefas.items():
            for modo in task.modos:
                for j in range(self.qtde_recursos_renovavel):
                    if kjr_[idx][j] < modo.qtde_recurso_renovavel[j]:
                        kjr_[idx][j] = modo.qtde_recurso_renovavel[j]
                        mjr_[idx][j] = modo.id

        # p(kjr_)
        # p(mjr_)

        ordencao_topologica = self.get_ordencao_topologica()
        utilizacao_de_recurso = [[0 for _ in range(self.qtde_recursos_renovavel)] for _ in range(horizon)]
        tempo_inicio_tarefas = [[0 for _ in range(self.qtde_recursos_renovavel)] for _ in range(self.qtde_tarefas + 2)]
        for i in ordencao_topologica:
            for j in range(self.qtde_recursos_renovavel):
                qtde_recurso = self.tarefas[i].modos[mjr_[i][j]].qtde_recurso_renovavel[j]
                tempo_inicio = 0
                for antecessor in self.tarefas[i].antecessores:
                    tempo_inicio = max(tempo_inicio, tempo_inicio_tarefas[antecessor][j] + self.tarefas[antecessor].modos[mjr_[antecessor][j]].duracao)
                tempo_inicio_tarefas[i][j] = tempo_inicio
                for t in range(tempo_inicio, tempo_inicio + self.tarefas[i].modos[mjr_[i][j]].duracao):
                    utilizacao_de_recurso[t][j] += qtde_recurso
        
        # for idx, t_ini in enumerate(tempo_inicio_tarefas):
        #     print(f"Tarefa {idx}: {t_ini} - modo {mjr_[idx]}")
        
        max_usage_renewable_per_resource_type = [0 for _ in range(self.qtde_recursos_renovavel)]
        for i in range(self.qtde_recursos_renovavel):
            for j in range(horizon):
                max_usage_renewable_per_resource_type[i] = max(max_usage_renewable_per_resource_type[i], utilizacao_de_recurso[j][i])
        
        # print(f"Max usage renewable per resource type: {max_usage_renewable_per_resource_type}")

        # print(f"Maximal renewable: {maximal_renewable}")
        # print(f"Minimal renewable: {minimal_renewable}")
        # print(f"Maximal non renewable: {maximal_non_renewable}")
        # print(f"Minimal non renewable: {minimal_non_renewable}")
        # print(f"K non renewable min: {k_non_renewable_min}")
        # print(f"K non renewable max: {k_non_renewable_max}")
        # print(f"max_usage_renewable_per_resource_type: {max_usage_renewable_per_resource_type}")
        # print(f"K renewable min: {k_renewable_min}")

        import math
        krn = [0 for _ in range(self.qtde_recursos_renovavel)]
        knr = [0 for _ in range(self.qtde_recursos_nao_renovavel)]
        for rr in range(self.qtde_recursos_renovavel):
            krn[rr] = k_renewable_min[rr] + math.ceil(self.resource_strength * (max_usage_renewable_per_resource_type[rr] - k_renewable_min[rr]))
        for nr in range(self.qtde_recursos_nao_renovavel):
            knr[nr] = k_non_renewable_min[nr] + math.ceil(self.resource_strength * (k_non_renewable_max[nr] - k_non_renewable_min[nr]))

        # print(f"Renovaveis: {krn}")
        # print(f"Nao-renovaveis: {knr}")
        self.recursos_renovaveis = krn
        self.recursos_nao_renovaveis = knr

        pass
    
    def get_ordencao_topologica(self):
        import queue
        ordencao_topologica = []
        grau_entrada = [0 for _ in range(self.qtde_tarefas + 2)]
        for idx, task in self.tarefas.items():
            grau_entrada[idx] = len(task.antecessores)
        q = queue.Queue()
        for idx, task in self.tarefas.items():
            if grau_entrada[idx] == 0:
                q.put(idx)
        while not q.empty():
            u = q.get()
            ordencao_topologica.append(u)
            for v in self.tarefas[u].sucessores:
                grau_entrada[v] -= 1
                if grau_entrada[v] == 0:
                    q.put(v)
        return ordencao_topologica
    

    def gerar_tarefas(self):
        self.tarefas[0] = Task(0, set(random.sample(range(1, self.qtde_tarefas + 1), random.randint(1, (self.qtde_tarefas % 10) + 1))), [Mode(0, 0, [0 for _ in range(self.qtde_recursos_renovavel)],[0 for _ in range(self.qtde_recursos_nao_renovavel)])] )
        self.tarefas[self.qtde_tarefas + 1] = Task(self.qtde_tarefas + 1, set(), [Mode(0, 0, [0 for _ in range(self.qtde_recursos_renovavel)], [0 for _ in range(self.qtde_recursos_nao_renovavel)])])

        for i in range(1, self.qtde_tarefas + 1):
            qtde_modos = random.randint(self.min_modos, self.max_modos)
            modos = []
            maximal_duration = 0
            for j in range(qtde_modos):
                duracao = random.randint(self.min_duracao, self.max_duracao)
                maximal_duration = max(maximal_duration, duracao)
                fator_uso = duracao/self.max_duracao
                uso_recurso_renovavel = []
                for k in range(self.qtde_recursos_renovavel):
                    vai_usar_o_recurso = random.random() < self.resource_factor
                    recurso = 0
                    if vai_usar_o_recurso:
                        recurso = random.randint(self.fator_min_uso_recurso, self.fator_max_uso_recurso)
                        recurso = int(recurso/fator_uso)
                    uso_recurso_renovavel.append(recurso)
                uso_recurso_nao_renovavel = []
                for k in range(self.qtde_recursos_nao_renovavel):
                    vai_usar_o_recurso = random.random() < self.resource_factor
                    recurso = 0
                    if vai_usar_o_recurso:
                        recurso = random.randint(self.fator_min_uso_recurso, self.fator_max_uso_recurso)
                        recurso = int(recurso/fator_uso)
                    uso_recurso_nao_renovavel.append(recurso)
                modos.append(Mode(j, duracao, uso_recurso_renovavel,uso_recurso_nao_renovavel))
            self.horizon += maximal_duration
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


    
    def gerar_relacao_precedencia_2(self) -> None:
        num_start = [self.min_atividades_iniciais, self.max_atividades_iniciais]
        num_finish = [self.min_atividades_iniciais, self.max_atividades_finais]
        empty_list: set[int] = set()
        sucessores: List[set[int]] = [empty_list.copy() for _ in range(self.qtde_tarefas + 2)]
        predecessores: List[set[int]] = [empty_list.copy() for _ in range(self.qtde_tarefas + 2)]
        total_arcs = []
        activities = list(range(1, self.qtde_tarefas + 1))

        #* Passo 1
        start_activities = random.sample(activities, random.choice(num_start))
        # finish activities precisam ser diferentes de start activities
        sucessores[0] = set(start_activities)
        for start in start_activities:
            predecessores[start] = {0}
            total_arcs.append((0, start))
        finish_activities = random.sample(activities, random.choice(num_finish))
        predecessores[self.qtde_tarefas + 1] = set(finish_activities)
        for finish in finish_activities:
            sucessores[finish] = {self.qtde_tarefas + 1}
            total_arcs.append((finish, self.qtde_tarefas + 1))

        
        # Single activities sao as que sao tanto iniciais quanto finais ao mesmo tempo
        single_activities = list(set(start_activities).intersection(set(finish_activities)))

        # removendo as atividades iniciais e finais da lista de atividades
        activities = set(activities)
        finish_activities = set(finish_activities)
        start_activities = set(start_activities)

        for start in start_activities:
            activities.discard(start)
        for finish in finish_activities:
            activities.discard(finish)
        for single in single_activities:
            finish_activities.discard(single)
            start_activities.discard(single)

        activities = list(activities)
        start_activities = list(start_activities)
        finish_activities = list(finish_activities)

        # print(f"Start activities: {start_activities}")
        # print(f"Finish activities: {finish_activities}")
        # print(f"Single activities: {single_activities}")
        # print(f"Activities: {activities}")

        # return
        
        # Todo: Analisar quais atividades vao ser contabilizadas nesse calculo para saber a quantidade maxima de arcos nao redundatnes, porque alguns nos vao ser desconsiderados
        
        maximal_non_redundant_arcs = 0
        num_atividades = self.qtde_tarefas - len(start_activities) - len(finish_activities) - len(single_activities)
        if num_atividades % 2 == 0:
            maximal_non_redundant_arcs = num_atividades - 2 + ((num_atividades-2)/2)**2
        else:
            maximal_non_redundant_arcs = num_atividades - 2 + ((num_atividades-1)/2) * ((num_atividades-3)/2)

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

        #* Passo 2
        for ac in non_start_activities:
            pred = random.choice(start_activities + activities)
            while pred == ac or len(sucessores[pred]) >= self.max_sucessores or self.is_redundant(pred, ac, sucessores, predecessores):
                pred = random.choice(start_activities + activities)
            # print(f"Pred: {pred} - Ac: {ac}")
            predecessores[ac].add(pred)
            sucessores[pred].add(ac)
            total_arcs.append((pred, ac))

        # print("Finalizou passo 2")
        # for i in range(len(sucessores)):
        #     print(f"{i}: {predecessores[i]} - {sucessores[i]}")
        
        #* Passo 3
        for ac in sorted(start_activities + activities):
            if len(sucessores[ac]) == 0:
                # print(f"Colocando sucessor para {ac}")
                # p(sucessores)
                suc = random.choice(non_start_activities)  
                cont = 1
                while suc == ac or self.is_redundant(ac, suc, sucessores, predecessores):
                    suc = random.choice(non_start_activities)
                    cont += 1
                    # print(f"Cont: {cont} - len: {len(non_start_activities)}")
                    if cont >= len(non_start_activities):
                        raise Exception("Nao foi possivel adicionar um sucessor")
                        # warnings.warn(f"seed: {self.seed} não funciona, precisa recomeçar com outra seed.")
                        
                        pass
                
                # print(f"Pred: {ac} - Suc: {suc}")
                sucessores[ac].add(suc)
                predecessores[suc].add(ac)
                total_arcs.append((ac, suc))

        # print("Finalizou passo 3")
        
        redundant_arcs = find_redundant_arcs(sucessores)
        non_redundant_arcs = [arc for arc in total_arcs if arc not in redundant_arcs]
        c = len(non_redundant_arcs)/len(sucessores)

        #* Passo 4: Adicionar arestas redundantes ate que algum limite seja estabelecido
        for i in range(100):
        # while c < self.complexidade_maxima and len(non_redundant_arcs) < maximal_non_redundant_arcs:
            # print(f"Complexidade: {c} - {len(non_redundant_arcs)}")
            #* Para cada atividade, vai tentar adicionar um predecessor
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


        # exit()

        for i in range(self.qtde_tarefas + 2):
            self.tarefas[i].sucessores = sucessores[i]
            self.tarefas[i].antecessores = predecessores[i]

        
    def visualizar_grafo(self, save = False):
        if not self.possivel:
            logging.error(f"Seed: {self.seed} não é possível visualizar o grafo.")
            return
        grafo = Graph()
        for tarefa in self.tarefas.values():
            for sucessor in tarefa.sucessores:
                grafo.add_edge(tarefa.id, sucessor)
            grafo.add_node(tarefa.id)
        grafo.visualize(self.seed, self.qtde_tarefas, save=save)

    def is_redundant(self, i:int, j:int, sucs: list[set[int]], preds: list[set[int]]) -> bool:
            #* 1: (i, j) Se j é um sucessor indireto de i
        if j in indiretos(sucs, i):
            return True

        #* 2: (i, j) se i e j tiverem um predecessor em comum
        #* Intercessao entre predecessores imediatos de j com predecessores (indiretos) de i for diferente de vazio
        pred_imediato_j = preds[j]
        pred_indireto_i = set(indiretos(preds, i))
        if len(pred_imediato_j.intersection(pred_indireto_i)) > 0:
            return True

        #* 3: (i, j) se existe um k que é sucessor indireto de j tal que a intercessao entre os predecessores imediatos de k com os predecessores de i seja diferente de vazio
        for k in indiretos(sucs, j):
            pred_imediato_k = preds[k]
            if len(pred_imediato_k.intersection(pred_indireto_i)) > 0:
                return True

        #* 4: (i, j) se a intercessao entre os sucessores imediatos de i com sucessores (indiretos) de j for diferente de vazio
        suc_imediato_i = sucs[i]
        suc_indireto_j = set(indiretos(sucs, j))
        if len(suc_imediato_i.intersection(suc_indireto_j)) > 0:
            return True

        return False
        
    def __str__(self):
        out = ""
        out += "seed " + str(self.seed) + "\n"
        out += "horizon " + str(self.horizon) + "\n"
        out += "jobs " + str(self.qtde_tarefas+2) + "\n"
        out += "RESOURCES\n"
        out += "renewable " + str(self.qtde_recursos_renovavel) + " r\n"
        out += "non-renewable " + str(self.qtde_recursos_nao_renovavel) + " n\n"
        out += "double " + str(0) + " d\n"
        out += "*"*25 + "\n"
        out += "pronr.\n"
        out += "Apenas caso queira mais informacoes, adicionar aqui\n"
        out += "*"*25 + "\n"
        out += "PRECEDENCE\n"
        out += "jobnr.    #modes  #successors   successors\n"
        # printar as relacoes de precedencia
        #    1        1          3           2   3   4
        for i in range(self.qtde_tarefas + 2):
            out += str(i+1) + " " + str(len(self.tarefas[i].modos)) + " " + str(len(self.tarefas[i].sucessores))
            for sucessor in self.tarefas[i].sucessores:
                out += " " + str(sucessor+1)
            out += "\n"
        out += "*"*25 + "\n"
        out += "REQUESTS/DURATIONS:\n"
        out += "jobnr. mode duration "
        out += "\t"
        for i in range(self.qtde_recursos_renovavel):
            out += "R" + str(i+1) + "\t"
        for i in range(self.qtde_recursos_nao_renovavel):
            out += "N" + str(i+1) + "\t"
        out += "\n"
        out += "-"*25 + "\n"
        for i in range(self.qtde_tarefas + 2):
            id_tarefa = i + 1
            out += str(id_tarefa) + " 1 " + str(self.tarefas[i].modos[0].duracao) + " "
            for recurso in self.tarefas[i].modos[0].qtde_recurso_renovavel:
                out += str(recurso) + " "
            for recurso in self.tarefas[i].modos[0].qtde_recurso_nao_renovavel:
                out += str(recurso) + " "
            out += "\n"
            for modo in self.tarefas[i].modos[1:]:
                # print("="*20, modo.id+1, "="*20)
                out += str(modo.id+1) + " "
                out += str(modo.duracao) + " "
                for recurso in modo.qtde_recurso_renovavel:
                    out += str(recurso) + " "
                for recurso in modo.qtde_recurso_nao_renovavel:
                    out += str(recurso) + " "
                out += "\n"
        out += "*"*25 + "\n"
        out += "RESOURCEAVAILABILITIES:\n"
        for i in range(self.qtde_recursos_renovavel):
            out += "R " + str(i+1) + " "
        for i in range(self.qtde_recursos_nao_renovavel):
            out += "N " + str(i+1) + " "
        out += "\n"
        for i in range(self.qtde_recursos_renovavel):
            out += str(self.recursos_renovaveis[i]) + " "
        for i in range(self.qtde_recursos_nao_renovavel):
            out += str(self.recursos_nao_renovaveis[i]) + " "
        out += "\n"

        return out


if __name__ == "__main__":
    seed = 388102 + 1 - 1
    print(f"Seed: {seed}")
    instance = Instance(seed=seed, qtde_tarefas=10)
    with open("j-test.mm", "w") as f:
        f.write(str(instance))
    # print(instance)
    # print(instance.print())
    # instance.visualizar_grafo()
    # with open('instance.txt', 'w') as f:
    #     f.write(str(instance))

    # import pandas as pd
    # # create a dataframe to show all acitivties and its modes
    # data = []
    # # fazer uma coluna pra cada recurso
    # for i in range(instance.qtde_tarefas + 2):
    #     for modo in instance.tarefas[i].modos:
    #         data.append([i, modo.id, modo.duracao] + modo.qtde_recurso_renovavel + modo.qtde_recurso_nao_renovavel)
    # df = pd.DataFrame(data, columns=['Tarefa', 'Modo', 'Duracao'] + [f"Recurso Renovavel {i}" for i in range(instance.qtde_recursos_renovavel)] + [f"Recurso Nao Renovavel {i}" for i in range(instance.qtde_recursos_nao_renovavel)])
    
    # with pd.ExcelWriter('instance.xlsx') as writer:
    #     df.to_excel(writer, sheet_name='Instance', index=False)

    pass
    