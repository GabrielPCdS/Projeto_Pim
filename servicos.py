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
    # NOVO MÉTODO: VALIDAÇÃO DE ENTRADA
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
        # APLICANDO A NOVA VALIDAÇÃO
        valido, erro_msg = self._validar_notas_range(np1, np2, pim)
        if not valido:
            return None, f"Erro de Cálculo: {erro_msg}", "secondary"

        # Cálculo da Média Semestral
        ms = (np1 * self.PESO_NP1) + (np2 * self.PESO_NP2) + (pim * self.PESO_PIM)
        ms_arredondada = round(ms, 2)
        
        status = ""
        cor_status = "" 
        
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
        nota_necessaria = 10.0 - ms
        nota_necessaria_limitada = max(self.NOTA_MINIMA, min(nota_necessaria, self.NOTA_MAXIMA))
        return round(nota_necessaria_limitada, 2)