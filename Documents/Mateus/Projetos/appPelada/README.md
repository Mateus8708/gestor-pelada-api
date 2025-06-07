# ⚽ Gestor de Pelada API

API completa desenvolvida em Python com FastAPI para gerenciar "peladas" de futebol, permitindo a criação de múltiplos grupos, gerenciamento de jogadores, sorteio inteligente de times e ranking de performance.

---

## 📖 Sobre o Projeto

Este projeto foi criado como parte de um portfólio de desenvolvimento back-end, demonstrando a construção de uma API RESTful robusta, segura e com regras de negócio complexas. A aplicação permite que diferentes usuários cadastrem suas próprias "peladas" (grupos de futebol), adicionem jogadores, sorteiem times de forma balanceada e acompanhem as estatísticas de gols e assistências a cada partida.

---

## ✨ Funcionalidades Principais

* **Autenticação e Segurança:** Sistema de registro e login com senhas hasheadas e autenticação por Token JWT.
* **Multi-Tenancy:** Suporte para múltiplos usuários, onde cada um gerencia suas próprias peladas de forma isolada e segura.
* **Gerenciamento de Peladas:** Criação e listagem de peladas por usuário.
* **Gerenciamento de Jogadores (CRUD):** Funcionalidades completas para Criar, Ler, Atualizar e Deletar jogadores dentro de cada pelada.
* **Sorteio Inteligente de Times:** Algoritmo de **Snake Draft** para sortear 4 times com 5 jogadores, balanceando as equipes com base na nota de cada jogador e adicionando aleatoriedade.
* **Registro de Partidas e Estatísticas:** Endpoint para registrar os resultados de cada jogo (gols e assistências por jogador).
* **Ranking de Performance:** Geração de um ranking por pelada, ordenado por gols e, como critério de desempate, por assistências.
* **Geração de Relatórios em PDF:** Endpoint que gera um arquivo PDF com o ranking da pelada, pronto para download e compartilhamento.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Framework:** FastAPI
* **Banco de Dados:** SQLAlchemy com SQLite (em desenvolvimento) e preparado para PostgreSQL (em produção)
* **Autenticação:** Passlib (para hashing de senha) e Python-JOSE (para tokens JWT)
* **Geração de PDF:** FPDF2
* **Servidor ASGI:** Uvicorn

---

## 🚀 Como Executar o Projeto Localmente

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/gestor-pelada-api.git](https://github.com/seu-usuario/gestor-pelada-api.git)
    cd gestor-pelada-api
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\Activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    
4.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  Acesse a documentação interativa em `http://127.0.0.1:8000/docs`.

---

## 📚 Endpoints Principais da API

* `POST /usuarios/`: Registra um novo usuário.
* `POST /login`: Realiza o login e retorna um token de acesso.
* `POST /peladas/`: Cria uma nova pelada para o usuário logado.
* `GET /peladas/`: Lista as peladas do usuário logado.
* `POST /peladas/{pelada_id}/jogadores/`: Adiciona um jogador a uma pelada específica.
* `POST /peladas/{pelada_id}/sorteio-times/`: Sorteia os times para uma pelada.
* `POST /peladas/{pelada_id}/partidas/`: Registra as estatísticas de uma partida.
* `GET /peladas/{pelada_id}/ranking/`: Exibe o ranking da pelada.
* `GET /peladas/{pelada_id}/ranking/pdf`: Gera o ranking em PDF.

---

## 👨‍💻 Autor

* **Mateus Cavvalcanti**
    * **LinkedIn:** [https://linkedin.com/in/mateus-cavalcanti-705769224/]