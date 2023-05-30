# Bibliotecas
from socket import *
from time import *
import threading

TEMPO_BAN = 15

# Endereco do servidor, constantes
PORTA_SERVIDOR = 7777
IP_SERVIDOR = 'localhost'
endereco_servidor = (IP_SERVIDOR, PORTA_SERVIDOR)

# Variáveis globais
msg = ""
leitura_buffer = ""
CONECTADO = 0
tempo_ant = -TEMPO_BAN

# Thread de receber e printar mensagens
def checar_mensagens():
    while True:
        # Se estiver conectado (foi registrado), ficar checando buffer
        if(CONECTADO == 1):
            leitura_buffer, endereco_servidor = clienteSocket.recvfrom(1024)
            print(leitura_buffer.decode())

# Criar socket do cliente
clienteSocket = socket(AF_INET, SOCK_DGRAM)

#Inicializar Thred
threading.Thread(target=checar_mensagens).start()

print("Primeiramente se conecte com o servidor (hi, meu nome eh <nome>).")

while True:

    # Enquanto não se registrar / não estiver conectado
    while (msg[0:15] != "hi, meu nome eh " and (not CONECTADO)):
        msg = str(input(''))
        msg = msg.strip()

        # Tentou registrar com nome muito pequeno
        if(msg[0:16] == "hi, meu nome eh " and len(msg) <= 18):
            print("Digite algum nome com pelo menos 3 caracteres!")

        # Registrou com nome correto
        if(msg[0:16] == "hi, meu nome eh " and len(msg) > 18):
            msg_enc = msg.encode()
            msg = ""

            # Enviar nome de registro
            clienteSocket.sendto(msg_enc, endereco_servidor)
            print("Registro enviado.")

            # Ler resposta do servidor, se aceitou ou se o nome já existe
            leitura_buffer, endereco_servidor = clienteSocket.recvfrom(1024)
            if(leitura_buffer.decode() == "cliente_aceito"):
                print("Entrou no Chat.")
                CONECTADO = 1
            elif(leitura_buffer.decode() == "cliente_recusado"):
                print("Nome já cadastrado")
                CONECTADO = 0

    # Como já conectado, não pode registrar de novo
    while True:
        msg = str(input(''))
        if((msg[0:15] == "hi, meu nome eh")):
            print("Você já se cadastrou")
        elif(msg == ""):
            continue
        else:
            break

    # Já registrado e enviando mensagens corretas
    msg = msg.strip()

    # Tratar mensagem particular, não enviar se tiver algo errado (continue)
    if(msg[0] == '@'):
        #Tiver apenas @ ou @ sem o nome
        if(len(msg) == 1 or msg[0:2] == "@ "):
            print("Digite algum nome particular!")
            continue
        #Tiver @ e nome, mas sem mensagem
        elif(" " not in msg):
            print("Digite alguma mensagem!")
            continue
        # Enviar caso tudo certo

    # Tratar mensagem de ban, não enviar se tiver algo errado (continue)
    if(((msg[0:3] == "ban") and (len(msg) == 3)) or ((msg[0:5] == "ban @") and (len(msg) == 5))):
        print("Digite algum nome para votar o banimento!")
        continue
    
    # Não deixar que vote de novo antes de passar o tempo
    if(msg[0:3] == "ban"):
        if(perf_counter() - tempo_ant <= TEMPO_BAN):
            print("Espere para votar novamente!")
            continue
        else:
            tempo_ant = perf_counter()

    # Enviar mensagem, caso tenha passado pelos tratamentos
    msg_enc = msg.encode()
    clienteSocket.sendto(msg_enc, endereco_servidor)

    # Se for bye, envia msg bye (linha acima) e fecha o cliente
    if(msg == "bye"):
        print("Saindo do chat...")
        break          
    
print("Desconectado!")


    
