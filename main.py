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
        

    class TelaCadastro(ttk.Frame):
        def __init__(self, master, app):
            super().__init__(master, padding=50)
            self.app = app
            self.gestor_bd = app.gestor_bd
            self._criar_widgets()

    def _criar_widgets(self):
        main_frame = ttk.Frame(self, padding=45, style='light.TFrame', relief=FLAT)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(main_frame, text="NOVO CADASTRO", font=('Arial', 20, 'bold'), bootstyle="primary").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(main_frame, text="Preencha seus dados para se registrar no sistema.", font=('Arial', 12), bootstyle="secondary").grid(row=1, column=0, columnspan=2, pady=(0, 20))

        self.tipo_cadastro_var = tk.StringVar(value='aluno')
        frame_tipo = ttk.Frame(main_frame)
        frame_tipo.grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Radiobutton(frame_tipo, text="Aluno", variable=self.tipo_cadastro_var, value='aluno', bootstyle="primary-round-toggle").pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        ttk.Radiobutton(frame_tipo, text="Professor", variable=self.tipo_cadastro_var, value='professor', bootstyle="primary-round-toggle").pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)

        r = 3 
        ttk.Label(main_frame, text="Nome Completo:", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='w', padx=5, pady=5)
        self.entry_nome = ttk.Entry(main_frame, bootstyle="primary", font=('Arial', 12))
        self.entry_nome.grid(row=r, column=1, sticky='ew', padx=5, pady=5, ipady=5)
        r += 1
        
        ttk.Label(main_frame, text="Email:", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='w', padx=5, pady=5)
        self.entry_email = ttk.Entry(main_frame, bootstyle="primary", font=('Arial', 12))
        self.entry_email.grid(row=r, column=1, sticky='ew', padx=5, pady=5, ipady=5)
        r += 1
        
        ttk.Label(main_frame, text="Senha:", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='w', padx=5, pady=5)
        self.entry_senha = ttk.Entry(main_frame, show="*", bootstyle="primary", font=('Arial', 12))
        self.entry_senha.grid(row=r, column=1, sticky='ew', padx=5, pady=5, ipady=5)
        r += 1
        
        ttk.Label(main_frame, text="Confirmar Senha:", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='w', padx=5, pady=5)
        self.entry_conf_senha = ttk.Entry(main_frame, show="*", bootstyle="primary", font=('Arial', 12))
        self.entry_conf_senha.grid(row=r, column=1, sticky='ew', padx=5, pady=5, ipady=5)
        r += 1
        
        self.label_ra = ttk.Label(main_frame, text="RA (Mín 7 Caracteres):", font=('Arial', 11, 'bold'))
        self.entry_ra = ttk.Entry(main_frame, bootstyle="primary", font=('Arial', 12))
        
        self.label_materia = ttk.Label(main_frame, text="Matéria Principal:", font=('Arial', 11, 'bold'))
        self.var_materia = tk.StringVar(main_frame)
        self.var_materia.set(MATERIAS_ADS[0]) 
        self.option_materia = ttk.OptionMenu(main_frame, self.var_materia, self.var_materia.get(), *MATERIAS_ADS, bootstyle="primary") 
        
        ttk.Button(main_frame, text="Cadastrar", command=self._processar_cadastro, bootstyle="primary", width=30, padding=10).grid(row=r+1, column=0, columnspan=2, pady=20) 
        ttk.Button(main_frame, text="Voltar para Login", command=lambda: self.app.mostrar_tela(TelaLogin), bootstyle="secondary-link", width=30, padding=10).grid(row=r+2, column=0, columnspan=2, pady=5) 
        
        self.tipo_cadastro_var.trace_add("write", self._alternar_campos)
        self._alternar_campos()

    def _alternar_campos(self, *args):
        tipo = self.tipo_cadastro_var.get()
        self.label_ra.grid_remove()
        self.entry_ra.grid_remove()
        self.label_materia.grid_remove()
        self.option_materia.grid_remove()
        
        if tipo == 'aluno':
            self.label_ra.grid(row=7, column=0, sticky='w', padx=5, pady=5)
            self.entry_ra.grid(row=7, column=1, sticky='ew', padx=5, pady=5, ipady=5)
        elif tipo == 'professor':
            self.label_materia.grid(row=7, column=0, sticky='w', padx=5, pady=5)
            self.option_materia.grid(row=7, column=1, sticky='ew', padx=5, pady=5)
            
    def _processar_cadastro(self):
        tipo = self.tipo_cadastro_var.get()
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha_limpa = self.entry_senha.get().strip()
        conf = self.entry_conf_senha.get().strip()

        if not nome or not email or not senha_limpa:
            messagebox.showerror("Erro", "Campos obrigatórios vazios.")
            return
        if senha_limpa != conf:
            messagebox.showerror("Erro", "Senhas não conferem.")
            return

        if tipo == 'aluno':
            ra = self.entry_ra.get().strip().upper() 
            if len(ra) < 7: messagebox.showerror("Erro", "RA inválido."); return
            usuario = Aluno(nome, email, "", ra, "ADS") 
        else: 
            materia = self.var_materia.get()
            usuario = Professor(nome, email, "", materia)

        sucesso, mensagem = self.gestor_bd.adicionar_usuario(usuario, senha_limpa)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.app.mostrar_tela(TelaLogin)
        else:
            messagebox.showerror("Erro", mensagem)

