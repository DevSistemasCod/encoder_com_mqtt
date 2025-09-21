import network
from umqtt.simple import MQTTClient
from machine import Pin, time_pulse_us
from time import sleep


# ======== CONFIGURAÇÕES ========
REDE_WIFI = "WIFI_IOT_CFP601"
SENHA_WIFI = "iot@senai601"

BROKER_MQTT = "10.110.22.10"
PORTA_MQTT = 1883
TOPICO_MQTT = "fabrica/encoder"
ID_CLIENTE_MQTT = "esp32-contador-encoder"

# Configuração dos pinos do encoder
CLK_PIN = 25
DT_PIN = 26
SW_PIN = 27

POSICAO_ALVO = 10  # Altere para a posição desejada


def conectar_wifi(nome_rede, senha):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("Conectando ao Wi-Fi...")
        wifi.connect(nome_rede, senha)
        while not wifi.isconnected():
            print(".", end="")
            sleep(0.5)
    print("\n Conectado ao Wi-Fi! IP:", wifi.ifconfig()[0])


def conectar_broker_mqtt(id_cliente, endereco_broker):
    cliente = MQTTClient(id_cliente, endereco_broker, port=PORTA_MQTT)
    while True:
        try:
            cliente.connect()
            print("Conectado ao broker MQTT!")
            return cliente
        except Exception as erro:
            print("Erro ao conectar ao MQTT:", erro)
            sleep(2)

def publicar_mensagem_mqtt(cliente, topico, mensagem):
    try:
        cliente.publish(topico, mensagem)
    except Exception as erro:
        print("Erro ao publicar, tentando reconectar...", erro)
        try:
            cliente.connect()
            cliente.publish(topico, mensagem)
            print("Reconectado e publicado com sucesso!")
        except:
            print("Falha ao reconectar ao broker MQTT.")

def main():
    conectar_wifi(REDE_WIFI, SENHA_WIFI)
    cliente = conectar_broker_mqtt(ID_CLIENTE_MQTT, BROKER_MQTT)
    
    #################################
    clk = Pin(CLK_PIN, Pin.IN, Pin.PULL_UP)
    dt = Pin(DT_PIN, Pin.IN, Pin.PULL_UP)
    sw = Pin(SW_PIN, Pin.IN, Pin.PULL_UP)

    posicao = 0
    ###
    contagem = 0;
    estado_alvo_anterior = False
    ###
    clk_ant = clk.value()

    while True:
        clk_atual = clk.value()

        # Detecta mudança no CLK
        if clk_atual != clk_ant:
            # Determina a direção do giro
            if dt.value() != clk_atual:
                posicao += 1
            else:
                posicao -= 1
            print("Posição atual:", posicao)

            # Verifica se atingiu a posição alvo
            #if posicao == POSICAO_ALVO:
            if posicao == POSICAO_ALVO and not estado_alvo_anterior:
                contagem = contagem + 1
                estado_alvo_anterior = True
                print(f"Posição alvo atingida: {contagem}")
                #####
                publicar_mensagem_mqtt(cliente, TOPICO_MQTT, str(contagem))
            #####
            elif posicao != POSICAO_ALVO:
                 estado_alvo_anterior = False
            #####
        clk_ant = clk_atual
        sleep(0.001) # pequeno delay para estabilidade

# Executa a função principal
if __name__ == "__main__":
    main()


