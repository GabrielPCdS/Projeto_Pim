# 🎓 Sistema de Gestão Acadêmica - ADS

Este projeto é um sistema desktop desenvolvido em **Python** para gerenciamento de notas acadêmicas, focado nas regras de negócio do curso de Análise e Desenvolvimento de Sistemas (Cálculo de NP1, NP2 e PIM).

O sistema conta com uma interface gráfica moderna, controle de acesso (Aluno/Professor), persistência de dados em banco SQL e criptografia de senhas.

## 🚀 Funcionalidades

### 👨‍🏫 Módulo Professor
- **Cadastro Rápido de Alunos:** Gera automaticamente credenciais provisórias.
- **Lançamento de Notas:** Interface intuitiva para inserir NP1, NP2 e PIM.
- **Sincronização de PIM:** A nota do Projeto Integrado Multidisciplinar (PIM) é replicada automaticamente para todas as matérias do semestre, conforme regra acadêmica.
- **Visualização da Turma:** Lista de alunos com status (Aprovado, Exame, Reprovado) em tempo real.

### 👨‍🎓 Módulo Aluno
- **Fluxo de Primeiro Acesso:** Obrigatoriedade de troca de senha e cadastro de e-mail no primeiro login.
- **Boletim Visual:** Visualização clara das notas e médias com indicadores de cor.
- **Simulador de Projeção:** Se a média for baixa, o sistema permite que o aluno simule "quanto preciso tirar" para passar.
- **Feedback Inteligente:** O sistema fornece dicas de estudo personalizadas baseadas na matéria em que o aluno está com dificuldade.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface Gráfica:** Tkinter + `ttkbootstrap` (Tema Flatly)
- **Banco de Dados:** SQLite3 (Nativo)
- **Segurança:** `bcrypt` (Para hash e sal de senhas)
- **Padrão de Projeto:** Arquitetura Modular (Separação entre Modelos, View, Controller e Regras de Negócio).

---

## ⚙️ Instalação e Execução

Siga os passos abaixo para rodar o projeto em sua máquina:

### 1. Clone o repositório
Baixe o código fonte para o seu computador:
```bash
git clone [https://github.com/GabrielPCdS/Projeto_Pim.git](https://github.com/GabrielPCdS/Projeto_Pim.git)
cd Projeto_Pim
```

### 2. Instale as dependências
Este projeto utiliza bibliotecas externas para a interface moderna e segurança. No terminal, execute:
```bash
pip install ttkbootstrap bcrypt
```

### 3. Execute o Sistema
Inicie a aplicação principal:
```bash
python main.py
```