class TelaPrimeiroAcesso(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=50)
        self.app = app
        self.gestor_bd = app.gestor_bd
        self._criar_widgets()

    def _criar_widgets(self):
        main_frame = ttk.Frame(self, padding=45, style='light.TFrame', relief=FLAT)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(main_frame, text="⚠️ PRIMEIRO ACESSO OBRIGATÓRIO ⚠️", font=('Arial', 18, 'bold'), bootstyle="danger").pack(pady=(0, 10))
        ttk.Label(main_frame, text=f"RA: {self.app.ra_logado}", font=('Arial', 14, 'bold')).pack(pady=5)
        ttk.Label(main_frame, text="Vincule um e-mail e defina nova senha.", wraplength=400, font=('Arial', 11)).pack(pady=(10, 20))

        ttk.Label(main_frame, text="Novo E-mail:", font=('Arial', 11, 'bold')).pack(pady=(15, 0), fill=tk.X)
        self.entry_email = ttk.Entry(main_frame, width=40, bootstyle="primary", font=('Arial', 12))
        self.entry_email.pack(pady=(0, 10), fill=tk.X, ipadx=30, ipady=5)
        
        ttk.Label(main_frame, text="Nova Senha:", font=('Arial', 11, 'bold')).pack(pady=(5, 0), fill=tk.X)
        self.entry_senha = ttk.Entry(main_frame, show="*", width=40, bootstyle="primary", font=('Arial', 12))
        self.entry_senha.pack(pady=(0, 10), fill=tk.X, ipadx=30, ipady=5)
        
        ttk.Button(main_frame, text="Salvar e Acessar Painel", command=self._processar, bootstyle="success", width=30, padding=10).pack(pady=20)

    def _processar(self):
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        ra = self.app.ra_logado
        
        if not email or len(senha) < 6:
            messagebox.showerror("Erro", "Preencha e-mail e senha (mín 6).")
            return

        sucesso, msg = self.gestor_bd.atualizar_aluno_primeiro_acesso(ra, email, senha)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.app.usuario_logado['email'] = email
            self.app.usuario_logado['primeiro_acesso'] = 0 
            self.app.mostrar_tela(PainelAluno)
        else:
            messagebox.showerror("Erro", msg)

