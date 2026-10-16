import requests
from datetime import datetime
from functools import lru_cache

OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "PrevisaoTempoEducacional/1.0 (app meteorologica)"}

DESCRICOES = {
    0: "Céu limpo", 1: "Predominantemente limpo", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Nevoeiro", 48: "Nevoeiro com geada",
    51: "Garoa fraca", 53: "Garoa moderada", 55: "Garoa intensa",
    56: "Garoa congelante fraca", 57: "Garoa congelante intensa",
    61: "Chuva fraca", 63: "Chuva moderada", 65: "Chuva forte",
    66: "Chuva congelante fraca", 67: "Chuva congelante forte",
    71: "Neve fraca", 73: "Neve moderada", 75: "Neve forte",
    77: "Grãos de neve", 80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas", 82: "Pancadas de chuva fortes",
    85: "Pancadas de neve fracas", 86: "Pancadas de neve fortes",
    95: "Trovoada", 96: "Trovoada com granizo fraco", 99: "Trovoada com granizo forte"
}

def _descricao(codigo):
    try:
        return DESCRICOES.get(int(codigo), "Condição não identificada")
    except (TypeError, ValueError):
        return "Condição não identificada"

def obter_previsao(latitude, longitude):
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "is_day", "precipitation", "rain", "showers", "weather_code",
            "cloud_cover", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
        ],
        "hourly": ["temperature_2m", "precipitation_probability", "precipitation", "weather_code", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min",
                  "apparent_temperature_max", "apparent_temperature_min", "precipitation_probability_max", "sunrise", "sunset"],
        "timezone": "auto",
        "forecast_days": 7
    }
    resposta = requests.get(OPEN_METEO_FORECAST, params=parametros, timeout=20)
    resposta.raise_for_status()
    dados = resposta.json()
    atual = dados.get("current", {})
    unidades = dados.get("current_units", {})
    diario = dados.get("daily", {})
    horarios = dados.get("hourly", {})
    dias = []
    for i, data in enumerate(diario.get("time", [])):
        dias.append({
            "data": data,
            "condicao": _descricao(diario.get("weather_code", [None])[i]),
            "codigo": diario.get("weather_code", [None])[i],
            "maxima": diario.get("temperature_2m_max", [None])[i],
            "minima": diario.get("temperature_2m_min", [None])[i],
            "sensacao_maxima": diario.get("apparent_temperature_max", [None])[i],
            "sensacao_minima": diario.get("apparent_temperature_min", [None])[i],
            "probabilidade_chuva": diario.get("precipitation_probability_max", [None])[i],
            "nascer_sol": diario.get("sunrise", [None])[i],
            "por_sol": diario.get("sunset", [None])[i],
        })
    proximas_horas = []
    agora = atual.get("time", "")
    for i, hora in enumerate(horarios.get("time", [])):
        if agora and hora < agora:
            continue
        if len(proximas_horas) >= 12:
            break
        proximas_horas.append({
            "hora": hora,
            "temperatura": horarios.get("temperature_2m", [None])[i],
            "probabilidade_chuva": horarios.get("precipitation_probability", [None])[i],
            "precipitacao": horarios.get("precipitation", [None])[i],
            "condicao": _descricao(horarios.get("weather_code", [None])[i]),
            "vento": horarios.get("wind_speed_10m", [None])[i]
        })
    return {
        "latitude": dados.get("latitude"),
        "longitude": dados.get("longitude"),
        "fuso_horario": dados.get("timezone"),
        "unidades": {
            "temperatura": unidades.get("temperature_2m", "°C"),
            "vento": unidades.get("wind_speed_10m", "km/h"),
            "precipitacao": unidades.get("precipitation", "mm")
        },
        "atual": {
            "horario": atual.get("time"),
            "temperatura": atual.get("temperature_2m"),
            "umidade": atual.get("relative_humidity_2m"),
            "sensacao": atual.get("apparent_temperature"),
            "dia": atual.get("is_day"),
            "precipitacao": atual.get("precipitation"),
            "chuva": atual.get("rain"),
            "pancadas": atual.get("showers"),
            "codigo": atual.get("weather_code"),
            "condicao": _descricao(atual.get("weather_code")),
            "nebulosidade": atual.get("cloud_cover"),
            "vento": atual.get("wind_speed_10m"),
            "direcao_vento": atual.get("wind_direction_10m"),
            "rajadas": atual.get("wind_gusts_10m")
        },
        "dias": dias,
        "proximas_horas": proximas_horas,
        "atualizado_em": datetime.now().isoformat(timespec="minutes")
    }

def buscar_cidades(consulta):
    resposta = requests.get(OPEN_METEO_GEOCODING, params={
        "name": consulta, "count": 8, "language": "pt", "format": "json"
    }, timeout=15)
    resposta.raise_for_status()
    resultados = []
    for item in resposta.json().get("results", []):
        resultados.append({
            "nome": item.get("name", ""),
            "estado": item.get("admin1", ""),
            "pais": item.get("country", ""),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude")
        })
    return resultados

def buscar_localizacao(latitude, longitude):
    resposta = requests.get(NOMINATIM_REVERSE, params={
        "lat": latitude, "lon": longitude, "format": "jsonv2", "zoom": 10,
        "addressdetails": 1
    }, headers=HEADERS, timeout=15)
    resposta.raise_for_status()
    item = resposta.json()
    endereco = item.get("address", {})
    nome = (endereco.get("city") or endereco.get("town") or endereco.get("village")
            or endereco.get("municipality") or endereco.get("county") or item.get("name", ""))
    if not nome:
        return None
    return {
        "nome": nome,
        "estado": endereco.get("state", ""),
        "pais": endereco.get("country", ""),
        "latitude": latitude,
        "longitude": longitude
    }
