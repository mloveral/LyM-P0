import lexer as lex

def parse (tokens):
    pos = 0
    #Lista de diccionarios con los nombres de los macros y los parametros que recibe
    token1 = tokens[pos]
    t_type = token1.type
    macros = {}
    variables = {}
    follows_rules = True
    while pos < len(tokens) and follows_rules:
        token1 = tokens[pos]
        if token1.type == "bEXECUTE":
            pos, follows_rules = parse_execution(tokens, pos+1, variables, macros)
        elif token1.type == "bMACRO":
            pos, follows_rules = parse_new_macro(tokens, pos+1, variables, macros)
        elif token1.type == "bVARIABLE":
            pos, follows_rules = parse_new_variable(tokens, pos+1, variables)
        else:
            follows_rules = False
    
    if follows_rules:
        print("The received program follows the grammar rules")
    else:
        print("The received program does not follow the grammar rules")

def parse_execution (tokens, pos, variables, macros):
    if pos >= len(tokens):
        return pos, False
    
    next_token = tokens[pos]
    if next_token.type == "LBRACE":
        pos, follows_rules = parse_command(tokens, pos+1, variables, macros)
        #Verifica que los comandos terminen con un }
        if pos < len(tokens) and follows_rules: 
            next_token = tokens[pos]
            if next_token.type != "RBRACE":
                follows_rules = False
        else:
            # Si ya se paso de la longitud de la lista sin cerrar con un }, se declara
            #que no sigue las reglas
            follows_rules = False
    else:
        follows_rules = False
    
    return pos+1, follows_rules

def parse_command(tokens, pos, variables, macros):
    """Parsea un comando de acuerdo con la gramática del lenguaje

    :param tokens: Los tokens generados por el lexer a partir del texto
    :type tokens: list
    :param pos: La posicion del current token en la lista de tokens
    :type pos: int
    :param variables: Un diccionario que tiene como llaves los nombres de las
                        variables y como valores los valores de las variables
    :type variables: dict
    :param macros: Un diccionario que tiene como llaves los nombres de los macros
                    y como valores una tupla con el número de parametros que recibe y
                    una lista de los comandos a ejecutar
    :type macros: dict
    :return: La posicion actual y si sigue o no las reglas del lenguaje
    """
    if pos >= len(tokens)-1:
        return pos, False
    
    next_token = tokens[pos]
    follows_rules = True
    # Si no se recibe ningun comando (ni siquiera un nop), se dice que no sigue las reglas
    if next_token.type != "bCOMMANDSEXE" and next_token.type != "bNAME":
        follows_rules = False
        return pos, follows_rules
    
    while pos < len(tokens)-1 and follows_rules:
        next_token = tokens[pos]

        if (next_token.type == "RBRACE" or next_token.type == "RPAREN"):
            break
        
        #Si lo que sigue no es un comando ni un nombre, se declara que no sigue las reglas
        if (next_token.type != "bCOMMANDSEXE" and next_token.type != "bNAME"):
            follows_rules = False
            return pos, follows_rules

        if next_token.type == "bNAME":
            #Mira el caso de que el command sea un macro
            pos, follows_rules = parse_macro(tokens, pos, variables, macros)
        elif next_token.value == "turntomy":
            #Caso en que sea un commando turnToMY
            pos, follows_rules = parse_DCK(tokens, pos+1)
        elif next_token.value == "turntothe":
            #Caso en que sea un commando turnToThe
            pos, follows_rules =parse_O(tokens, pos+1)
        elif next_token.value == "walk" or next_token.value == "jump" or next_token.value == "drop" or next_token.value == "pick" or next_token.value == "grab" or next_token.value == "letgo" or next_token.value == "pop":
            #Caso en que sea un commando walk, jump, drop, pick, grab, letGo y pop
            pos, follows_rules = parse_fun_n(tokens, pos+1, variables)
        elif next_token.value == "moves":
            #Caso en que sea un commando moves
            pos, follows_rules = parse_Ds(tokens, pos+1)
        elif next_token.value == "nop":
            #Caso en que sea un commando nop
            pos += 1
            pass
        elif next_token.value == "safeexe":
            #Caso en que sea un commando safeExe
            pos, follows_rules = parse_CM(tokens, pos+1, variables, macros)
        elif next_token.value == "bCONDITIONAL":
            #Caso en que sea un commando conditional
            if next_token.value == "if":
                pos, follows_rules = parse_conditional(tokens, pos+1)
            else:
                follows_rules = False
        elif next_token.value == "bLOOP":
            #Caso en que sea un commando loop
            if next_token.value == "do":
                pos, follows_rules = parser_loop(tokens, pos+1)
            else:
                follows_rules = False
        elif next_token.value == "bREPEATS":
            #Caso en que sea un commando repeats
            if next_token.value == "repeats":
                pos, follows_rules = parse_conditional(tokens, pos+1)
            else:
                follows_rules = False
        else: 
            follows_rules = False
        
        if pos >= len(tokens):
                follows_rules = False
        else:
            next_token = tokens[pos]
            if next_token.type != "SEMICOLON":
                    follows_rules = False
                    return pos, follows_rules
            else:
                pos += 1
                    

    return pos, follows_rules            
        
