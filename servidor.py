# Bibliotecas
from socket import *
from time import *
from datetime import datetime

# Endereco do servidor, constantes
PORTA_SERVIDOR = 7777
IP_SERVIDOR = "localhost"
endereco_servidor = (IP_SERVIDOR, PORTA_SERVIDOR)

# Ligar o socket com o ip e porta selecionados
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(endereco_servidor)

# Guardar nomes e endereços de clientes conectados em um dicionário
clientes_conectados = {}
ban_cont = {}
clientes_banidos = []
temp = ""

#--------------------Funcoes criadas--------------------#

# Procurar nome do cliente, tendo seu endereço
def procurar_nome(endereco_cliente):
    for nome in clientes_conectados:
        if(clientes_conectados[nome] == endereco_cliente):
            return nome

# Enviar mensagem para todos menos para um selecionado
def enviar_evento(msg, endereco_ignorar):
    for nome in clientes_conectados:
        #Se for o proprio cliente, ignorar
        if(clientes_conectados[nome] == endereco_ignorar):
            continue
        # Se não for, enviar a mensagem
        else:
            serverSocket.sendto(msg.encode(), clientes_conectados[nome])

# Pegar a hora atual do servidor em string
def hora():
    h = datetime.now().hour
    m = datetime.now().minute
    s = datetime.now().second
    if h <= 9:
        h = f'0{h}'
    if m <= 9:
        m = f'0{m}'
    if s <= 9:
        s = f'0{s}'
    return(f'{h}:{m}:{s}')

#------------------------------------------------------#

print("Socket do servidor ligado.")

while True:

    #--------------------Esperar receber algo--------------------#

    print("Esperando Receber algum dado novo...")
    dado, endereco_cliente = serverSocket.recvfrom(1024)
    
    print("Novos dados Recebidos.")
    dado_dec = dado.decode()

    #---------------------Se Banido, ignorar---------------------#

    if(endereco_cliente in clientes_banidos):
        serverSocket.sendto("Cliente banido!".encode(), endereco_cliente)

    #---------------Funcionalidade conectar à sala---------------#
    
    #Verificando se o que recebeu é um registro novo
    elif(dado_dec[0:16] == "hi, meu nome eh "):
        
        # Se não estiver registrado, adicionar e avisar
        if(dado_dec[16:] not in clientes_conectados):
            clientes_conectados[dado_dec[16:]] = endereco_cliente
            ban_cont[dado_dec[16:]] = 0
            serverSocket.sendto("cliente_aceito".encode(), endereco_cliente)
            # Avisar a todos o novo usuário que entrou
            enviar_evento("-> "+dado_dec[16:]+" entrou no chat.", endereco_cliente)
            
        # Se nome já estiver registrado, rejeitar
        else:
            serverSocket.sendto("cliente_recusado".encode(), endereco_cliente)

    #---------------------Funcionalidade Bye---------------------#

    elif(dado_dec == "bye" and (len(dado_dec) == 3)):
        # Procura o nome pelo endereço, deleta do dicionario de clientes e avisa
        nome_cliente = procurar_nome(endereco_cliente)
        del clientes_conectados[nome_cliente]
        del ban_cont[nome_cliente]
        enviar_evento("-> "+nome_cliente+" saiu do chat", endereco_cliente)

    #---------------------Funcionalidade Lits---------------------#

    elif(dado_dec == "list"  and (len(dado_dec) == 4)):
        todos_nomes = ""
        
        for x in clientes_conectados:
            todos_nomes += "-" + x + "\n"
        serverSocket.sendto(("\n"+todos_nomes).encode(), endereco_cliente)

    #------------------Funcionalidade Particular------------------#

    elif(dado_dec[0] == '@'):
        # Pegar nome origem, nome destino e mensagem particular
        para_nome_part = dado_dec.split(' ')[0][1:]
        mensagem_part = dado_dec.replace('@'+para_nome_part+' ', '')
        de_nome_part = procurar_nome(endereco_cliente)
        
        if(para_nome_part not in clientes_conectados):
            serverSocket.sendto("Este usuário não existe!".encode(), endereco_cliente)
        else:
            serverSocket.sendto((hora() + " @" + de_nome_part + ": " + mensagem_part).encode() , clientes_conectados[para_nome_part])

    #-------------------Funcionalidade Expulsão-------------------#

    elif(dado_dec[0:5] == "ban @"):

        # Informar se o usuário votado não existe
        if(dado_dec[5:] not in clientes_conectados):
            serverSocket.sendto("Este usuário não existe!".encode(), endereco_cliente)
            
        # Incrementar contador se existe
        else:
            ban_cont[dado_dec[5:]] = ban_cont[dado_dec[5:]] + 1

        # Checar todos usuários, se algum tiver +2/3 da sala, bé banido
        for x in ban_cont:
            if(ban_cont[x] >= ((2*len(clientes_conectados))/3)):
                serverSocket.sendto("Cliente banido!".encode(), clientes_conectados[x])
                clientes_banidos.append(clientes_conectados[x])
                # Excluiu cliente banido da conexão
                del clientes_conectados[x]
                temp = x

        # Excluir cliente banido do contador
        if(temp != ""):
            print(temp)
            del ban_cont[temp]
            temp = ""

    #-------------------Enviar Mesagens de chat-------------------#

    else:
        enviar_evento(hora() + ' '+ procurar_nome(endereco_cliente) + ': ' + dado_dec, endereco_cliente)
    print("Dados processados.\n")

    



    
