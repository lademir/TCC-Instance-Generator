from window import Window
import random
import os
import shutil
from instance import Instance

def ui():
    window = Window()
    window.start()


def save_instance(ins: Instance, index: int):
    with open(f"instancias_{ins.qtde_tarefas}/instancia_{index}.txt", "w") as f:
        f.write(f"{ins}")

def main():
    qtde_instances = 10
    qtde_atividades = 10
    if os.path.exists(f"instancias_{qtde_atividades}"):
        shutil.rmtree(f"instancias_{qtde_atividades}")
    os.mkdir(f"instancias_{qtde_atividades}")
    # for i in range(qtde_instances):
    #     seed = random.randint(1, 9999999999)
    #     instance = Instance(seed=seed, qtde_tarefas=qtde_atividades)
    #     save_instance(instance, i)
    qtde_saved_instances = 0
    while qtde_saved_instances < qtde_instances:
        seed = random.randint(1, 9999999999)
        instance = Instance(seed=seed, qtde_tarefas=qtde_atividades)
        if instance.possivel:
            save_instance(instance, qtde_saved_instances)
            qtde_saved_instances += 1


if __name__ == "__main__":
    main()