def parse_macro(tokens, pos, variables, macros):
    """
    Funcion que verifica si el macro invocado sigue las reglas de produccion
    bNAME'('PARAMS')' donde PARAMS deben ser de tipo value
    """
    if pos >= len(tokens)-2:
        return pos, False
    
    next_token = tokens[pos]
    follows_rules = True
    macro_name = next_token.value
    
    if macro_name not in macros:
        return pos, False
    
    num_params = macros[macro_name][0]
    
    pos+=1
    next_token = tokens[pos]
    
    if next_token.type != "LPAREN":
        follows_rules = False
    
    pos += 1
    contador_param = 0
    # Verifica si los parametros dados son tipo bNAME. Si son más de uno, 
    # verifica que estén separados por comas
    while follows_rules and pos < len(tokens)-1:
        next_token = tokens[pos]
        is_value = parse_n(next_token, variables)
        if not is_value and next_token.type != "RPAREN":
            follows_rules = False
        else:
            if is_value:
                contador_param += 1
            if contador_param > num_params:
                return pos, False
            pos += 1
            next_token = tokens[pos]
            if next_token.type == "RPAREN":
                if contador_param != num_params:
                    follows_rules = False
                break 
            elif next_token.type != "COMA":
                follows_rules = False
        
        pos += 1
    
    next_token = tokens[pos]
    #Si al final (en el caso de que se halla llegado al final del archivo) no termina
    #con un paréntesis, se declara que no sigue las reglas
    if follows_rules and next_token.type != "RPAREN":
        follows_rules = False
    
    return pos+1, follows_rules


def parse_DCK(tokens, pos):
    """ Parsea una direccion para el comando turnToMy(D), donde D
    puede ser left, right, o back

    :param tokens: Los tokens generados por el lexer a partir del texto
    :type tokens: list
    :param pos: La posicion del current token en la lista de tokens
    :type pos: int
    :return: Retorna la posicion del siguiente token y un bool que indica si se siguen las reglas
    """
    
    dir_validas = ["left", "right", "back"]
    if pos >= len(tokens)-2:
        return pos, False
    
    #Se verifica que se empiece con un (
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "LPAREN":
        follows_rules = False
    pos += 1
    
    next_token = tokens[pos]
    #Se verifica que el tipo del token sea una bDIRECTION
    if next_token.type == "bDIRECTIONS" and next_token.value in dir_validas:
        follows_rules = True
        # Actualiza last_O si el token es de tipo bCOMMAND
    else:
        follows_rules = False
    
    pos += 1
    #Se verifica que termine con un )
    next_token = tokens[pos]
    if next_token.type!= "RPAREN":
        follows_rules = False    
    
    return pos+1, follows_rules

def parse_O(tokens, pos):
    if pos >= len(tokens)-2:
        return pos, False
    
    #Se verifica que se empiece con un (
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "LPAREN":
        follows_rules = False
    pos += 1
    
    #Se verifica que el tipo del token sea una bORIENTATION
    if next_token.type == "bORIENTATION":
        # Actualiza last_O si el token es de tipo bCOMMAND
        follows_rules = True
    else:
        follows_rules = False
    
    #Se verifica que termine con un )
    pos += 1
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "RPAREN":
        follows_rules = False
    
    return pos+1, follows_rules

