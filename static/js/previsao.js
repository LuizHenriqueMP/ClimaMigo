const id = window.CIDADE_ID;
let cidadeAtual = null;
let previsaoAtual = null;
const mensagem = document.querySelector("#mensagem");
function aviso(texto, erro = false) {
  mensagem.textContent = texto;
  mensagem.className = `message ${erro ? "error" : "success"}`;
}
function escapar(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
function numero(valor, casas = 0) {
  return valor === null || valor === undefined || valor === "" || !Number.isFinite(Number(valor)) ? "—" : Number(valor).toFixed(casas);
}
function dataCurta(data) {
  const d = new Date(`${data}T12:00:00`);
  return d.toLocaleDateString("pt-BR", {weekday:"short", day:"2-digit", month:"2-digit"});
}
async function requisicao(url, opcoes = {}) {
  const resposta = await fetch(url, opcoes);
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || "Ocorreu um erro.");
  return dados;
}
async function carregar() {
  try {
    [cidadeAtual, previsaoAtual] = await Promise.all([
      requisicao(`/api/cidades/${encodeURIComponent(id)}`),
      requisicao(`/api/cidades/${encodeURIComponent(id)}/previsao`)
    ]);
    renderizar();
  } catch (erro) {
    aviso(erro.message, true);
  }
}
function renderizar() {
  const c = cidadeAtual, p = previsaoAtual, a = p.atual;
  document.title = `${c.nome} | ClimaMigo`;
  document.querySelector("#nome-cidade").textContent = c.nome;
  document.querySelector("#local-cidade").textContent = [c.estado, c.pais].filter(Boolean).join(", ");
  document.querySelector("#condicao").textContent = a.condicao || "Condição indisponível";
  document.querySelector("#temperatura").textContent = numero(a.temperatura);
  document.querySelector("#sensacao").textContent = numero(a.sensacao);
  document.querySelector("#umidade").textContent = a.umidade == null ? "—" : `${a.umidade}%`;
  document.querySelector("#vento").textContent = a.vento == null ? "—" : `${numero(a.vento)} km/h`;
  document.querySelector("#chuva").textContent = a.precipitacao == null ? "—" : `${numero(a.precipitacao, 1)} mm`;
  document.querySelector("#nuvens").textContent = a.nebulosidade == null ? "—" : `${a.nebulosidade}%`;
  document.querySelector("#lista-dias").innerHTML = p.dias.map(d => `
    <article class="day-card"><p>${escapar(dataCurta(d.data))}</p><div class="weather-symbol">${icone(d.codigo)}</div>
    <strong>${escapar(d.condicao)}</strong><div class="minmax"><b>${numero(d.maxima)}°</b><span>${numero(d.minima)}°</span></div>
    <small>☂ ${d.probabilidade_chuva == null ? "—" : `${d.probabilidade_chuva}%`}</small></article>`).join("");
  document.querySelector("#lista-horas").innerHTML = p.proximas_horas.map(h => `
    <tr><td>${escapar(h.hora.replace("T", " "))}</td><td>${icone(h.condicao)} ${escapar(h.condicao)}</td>
    <td>${numero(h.temperatura)}°C</td><td>${h.probabilidade_chuva == null ? "—" : `${h.probabilidade_chuva}%`}</td><td>${numero(h.vento)} km/h</td></tr>`).join("");
  preencherEdicao();
}
function icone(codigo) {
  const c = Number(codigo);
  if (c === 0) return "☀️";
  if ([1,2].includes(c)) return "🌤️";
  if (c === 3) return "☁️";
  if ([45,48].includes(c)) return "🌫️";
  if ([95,96,99].includes(c)) return "⛈️";
  if ([71,73,75,77,85,86].includes(c)) return "❄️";
  if ([51,53,55,56,57,61,63,65,66,67,80,81,82].includes(c)) return "🌧️";
  return "🌡️";
}
document.querySelector("#atualizar").addEventListener("click", async () => {
  const botao = document.querySelector("#atualizar");
  botao.disabled = true; botao.textContent = "Atualizando...";
  try { previsaoAtual = await requisicao(`/api/cidades/${encodeURIComponent(id)}/previsao`); renderizar(); aviso("Previsão atualizada."); }
  catch (e) { aviso(e.message, true); }
  finally { botao.disabled = false; botao.textContent = "↻ Atualizar"; }
});
document.querySelector("#pedir-recomendacao").addEventListener("click", async () => {
  const botao = document.querySelector("#pedir-recomendacao");
  const area = document.querySelector("#texto-recomendacao");
  botao.disabled = true; botao.textContent = "Analisando...";
  area.textContent = "Consultando os dados meteorológicos...";
  try {
    const dados = await requisicao(`/api/cidades/${encodeURIComponent(id)}/recomendacao`, {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({previsao: previsaoAtual})
    });
    area.textContent = dados.recomendacao;
  } catch (e) { area.textContent = e.message; }
  finally { botao.disabled = false; botao.textContent = "Gerar recomendação"; }
});
function preencherEdicao() {
  document.querySelector("#edit-nome").value = cidadeAtual.nome;
  document.querySelector("#edit-estado").value = cidadeAtual.estado || "";
  document.querySelector("#edit-pais").value = cidadeAtual.pais || "";
  document.querySelector("#edit-lat").value = cidadeAtual.latitude;
  document.querySelector("#edit-lon").value = cidadeAtual.longitude;
}
document.querySelector("#editar-cidade").addEventListener("click", () => {
  const form = document.querySelector("#form-edicao");
  form.classList.toggle("hidden");
  document.querySelector("#editar-cidade").textContent = form.classList.contains("hidden") ? "Editar dados" : "Cancelar edição";
});
document.querySelector("#form-edicao").addEventListener("submit", async e => {
  e.preventDefault();
  const dados = {
    nome: document.querySelector("#edit-nome").value.trim(),
    estado: document.querySelector("#edit-estado").value.trim(),
    pais: document.querySelector("#edit-pais").value.trim(),
    latitude: document.querySelector("#edit-lat").value,
    longitude: document.querySelector("#edit-lon").value
  };
  try {
    cidadeAtual = await requisicao(`/api/cidades/${encodeURIComponent(id)}`, {
      method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados)
    });
    document.querySelector("#form-edicao").classList.add("hidden");
    renderizar(); aviso("Cidade atualizada com sucesso.");
  } catch (e2) { aviso(e2.message, true); }
});
document.querySelector("#excluir-cidade").addEventListener("click", async () => {
  if (!confirm(`Deseja realmente excluir ${cidadeAtual.nome}?`)) return;
  try {
    await requisicao(`/api/cidades/${encodeURIComponent(id)}`, {method:"DELETE"});
    window.location.href = "/";
  } catch (e) { aviso(e.message, true); }
});
carregar();
