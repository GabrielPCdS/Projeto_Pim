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