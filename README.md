Sistema de Rastreamento Solar Automatizado

Este projeto implementa um sistema automatizado de rastreamento solar que utiliza microcontrolador, GPS e bússola digital para ajustar um painel solar na direção ideal do sol. Ele também registra dados de geração (tensão gerada, e não potência) e exibe informações relevantes em um display OLED e permite interações manuais e automáticas.

Componentes Utilizados
- BitDogLab, que inclui:
    - Microcontrolador: Raspberry Pi Pico ou similar.
    - Display OLED: SSD1306 conectado via I2C.
    - Botões: Para interação manual.
    - Joystick analógico: Para ajustes manuais no painel solar.
- GPS: Para determinar a localização e tempo.
- Bússola digital: Sensor QMC5883L para medir o norte magnético.
- Motores: Controlam a posição do painel solar.
- Placa solar: Mede a tensão gerada.
- Resistor e capacitor para implementação de um filtro passa baixas para filtrar o ruído do painel.

Pinagem
Placa solar: GPIO28 (ADC para a medida de tensão)
Motor da base: GPIO16
Motor do topo: GPIO17
GPS: GPIO8 e GPIO9 (TX e RX)
Bussola: GPIO18 e GPIO19 (SDA e SLC)

Funcionalidades
- Ajuste automático do painel solar: Baseado na posição estimada do sol realizada a cada 20 minutos, calculada usando dados de GPS e bússola junto de um modelo simples para a posição do sol ou de um banco de dados com a posição precisa utilizando um modelo complexo executado a priori (fora do sistema embarcado).
- Exibição em display OLED, alternando através dos botões A e B da BitDogLab:
    - Posição atual da placa e tensão sendo gerada.
    - Direção do norte magnético e pontos da última obtidos na última calibração da bússola para validação da calibração.
    - Dados da posição, data e horário do GPS.
    - Gráficos de barras com a média de geração de energia em cada hora ao longo do dia.
- Calibração da bússola: Facilmente acessível ao manter pressionado o botão B da BitDogLab.
- Registro de dados: Salva dados de geração de energia em um arquivo JSON para análise posterior. O registro atual pode ser excluido ao manter pressionado o botão A da BitDogLab e confirmar a ação em seguida.
- Modo manual: Ajuste da posição do painel via joystick.
- Sistema de recuperação de geração: Detecta quedas abruptas de tensão e tenta recuperar a posição ideal automaticamente através da rotina de ajuste do módulo do vira_sol, utilizando a informação de tensão gerada, e não de posição do sol.

Estrutura de Código
Principais Arquivos
    - main.py: Código principal que gerencia a lógica do sistema.
    - vira_sol.py: Classe para controle do painel solar.
    - modulo_bussola.py: Classe para interface com o sensor de bússola.
    - micropyGPS.py: Biblioteca para controle do módulo GPS, utilizada neste implementação para controlar e intrepertar o tráfego de informação pelo interface serial onde o GPS está conectado.
    - dados_geracao.json: Arquivo gerado dinamicamente para armazenar dados de geração de energia.
    - calibracao_bussola.json: Arquivo gerenciado pelo módulo de controle da bússola para armazenar e utilizar os dados da última calibração realizada.
    - dados_sol.json: Arquivo gerado a priori contendo as posições precisas do sol (azimute e altitude) para a região e data onde o projeto será executado. Caso não exista ou esteja vazio, um modelo simples e menos preciso será utilizado como alternativa. Neste arquivo, a data e horário no formato de uma srting "AAAA MM DD (H)H MM" (a hora pode ter um ou dois dígitos) é uma chave de um segundo dicionário contendo o azimute e a altitude para aquele instante, o azimute está referenciado como 90° oeste, 0° sul, -90° leste e -180° norte. O código converte este ângulo para o referencial utilizado pela bússola e pela placa, onde o eixo x, fisicamente interpretado como a direção para baixo da placa representa o 0°, e o sentido positivo é o anti-horário. O código também adiciona o desvio do norte magnético em relação a placa, medido pela bússola, para obter o azimute em relação a placa solar.

Fluxo do Programa
1. Inicialização:
    - Configuração dos sensores (bússola e tensão), GPS (verificação de disponibilidade de sinal), display, botões, joystick, painel (motores e placa solar).
    - Sugestão de calibração inicial da bússola.
2. Loop Principal:
    - Monitoramento de botões, joystick, sensores, GPS e temporização.
    - Aplicação das rotinas adequadas indentificadas pela varredura.
    - Ajustes automáticos da posição do painel solar.
    - Registro periódico dos dados de geração de energia.
    - Atualização do display

Operação
1. Início:
    - Conecte o hardware conforme especificado.
    - Inicie o sistema e siga as instruções no display.
2. Botões:
    - Botão A: Alterna entre telas no display ou exclui o histórico de geração ao ser pressionado por mais tempo.
    - Botão B: Alterna entre telas no display ou inicia a calibração da bússola ao ser pressionado por mais tempo.
    - Joystick: Realiza um ajuste da placa baseado no modelo de posição do sol e nas informações do GPS ou realiza um ajuste do painel baseado no algoritmo de gradiente ascendente guiado pela tensão gerada ao ser pressionado por mais tempo.
3. Joystick:
    - Movimente o joystick para mover a base ou o topo do painel em incrementos de 5 em 5 graus.
4. Modo Automático:
    - O sistema ajustará o painel automaticamente com base na posição estimada do sol e nos dados do GPS a cada 20 minutos e salvará os dados de geração neste mesmo instante.
    - O sistema indentificará uma variação abrupta de tensão (maior que 1 V em menos de 1 minuto) e buscará a melhor posição a partir do algoritmo de gradiente, tentando contornar momentos de obstrução da luz do sol, onde o modelo de posicionamento baseado na posição do sol não seja o mais eficiente.
5. Monitoramento:
    - Acompanhe os dados exibidos no display OLED.
    - Exporte o arquivo "dados_geracao.json" para melhor interpretação do histórico	de geração.