class PainelAluno(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=20)
        self.app = app
        self.ra = app.ra_logado
        self.gestor_bd = app.gestor_bd
        self.calculadora = app.calculadora
        self._materia_frames = {}
        self.entradas_projecao = {}
        self.labels_projecao_resultado = {}
        
        self._criar_widgets()
        self._atualizar_todas_abas() 

    def _criar_widgets(self):
        header = ttk.Frame(self, padding=(15, 10), bootstyle="primary")
        header.pack(fill='x', pady=(0, 15))
        ttk.Label(header, text=f"Bem-vindo(a), {self.app.usuario_logado['nome']}!", font=('Arial', 20, 'bold'), bootstyle="inverse-primary").pack(side=tk.LEFT, padx=10)
        ttk.Button(header, text="Sair", command=lambda: self.app.mostrar_tela(TelaLogin), bootstyle="danger").pack(side=tk.RIGHT, padx=10)
        
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(expand=True, fill="both")
        self._criar_aba_resumo()
        for materia in MATERIAS_ADS:
            self._criar_aba_materia(materia)
            
    def _criar_aba_resumo(self):
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text="Sumário")
        self.tree_resumo = ttk.Treeview(frame, columns=('NP1', 'NP2', 'PIM', 'MS', 'Status'), show='headings', bootstyle="info")
        for col in ('NP1', 'NP2', 'PIM', 'MS', 'Status'): self.tree_resumo.heading(col, text=col)
        self.tree_resumo.pack(expand=True, fill='both')
        self.tree_resumo.tag_configure('success', foreground='#28a745'); self.tree_resumo.tag_configure('danger', foreground='#dc3545')

    def _criar_aba_materia(self, materia):
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text=materia)
        frame.columnconfigure(0, weight=1); frame.columnconfigure(1, weight=1)
        
        # Frame Notas
        f_notas = ttk.Labelframe(frame, text="Notas Lançadas", bootstyle="primary")
        f_notas.grid(row=0, column=0, padx=10, sticky='nsew')
        self._materia_frames[materia] = {}
        for i, nome in enumerate(["NP1", "NP2", "PIM", "Média", "Status"]):
            ttk.Label(f_notas, text=f"{nome}:").grid(row=i, column=0, sticky='w')
            lbl = ttk.Label(f_notas, text="-")
            lbl.grid(row=i, column=1, sticky='e')
            self._materia_frames[materia][nome] = lbl

        # Frame Projeção
        f_proj = ttk.Labelframe(frame, text="Simulador (Se MS < 7.0)", bootstyle="info")
        f_proj.grid(row=0, column=1, padx=10, sticky='nsew')
        self.entradas_projecao[materia] = {}
        for i, key in enumerate(['NP1', 'NP2', 'PIM']):
            ttk.Label(f_proj, text=f"Simular {key}:").grid(row=i, column=0)
            e = ttk.Entry(f_proj, width=10); e.grid(row=i, column=1)
            self.entradas_projecao[materia][key] = e
            
        ttk.Button(f_proj, text="Calcular", command=lambda m=materia: self._simular(m)).grid(row=3, columnspan=2, pady=10)
        self.labels_projecao_resultado[materia] = ttk.Label(f_proj, text="Resultado: -")
        self.labels_projecao_resultado[materia].grid(row=4, columnspan=2)
        
        # Feedback
        self.labels_projecao_resultado[materia+"_FB"] = ttk.Label(frame, text="Dica...", bootstyle="secondary", wraplength=700)
        self.labels_projecao_resultado[materia+"_FB"].grid(row=1, columnspan=2, pady=10)

    def _atualizar_todas_abas(self):
        self.tree_resumo.delete(*self.tree_resumo.get_children())
        _, _, pim_g = self.gestor_bd.buscar_notas_aluno(self.ra, PIM_MATERIA)
        
        for mat in MATERIAS_ADS:
            np1, np2, _ = self.gestor_bd.buscar_notas_aluno(self.ra, mat)
            pim = pim_g
            ms, st, cor = self.calculadora.calcular_ms(np1 or 0, np2 or 0, pim or 0)
            
            # Atualiza labels
            lbls = self._materia_frames[mat]
            lbls['NP1'].config(text=f"{np1:.1f}" if np1 else "-")
            lbls['NP2'].config(text=f"{np2:.1f}" if np2 else "-")
            lbls['PIM'].config(text=f"{pim:.1f}" if pim else "-")
            lbls['Média'].config(text=f"{ms:.2f}", bootstyle=cor)
            lbls['Status'].config(text=st, bootstyle=cor)
            
            self.tree_resumo.insert('', END, values=(np1, np2, pim, f"{ms:.2f}", st), tags=(cor,))
            
            # Feedback
            if st in ["Reprovado", "Em Exame"]:
                msg = FEEDBACKS_ESTUDO.get(mat, "Estude mais!")
                self.labels_projecao_resultado[mat+"_FB"].config(text=f"⚠️ {msg}", bootstyle="danger")
            else:
                 self.labels_projecao_resultado[mat+"_FB"].config(text="Aprovado! Parabéns.", bootstyle="success")

    def _simular(self, materia):
        ents = self.entradas_projecao[materia]
        try:
            v_np1 = float(ents['NP1'].get().replace(',','.')) if ents['NP1'].get() else 0.0
            v_np2 = float(ents['NP2'].get().replace(',','.')) if ents['NP2'].get() else 0.0
            v_pim = float(ents['PIM'].get().replace(',','.')) if ents['PIM'].get() else 0.0
            ms, st, cor = self.calculadora.calcular_ms(v_np1, v_np2, v_pim)
            self.labels_projecao_resultado[materia].config(text=f"Simulação: {ms:.2f} ({st})", bootstyle=cor)
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos")

