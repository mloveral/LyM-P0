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
                    value = match.group().lower() if token_type[0] == "b" else match.group()
                    tokens.append(Token(token_type, match.group()))
                    pos = match.end()
            else:
                raise SyntaxError(f"Unexpected character: {text[pos]}")
                    
        return tokens
                    
# Reglas de producción para el lenguaje
rules = [
    ("bEXECUTE", r'\b exec'), # Ejecutar
    ("bDEFINITION", r'\b(new var|new macro)'), #Definiciones de variables o macros
    ("bNOMBRE", r'\w'), # Nombres de variables o macros
    
    ("LPAREN", r'\('),  # Paréntesis izquierdo
    ("RPAREN", r'\)'),  # Paréntesis derecho
    ("LBRACE", r'\{'),  # Llave izquierda
    ("RBRACE", r'\}'),  # Llave derecha
    ("bMACRO", r'\b(new macro)'),  # Definición de macro
    ("bVARIABLE", r'\b(new variable)'),  # Definición de variable
    ("bNAME", r'\w+'),  # Nombres de variables o macros (modificado para capturar nombres completos)
    ("NUMBER", r'\d+(\.\d*)?'),  # Valores numéricos
    ("bCONSTANTS", r'\b(size|myx|myy|mychips|myballoons|balloonshere|chipshere|roomforchips)\b'),  # Constantes
    ("bCONDITIONAL", r'\b(if|then|else|fi)\b'),  # Condicionales
    ("bLOOP", r'\b(do|od)\b'),  # Bucles
    ("bREPEAT", r'\b(rep|times)\b'),  # Repetición
    ("bCONDITION", r'\b(isblocked\?|isfacing\?|zero\?|not)\b'),  # Condiciones
    ("SEMICOLON", r'\;'),  # Punto y coma
    ("bDIRECTIONS", r'\b(forward|right|backwards|left)\b'),  # Direcciones
    ("bDIRECTION", r'\b(left|right|back)\b'),  # Dirección
    ("bORIENTATION", r'\b(north|east|south|west)\b'),  # Orientación
    ("bCOMMANDSEXE", r'\b(turntomy|turntothe|walk|jump|drop|pick|grab|letgo|pop)\b'),  # Comandos de ejecución
    ("bOTHERCOMMANDS", r'\b(moves|nop|safeexe)\b')  # Otros comandos
    
]
