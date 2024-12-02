O ViraSol é uma implementação em MicroPython que controla o movimento de um painel solar em dois eixos, podendo ajustar automaticamente sua orientação para maximizar a captação de energia solar. Ele utiliza servomotores para movimentar a base e o topo do painel, o próprio painel para medir a tensão gerada e um display OLED para exibir os dados medidos. O módulo também foi projetado para ser utilizado junto da BitDogLab, logo a pinagem padrão do display oled na BitDogLab já foi inserida como valor padrão para a inicialização da classe, podendo ser alterado, e o método que controla o display foi implementado para um display de 128x64 pixels.

Recursos
Ajuste dos ângulos da base e do topo do painel solar.
Algoritmo de busca para maximizar a tensão gerada pelo painel solar.
Exibe no display OLED os ângulos e a tensão gerada pelo painel.

Requisitos de Hardware
Microcontrolador compatível com MicroPython (ex.: Raspberry Pi Pico, incluso na BitDogLab).
2 servomotores (para base e topo do painel).
Painel solar.
Display OLED com protocolo I2C. (incluso na BitDogLab).
Base para o acoplamento dos dois motores, permitindo o movimento em dois sentidos de rotação, e do painel solar o seu topo.

Como Usar

1. Configuração Inicial
from machine import Pin, PWM, ADC  
from virasol import virasol  

# Configuração dos pinos  
servo_base = Pin(16)  
servo_topo = Pin(17)  
sensor_adc = Pin(36)  
scl_oled   = Pin(15)
sda_oled   = Pin(14)

# Inicialização do ViraSol  
painel = virasol(servo_base, servo_topo, sensor_adc, GPIO_oled_scl=scl_oled, GPIO_oled_sda=sda_oled)

2. Movimentar Manualmente
# Ajustar manualmente os ângulos da base e do topo  
painel.movimenta_base(90)  # Ajusta a base para 90°  
painel.movimenta_topo(120)  # Ajusta o topo para 120°  

# Obter os ângulos atuais  
print(f"Ângulo Base: {painel.obter_ang_base()}°")  
print(f"Ângulo Topo: {painel.obter_ang_topo()}°") 

Obs: A relação entre a posição do servo e o ângulo inserido foi definida ao configurar manualmente os valores de ângulo mínimo e máximo, juntos dos respectivos valores mínimo e máximo de dutycicle dos servo-motores, para a base e o topo, que são parâmetros internos da classe. Em outras montagens, pode ser necessário a alteração destes valores. A criação de um método de calibração manual, permitindo esta calibração fora do código do módulo pode ser interessante. Inverter os valores dos parâmetros de ângulo mínimo e máximo altera o sentido de rotação.
Os métodos obter_ang_base() e obter_ang_topo() podem ser utilizados para obter a posição atual do painel, permitindo em seguida uma movimentação que apenas incremente uma das posições.

Medir Tensão
# Ler a tensão gerada pelo painel solar  
tensao = painel.obter_tensao()  
print(f"Tensão Gerada: {tensao:.2f} V") 

Obs.: Esta função implementa um filtro de média simples para aumentar a precisão e os parâmetros, com seus respectivos valores padrão, amostras=100 e delay_us=20 podem ser alterados para definir o número e o intervalo entre as amostras.

Atualizar Display OLED
# Atualiza as informações exibidas no display OLED  
painel.atualizar_display() 

Otimização Automática
# Iniciar o ajuste automático para maximizar a tensão gerada  
painel.ajuste_auto(passo_base=10, passo_topo=10, tempo_espera=1)

Obs.: Este método busca de forma automática a posição ideal da placa, utilizando sua própria medida de tensão como guia para a otimização. O algorítimo utiliza uma adaptação simples do método de gradiente ascendente, movimentando a placa para pocições adjacentes à inicial e sempre selecionando a que proporcionou um aumento na tensão gerada, até que esta para de crescer. O método parte do ângulo médio da base e do topo, para evitar logo de início as regiões de máxima escursão, onde o algorpitimo é menos eficiente.