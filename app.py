import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from cidades import listar_cidades, obter_cidade, criar_cidade, atualizar_cidade, excluir_cidade
from previsao import obter_previsao, buscar_cidades, buscar_localizacao
from chatbot import gerar_recomendacao

load_dotenv()
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/cidade/nova")
def nova_cidade():
    return render_template("cidade_form.html")

@app.get("/cidade/<cidade_id>")
def detalhe_cidade(cidade_id):
    cidade = obter_cidade(cidade_id)
    if not cidade:
        return render_template("index.html"), 404
    return render_template("previsao.html", cidade_id=cidade_id)

@app.get("/api/cidades")
def api_listar_cidades():
    return jsonify(listar_cidades())

@app.get("/api/cidades/<cidade_id>")
def api_obter_cidade(cidade_id):
    cidade = obter_cidade(cidade_id)
    if not cidade:
        return jsonify({"erro": "Cidade não encontrada."}), 404
    return jsonify(cidade)

@app.post("/api/cidades")
def api_criar_cidade():
    dados = request.get_json(silent=True) or {}
    try:
        cidade = criar_cidade(dados)
        return jsonify(cidade), 201
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400
    except Exception:
        app.logger.exception("Erro ao cadastrar cidade")
        return jsonify({"erro": "Não foi possível salvar a cidade."}), 500

@app.put("/api/cidades/<cidade_id>")
def api_atualizar_cidade(cidade_id):
    dados = request.get_json(silent=True) or {}
    try:
        cidade = atualizar_cidade(cidade_id, dados)
        if not cidade:
            return jsonify({"erro": "Cidade não encontrada."}), 404
        return jsonify(cidade)
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400
    except Exception:
        app.logger.exception("Erro ao atualizar cidade")
        return jsonify({"erro": "Não foi possível atualizar a cidade."}), 500

@app.delete("/api/cidades/<cidade_id>")
def api_excluir_cidade(cidade_id):
    if not excluir_cidade(cidade_id):
        return jsonify({"erro": "Cidade não encontrada."}), 404
    return jsonify({"mensagem": "Cidade excluída com sucesso."})

@app.get("/api/geocodificar")
def api_geocodificar():
    consulta = request.args.get("q", "").strip()
    if len(consulta) < 2:
        return jsonify({"erro": "Digite pelo menos dois caracteres."}), 400
    try:
        return jsonify(buscar_cidades(consulta))
    except Exception:
        app.logger.exception("Erro na pesquisa geográfica")
        return jsonify({"erro": "Não foi possível pesquisar essa localização agora."}), 502

@app.get("/api/localizacao-reversa")
def api_localizacao_reversa():
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
    except ValueError:
        return jsonify({"erro": "Coordenadas inválidas."}), 400
    try:
        local = buscar_localizacao(lat, lon)
        return jsonify(local) if local else (jsonify({"erro": "Não foi possível identificar a cidade neste ponto."}), 404)
    except Exception:
        app.logger.exception("Erro na localização reversa")
        return jsonify({"erro": "Não foi possível identificar essa localização agora."}), 502

@app.get("/api/cidades/<cidade_id>/previsao")
def api_previsao(cidade_id):
    cidade = obter_cidade(cidade_id)
    if not cidade:
        return jsonify({"erro": "Cidade não encontrada."}), 404
    try:
        return jsonify(obter_previsao(cidade["latitude"], cidade["longitude"]))
    except Exception:
        app.logger.exception("Erro ao consultar previsão")
        return jsonify({"erro": "Não foi possível obter a previsão meteorológica. Tente novamente."}), 502

@app.post("/api/cidades/<cidade_id>/recomendacao")
def api_recomendacao(cidade_id):
    cidade = obter_cidade(cidade_id)
    if not cidade:
        return jsonify({"erro": "Cidade não encontrada."}), 404
    dados = request.get_json(silent=True) or {}
    previsao = dados.get("previsao")
    if not isinstance(previsao, dict):
        try:
            previsao = obter_previsao(cidade["latitude"], cidade["longitude"])
        except Exception:
            return jsonify({"erro": "Não foi possível obter os dados meteorológicos."}), 502
    try:
        texto = gerar_recomendacao(cidade, previsao)
        return jsonify({"recomendacao": texto, "modo": "ia" if os.getenv("GROQ_API_KEY") else "local"})
    except Exception:
        app.logger.exception("Erro ao gerar recomendação")
        return jsonify({"erro": "Não foi possível gerar a recomendação agora."}), 502

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
