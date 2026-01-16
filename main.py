import tkinter as tk
from tkinter import messagebox, END
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import typing

# IMPORTAÇÕES DOS NOSSOS MÓDULOS (Conexão entre arquivos)
from modelos import Aluno, Professor, MATERIAS_ADS, PIM_MATERIA
from calculadora_academica import CalculadoraAcademica
from gestor_db import GestorBD

# --- CONSTANTES DE INTERFACE ---
TEMA_BOOTSTRAP = "flatly" 

FEEDBACKS_ESTUDO = {
    PIM_MATERIA: (
        "Seu PIM é crucial! Foco na documentação, metodologia e integração entre os conhecimentos "
        "adquiridos. Reveja o escopo e os requisitos definidos. Aprimorar o PIM eleva a média de todas as matérias."
    ),
    "ENGENHARIA DE SOFTWARE AGIL": (
        "Revisite os princípios Ágeis (Scrum, Kanban). Pratique a escrita de User Stories e "
        "entenda o papel das cerimônias (Daily, Planning, Review). O foco deve ser em Processos e entrega de valor!"
    ),
    "ALGORIT E ESTRUT DADOS PYTHON": (
        "Dedique-se a estruturas como Listas, Dicionários e Sets em Python. Pratique a complexidade "
        "de tempo (O(n), O(log n)) e resolva problemas em plataformas de codificação. Foco em lógica e eficiência!"
    ),
    "PROGRAMACAO ESTRUTURADA EM C": (
        "Revise Pointers, alocação de memória (malloc/free) e o uso de structs. A linguagem C exige "
        "precisão em controle de fluxo e manipulação de variáveis. Tente reescrever exercícios básicos de memória."
    ),
    "ANALISE E PROJETO DE SISTEMAS": (
        "Concentre-se em UML (diagramas de classes, casos de uso), levantamento de requisitos (funcionais "
        "e não funcionais) e na modelagem de dados. Estude a transição entre as fases do ciclo de vida de um projeto."
    )
}

# -----------------------------------------------------
# CLASSES PRINCIPAIS (App e Login)
# -----------------------------------------------------

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename=TEMA_BOOTSTRAP)
        self.title("Sistema Acadêmico ADS | Gestão de Notas")
        self.geometry("900x700") 
        self.minsize(700, 550) 
        self.place_window_center()

        # Inicializa os módulos lógicos
        self.gestor_bd = GestorBD()
        self.gestor_bd.inicializar_db() # Garante que tabelas existam
        self.calculadora = CalculadoraAcademica()
        
        self.usuario_logado: typing.Optional[dict] = None 
        self.ra_logado: typing.Optional[str] = None
        self.materia_logado: typing.Optional[str] = None

        self._criar_container()
        self.mostrar_tela(TelaLogin)

        self.protocol("WM_DELETE_WINDOW", self.fechar_app)

    def _criar_container(self):
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

    def mostrar_tela(self, ClasseTela: typing.Type[ttk.Frame], **kwargs: typing.Any) -> None:
        for widget in self.container.winfo_children():
            widget.destroy()
        tela = ClasseTela(self.container, self, **kwargs)
        tela.pack(fill="both", expand=True)

    def fechar_app(self):
        self.gestor_bd.fechar_conexao()
        self.destroy()

class TelaLogin(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=50)
        self.app = app
        self.gestor_bd = app.gestor_bd
        self._criar_widgets()

    def _criar_widgets(self):
        main_frame = ttk.Frame(self, padding=45, style='light.TFrame', relief=FLAT) 
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(main_frame, text="🎓 Sistema Acadêmico ADS", font=('Arial', 24, 'bold'), bootstyle="primary").pack(pady=(0, 5))
        ttk.Label(main_frame, text="Acesso ao Portal do Aluno/Professor", font=('Arial', 14, 'italic'), bootstyle="secondary").pack(pady=(5, 30))

        self.tipo_login_var = tk.StringVar(value='aluno')
        
        frame_tipo = ttk.Frame(main_frame)
        frame_tipo.pack(pady=20)
        
        ttk.Radiobutton(frame_tipo, text="Sou Aluno", variable=self.tipo_login_var, value='aluno', bootstyle="primary-round-toggle").pack(side=tk.LEFT, padx=15, ipadx=15, ipady=8)
        ttk.Radiobutton(frame_tipo, text="Sou Professor", variable=self.tipo_login_var, value='professor', bootstyle="primary-round-toggle").pack(side=tk.LEFT, padx=15, ipadx=15, ipady=8)
        
        self.label_credencial = ttk.Label(main_frame, text="RA:", font=('Arial', 12, 'bold'))
        self.label_credencial.pack(pady=(20, 5), fill=tk.X)
        self.entry_credencial = ttk.Entry(main_frame, bootstyle="primary", font=('Arial', 12))
        self.entry_credencial.pack(pady=(0, 15), ipadx=30, ipady=8, fill=tk.X) 
        
        ttk.Label(main_frame, text="Senha:", font=('Arial', 12, 'bold')).pack(pady=(5, 5), fill=tk.X)
        self.entry_senha = ttk.Entry(main_frame, show="*", bootstyle="primary", font=('Arial', 12))
        self.entry_senha.pack(pady=(0, 30), ipadx=30, ipady=8, fill=tk.X)
        
        ttk.Button(main_frame, text="Entrar", command=self._processar_login, bootstyle="primary", width=30, padding=10).pack(pady=10)
        ttk.Button(main_frame, text="Novo Cadastro", command=lambda: self.app.mostrar_tela(TelaCadastro), bootstyle="secondary-link", width=30, padding=10).pack(pady=5)

        self.tipo_login_var.trace_add("write", self._atualizar_credencial_label)
        
    def _atualizar_credencial_label(self, *args):
        tipo = self.tipo_login_var.get()
        self.label_credencial.config(text="RA:" if tipo == 'aluno' else "Email:")

    def _processar_login(self):
        credencial = self.entry_credencial.get().strip()
        senha_limpa = self.entry_senha.get().strip()
        tipo = self.tipo_login_var.get()

        if not credencial or not senha_limpa:
            messagebox.showerror("Erro de Login", "Por favor, preencha a credencial e a senha.")
            return

        usuario_data = self.gestor_bd.buscar_login(credencial, senha_limpa, tipo)

        if usuario_data:
            self.app.usuario_logado = usuario_data
            if tipo == 'aluno':
                self.app.ra_logado = usuario_data['ra'] 
                if usuario_data.get('primeiro_acesso'):
                    messagebox.showinfo("Primeiro Acesso", "Você precisa vincular um e-mail e definir uma nova senha para continuar.")
                    self.app.mostrar_tela(TelaPrimeiroAcesso)
                else:
                    self.app.mostrar_tela(PainelAluno)
            elif tipo == 'professor':
                self.app.materia_logado = usuario_data['materia_principal']
                self.app.mostrar_tela(PainelProfessor) 
        else:
            messagebox.showerror("Erro de Login", "Credenciais incorretas ou tipo de usuário inválido.")