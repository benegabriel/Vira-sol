Esta é uma implementação de uma classe para o sensor magnetômetro QMC5883L utilizando MicroPython. Esta classe permite configurar, calibrar e obter leituras precisas de direção e intensidade do campo magnético, podendo ser facilmente integrado a projetos embarcados como robótica, drones e sistemas de navegação.

Esta classe foi implementada com o intuido de utilizar o sensor como bússola, logo, os métodos implementados são aquele que ajudam a este fim, porém novos métodos podem ser adicionados. O ponto principal é que o bom desempenho do sensor para esta função depende totalmente da sua calibração. Logo, a função de calibração implementada deve ser utilizada se o objetivo for medir a direção do campo magnético, e ela foi implementada para o caso 2D. O dados brutos da calibração podem ser obtidos pelo método obter_dados_calibracao() para verificar a qualidade da calibração. Idealmente, ao rotacionar o sensor, imenso em um campo constante, em 360 graus os valores do campo magnético medido deveriam formar um círculo centrado na origem. Porém, distorções de escala e offsets podem aparecer e são corrigidas com a calibração. Logo, se os pontos obtidos formarem uma elípse eles podem ser tratados pela calibração e em seguida o sensor pode ser utilizado nas mesmas condições que foi calibrado para obter o ângulo do campo magnético (ângulo do Norte). Caso os pontos de calibração formem outro padrão, é possível que a medida do sensor esteja influenciada por circuitos eletrônicos próximos ou pela presenção de materiais com elevado permissividade magnética.

Recursos:
Configuração automática do sensor no modo contínuo.
Leitura dos valores do campo magnético nos eixos x, y, z
Calibração de offsets e fatores de escala com persistência em arquivo JSON.
Cálculo de direção (heading) corrigido.
Modos de operação: standby (economia de energia) e contínuo (ativo).
Configuração da sensibilidade: 2G (maior sensibilidade) ou 8G (menor sensibilidade).

Como usar:

1. Configuração Inicial
from machine import SoftI2C, Pin  
from qmc5883l import QMC5883L  

# Configuração do barramento I2C  
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  

# Inicialização do sensor  
compass = QMC5883L(i2c)

2. Leitura do Magnetômetro
# Leitura direta dos valores dos eixos X, Y, Z  
x, y, z = compass.read_magnetometer()  
print(f"X: {x}, Y: {y}, Z: {z}")

Obs.: esta é a medida dos valores brutos obtidos pelo sensor, sem a aplicação da calibração, que foi implementada apenas para o caso 2D (x, y) e aplicada apenas para o cálculo do ângulo.

3. Calibração
# Calibração do sensor  
compass.calibrate_sensor(samples=250)  
# O sensor deve ser girado em todas as direções horizontais durante a calibração.  

4. Leitura de Heading (Azimute)
# Calcula a direção corrigida pela calibração em graus (em relação ao eixo x do sensor)
heading = compass.read_heading()  
print(f"Heading: {heading:.2f}°")

5. Modos de Operação
# Alternar entre modos de operação  
compass.set_standby()  # Standby (economia de energia)  
compass.set_active()   # Ativo (modo contínuo) 

6. Ajuste de Sensibilidade
# Configurar sensibilidade do sensor  
compass.set_sensibility("2G")  # Maior sensibilidade  
compass.set_sensibility("8G")  # Menor sensibilidade  

O sensor permite outras configurações, como a frequência de amostragem da saída para o modo contínuo e alterar o OSR para obter maior precisão ou menor consumo de energia. A implementação dos métodos para permitir estas configurações pode ser feita de forma análoga ao método que configura a sensibilidade, utilizando uma máscara para o registrador de configuração do sensor e seguindo o seu datasheet.

Datasheet QMC5883L: https://github.com/e-Gizmo/QMC5883L-GY-271-Compass-module/blob/master/QMC5883L%20Datasheet%201.0%20.pdf