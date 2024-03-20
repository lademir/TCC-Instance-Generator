## Formato de uma instância

* Determinar a quantidade de projetos
  * O tempo total para conclusão de cada projeto
* Determinar a quantidade de tarefas em cada projeto
  * Quais são as relações de precedência entre tarefas
  * Quais são os recursos necessários para cada tarefa
  * Quais são os modos de execução de cada tarefa (quantidade de recurso utilizado, tempo de execução)
* Determinar a quantidade de cada tipo de recurso (renovável e não renovável)
  * Renovável: quantidade disponível por unidade de tempo
  * Não renovável: quantidade disponível




## O que o gerador ira fazer
* "Gerar X quantidades de instancias com Y Projetos e Z tarefas" <- precisa ser desse formato
  [ x ] A quantidade de cada recurso
  [ x ] Fazer com que cada atividade tenha vários modos de execução com uso de recurso e duracao diferentes
  Ps: Não precisa ter a quantidade de recursos não renovável, uma vez que busca minimizar esse valor junto com a duração total
  [ x ] Fazer com que cada atividade tenha uma relação de precedência
  [ x ] Fazer com que cada atividade tenha um tempo de execução
  [ x ] Fazer com que cada atividade tenha um recurso necessário
  [ x ] Fazer com que cada atividade tenha um ou mais modos de execução