def parse_fun_n(tokens, pos, variables):
    """ Parsea las funciones que reciben como paramentro un valor n

    :param tokens: Los tokens generados por el lexer a partir del texto
    :type tokens: list
    :param pos: La posicion del current token en la lista de tokens
    :type pos: int
    :param variables: Un diccionario donde las llaves son los nombres de las
                        variables declaradas y su valor son los valores asociados
    :return: Retorna la posicion del siguiente token y un bool que indica si se siguen las reglas
    """
    if pos >= len(tokens)-2:
        return pos, False
    
    follows_rules = True
    
    next_token = tokens[pos]
    if next_token.type != "LPAREN":
        return pos, False
    
    pos += 1
    next_token = tokens[pos]
    is_value = parse_n(next_token, variables)
    if not is_value:
        return pos, False
    
    pos += 1
    next_token = tokens[pos]
    if next_token.type!= "RPAREN":
        follows_rules = False
    
    return pos+1, follows_rules

def parse_Ds(tokens, pos):
    if pos >= len(tokens)-2:
        return pos, False
    
    dir_validas = ["forward", "backwards", "left", "right"]
    
    #Se verifica que se empiece con un (
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "LPAREN":
        follows_rules = False
    pos += 1
    
    #Se verifica que en la siguiente posición el token no sea un ), para poder continuar con mas
    # bDIRECTIONS, que despues de cada bDIRECTIONS se ponga una coma y que se termine con un ).  
    while follows_rules and pos < len(tokens)-1:
        next_token = tokens[pos]
        if next_token.type != "bDIRECTIONS" and next_token.value not in dir_validas:
            follows_rules = False
        else:
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN" and next_token.type != "COMA":
                follows_rules = False
            elif next_token.type == "RPAREN":
                break
        pos+=1
    
    if pos <= len(tokens)-1 and next_token.type != "RPAREN":
        next_token = tokens[pos]
        if next_token.type != "RPAREN":
            follows_rules = False
    
    return pos+1, follows_rules

def parse_CM(tokens, pos, variables, macros):
    """Parsea un comando safeExe para que siga las reglas de la gramática

    :param tokens: Los tokens generados por el lexer a partir del texto
    :type tokens: list
    :param pos: La posicion del current token en la lista de tokens
    :type pos: int
    :param variables: Un diccionario que tiene como llaves los nombres de las
                        variables y como valores los valores de las variables
    :type variables: dict
    :param macros: Un diccionario que tiene como llaves los nombres de los macros
                    y como valores una tupla con el número de parametros que recibe y
                    una lista de los comandos a ejecutar
    :type macros: dict
    :return: La posicion actual y si sigue o no las reglas del lenguaje
    """
    if pos >= len(tokens) - 1:
        return pos, False
    
    #Se verifica que se empiece con un (
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "LPAREN":
        follows_rules = False
    pos += 1
    
    #Se verifica que en la siguiente posición el token no sea un ), para poder continuar con mas
    # bCOMMANDSEXE, que despues de cada bCOMMANDSEXE se ponga una coma y que se termine con un ). 
    while follows_rules and pos < len(tokens)-1 and next_token.type != "RPAREN":
        next_token = tokens[pos]
        if next_token.type != "bCOMMANDSEXE":
            follows_rules = False
        else:
            pos, follows_rules = parse_command(tokens, pos, variables, macros)
            next_token = tokens[pos]
            if next_token.type != "RPAREN":
                follows_rules = False
            elif next_token.type == "RPAREN":
                break
                        
        pos += 1
    
    return pos+1, follows_rules

def parse_for_n():
    if pos >= len(tokens)-2:
        return pos, False
    
    #Se verifica que se empiece con un (
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "LPAREN":
        follows_rules = False
    pos += 1
    
    #Se verifica que el tipo del token sea una bNUMBER
    next_token = tokens[pos]
    if parse_n(next_token):
        follows_rules = True

    #Se verifica que termine con un (
    pos += 1
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "RPAREN":
        follows_rules = False
    
    return pos+1, follows_rules

