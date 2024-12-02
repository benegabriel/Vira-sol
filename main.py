from machine import Pin, PWM, ADC, I2C, SoftI2C, UART
import time
from ssd1306 import SSD1306_I2C
from micropyGPS import MicropyGPS
import vira_sol as vs
import modulo_bussola as bs
import json
import os

'''
Placa solar: GPIO28
Motor 1: GPIO16
Motor 2: GPIO17
GPS: GPIO8 e GPIO9
Bussola: GPIO18 e GPIO19
'''
###################################### VIRA-SOL ################################################

vira_sol = vs.virasol(Pin(16), Pin(17), Pin(28))

###################################### BOTOES ##################################################

botao_A = Pin(5, Pin.IN, Pin.PULL_UP)
botao_B = Pin(6, Pin.IN, Pin.PULL_UP)
botao_Joystick = Pin(22, Pin.IN, Pin.PULL_UP)

def tratar_botao_A():
    time.sleep(0.5)
    
    # Se foi segurado
    if (not botao_A.value()):
        # Sugerir apagar os arquivos de geracao
        oled.fill(0)
        oled.text("Apagar historico", 0, 0)
        oled.text("de geracao?", 0, 10)
        time.sleep(2)
        oled.show()
        oled.text("Botao A:  Sim", 0, 30)
        oled.text("Botao B:  Nao", 0, 40)
        oled.show()
        time.sleep(0.5)
        while True:
            if (not botao_A.value()):
                if os.path.exists("/dados_geracao.json"):
                    os.remove("/dados_geracao.json")
                    oled.fill(0)
                    oled.text("Removido!", 30, 0)
                    time.sleep(1)
            if (not botao_B.value()):
                break
        # Limpar display
        oled.fill(0)
        oled.show()
        time.sleep(0.5)
    # Se foi clicado
    else:
        global estado_display
        estado_display = (estado_display - 1) % 4


def tratar_botao_B():
    time.sleep(0.5)
    
    # Se foi segurado
    if (not botao_B.value()):
        # Sugerir calibracao da bussola
        oled.fill(0)
        oled.text("Calibrar bussola", 0, 0)
        oled.text("?", 120, 10)
        oled.text("Botao A:  Sim", 0, 30)
        oled.text("Botao B:  Nao", 0, 40)
        oled.show()
        time.sleep(2)
        while True:
            if (not botao_A.value()):
                calibrar_bussola()
                break
            if (not botao_B.value()):
                # Limpar display
                oled.fill(0)
                oled.show()
                time.sleep(0.5)
                break
        
    # Se foi clicado
    else:
        global estado_display
        estado_display = (estado_display + 1) % 4


