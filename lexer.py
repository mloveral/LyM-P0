import re
from Typing import List, Tuple

# Clase para dividir el archivo de texto en pequeños tokens 
#para simplificar el proceso de ver si la estructura del archivo
#sigue las reglas de producción del lenguaje
class Token:
    def __init__(self, i_type:str, value: str):
        self.type = i_type
        self.value = value
        
    # Para mostrar el objeto y debuggear el código
    def __repr__(self):
        return f"{self.type}: {self.value}"

# Clase para analizar el texto y extraer tokens
# Esta clase define el lexer del parser
class Lexer:
    def __init__(self, rules: List[Tuple[str, str]]):
        self.reglas = [(regla, re.compile(pattern)) for regla, pattern in rules]
        self.espacio= re.compile(r'\s+')
    
    def tokenize(self, text:str) -> List[Token]:
        tokens = []
        pos = 0
        while pos < len(text):
            match = self.espacio.match(text, pos)
            if match:
                pos = match.end()
                continue 
                
            for token_type, pattern in self.rules:
                match = pattern.match(text, pos)
                if match:
                    tokens.append(Token(token_type, match.group()))
                    pos = match.end()
            else:
                raise SyntaxError(f"Unexpected character: {text[pos]}")
                    
        return tokens
                    
# Reglas de producción para el lenguaje
rules = [
    ("EXECUTE", r'\bEXEC'),
    ("DEFINITIONS", r'\bNEW'),
]