def parse_new_macro(tokens, pos,variables, macros):
    if pos >= len(tokens)-2:
        return pos, False

    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "bNAME":
        follows_rules = False
        return pos, follows_rules
    
    macro_name = next_token.value
    num_params = 0
    commands = []
    
    pos += 1
    next_token = tokens[pos]
    if next_token.type!= "LPAREN":
        follows_rules = False
        return pos, follows_rules
    
    pos += 1
    while pos < len(tokens)-1 and follows_rules:
        next_token = tokens[pos]
        
        if next_token.type == "bNAME":
            num_params+=1 #se agrega un parametro
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN" and next_token.type!= "COMA":
                follows_rules = False
            elif next_token.type == "RPAREN":
                break
            else:
                pos += 1
        else:
            follows_rules = False
    
    if  follows_rules and pos <= len(tokens)-1:
        next_token = tokens[pos]
        if next_token.type != "RPAREN":
            follows_rules = False
    
    pos += 1
    if pos < len(tokens)-1:
        next_token = tokens[pos]
        if next_token.type != "LBRACE":
            follows_rules = False
        pos += 1
        while follows_rules and pos < len(tokens):
            next_token = tokens[pos]
            if next_token.type == "bCONDITIONAL":
                if next_token.value == "if":
                    pos, follows_rules = parse_conditional(tokens, pos+1)
                else:
                    follows_rules = False
            elif next_token.type == "bLOOP":
                if next_token.value == "do":
                    pos, follows_rules = parse_conditional(tokens, pos+1)
                else:
                    follows_rules = False
            elif next_token.type == "bREPEATS":
                if next_token.value == "repeats":
                    pos, follows_rules = parse_conditional(tokens, pos+1)
                else:
                    follows_rules = False
            elif next_token.type == "bCOMMANDSEXE":
                
                pos, follows_rules = parse_command(tokens, pos, variables, macros)
            elif next_token.type != "RBRACE":
                follows_rules = False
            next_token = tokens[pos]
            if next_token.type == "RBRACE":
                break
            pos += 1
        
        if follows_rules and pos <= len(tokens)-1:
            next_token = tokens[pos]
            if next_token.type != "RBRACE":
                follows_rules = False
            else:
                macros[macro_name] = (num_params, commands)
    else:
        follows_rules = False
    
    return pos+1, follows_rules

def parse_new_variable(tokens, pos, variables):
    tokens_len = len(tokens)
    if pos >= len(tokens)-2:
        return pos, False

    follows_rules = True
    
    next_token = tokens[pos]
    if next_token.type != "bNAME":
        follows_rules = False
        return pos, follows_rules
    
    variable = next_token.value
    
    pos += 1
    next_token = tokens[pos]
    if next_token.type!= "EQUALS":
        follows_rules = False
        return pos, follows_rules
    
    pos += 1
    next_token = tokens[pos]
    follows_rules = parse_n
    
    if follows_rules:
        variables[variable] = next_token.value

    return pos+1, follows_rules

def parse_n(token, variables):
    """
    Parser los posibles valores. Si el valor no es ninguno de los permitidos, se devuelve
    que no sigue las reglas
    """
    if token.type == "bNAME":
        #Verifica que si es una variable, que esta se haya declarado antes
        if token.value in variables:
            return True
        else:
            return False
    elif token.type == "NUMBER" or token.type == "bCONSTANTS":
        return True
    else:
        return False

def parse_conditional(tokens, pos):
    if pos >= len(tokens):
        return pos, False
    next_token = tokens[pos]
    follows_rules = True
    if next_token.value == "not":
        pos, follows_rules = parse_conditional(tokens, pos+1)
    elif next_token.type != "LPAREN":
        follows_rules = False
    
    pos, follows_rules = parse_condition(tokens, pos+1)
    
    if pos >= len(tokens) and follows_rules:
        follows_rules = False
    else:
        next_token = tokens[pos]
        if next_token.type != "RPAREN":
            follows_rules = False
    
    return pos+1, follows_rules

def check_question_mark(tokens, pos):
    """
    Funcion que verifica si el token es un signo de interrogacion
    """
    pos += 1
    next_token = tokens[pos]
    if next_token.type == "QUESTIONMARK":
        return True, pos
    else:
        return False, pos


def parse_condition(tokens, pos):
    if pos >= len(tokens)-3:
        return pos, False
    
    next_token = tokens[pos]
    hay_question, pos = check_question_mark(tokens, pos)
    if not hay_question:
        return pos, False
    
    next_token = tokens[pos]
    follows_rules = True
    if next_token.type != "bCONDITION":
        follows_rules = False
        return pos, follows_rules
    
    value = next_token.value
    
    pos += 1
    next_token = tokens[pos]
    if next_token.type!= "LPAREN":
        follows_rules = False
        return pos, follows_rules
    
    pos+= 1
    next_token = tokens[pos]
    if value == "zero?":
        if not parse_n(next_token):
            follows_rules = False
            return pos, follows_rules
    elif value == "isfacing?":
        if next_token.type != "bORIENTATION":
            follows_rules = False
            return pos, follows_rules
    elif value == "isblocked?":
        if next_token.type!= "bDIRECTION":
            follows_rules = False
            return pos, follows_rules
    
    pos+= 1
    next_token = tokens[pos]
    if next_token.type!= "RPAREN":
        follows_rules = False
    
    return pos+1, follows_rules

