# Gomoku 9x9 — TDE 2: Busca Competitiva - 23/05/26

**Disciplina:** Inteligência Artificial  
**Professor:** Antônio David Viniski  
**Instituição:** Pontifícia Universidade Católica do Paraná (PUCPR)

---

## Sobre o jogo

Gomoku (Cinco em Linha) é um jogo de tabuleiro para dois jogadores. O objetivo é formar **5 peças consecutivas** em qualquer direção: horizontal, vertical ou diagonal.

- **Humano** → peças **PRETAS** (joga primeiro)
- **IA** → peças **BRANCAS** (responde automaticamente)
- Tabuleiro: **9x9**

---

## Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Biblioteca pygame

### Instalação do pygame

```bash
py -m pip install pygame-ce
```

> Se estiver usando Python 3.14+, use `pygame-ce` (Community Edition), que tem suporte às versões mais recentes.

### Rodando o jogo

```bash
py main.py
```

---

## Como jogar

1. Ao abrir, selecione a **dificuldade** da IA no menu inicial.
2. Você (**peças pretas**) joga primeiro — clique em qualquer célula vazia do tabuleiro.
3. A IA (**peças brancas**) responde automaticamente.
4. Vence quem formar **5 peças em linha** primeiro.
5. Se o tabuleiro encher sem vencedor, é **empate**.

---

## Estrutura do projeto

```
TDE-2---Busca-Competitiva/
├── main.py          # Loop principal do jogo (eventos Pygame e turnos)
├── board.py         # Classe Board: estado do tabuleiro, vitória e empate
├── heuristics.py    # Funções de avaliação heurística (uma por nível)
├── ai.py            # Algoritmos Minimax e função de decisão da IA
└── ui.py            # Renderização: menu, tabuleiro, peças e HUD
```

---

## Níveis de dificuldade

### Iniciante

- **Algoritmo:** Minimax puro (sem poda alfa-beta)
- **Profundidade:** 2 jogadas à frente
- **Heurística:** conta sequências curtas (pares e trincas) de cada jogador

### Intermediário

- **Algoritmo:** Minimax com poda alfa-beta
- **Profundidade:** 4 jogadas à frente
- **Heurística:** diferencia sequências abertas (vivas) e fechadas, aplica bônus por centralidade e penaliza ameaças do humano

### Profissional

- **Algoritmo:** Minimax com poda alfa-beta + ordenação de movimentos + aprofundamento iterativo
- **Profundidade:** busca até profundidade 10, limitada a **3 segundos** por jogada
- **Heurística:** identifica sequências vivas, detecta forks (ameaças duplas), aplica penalização forte para 4 em linha do oponente

---

## Saída após cada jogada da IA

O terminal exibe três informações obrigatórias:

```
Turno 2 - IA jogou em E5
    A  B  C  D  E  F  G  H  I
 1  .  .  .  .  .  .  .  .  .
 2  .  .  .  .  .  .  .  .  .
 3  .  .  .  .  .  .  .  .  .
 4  .  .  .  .  .  .  .  .  .
 5  .  .  .  .  O  .  .  .  .
 6  .  .  .  .  X  .  .  .  .
 ...

Tempo da jogada: 0.83s
Avaliacao do estado: 1240
```

Essas mesmas informações também aparecem no **HUD** na parte inferior da janela.

---

## Algoritmos implementados

### Minimax

Explora a árvore de decisão simulando jogadas alternadas entre IA e humano. A IA escolhe o movimento que maximiza sua pontuação assumindo que o humano sempre joga de forma ótima.

### Poda Alfa-Beta

Otimização do Minimax que elimina ramos da árvore que não podem influenciar o resultado final. Permite buscar em profundidades maiores no mesmo tempo.

### Ordenação de Movimentos (nível Profissional)

Antes de explorar os ramos, ordena os candidatos pelos mais promissores (avaliados pela heurística). Movimentos bons avaliados primeiro geram mais cortes alfa-beta.

### Aprofundamento Iterativo (nível Profissional)

Executa a busca com profundidade 2, depois 3, depois 4... até o limite de 3 segundos. Garante que sempre há uma jogada válida mesmo se o tempo acabar no meio de uma busca.

### Candidatos por proximidade

Em vez de avaliar todas as 81 células, a IA considera apenas células vazias **adjacentes a peças já jogadas**. Isso reduz drasticamente o espaço de busca mantendo a qualidade das jogadas.
