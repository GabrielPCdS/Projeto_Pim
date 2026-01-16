from typing import Tuple, Union
import math 

class CalculadoraAcademica:
    
    # Constantes
    PESO_NP1 = 0.4
    PESO_NP2 = 0.4
    PESO_PIM = 0.2
    NOTA_APROVACAO = 7.0
    NOTA_EXAME_MIN = 4.0 
    NOTA_MAXIMA = 10.0
    NOTA_MINIMA = 0.0

    # -----------------------------------------------
    # VALIDAÇÃO DE ENTRADA
    # -----------------------------------------------
    def _validar_notas_range(self, np1: float, np2: float, pim: float) -> Tuple[bool, str]:
        """
        Verifica se as notas de entrada estão no intervalo [0.0, 10.0].
        Retorna (True, "") se forem válidas, ou (False, "Mensagem de Erro") caso contrário.
        """
        notas = {'NP1': np1, 'NP2': np2, 'PIM': pim}
        
        for nome, nota in notas.items():
            if not (self.NOTA_MINIMA <= nota <= self.NOTA_MAXIMA):
                return False, f"A nota de {nome} ({nota:.2f}) deve estar entre {self.NOTA_MINIMA:.1f} e {self.NOTA_MAXIMA:.1f}."
        
        return True, ""
    
    # -----------------------------------------------
    # MÉTODOS ACADÊMICOS
    # -----------------------------------------------

    def calcular_ms(self, np1: float, np2: float, pim: float) -> Tuple[Union[float, None], str, str]:
        """
        Calcula a Média Semestral (MS), o Status e a Cor do Status.
        Retorno: (MS | None, Status, Cor_Bootstrap)
        """
        # APLICANDO A VALIDAÇÃO
        valido, erro_msg = self._validar_notas_range(np1, np2, pim)
        if not valido:
            # Retorna None para a média e uma mensagem de erro/status de falha
            return None, f"Erro: {erro_msg}", "secondary"

        # Cálculo da Média Semestral
        ms = (np1 * self.PESO_NP1) + (np2 * self.PESO_NP2) + (pim * self.PESO_PIM)
        ms_arredondada = round(ms, 2)
        
        status = ""
        cor_status = "" # Cor para o ttkbootstrap
        
        if ms_arredondada >= self.NOTA_APROVACAO:
            status = "Aprovado"
            cor_status = "success"
        elif ms_arredondada >= self.NOTA_EXAME_MIN:
            status = "Em Exame"
            cor_status = "warning"
        else:
            status = "Reprovado"
            cor_status = "danger"
            
        return ms_arredondada, status, cor_status

    def calcular_nota_exame(self, ms: float) -> float:
        """
        Calcula a nota mínima necessária no Exame Final (para a média final ser 5.0).
        Média Final = (MS + Exame) / 2
        """
        if ms is None: return 0.0
        
        # Se a MS for 10.0, a nota necessária é 0.0.
        nota_necessaria = 10.0 - ms
        
        # Garante que a nota esteja no intervalo [0.0, 10.0]
        nota_necessaria_limitada = max(self.NOTA_MINIMA, min(nota_necessaria, self.NOTA_MAXIMA))
        
        return round(nota_necessaria_limitada, 2)
        
    def gerar_feedback_ia(self, ms: float, status: str, materia: str) -> str:
        """Gera um feedback motivacional baseado no status."""
        
        if ms is None or status.startswith("Erro"):
            return "Não foi possível gerar feedback. Verifique a validade das notas informadas."
            
        if status == "Aprovado":
            return f"Parabéns! Sua média em **{materia}** é excelente ({ms:.2f}). Você está **Aprovado**! Mantenha o foco. 🎉"
        elif status == "Em Exame":
            nota_exame = self.calcular_nota_exame(ms)
            return f"Atenção! Sua média em **{materia}** é {ms:.2f}. Você está de **Exame Final**. Precisa de aprox. **{nota_exame:.2f}** no Exame. 📚"
        elif status == "Reprovado":
            return f"Alerta! Sua média em **{materia}** ({ms:.2f}) indica **Reprovação**. 🛑"
        else:
            return "Status acadêmico em análise."
        