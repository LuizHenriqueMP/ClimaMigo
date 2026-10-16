# ClimaMigo — aplicação web de previsão do tempo

Aplicação Flask com frontend HTML/CSS/JavaScript, CRUD de cidades em JSON, mapa Leaflet/OpenStreetMap, previsão Open-Meteo e recomendações de roupa. A chave da Groq é opcional.

## Requisitos

- Python 3.10 ou superior
- Acesso à internet para consultar Open-Meteo, tiles do OpenStreetMap e, opcionalmente, Groq

## Instalação

### Windows (PowerShell)

```powershell
cd previsao-tempo
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Se o PowerShell bloquear a ativação, você pode executar diretamente `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` e depois `.\.venv\Scripts\python.exe app.py`.

### Linux / macOS

```bash
cd previsao-tempo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python app.py
```

Abra `http://127.0.0.1:5000`.

## Ativar a Groq (opcional)

Edite `.env` e informe sua chave:

```env
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=llama-3.3-70b-versatile
FLASK_DEBUG=true
```

Reinicie o Flask. Sem `GROQ_API_KEY`, o sistema fornece recomendações simples com regras locais. Nunca publique a chave nem faça commit do `.env`.

## Funcionalidades

- Listagem e busca local de cidades cadastradas.
- Cadastro por pesquisa de cidade ou clique no mapa.
- CRUD: criar, ler, editar e excluir cidades.
- Persistência em `data/cidades.json`.
- Previsão atual, próximos sete dias e próximas horas.
- Recomendações de roupa via Groq ou fallback local.
- Endpoints JSON para integração com outros frontends.

## API

- `GET /api/cidades`
- `POST /api/cidades`
- `GET /api/cidades/<id>`
- `PUT /api/cidades/<id>`
- `DELETE /api/cidades/<id>`
- `GET /api/cidades/<id>/previsao`
- `POST /api/cidades/<id>/recomendacao`
- `GET /api/geocodificar?q=Feliz`
- `GET /api/localizacao-reversa?lat=-29.37&lon=-51.11`

Exemplo de corpo para criar cidade:

```json
{
  "nome": "Feliz",
  "estado": "Rio Grande do Sul",
  "pais": "Brasil",
  "latitude": -29.3764,
  "longitude": -51.1144
}
```

## Observações

- As previsões vêm da API Open-Meteo; a aplicação não é responsável por garantir a precisão meteorológica.
- O mapa usa Leaflet e tiles OpenStreetMap. A busca usa o geocodificador Open-Meteo e a identificação reversa usa Nominatim. Para produção com tráfego significativo, respeite as políticas de uso dos provedores, configure cache e considere um serviço de geocodificação próprio/comercial.
- JSON é apropriado para um protótipo de uso limitado. Para múltiplos usuários gravando ao mesmo tempo, migre o armazenamento para SQLite/PostgreSQL/MySQL.
- O modo `debug` deve ser desativado em produção (`FLASK_DEBUG=false`) e a aplicação deve rodar atrás de um servidor WSGI.
- A recomendação não substitui alertas oficiais. A IA só recebe os dados meteorológicos resumidos; o prompt orienta a não inventar tipos de nuvens não fornecidos pela API.
