import re
from typing import List, Tuple

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

    def returnDict(self):
        return {'type': self.type, 'value': self.value}

# Clase para analizar el texto y extraer tokens
# Esta clase define el lexer del parser
class Lexer:
    def __init__(self, rules: List[Tuple[str, str]]):
        self.rules = [(token_type, re.compile(pattern)) for token_type, pattern in rules]
        self.espacio= re.compile(r'\s+')
    
    def tokenize(self, text:str) -> List[Token]:
        
        text = text.lower()
        
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
                    tokens.append(Token(token_type, value))
                    pos = match.end()
                    found_match = True
            
            if not found_match:
                raise SyntaxError(f"Unexpected character: {text[pos]}")
                    
        return tokens
                    
# Reglas para formar tokens
rules = [
    ("LPAREN", r'\('),  # Paréntesis izquierdo
    ("RPAREN", r'\)'),  # Paréntesis derecho
    ("LBRACE", r'\{'),  # Llave izquierda
    ("RBRACE", r'\}'),  # Llave derecha
    ("bCONSTANTS", r'\b(size|myx|myy|mychips|myballoons|balloonshere|chipshere|roomforchips)\b'),  # Constantes
    ("bCONDITIONAL", r'\b(if|then|else|fi)\b'),  # Condicionales
    ("bLOOP", r'\b(do|od)\b'),  # Bucles
    ("bREPEAT", r'\b(rep|times)\b'),  # Repetición
    ("bCONDITION", r'\b(isblocked|isfacing|zero|not)\b'),  # Condiciones
    ("QUESTIONMARK", r'\?'),
    ("SEMICOLON", r'\;'),  # Punto y coma
    ("COMA", r'\,'), # Comma
    ("EQUALS", r'\='), # Equals
    ("bDIRECTIONS", r'\b(forward|right|backwards|left|back)\b'),  # Direcciones
    ("bORIENTATION", r'\b(north|east|south|west)\b'),  # Orientación
    ("bCOMMANDSEXE", r'\b(turntomy|turntothe|walk|jump|drop|pick|grab|letgo|pop|moves|nop|safeexe)\b'),  # Otros comandos 
    ("bEXECUTE", r'\b(exec)\b'), # Ejecutar
    ("bMACRO", r'\b(new macro|newmacro)\b'),  # Definición de macro
    ("bVARIABLE", r'\b(new var|newvar)\b'),  # Definición de variable
    ("NUMBER", r'\d+(\.\d*)?'),  # Valores numéricos 
    ("bNAME", r'\w+'),  # Nombres de variables o macros (modificado para capturar nombres completos) 
]

lexer = Lexer(rules)

# Example input
input_text = "safeExe (walk(1) ) ; New Macro { } exec1 New Variable isblocked?"

# Tokenize the input
#tokens = lexer.tokenize(input_text)

# Output the list of tokens
#print(tokens)
