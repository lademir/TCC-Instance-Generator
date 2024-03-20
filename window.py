import tkinter as tk
from tkinter import ttk as widgets
from tkinter import messagebox
from instance import Instance
import random
import os
import shutil

SIZEX, SIZEY = 400, 350

class Window:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Criação de instâncias voltadas para estrutura de eventos")
        self.win.geometry(f"{SIZEX}x{SIZEY}")

        self.qtde_tarefas = tk.IntVar(value=10)
        self.seed = tk.IntVar(value=random.randint(1, 999999999))
        self.qtde_instancias = tk.IntVar(value=10)

        self.seeds = []

        self.visu_instance = tk.IntVar(value=0)

        # Criacao do primeiro frame
        self.frame1 = self.create_frame()
        self.frame1.pack()

        # Salvando a quantidade de tarefas
        self.project_info_frame = widgets.LabelFrame(self.frame1, text="Informações do projeto")
        self.project_info_frame.grid(row=0, column=0, padx=10, pady=10)

        self.qtde_tarefas_label = widgets.Label(self.project_info_frame, text="Quantidade de tarefas")
        self.qtde_tarefas_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.qtde_tarefas_entry = widgets.Spinbox(self.project_info_frame, from_=1, to=100, textvariable=self.qtde_tarefas, width=10)
        self.qtde_tarefas_entry.grid(row=0, column=2, padx=10, pady=10)

        self.qtde_instancias_label = widgets.Label(self.project_info_frame, text="Quantidade de instâncias")
        self.qtde_instancias_label.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        self.qtde_instancias_entry = widgets.Spinbox(self.project_info_frame, from_=1, to=100, width=10, textvariable=self.qtde_instancias)
        self.qtde_instancias_entry.grid(row=1, column=2, padx=10, pady=10)


        self.qtde_instancias_label = widgets.Label(self.project_info_frame, text="Visualização do grafo da instância")
        self.qtde_instancias_label.grid(row=2, column=0, padx=10, pady=10, columnspan=2)
        self.qtde_instancias_entry = widgets.Spinbox(self.project_info_frame, from_=0, to=100, width=10, textvariable=self.visu_instance)
        self.qtde_instancias_entry.grid(row=2, column=2, padx=10, pady=10)
        self.generate_button = widgets.Button(self.project_info_frame, text="Visualizar",command=self.visualizar_grafo)
        self.generate_button.grid(row=3, column=1, padx=10, pady=10)

        # Salvamento da instancia em um arquivo
        self.generate_frame = self.create_frame()
        self.generate_frame.pack(side=tk.BOTTOM, pady=30)

        self.generate_button = widgets.Button(self.generate_frame, text="Gerar instâncias",command=self.generate_instances)
        self.generate_button.grid(row=1, column=0, padx=10, pady=10)


    def create_frame(self):
        frame = widgets.Frame(self.win)
        return frame
    
    def generate_seed(self):
        self.seed.set(random.randint(1, 9999999999))

    def visualizar_grafo(self):
        ins_seed = self.seeds[self.visu_instance.get()]
        instance = Instance(seed=ins_seed, qtde_tarefas=self.qtde_tarefas.get())
        instance.visualizar_grafo()

    def generate_instances(self):
        if os.path.exists(f"instancias_{self.qtde_tarefas.get()}"):
            shutil.rmtree(f"instancias_{self.qtde_tarefas.get()}")
        os.mkdir(f"instancias_{self.qtde_tarefas.get()}")
        for i in range(0, self.qtde_instancias.get()):
            self.generate_seed()
            self.seeds.append(self.seed.get())
            instance = Instance(seed=self.seed.get(), qtde_tarefas=self.qtde_tarefas.get())
            with open(f"instancias_{self.qtde_tarefas.get()}/instancia_{i}.txt", "w") as f:
                f.write(f"{instance}")
        messagebox.showinfo("Instâncias geradas", f"As instâncias foram geradas e salvas na pasta instancias_{self.qtde_tarefas.get()}")

    def render_tree_view(self):
        # Mostrando as precedencias
        self.precedencias_frame = self.create_frame()
        self.precedencias_frame.pack()

        self.precedencias_frame_label = widgets.LabelFrame(self.precedencias_frame, text="Relação de precedência")
        self.precedencias_frame_label.grid(row=0, column=0, padx=10, pady=10)
        self.precedence_button_generate = widgets.Button(self.precedencias_frame_label, text="Gerar precedências", command=self.generate_precedences)
        self.precedence_button_generate.grid(row=0, column=0, padx=10, pady=10)

        self.visualizar_precedencias_button = widgets.Button(self.precedencias_frame_label, text="Visualizar grafo", command=lambda: self.instance.visualizar_grafo())
        self.visualizar_precedencias_button.grid(row=0, column=1, padx=10, pady=10)
    

        # Mostrando o grafo
        self.grafo_frame = self.create_frame()
        self.grafo_frame.pack()
        
        self.grafo_frame_label = widgets.LabelFrame(self.grafo_frame, text="Visualização do grafo", width=400)
        self.grafo_frame_label.grid(row=0, column=0, padx=10, pady=10)
        self.tree = widgets.Treeview(self.win, columns=("Tarefa", "Sucessor", "Recursos", "Duração"), show="headings")
        self.tree.heading("Tarefa", text="Tarefa")
        self.tree.heading("Sucessor", text="Sucessor")
        self.tree.heading("Recursos", text="Recursos")
        self.tree.heading("Duração", text="Duração")
        self.tree.pack(expand=1)

        self.update_precedences_treeview()

    def render_seed_entry(self):
        self.seed_label = widgets.Label(self.project_info_frame, text="Seed")
        self.seed_label.grid(row=2, column=0, padx=10, pady=10)
        self.seed_entry = widgets.Entry(self.project_info_frame, width=5, textvariable=self.seed)
        self.seed_entry.grid(row=2, column=1, padx=10, pady=10)
        self.seed_generate_button = widgets.Button(self.project_info_frame, text="Gerar seed", command=self.generate_seed)
        self.seed_generate_button.grid(row=2, column=2,columnspan=1, padx=10, pady=10)

    def generate_precedences(self):
        self.instance = Instance(seed=self.seed.get(), qtde_tarefas=self.qtde_tarefas.get())
        self.update_precedences_treeview()

    def update_precedences_treeview(self):
        # Limpar o treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Salvar todos as precedencia em um dict, a[0] possui todas as atividades que tem a[0] como precedente
        
        tarefas = self.instance.tarefas
        # Adicionar as precedencias ao treeview
        for tarefa in tarefas.values():
            self.tree.insert("", "end", values=(tarefa.id, ', '.join(map(str, tarefa.sucessores)), ', '.join(map(str, tarefa.qtde_recurso)), tarefa.duracao))

    def start(self):
        self.win.mainloop()
