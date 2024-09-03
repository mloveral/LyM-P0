import lexer as lex

lexer = lex.Lexer(lex.rules)

# Example input
input_text = "safeExe (walk(1) ) ; New Macro { } exec1 New Variablew"

# Tokenize the input
tokens = lexer.tokenize(input_text)

def parse (tokens):
    pos = 0
    #Lista de diccionarios con los nombres de los macros y los parametros que recibe
    token1 = tokens[pos]
    follows_rules = True
    while pos < len(tokens) and follows_rules:
        if token1.type == "bEXECUTION":
            pos, follows_rules = parse(tokens, pos+1)
        elif token1.type == "bNEW_MACRO":
            parse_new_macro(tokens, pos+1)
        elif token1.type == "bNEW_VARIABLE":
            parse_new_variable(tokens, pos+1)
        else:
            follows_rules = False
    
    if follows_rules:
        print("The received program follows the grammar rules")
    else:
        print("The received program does not follow the grammar rules")

def parse_execution (tokens, pos):
    next_token = tokens[pos]
    if next_token.type == "LBBRACE":
        pos, follows_rules = parse_command(tokens, pos+1)
    else:
        follows_rules = False
    
    return pos+1, follows_rules

def parse_command(tokens, pos):
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "bCOMMANDSEXE":
        follows_rules = False
        return pos, follows_rules
    
    while pos < len(tokens)-1 and follows_rules:
        next_token = tokens[pos]

        #Si lo que sigue no es un comando ni un }, se declara que no sigue las reglas
        if (next_token.type != "bCOMMANDSEXE" and next_token.type != "RBRACE"):
            follows_rules = False
            return pos, follows_rules
        
        # 
        if (next_token.type != "RBRACE"):
            break

        #Mira el caso de que el command sea 
        if next_token.value == "bNAME":
            pos, follows_rules = parse_macro(tokens, pos+1)
        elif next_token.value == "turnToMy":
            pos, follows_rules = parse_DCK(tokens, pos+1)
        elif next_token.value == "turnToThe":
            pos, follows_rules =parse_O(tokens, pos+1)
        elif next_token.value == "walk" or next_token.value == "jump" or next_token.value == "drop" or next_token.value == "pick" or next_token.value == "grab" or next_token.value == "letGo" or next_token.value == "pop":
            pos, follows_rules = parse_n(tokens, pos+1)
        elif next_token.value == "moves":
            pos, follows_rules = parse_Ds(tokens, pos+1)
        elif next_token.value == "nop":
            pass
        elif next_token.value == "safeExe":
            pos, follows_rules = parse_CM(tokens, pos+1)
        
        if pos >= len(tokens):
                follows_rules = False
        else:
            next_token = tokens[pos]
            if next_token.type != "SEMICOLON":
                    follows_rules = False
                    return pos, follows_rules
                    
        pos += 1
    
    #Finalmente, verifica que los comandos terminen con un }
    if (pos < len(tokens)): 
        next_token = tokens[pos]
        if next_token.type != "RBRACE":
            follows_rules = False
    else:
        # Si ya se paso de la longitud de la lista sin cerrar con un }, se declara
        #que no sigue las reglas
        follows_rules = False

    return pos, follows_rules
            
        
def parse_macro(tokens, pos):
    """
    Funcion que verifica si el macro invocado sigue las reglas de produccion
    bNAME'('PARAMS')' donde PARAMS deben ser de tipo bNAME
    """
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "LPAREN":
        follows_rules = False
    
    pos += 1
    # Verifica si los parametros dados son tipo bNAME. Si son más de uno, 
    # verifica que estén separados por comas
    while follows_rules and pos < len(tokens)-1 and next_token.type != "RPAREN":
        next_token = tokens[pos]
        if next_token.type != "bNAME" and next_token.type != "RPAREN":
            follows_rules = False
        else:
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN" and next_token.type != "COMMA":
                follows_rules = False
        
        pos += 1
    
    next_token = tokens[pos]
    #Si al final (en el caso de que se halla llegado al final del archivo) no termina
    #con un paréntesis, se declara que no sigue las reglas
    if follows_rules and next_token.type != "RPAREN":
        follows_rules = False
    
    return pos+1, follows_rules


def parse_DCK(tokens, pos):
    next_token = tokens[pos]
    follows_rules = False
    if next_token.type == "bDIRECTION":
        follows_rules = True
    return pos+1, follows_rules

def parse_O(tokens, pos):
    next_token = tokens[pos]
    follows_rules = False
    if next_token.type == "bORIENTATION":
        follows_rules = True
    return pos+1, follows_rules

def parse_n(tokens, pos):
    next_token = tokens[pos]
    follows_rules = False
    if next_token.type == "NUMBER":
        follows_rules = True
    return pos+1, follows_rules

def parse_Ds(tokens, pos):
    next_token = tokens[pos]
    follows_rules = False
    if next_token.type == "bDIRECTIONS":
        follows_rules = True
    
    pos += 1
    while follows_rules and pos < len(tokens)-1 and next_token.type != "RPAREN":
        next_token = tokens[pos]
        if next_token.type != "bDIRECTIONS":
            follows_rules = False
        else:
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN" and next_token.type != "COMMA":
                follows_rules = False
    
    return pos+1, follows_rules

def parse_CM(tokens, pos):
    next_token = tokens[pos]
    follows_rules = False
    if next_token.type == "bCOMMANDSEXE":
        follows_rules = True
    
    pos += 1
    while follows_rules and pos < len(tokens)-1 and next_token.type != "RPAREN":
        next_token = tokens[pos]
        if next_token.type != "bCOMMANDSEXE":
            follows_rules = False
        else:
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN" and next_token.type != "COMMA":
                follows_rules = False

        pos, follows_rules = parse_command(tokens, pos+1)
    
    return pos+1, follows_rules


def parse_new_variable(tokens, pos):
    