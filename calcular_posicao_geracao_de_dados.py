from suncalc import get_position, get_times
from datetime import datetime, timedelta, timezone
import math
import json


# Data dede inicio
ano = 2024
mes = 11
dia = 27
hora = 0
minuto = 0
fuso_horario_menos_3 = timezone(timedelta(hours=-3))
date_inicial = datetime(ano, mes, dia, hora, minuto, tzinfo=fuso_horario_menos_3)

# Unicamp (aproximadamente)
lon = -47.073898
lat = -22.816744

sun_positions = {}
sun_positions["timezone"] = str(date_inicial.tzinfo)
sun_positions["longitude"] = lon
sun_positions["latitude"] = lat

total_dias = 90
for i in range(3*24*total_dias):
    date = date_inicial + timedelta(minutes=20*i)
    tupla_data = (date.year, date.month, date.day, date.hour, date.minute)
    pos = get_position(date, lon, lat)

    if (math.degrees(pos['altitude']) > 0):
        azimuth = math.degrees(pos['azimuth'])
        altitude = math.degrees(pos['altitude'])
        azimuth = math.trunc(azimuth * 10) / 10
        altitude = math.trunc(altitude * 10) / 10

        sun_positions[' '.join(map(str, tupla_data))] = {}
        sun_positions[' '.join(map(str, tupla_data))]["azimute"] = azimuth
        sun_positions[' '.join(map(str, tupla_data))]["altitude"] = altitude
    #print(i)

# Nome do arquivo para salvar
nome_arquivo = "dados_sol.json"

# Abrir o arquivo em modo de escrita e salvar o dicionário
with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
    # indent=4 gera um arquivo mais legível, porém maior, indent=None gera o menor arquivo possível
    indent = 4
    json.dump(sun_positions, arquivo, ensure_ascii=False, indent=indent)