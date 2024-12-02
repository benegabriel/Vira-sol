from machine import Pin, SoftI2C
import time
import math
import json


class QMC5883L:
    
    QMC5883L_ADDR = 0x0D
    CONTROL_REG = 0x09
    SET_RESET_REG = 0x0B
    DATA_X_LSB = 0x00
    STATUS_REG = 0x06    
    calibration_file = "/calibracao_bussola.json"
    
    
    def __init__(self, i2c, address=QMC5883L_ADDR):
        self.i2c = i2c
        self.address = address
        
        try:
            # Carregar as variáveis de calibracao do arquivo JSON
            with open(self.calibration_file, "r") as json_file:
                data = json.load(json_file)
                self.x_offset = data["x_offset"]
                self.y_offset = data["y_offset"]
                self.x_fator_escala = data["x_fator_escala"]
                self.y_fator_escala = data["y_fator_escala"]
        except:  # open failed
            self.x_offset = 0
            self.y_offset = 0
            self.x_fator_escala = 1
            self.y_fator_escala = 1
            print("Bússola sem calibração")

        self.config_status = b'\x11' # 512 OSR, 8G, 10 Hz de amostragem, Modo contínuo
        self.setup()
    
    
    def setup(self):
        # Configura o período de Set/Reset
        self.i2c.writeto_mem(self.address, self.SET_RESET_REG, b'\x01')
        # Configura o status do módulo
        self.i2c.writeto_mem(self.address, self.CONTROL_REG, self.config_status)
    
    
    def set_standby(self):
        """
        Coloca o QMC5883L em modo standby para economizar energia.
        """
        configuracao = self.config_status[0]
        configuracao = configuracao & ~(1 << 0)
        configuracao = configuracao & ~(1 << 1)
        self.config_status = bytes([configuracao])
        
        self.i2c.writeto_mem(self.address, self.CONTROL_REG, self.config_status)  # MODO = 00 (standby)
        print("QMC5883L em modo standby.")


    def set_active(self):
        """
        Coloca o QMC5883L em modo contínuo (ativo).
        """
        configuracao = self.config_status[0]
        configuracao = configuracao | (1 << 0)
        configuracao = configuracao & ~(1 << 1)
        self.config_status = bytes([configuracao])
        
        self.i2c.writeto_mem(self.address, self.CONTROL_REG, self.config_status)  # MODO = 01
        print("QMC5883L em modo ativo (contínuo).")
    
    
    def set_sensibility(self, sensibilidade):
        # Full Scale = 2G (maoir sensibilidade)
        if(sensibilidade == "2G"):#00
            configuracao = self.config_status[0]
            configuracao = configuracao & ~(1 << 4)
            configuracao = configuracao & ~(1 << 5)
            self.config_status = bytes([configuracao])
            
            self.i2c.writeto_mem(self.address, self.CONTROL_REG, self.config_status)
            print("Full Scale = 2G (maoir sensibilidade)")
            
        # Full Scale = 8G (menor sensibilidade)    
        elif(sensibilidade == "8G"):	#01
            configuracao = self.config_status[0]
            configuracao = configuracao | (1 << 4)
            configuracao = configuracao & ~(1 << 5)
            self.config_status = bytes([configuracao])
            
            self.i2c.writeto_mem(self.address, self.CONTROL_REG, self.config_status)
            print("Full Scale = 8G (menor sensibilidade)")
            
        else:
            print("Valor de sensibilidade inválido, use '2G' ou '8G'")
        
    
    def read_magnetometer(self):
        data = self.i2c.readfrom_mem(self.address, self.DATA_X_LSB, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]

        # Ajuste para valores negativos
        if x >= 0x8000:
            x = -(65536 - x)
        if y >= 0x8000:
            y = -(65536 - y)
        if z >= 0x8000:
            z = -(65536 - z)
            
        return x, y, z
    
    
    def calibrate_sensor(self, samples=250):
        x_vals = []
        y_vals = []

        print("Gire o sensor em todas as direções horizontais para calibrar...")
        
        # Descarta a primeira leitura (pode vir de uma conficuração anterior)
        self.read_magnetometer()
        time.sleep(0.2)
        
        for i in range(samples):
            x, y, _ = self.read_magnetometer()  # Leia apenas x e y para calibração
            x_vals.append(x)
            y_vals.append(y)
            time.sleep(0.1)  # Aguarde um pouco entre as leituras
        
        # Calcula os extremos da elipse
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)
        
        # Calcula os offsets
        x_offset = (x_max + x_min) / 2
        y_offset = (y_max + y_min) / 2
        
        # Retira o offset dos extermos da elipse
        x_min -= x_offset
        x_max -= x_offset
        y_min -= y_offset
        y_max -= y_offset
        
        # Calcula o fator de escala dos eixos, para trasformar a elipse em uma esfera
        media_maximos = (x_max + y_max) / 2
        x_fator_escala = media_maximos / x_max
        y_fator_escala = media_maximos / y_max
        
        # Atualiza ods parâmetros de calibracao
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_fator_escala = x_fator_escala
        self.y_fator_escala = y_fator_escala
        
        # Estruturar as variáveis em um dicionário
        data = {
            "x": x_vals,
            "y": y_vals,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "x_fator_escala": x_fator_escala,
            "y_fator_escala": y_fator_escala
        }

        # Salvar as variáveis no arquivo JSON
        with open(self.calibration_file, "w") as json_file:
            json.dump(data, json_file)        
        print("Calibração Completa:")
        print(f"Offset X: {x_offset}, Offset Y: {y_offset}")
        print(f"Fator escala X: {x_fator_escala}, Fator escala Y: {y_fator_escala}")


    def read_heading(self):
        x, y, _ = self.read_magnetometer()
        x_corrigido = (x - self.x_offset) * self.x_fator_escala
        y_corrigido = (y - self.y_offset) * self.y_fator_escala
        
        heading = math.atan2(y_corrigido, x_corrigido) * (180 / math.pi)
        if heading < 0:
            heading += 360
        return heading
    
    
    def obter_dados_calibracao(self):
        with open(self.calibration_file, "r") as json_file:
            data = json.load(json_file)
            x_bruto = data["x"]
            y_bruto = data["y"]
        return x_bruto, y_bruto



