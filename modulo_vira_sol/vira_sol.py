from machine import Pin, PWM, ADC, SoftI2C
import time
from ssd1306 import SSD1306_I2C

class virasol:

    min_ang_base = 0
    max_ang_base = 180
    min_duty_base = 0.0275
    max_duty_base = 0.126

    min_ang_topo = 40
    max_ang_topo = 140
    min_duty_topo = 0.02
    max_duty_topo = 0.09
    
    def __init__(self, GPIO_base, GPIO_topo, GPIO_painel, GPIO_oled_scl=Pin(15), GPIO_oled_sda=Pin(14)):
        self.GPIO_base = GPIO_base
        self.PWM_base = PWM(self.GPIO_base)
        self.PWM_base.freq(50)
        
        self.GPIO_topo = GPIO_topo
        self.PWM_topo = PWM(self.GPIO_topo)
        self.PWM_topo.freq(50)
        
        self.GPIO_painel = GPIO_painel
        self.ADC_painel = ADC(self.GPIO_painel)
        
        self.i2c = SoftI2C(scl=GPIO_oled_scl, sda=GPIO_oled_sda)
        self.oled = SSD1306_I2C(128, 64, self.i2c)
        
        self.__ang_base = (self.min_ang_base + self.max_ang_base) // 2
        self.__ang_topo = (self.min_ang_topo + self.max_ang_topo) // 2
        self.ultima_tensao = 0
        
        self.movimenta_base(self.__ang_base)
        self.movimenta_topo(self.__ang_topo)
        self.ultima_tensao = self.obter_tensao()
        
        
    def movimenta_base(self, angulo):       
        if angulo < self.min_ang_base:
            angulo = self.min_ang_base
        elif angulo > self.max_ang_base:
            angulo = self.max_ang_base
            
        self.__ang_base = angulo
        
        duty = ((angulo - self.min_ang_base) / (self.max_ang_base - self.min_ang_base)) * (self.max_duty_base - self.min_duty_base) + self.min_duty_base
        self.PWM_base.duty_u16(int(65535 * duty))
        
        
    def obter_ang_base(self):
        return self.__ang_base


    def movimenta_topo(self, angulo):        
        if angulo < self.min_ang_topo:
            angulo = self.min_ang_topo
        elif angulo > self.max_ang_topo:
            angulo = self.max_ang_topo
            
        self.__ang_topo = angulo
            
        duty = ((angulo - self.min_ang_topo) / (self.max_ang_topo - self.min_ang_topo)) * (self.max_duty_topo - self.min_duty_topo) + self.min_duty_topo
        self.PWM_topo.duty_u16(int(65535 * duty))
        
        
    def obter_ang_topo(self):
        return self.__ang_topo
    
    
    def obter_tensao(self, amostras=100, delay_us=20):
        # Lê o valor analógico (entre 0 e 4095)
        valor_analogico = 0
        for i in range(amostras):
            valor_analogico += self.ADC_painel.read_u16() / amostras
            time.sleep_us(delay_us)
        # Converte o valor lido para a faixa de 0 a 3.3V com duas casas decimais
        tensao = round(valor_analogico * (3.3 / 65535) * 100) / 100
        self.ultima_tensao = tensao
        
        return tensao
    
    
    def atualizar_display(self, atualizar_tensao=True):
        if (atualizar_tensao):
            self.obter_tensao()
        
        # Limpar o display
        self.oled.fill(0)

        # Escrever texto no display
        self.oled.text("Placa Solar", 0, 0)     # Texto na posição (0, 0)
        self.oled.text(f"Ang. Base:  {int(self.__ang_base):3d}", 0, 20)
        self.oled.text(f"Ang. Topo:  {int(self.__ang_topo):3d}", 0, 30)
        self.oled.text(f"Tensao:  {self.ultima_tensao:.2f} V", 0, 50)  

        # Atualizar o display para mostrar o texto
        self.oled.show()
    
    
    def ajuste_auto(self, passo_base=15, passo_topo=15, tempo_espera=1):
        
        self.movimenta_base((self.min_ang_base + self.max_ang_base) // 2)
        self.movimenta_topo((self.min_ang_topo + self.max_ang_topo) // 2)
        time.sleep(tempo_espera)
        
        tensao_antes = -9999
        tensao_atual = self.obter_tensao()
        self.atualizar_display(atualizar_tensao=False)
        
        while tensao_antes < tensao_atual:
            tensao_antes = tensao_atual
            
            # ajusta base
            self.movimenta_base(self.__ang_base + passo_base)
            time.sleep(tempo_espera)
            tensao_mais =  self.obter_tensao()
            self.atualizar_display(atualizar_tensao=False)
            
            if tensao_mais > tensao_atual:
                tensao_atual = tensao_mais
            else:
                self.movimenta_base(self.__ang_base - 2*passo_base)
                time.sleep(tempo_espera)            
                tensao_menos = self.obter_tensao()
                self.atualizar_display(atualizar_tensao=False)
                
                if tensao_menos > tensao_atual:
                    tensao_atual = tensao_menos
                else:
                    self.movimenta_base(self.__ang_base + passo_base)
                    time.sleep(tempo_espera)
                    self.atualizar_display(atualizar_tensao=True)
                    
            # ajusta topo
            self.movimenta_topo(self.__ang_topo + passo_topo)
            time.sleep(tempo_espera)        
            tensao_mais = self.obter_tensao()
            self.atualizar_display(atualizar_tensao=False)
            
            if tensao_mais > tensao_atual:
                tensao_atual = tensao_mais
            else:
                self.movimenta_topo(self.__ang_topo - 2*passo_topo)
                time.sleep(tempo_espera)            
                tensao_menos = self.obter_tensao()
                self.atualizar_display(atualizar_tensao=False)
                
                if tensao_menos > tensao_atual:
                    tensao_atual = tensao_menos
                else:
                    self.movimenta_topo(self.__ang_topo + passo_topo)
                    time.sleep(tempo_espera)
                    self.atualizar_display(atualizar_tensao=True)
    