def tratar_botao_Joystick():
    time.sleep(0.5)
    
    # Se foi segurado
    if (not botao_Joystick.value()):
        global vira_sol
        vira_sol.ajuste_auto()
    # Se foi clicado
    else:
        # Varrer GPS
        data, latidude, longitude = ler_gps()
        data_arredondada = (data[0], data[1], data[2], data[3], int((data[4] // 20) * 20))
        ajustar_posicao_sol(data_arredondada)
        time.sleep(0.5)
        salvar_medida(data)

    

###################################### JOYSTICK ################################################

# Configuração dos eixos analógicos do joystick
vrx = ADC(Pin(27))  # Eixo X
vry = ADC(Pin(26))  # Eixo Y

def ler_joystick():
    # Leitura dos valores analógicos (invertendo as direcoes dos eixos para corrigir
    # a posicao na placa)
    valor_x = -(vrx.read_u16() - 2**15) # Leitura do eixo X
    valor_y = -(vry.read_u16() - 2**15) # Leitura do eixo Y
    
    # Conversao dos valores para uma faixa de 0 a 100
    eixo_x = int((valor_x / 65535) * 100)
    eixo_y = int((valor_y / 65535) * 100)
    
    return eixo_x, eixo_y

###################################### DISPLAY #################################################

# Configuração do barramento I2C (I2C0)
i2c0 = SoftI2C(scl=Pin(15), sda=Pin(14))

# Inicializar o display OLED
oled = SSD1306_I2C(128, 64, i2c0)

estado_display = 0

def show_display(oled, data, latitude, longitude):
    global estado_display
    
    # Dados do virasol
    if estado_display == 0:
        global vira_sol
        vira_sol.atualizar_display()
        
    # Bussola
    elif estado_display == 1:
        exibir_calibracao(segurar=False)
        angulo_norte = (-bussola.read_heading() + 180) % 360		# Medida da bussola corrigida para o referencial da placa
        oled.pixel(125, 1, 1)  
        oled.pixel(126, 1, 1)
        oled.pixel(125, 4, 1)
        oled.pixel(126, 4, 1)
        oled.pixel(127, 2, 1)
        oled.pixel(127, 3, 1)
        oled.pixel(124, 2, 1)
        oled.pixel(124, 3, 1)
        oled.text(f"Norte:    {angulo_norte:5.1f}", 0, 0)
        oled.show()
    
    # GPS
    elif estado_display == 2:
        # Limpar o display
        oled.fill(0)

        # Escrever texto no display
        oled.text("GPS", 0, 0)     # Texto na posição (0, 0)
        oled.text(f"Latitude:  {latitude}", 0, 20)
        oled.text(f"Longitude: {longitude}", 0, 30)
        oled.text(f"Data: {data[2]:02}/{data[1]:02}/{data[0]}", 0, 40)
        oled.text(f"Hora:      {data[3]:02}:{data[4]:02}", 0, 50)

        # Atualizar o display para mostrar o texto
        oled.show()
    
    # Dados geracao
    elif estado_display == 3:
        try:
            # Tenta abrir e carregar o conteúdo existente do arquivo JSON
            with open("/dados_geracao.json", "r") as arquivo:
                dados = json.load(arquivo)  # Carrega o conteúdo existente
                geracao = [0 for i in range(24)]
                amostras = [0 for i in range(24)]
                for chave in dados.keys():
                    hora = int(chave.split()[3])
                    geracao[hora] += dados[chave]
                    amostras[hora] += 1
                for hora in range(24):
                    if amostras[hora] != 0:
                        geracao[hora] = geracao[hora] / amostras[hora]
                exibir_grafico_barras(oled, geracao)
        
        except:
            # Caso o arquivo não exista, cria um dicionário vazio
            oled.fill(0)
            oled.text(f"Erro: sem dados", 0, 20)
            oled.text(f"de geracao", 0, 30)
            oled.show()            


###################################### BUSSOLA #################################################

i2c1 = SoftI2C(sda=Pin(18), scl=Pin(19))
bussola = bs.QMC5883L(i2c1)

def calibrar_bussola():
    oled.fill(0)
    oled.text("Calibrando...", 0, 0)
    oled.text(f"Gire o sensor em", 0, 20)
    oled.text(f"todas as direcoes", 0, 30)
    oled.text(f"para calibrar", 0, 40)  
    oled.show()
    bussola.calibrate_sensor()
    exibir_calibracao(segurar=True)
    
    
def exibir_calibracao(segurar=True):
    x_bruto, y_bruto = bussola.obter_dados_calibracao()
    
    # Limpa o display
    oled.fill(0)
    
    if segurar:
        oled.text("--- Aperte A ---", 0, 0)

    # Dimensões do OLED
    WIDTH, HEIGHT = 128, 54

    # Encontra os limites dos dados
    min_x, max_x = min(x_bruto), max(x_bruto)
    min_y, max_y = min(y_bruto), max(y_bruto)

    # Calcula os fatores de escala
    range_x = max_x - min_x
    range_y = max_y - min_y

    scale_x = WIDTH / range_x if range_x != 0 else 1
    scale_y = HEIGHT / range_y if range_y != 0 else 1

    # Usa o menor fator de escala para manter a proporção
    scale = min(scale_x, scale_y)

    # Offset para centralizar o gráfico
    offset_x = (WIDTH - (range_x * scale)) / 2
    offset_y = (HEIGHT - (range_y * scale)) / 2

    # Ajusta e desenha os pontos no OLED
    for x, y in zip(x_bruto, y_bruto):
        # Ajusta os pontos ao tamanho do display
        screen_x = int((x - min_x) * scale + offset_x)
        screen_y = int((y - min_y) * scale + offset_y)

        # Inverte o eixo Y para o OLED (origem no canto superior esquerdo)
        screen_y = HEIGHT - screen_y
        
        # Desce o ponto 10 pixels
        screen_y += 10
        
        # Desenha o ponto
        oled.pixel(screen_x, screen_y, 1)

    if not segurar:
        return
    
    # Atualiza o display
    oled.show()
    
    # Espera um tempo mínimo de exibicao e trava o programa ate sair da exibicao
    time.sleep(0.5)
    while True:
        if (not botao_A.value()):
            oled.fill(0)
            oled.show()
            # Impede dupla identificação do clique do botão pela varredura do loop principal
            time.sleep(0.5)
            return

###################################### GPS #####################################################

gps_module = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
gps = MicropyGPS()


def convert_coordinates(sections):
    if sections[0] == 0:  # sections[0] contains the degrees
        return None

    # sections[1] contains the minutes
    data = sections[0] + (sections[1] / 60.0)

    # sections[2] contains 'E', 'W', 'N', 'S'
    if sections[2] == 'S':
        data = -data
    if sections[2] == 'W':
        data = -data

    data = '{0:.6f}'.format(data)  # 6 decimal places
    return str(data)


def ler_gps(fuso_horario=-3):
    while True:
        length = gps_module.any()

        if length > 0:
            data = gps_module.read(length)
            for byte in data:
                message = gps.update(chr(byte))

        latitude = convert_coordinates(gps.latitude)
        longitude = convert_coordinates(gps.longitude)

        if latitude is None or longitude is None or (not sum(gps.date)) or (not sum(gps.timestamp)):
            print("GPS sem sinal")
            oled.fill(0)
            oled.text(f"GPS sem sinal", 0, 30)
            oled.show()
            time.sleep(0.5)
        else:            
            break
    
    secs = time.mktime((2000 + gps.date[2], gps.date[1], gps.date[0], gps.timestamp[0], gps.timestamp[1], int(gps.timestamp[2]), None, None))
    secs_com_fuso = secs + fuso_horario * 3600
    data_com_fuso = time.localtime(secs_com_fuso)
    return data_com_fuso[:-3], latitude, longitude

###################################### FUNCOES #################################################

def ajustar_posicao_sol(data):
    
    angulo_norte = (-bussola.read_heading() + 180) % 360
    
    try:
        # Carregar a posicao do sol
        with open("/dados_sol.json", "r") as json_file:
            dados_sol = json.load(json_file)
            azimute = dados_sol[" ".join(map(str, data))]["azimute"]
            altitude = dados_sol[" ".join(map(str, data))]["altitude"]
            
            azimute_corrigido = (azimute + 180) % 360			# Translada para que o norte fique na posicao 0
            azimute_corrigido = (-azimute_corrigido) % 360		# Inverte o sentido para que N -> O -> S -> L seja o sentido positivo
            azimute_corrigido = (azimute_corrigido + angulo_norte) % 360	# Corrige para o refencial da placa, e não o do norte
            azimute = azimute_corrigido
    except:
        if data[3] < 6:
            altitude = 0
            azimute = 270            
        elif data[3] < 12:
            altitude = 90 * (((data[3] - 6) * 60 + data[4]) / 360)
            azimute = 270        
        elif data[3] < 18:
            altitude = 90 - 90 * (((data[3] - 12) * 60 + data[4]) / 360)
            azimute = 90        
        else:
            altitude = 0
            azimute = 90
        azimute = (azimute + angulo_norte) % 360	# Corrige para o refencial da placa, e não o do norte
    
    # Adapter posicoes que o virasol nao alcanca
    if azimute > 180:
        azimute = (azimute - 180) % 360
        altitude = 90 + (90 - altitude)
    
    # Mover o vira sol
    global vira_sol
    vira_sol.movimenta_base(azimute)
    vira_sol.movimenta_topo(altitude)            
    vira_sol.atualizar_display()


def salvar_medida(data):
    try:
        # Tenta abrir e carregar o conteúdo existente do arquivo JSON
        with open("/dados_geracao.json", "r") as arquivo:
            dados = json.load(arquivo)  # Carrega o conteúdo existente
    except:
        # Caso o arquivo não exista, cria um dicionário vazio
        dados = {}

    # Atualiza os dados com a nova chave e valor
    global vira_sol
    tensao = vira_sol.obter_tensao()
    dados[" ".join(map(str, data))] = tensao

    # Escreve os dados atualizados de volta no arquivo JSON
    with open("/dados_geracao.json", "w") as arquivo:
        json.dump(dados, arquivo)



def exibir_grafico_barras(oled, geracao):
    """
    Exibe um gráfico de barras no display OLED representando a geração solar em 24 horas.
    
    :param oled: Objeto de display OLED (como SSD1306).
    :param geracao: Lista de 24 valores de geração solar (um por hora).
    """
    largura_display = 128  # Ajuste conforme o seu display
    altura_display = 44    # Ajuste conforme o seu display
    num_barras = len(geracao)  # Número de barras (24 horas)
    
    largura_barra = largura_display // num_barras  # Largura de cada barra
    max_geracao = 3.3  # Valor máximo para escalar
    
    # Limpar o display antes de desenhar
    oled.fill(0)
    
    for i, valor in enumerate(geracao):
        # Escalar a altura da barra para caber no display
        altura_barra = int((valor / max_geracao) * (altura_display - 1))
        x = i * largura_barra
        y = altura_display - altura_barra  # Base da barra no eixo Y
        
        # Desenhar a barra (preenchida)
        oled.fill_rect(x, y, largura_barra, altura_barra, 1)
    
    oled.text("0  06  12 18 23", 0, 50)
    # Atualizar o display para mostrar o gráfico
    oled.show()


###################################### SETUP ###################################################

# Verificar sinal do GPS
ler_gps(-3)

# Sugerir calibracao da bussola
oled.fill(0)
oled.text("Calibrar bussola", 0, 0)
oled.text("?", 120, 10)
oled.text("Botao A:  Sim", 0, 30)
oled.text("Botao B:  Nao", 0, 40)
oled.show()

while True:
    if (not botao_A.value()):
        time.sleep(0.5)
        calibrar_bussola()
        break
    if (not botao_B.value()):
        time.sleep(0.5)
        break

# Limpar display
oled.fill(0)
oled.show()
    

###################################### LOOP PRINCIPAL ##########################################

ultima_data_processada = 0
geracao_atual = [time.time(), vira_sol.obter_tensao()]

while (True):
    # Varrer joystick e mover placa
    joy_x, joy_y = ler_joystick()
    
    if joy_x > 30:
        vira_sol.movimenta_base(vira_sol.obter_ang_base() + 5)
    elif joy_x < -30:
        vira_sol.movimenta_base(vira_sol.obter_ang_base() - 5)
        
    if joy_y > 30:
        vira_sol.movimenta_topo(vira_sol.obter_ang_topo() + 5)
    elif joy_y < -30:
        vira_sol.movimenta_topo(vira_sol.obter_ang_topo() - 5)
    
    # Varrer botoes
    if (not botao_A.value()):
        tratar_botao_A()
        
    if (not botao_B.value()):
        tratar_botao_B()
        
    if (not botao_Joystick.value()):
        tratar_botao_Joystick()
    
    # Varrer GPS
    data_atual, latidude, longitude = ler_gps()
    
    if ((data_atual[4] % 20) == 0) and (data_atual != ultima_data_processada):
        ajustar_posicao_sol(data_atual)
        time.sleep(0.5)
        salvar_medida(data_atual)
        ultima_data_processada = data_atual
        
    # Verificar queda abrupta de geracao (tensao)
    tensao = vira_sol.obter_tensao()
    instante = time.time()
    if (geracao_atual[1] - tensao) > 1:
        vira_sol.ajuste_auto()
        geracao_atual = [time.time(), vira_sol.obter_tensao()]
    
    elif (instante - geracao_atual[0] >= 60):
        geracao_atual = [instante, tensao]
        
    elif (tensao > geracao_atual[1]):
        geracao_atual = [instante, tensao]   
        
    
    # Atualizar display
    show_display(oled, data_atual, latidude, longitude)


