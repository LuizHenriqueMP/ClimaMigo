const mapa = L.map("mapa").setView([-14.235, -51.9253], 4);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mapa);
let marcador = null;
let localSelecionado = null;
const campoNome = document.querySelector("#nome");
const campoEstado = document.querySelector("#estado");
const campoPais = document.querySelector("#pais");
const campoLat = document.querySelector("#latitude");
const campoLon = document.querySelector("#longitude");
const resultados = document.querySelector("#resultados-busca");
const mensagem = document.querySelector("#mensagem");

function aviso(texto, erro = false) {
  mensagem.textContent = texto;
  mensagem.className = `message ${erro ? "error" : "success"}`;
}
function selecionarLocal(local, centralizar = true) {
  const lat = Number(local.latitude);
  const lon = Number(local.longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
  localSelecionado = {...local, latitude: lat, longitude: lon};
  campoNome.value = local.nome || "";
  campoEstado.value = local.estado || "";
  campoPais.value = local.pais || "";
  campoLat.value = lat;
  campoLon.value = lon;
  document.querySelector("#lat-label").textContent = lat.toFixed(6);
  document.querySelector("#lon-label").textContent = lon.toFixed(6);
  if (marcador) marcador.remove();
  marcador = L.marker([lat, lon]).addTo(mapa).bindPopup(`${local.nome || "Local selecionado"}`).openPopup();
  if (centralizar) mapa.setView([lat, lon], 11);
  resultados.innerHTML = "";
}
async function buscar() {
  const termo = document.querySelector("#pesquisa-mapa").value.trim();
  if (termo.length < 2) return aviso("Digite pelo menos dois caracteres para pesquisar.", true);
  resultados.textContent = "Pesquisando...";
  try {
    const resposta = await fetch(`/api/geocodificar?q=${encodeURIComponent(termo)}`);
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Falha na pesquisa.");
    if (!dados.length) {
      resultados.textContent = "Nenhuma cidade encontrada. Você pode clicar diretamente no mapa.";
      return;
    }
    resultados.innerHTML = "";
    dados.forEach(local => {
      const botao = document.createElement("button");
      botao.type = "button";
      botao.className = "search-result";
      botao.textContent = [local.nome, local.estado, local.pais].filter(Boolean).join(", ");
      botao.addEventListener("click", () => selecionarLocal(local));
      resultados.appendChild(botao);
    });
  } catch (erro) {
    resultados.textContent = erro.message;
  }
}
document.querySelector("#btn-pesquisar").addEventListener("click", buscar);
document.querySelector("#pesquisa-mapa").addEventListener("keydown", e => {
  if (e.key === "Enter") { e.preventDefault(); buscar(); }
});
mapa.on("click", async evento => {
  const {lat, lng} = evento.latlng;
  selecionarLocal({nome: "", estado: "", pais: "", latitude: lat, longitude: lng}, false);
  try {
    const resposta = await fetch(`/api/localizacao-reversa?lat=${lat}&lon=${lng}`);
    const local = await resposta.json();
    if (resposta.ok) selecionarLocal({...local, latitude: lat, longitude: lng}, false);
    else aviso("Coordenadas selecionadas. Preencha o nome da cidade manualmente se não for identificado.", true);
  } catch {
    aviso("Coordenadas selecionadas. Preencha o nome da cidade manualmente.", true);
  }
});
document.querySelector("#form-cidade").addEventListener("submit", async evento => {
  evento.preventDefault();
  const dados = {
    nome: campoNome.value.trim(), estado: campoEstado.value.trim(), pais: campoPais.value.trim(),
    latitude: campoLat.value, longitude: campoLon.value
  };
  if (!dados.latitude || !dados.longitude) return aviso("Pesquise uma cidade ou selecione um ponto no mapa.", true);
  try {
    const resposta = await fetch("/api/cidades", {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados)
    });
    const resultado = await resposta.json();
    if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível salvar.");
    window.location.href = `/cidade/${encodeURIComponent(resultado.id)}`;
  } catch (erro) {
    aviso(erro.message, true);
  }
});
setTimeout(() => mapa.invalidateSize(), 250);
