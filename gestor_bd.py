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
    
    # -----------------------------------------------
    # MÉTODOS DE BUSCA AUXILIARES
    # -----------------------------------------------
    
    def _executar_busca(self, sql: str, params: tuple) -> typing.Optional[sqlite3.Row]:
        """Método auxiliar para executar buscas simples e fechar a conexão."""
        self._conectar()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            self.fechar_conexao()

    def buscar_aluno_por_ra(self, ra: str) -> bool:
        return self._executar_busca("SELECT 1 FROM Alunos WHERE ra = ?", (ra.upper(),)) is not None
            
    def buscar_professor_por_email(self, email: str) -> bool:
        return self._executar_busca("SELECT 1 FROM Professores WHERE email = ?", (email.lower(),)) is not None

    # -----------------------------------------------
    # MÉTODOS DE CADASTRO E LOGIN
    # -----------------------------------------------

    def buscar_login(self, credencial: str, senha_limpa: str, tipo: str) -> typing.Optional[dict]:
        """Busca o usuário e verifica a senha para o login."""
        self._conectar()
        try:
            cursor = self.conn.cursor()
            usuario_data = None
            
            if tipo == 'aluno':
                cursor.execute("SELECT ra, nome, senha_hash, curso, primeiro_acesso, email FROM Alunos WHERE ra = ?", (credencial.upper(),))
                usuario_data = cursor.fetchone()
                
                if usuario_data and self._checar_senha(senha_limpa, usuario_data['senha_hash']):
                    return {
                        'ra': usuario_data['ra'],
                        'nome': usuario_data['nome'],
                        'curso': usuario_data['curso'],
                        'email': usuario_data['email'],
                        'primeiro_acesso': bool(usuario_data['primeiro_acesso']), 
                        'tipo': 'aluno'
                    }
                
            elif tipo == 'professor':
                cursor.execute("SELECT email, nome, senha_hash, materia_principal FROM Professores WHERE email = ?", (credencial.lower(),))
                usuario_data = cursor.fetchone()
                
                if usuario_data and self._checar_senha(senha_limpa, usuario_data['senha_hash']):
                    return {
                        'email': usuario_data['email'],
                        'nome': usuario_data['nome'],
                        'materia_principal': usuario_data['materia_principal'],
                        'tipo': 'professor'
                    }
                
            return None
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar login: {e}") 
            return None
        finally:
            self.fechar_conexao()

    def adicionar_usuario(self, usuario: typing.Union[Aluno, Professor], senha_limpa: str) -> tuple[bool, str]:
        """Adiciona um novo aluno ou professor ao banco de dados."""
        self._conectar()
        
        try:
            senha_hash = self._hash_senha(senha_limpa)
            cursor = self.conn.cursor()
            
            if isinstance(usuario, Aluno):
                if not usuario.email or not self._validar_email(usuario.email): 
                    return False, "O e-mail é obrigatório e precisa ter um formato válido."
                    
                cursor.execute(
                    "INSERT INTO Alunos (ra, nome, email, senha_hash, curso, primeiro_acesso) VALUES (?, ?, ?, ?, ?, 0)",
                    (usuario.ra.upper(), usuario.nome, usuario.email.lower(), senha_hash, usuario.curso)
                )
                
                for materia in MATERIAS_ADS:
                    cursor.execute(
                        "INSERT INTO Notas (ra_aluno, materia, np1, np2, pim) VALUES (?, ?, ?, ?, ?)",
                        (usuario.ra.upper(), materia, 0.0, 0.0, 0.0)
                    )

                self.conn.commit()
                return True, "Aluno cadastrado com sucesso!"
                
            elif isinstance(usuario, Professor):
                if not self._validar_email(usuario.email):
                    return False, "O e-mail do professor precisa ter um formato válido."
                
                cursor.execute(
                    "INSERT INTO Professores (email, nome, senha_hash, materia_principal) VALUES (?, ?, ?, ?)",
                    (usuario.email.lower(), usuario.nome, senha_hash, usuario.materia_principal)
                )
                self.conn.commit()
                return True, "Professor cadastrado com sucesso!"
                
            return False, "Tipo de usuário inválido."

        except sqlite3.IntegrityError:
            if isinstance(usuario, Aluno):
                return False, "Erro: RA ou Email já cadastrado."
            else:
                return False, "Erro: Email do professor já cadastrado."
        except sqlite3.Error as e:
            return False, f"Erro no banco de dados: {e}"
        except ValueError as ve:
            return False, str(ve)
        finally:
            self.fechar_conexao()

    def adicionar_aluno_professor(self, nome: str, ra: str, materia: str, senha_limpa: str) -> tuple[bool, str]:
        """Adiciona um novo aluno via painel do professor."""
        self._conectar()
        ra_upper = ra.upper()
        
        try:
            if self.buscar_aluno_por_ra(ra):
                 return False, f"Erro: RA já cadastrado no sistema ({ra_upper})."

            senha_hash = self._hash_senha(senha_limpa)
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO Alunos (ra, nome, email, senha_hash, curso, primeiro_acesso) VALUES (?, ?, NULL, ?, ?, 1)",
                (ra_upper, nome, senha_hash, "ADS")
            )
            
            for m in MATERIAS_ADS:
                cursor.execute(
                    "INSERT INTO Notas (ra_aluno, materia, np1, np2, pim) VALUES (?, ?, ?, ?, ?)",
                    (ra_upper, m, 0.0, 0.0, 0.0)
                )

            self.conn.commit()
            return True, f"Aluno {nome} cadastrado. Senha inicial é: {senha_limpa}"

        except sqlite3.Error as e:
            return False, f"Erro no banco de dados: {e}"
        except ValueError as ve:
            return False, str(ve)
        finally:
            self.fechar_conexao()

    def atualizar_aluno_primeiro_acesso(self, ra: str, novo_email: str, nova_senha_limpa: str) -> tuple[bool, str]:
        """Atualiza email, senha e marca o primeiro acesso como concluído."""
        self._conectar()
        try:
            if not self._validar_email(novo_email):
                 return False, "Formato de e-mail inválido."
                
            senha_hash = self._hash_senha(nova_senha_limpa)
            cursor = self.conn.cursor()
            
            cursor.execute(
                "UPDATE Alunos SET email = ?, senha_hash = ?, primeiro_acesso = 0 WHERE ra = ?",
                (novo_email.lower(), senha_hash, ra.upper())
            )
            self.conn.commit()
            
            if cursor.rowcount == 0:
                 return False, "Aluno (RA) não encontrado para atualização."
                
            return True, "Dados de acesso atualizados."
        except sqlite3.Error as e:
            return False, f"Erro ao atualizar dados: {e}"
        except ValueError as ve:
            return False, str(ve)
        finally:
            self.fechar_conexao()