def parser_loop(tokens, pos):
    if pos >= len(tokens) - 4:
        return pos, False
    
    next_token = tokens[pos]
    follows_rules = True
    
    # se verifica que le siga un (
    next_token = tokens[pos]
    if next_token.type != "LPAREN":
        follows_rules = False
    pos += 1
    
    # despues del parentesis tiene que ir una condicción
    next_token = tokens[pos]
    if next_token.type == "bCONDITION":
        
        # se verifica que condición es y si es True or False para poder seguir corriendo el programa
        # tambien se verifica que las especificaciones de las condiciones esten entre parentesis
        if next_token.value == "isblocked":
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "QUESTIONMARK":
                follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "LPAREN":
                follows_rules = False
                
            pos += 1
            next_token = tokens[pos]
            por_DCK, follows_rules_DCK = parse_DCK(tokens, pos)
            if not follows_rules_DCK:
                    follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN":
                follows_rules = False
        
        elif next_token.value == "isfacing":
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "QUESTIONMARK":
                follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "LPAREN":
                follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            pos_O, follows_rules_O, last_O = parse_O(tokens, pos)
            if follows_rules_O != last_O:
                    follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN":
                follows_rules = False
            
            
        elif next_token.value == "zero":
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "QUESTIONMARK":
                follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "LPAREN":
                follows_rules = False
                        
            pos += 1
            next_token = tokens[pos]
            if next_token.value == 0:
                    follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN":
                follows_rules = False
            
        elif next_token.value == "not":
            pos += 1
            next_token = tokens[pos]
            if next_token.type != "LPAREN":
                follows_rules = False
            
            pos += 1
            next_token = tokens[pos]
            if next_token.value == True:
                    follows_rules = False

            pos += 1
            next_token = tokens[pos]
            if next_token.type != "RPAREN":
                follows_rules = False
        
    # se verifica que despues de las condiciones se cierre el parentesis inicial
    pos+= 1
    next_token = tokens[pos]
    if next_token.type!= "RPAREN":
        follows_rules = False
    
    # se revisa que despues se encuentre un bloque
    pos += 1
    next_token = tokens[pos] 
    if not parse_execution(tokens, pos):
        follows_rules = False
    
    # se verifica que se termine la instruccion con un od
    pos += 1
    next_token = tokens[pos]
    if next_token.type != "bLOOP" and next_token.value != "od":
        follows_rules = False
        
    return pos+1, follows_rules
        
def parser_repeat(tokens, pos):
    next_token = tokens[pos]
    follows_rules = True
    
    #Verificamos que empiece con un repeat
    if next_token.type != "bREPEAT" and next_token.value != "repeat":
        follows_rules = False
    
    #Verificamos que lo que le sigue sea un valor n
    pos += 1
    next_token = tokens[pos]
    if not parse_n(next_token):
        follows_rules = False
    
    #Verificamos que en le siguiente haya un repeat
    pos += 1
    next_token = tokens[pos] 
    if next_token.type != "bREPEAT" and next_token.value != "times":
        follows_rules = False
    
    #Verificamos que despues de ese repeat haya un bloque
    pos += 1
    next_token = tokens[pos] 
    if not parse_execution(tokens, pos):
        follows_rules = False
    
    return pos+1, follows_rules


#Prueba
lexer = lex.Lexer(lex.rules)

# Example input
input_text1 = "NEW VAR hola = 3" #new variable

input_text2 = "new var two =2 new var trois =3 new var ochenta = 12 new var left2=left Exec { if (isfacing?(north)) then {pop(two);}else{nop;} fi pop((2);) } EXEC { if not(isBlocked?(left ) ) then { turnToMy( left2 ) ; walk(balloonsHere) ; } else {nop;} fi } EXEC { safeExe (walk(1) ) ; }"

input_text3 = "new macro diego(ganas, de, vivir) { nop; }"

input_text4 = "new var hola = 3 new macro diego(ganas, de, vivir) { nop; } exec{safeExe(pop(balloonsHere); jump(2););}"

# Tokenize the input
tokens = lexer.tokenize(input_text4)

print(tokens)
parse(tokens)    