from dataclasses import dataclass, field
import typing

# --- CONSTANTES GLOBAIS ---
# Esta constante precisava estar aqui para ser importada pelo main.py
PIM_MATERIA = "PROJ INTEG MULTIDISCIPLINAR II"

# Lista de matérias para o curso ADS
MATERIAS_ADS = [
    PIM_MATERIA,
    "ENGENHARIA DE SOFTWARE AGIL",
    "ALGORIT E ESTRUT DADOS PYTHON",
    "PROGRAMACAO ESTRUTURADA EM C",
    "ANALISE E PROJETO DE SISTEMAS"
]

# --- CLASSES DE MODELO ---

@dataclass
class Pessoa:
    """
    Classe base para Aluno e Professor.
    Define atributos comuns e realiza limpeza básica de dados.
    """
    nome: str
    # O email pode ser None (caso do Aluno recém-cadastrado pelo professor)
    email: typing.Optional[str]
    senha_hash: str
    # O campo 'tipo' será definido pelas subclasses. Não inicializado aqui.
    tipo: str = field(init=False, repr=False) 

    def __post_init__(self):
        """
        Garante que strings vazias sejam convertidas para None 
        para melhor compatibilidade com NULL no banco de dados, e 
        converte o e-mail para minúsculas.
        """
        # Limpa e-mail se for uma string vazia
        if self.email == "":
            self.email = None
        
        # Converte e-mail para minúsculas se existir
        if self.email is not None:
            self.email = self.email.lower()

@dataclass
class Aluno(Pessoa):
    """Modelo de dados para um Aluno."""
    ra: str
    curso: str
    
    # Define o tipo, sobrescrevendo o campo 'tipo' de Pessoa
    tipo: str = field(init=False, default='aluno') 
    
    def __post_init__(self):
        """
        Executa a inicialização da classe base e depois customiza o RA.
        """
        # Chama o __post_init__ da classe Pessoa para limpeza de e-mail
        super().__post_init__() 
        
        # Garante que o RA esteja em maiúsculas (customização do Aluno)
        if self.ra:
            self.ra = str(self.ra).upper()

@dataclass
class Professor(Pessoa):
    """Modelo de dados para um Professor."""
    materia_principal: str # Matéria principal que leciona
    
    # Define o tipo, sobrescrevendo o campo 'tipo' de Pessoa
    tipo: str = field(init=False, default='professor')
    
    def __post_init__(self):
        """
        Executa a inicialização da classe base.
        """
        # Chama o __post_init__ da classe Pessoa para limpeza e conversão de e-mail
        super().__post_init__()