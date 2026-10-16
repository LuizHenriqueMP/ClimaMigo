import json
import os
import threading
import uuid

CAMINHO_DADOS = os.path.join(os.path.dirname(__file__), "data", "cidades.json")
_LOCK = threading.Lock()

def _garantir_arquivo():
    os.makedirs(os.path.dirname(CAMINHO_DADOS), exist_ok=True)
    if not os.path.exists(CAMINHO_DADOS):
        with open(CAMINHO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump({"cidades": []}, arquivo, ensure_ascii=False, indent=2)

def _ler():
    _garantir_arquivo()
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
        conteudo = json.load(arquivo)
    if not isinstance(conteudo, dict) or not isinstance(conteudo.get("cidades"), list):
        raise ValueError("O arquivo cidades.json possui formato inválido.")
    return conteudo["cidades"]

def _gravar(cidades):
    _garantir_arquivo()
    temporario = CAMINHO_DADOS + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump({"cidades": cidades}, arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, CAMINHO_DADOS)

def listar_cidades():
    with _LOCK:
        return sorted(_ler(), key=lambda c: c.get("nome", "").casefold())

def obter_cidade(cidade_id):
    with _LOCK:
        return next((c for c in _ler() if c["id"] == cidade_id), None)

def _validar(dados):
    nome = str(dados.get("nome", "")).strip()
    estado = str(dados.get("estado", "")).strip()
    pais = str(dados.get("pais", "")).strip()
    try:
        latitude = float(dados.get("latitude"))
        longitude = float(dados.get("longitude"))
    except (TypeError, ValueError):
        raise ValueError("Selecione uma localização válida no mapa.")
    if not nome:
        raise ValueError("O nome da cidade é obrigatório.")
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("As coordenadas estão fora dos limites válidos.")
    return {
        "nome": nome[:120],
        "estado": estado[:120],
        "pais": pais[:120],
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
    }

def criar_cidade(dados):
    cidade = _validar(dados)
    with _LOCK:
        cidades = _ler()
        duplicada = next((c for c in cidades
                          if abs(c["latitude"] - cidade["latitude"]) < 0.0001
                          and abs(c["longitude"] - cidade["longitude"]) < 0.0001), None)
        if duplicada:
            raise ValueError(f"Essa localização já está cadastrada como {duplicada['nome']}.")
        cidade["id"] = str(uuid.uuid4())
        cidades.append(cidade)
        _gravar(cidades)
    return cidade

def atualizar_cidade(cidade_id, dados):
    cidade_nova = _validar(dados)
    with _LOCK:
        cidades = _ler()
        indice = next((i for i, c in enumerate(cidades) if c["id"] == cidade_id), None)
        if indice is None:
            return None
        cidade_nova["id"] = cidade_id
        for i, c in enumerate(cidades):
            if i != indice and abs(c["latitude"] - cidade_nova["latitude"]) < 0.0001 and abs(c["longitude"] - cidade_nova["longitude"]) < 0.0001:
                raise ValueError(f"Essa localização já está cadastrada como {c['nome']}.")
        cidades[indice] = cidade_nova
        _gravar(cidades)
    return cidade_nova

def excluir_cidade(cidade_id):
    with _LOCK:
        cidades = _ler()
        filtradas = [c for c in cidades if c["id"] != cidade_id]
        if len(filtradas) == len(cidades):
            return False
        _gravar(filtradas)
        return True