class FormularioLancamentoNotas(tk.Toplevel):
    def __init__(self, master, gestor_bd, materia, ra, callback):
        super().__init__(master); self.gestor = gestor_bd; self.materia = materia; self.ra = ra; self.cb = callback
        self.title(f"Notas - {ra}"); self.geometry("300x250")
        
        ttk.Label(self, text=f"Notas para {materia}", font=('Arial', 10, 'bold')).pack(pady=10)
        self.entries = {}
        for k in ["NP1", "NP2", "PIM"]:
            frame = ttk.Frame(self); frame.pack(pady=5)
            ttk.Label(frame, text=k).pack(side='left')
            self.entries[k] = ttk.Entry(frame, width=10); self.entries[k].pack(side='left')
            
        ttk.Button(self, text="Salvar", command=self._salvar, bootstyle="success").pack(pady=15)
        self._carregar()

    def _carregar(self):
        np1, np2, _ = self.gestor.buscar_notas_aluno(self.ra, self.materia)
        _, _, pim = self.gestor.buscar_notas_aluno(self.ra, PIM_MATERIA) # PIM Global
        
        if np1: self.entries['NP1'].insert(0, np1)
        if np2: self.entries['NP2'].insert(0, np2)
        if pim: self.entries['PIM'].insert(0, pim)
        
        # Regra de negócio: PIM só edita na matéria PIM
        if self.materia != PIM_MATERIA:
            self.entries['PIM'].config(state='disabled')

    def _salvar(self):
        try:
            n1 = float(self.entries['NP1'].get()) if self.entries['NP1'].get() else None
            n2 = float(self.entries['NP2'].get()) if self.entries['NP2'].get() else None
            pim_val = float(self.entries['PIM'].get()) if self.entries['PIM'].get() else None
            
            self.gestor.lancar_nota(self.ra, self.materia, 'NP1', n1 if n1 is not None else 0)
            self.gestor.lancar_nota(self.ra, self.materia, 'NP2', n2 if n2 is not None else 0)
            
            # Se for matéria PIM, lança o PIM.
            if self.materia == PIM_MATERIA and pim_val is not None:
                # Atualiza PIM em TODAS as matérias (Requisito do Sistema)
                for m in MATERIAS_ADS:
                     self.gestor.lancar_nota(self.ra, m, 'PIM', pim_val)

            messagebox.showinfo("Sucesso", "Notas salvas!"); self.cb(self.ra); self.destroy()
        except ValueError: messagebox.showerror("Erro", "Valores numéricos inválidos")

class PainelProfessor(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=20)
        self.app = app; self.gestor = app.gestor_bd; self.materia = app.materia_logado
        
        ttk.Label(self, text=f"Professor - {self.materia}", font=('Arial', 18, 'bold')).pack(pady=10)
        ttk.Button(self, text="Sair", command=lambda: app.mostrar_tela(TelaLogin), bootstyle="danger").pack(anchor='ne')
        
        ttk.Button(self, text="Cadastrar Aluno (Rápido)", command=self._cadastrar_aluno_rapido).pack(pady=5)
        
        self.tree = ttk.Treeview(self, columns=('RA', 'Nome', 'Média', 'Status'), show='headings')
        for c in ('RA', 'Nome', 'Média', 'Status'): self.tree.heading(c, text=c)
        self.tree.pack(expand=True, fill='both')
        self.tree.bind('<Double-1>', self._editar_nota)
        self._atualizar()

    def _atualizar(self, *args):
        self.tree.delete(*self.tree.get_children())
        alunos = self.gestor.buscar_todos_alunos_da_materia(self.materia)
        for nome, ra in alunos:
            np1, np2, _ = self.gestor.buscar_notas_aluno(ra, self.materia)
            _, _, pim = self.gestor.buscar_notas_aluno(ra, PIM_MATERIA)
            ms, st, _ = self.app.calculadora.calcular_ms(np1 or 0, np2 or 0, pim or 0)
            self.tree.insert('', END, values=(ra, nome, f"{ms:.2f}", st))

    def _editar_nota(self, event):
        item = self.tree.selection()
        if not item: return
        ra = self.tree.item(item, 'values')[0]
        FormularioLancamentoNotas(self, self.gestor, self.materia, ra, self._atualizar)
        
    def _cadastrar_aluno_rapido(self):
        # Janela simples para cadastro rápido pelo professor
        top = tk.Toplevel(self); top.title("Novo Aluno")
        ttk.Label(top, text="Nome:").pack(); e_nome = ttk.Entry(top); e_nome.pack()
        ttk.Label(top, text="RA:").pack(); e_ra = ttk.Entry(top); e_ra.pack()
        def save():
             if self.gestor.adicionar_aluno_professor(e_nome.get(), e_ra.get(), self.materia, "123456"):
                 messagebox.showinfo("Ok", "Cadastrado! Senha inicial: 123456"); self._atualizar(); top.destroy()
             else: messagebox.showerror("Erro", "Erro ao cadastrar")
        ttk.Button(top, text="Salvar", command=save).pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()

    