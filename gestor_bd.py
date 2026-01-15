import sqlite3
import bcrypt
import typing
import re

# Importa as classes modelo E a lista de matérias
from modelos import Aluno, Professor, MATERIAS_ADS 

class GestorBD:
    def __init__(self, db_name='sistema_academico.db'):
        """
        Inicializa o gestor, apenas definindo o nome do DB. 
        A conexão é estabelecida apenas quando necessária.
        """
        self.db_name = db_name
        self.conn: typing.Optional[sqlite3.Connection] = None 
        
    def inicializar_db(self):
        """
        Método público chamado no início da aplicação para garantir 
        que as tabelas existam e o DB esteja pronto.
        """
        self._conectar()
        try:
            self._criar_tabelas()
        except Exception as e:
            print(f"Erro ao inicializar DB: {e}")
        finally:
            self.fechar_conexao() 

    def _conectar(self):
        """Estabelece a conexão com o banco de dados, se não estiver aberta."""
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_name)
                self.conn.row_factory = sqlite3.Row 
            except sqlite3.Error as e:
                raise ConnectionError(f"Falha ao conectar ao banco de dados: {e}")

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _criar_tabelas(self):
        """Cria as tabelas Alunos, Professores e Notas se não existirem."""
        cursor = self.conn.cursor()
        
        # Tabela Alunos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Alunos (
                ra TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE, 
                senha_hash TEXT NOT NULL,
                curso TEXT NOT NULL,
                primeiro_acesso INTEGER DEFAULT 1
            )
        """)
        
        # Tabela Professores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Professores (
                email TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                materia_principal TEXT NOT NULL
            )
        """)

        # Tabela Notas (Relacionamento Aluno-Matéria)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ra_aluno TEXT NOT NULL,
                materia TEXT NOT NULL,
                np1 REAL DEFAULT 0.0,
                np2 REAL DEFAULT 0.0,
                pim REAL DEFAULT 0.0,
                FOREIGN KEY (ra_aluno) REFERENCES Alunos(ra) ON DELETE CASCADE, 
                UNIQUE (ra_aluno, materia)
            )
        """)
        
        self.conn.commit()

    def _hash_senha(self, senha_limpa: str) -> str:
        """Gera o hash da senha usando bcrypt."""
        if not senha_limpa:
            raise ValueError("A senha não pode ser vazia.")
            
        return bcrypt.hashpw(senha_limpa.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _checar_senha(self, senha_limpa: str, senha_hash: str) -> bool:
        """Verifica se a senha limpa corresponde ao hash armazenado."""
        try:
            return bcrypt.checkpw(senha_limpa.encode('utf-8'), senha_hash.encode('utf-8'))
        except ValueError:
            return False
            
    def _validar_email(self, email: str) -> bool:
        """Verifica se o formato do e-mail é válido usando expressão regular."""
        if not email:
            return False
        return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))