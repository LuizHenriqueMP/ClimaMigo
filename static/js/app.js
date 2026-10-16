const lista = document.querySelector("#lista-cidades");
const busca = document.querySelector("#busca-cidades");
const mensagem = document.querySelector("#mensagem");
let cidades = [];

function mostrarMensagem(texto, erro = false) {
  mensagem.textContent = texto;
  mensagem.className = `message ${erro ? "error" : "success"}`;
}
async function carregarCidades() {
  try {
    const resposta = await fetch("/api/cidades");
    if (!resposta.ok) throw new Error("Falha ao carregar cidades.");
    cidades = await resposta.json();
    renderizarCidades();
  } catch (erro) {
    lista.innerHTML = "";
    mostrarMensagem(erro.message, true);
  }
}
function renderizarCidades() {
  const termo = busca.value.trim().toLocaleLowerCase("pt-BR");
  const filtradas = cidades.filter(c => `${c.nome} ${c.estado} ${c.pais}`.toLocaleLowerCase("pt-BR").includes(termo));
  document.querySelector("#contador-cidades").textContent = `${filtradas.length} cidade(s)`;
  if (!filtradas.length) {
    lista.innerHTML = `<div class="empty-state"><div class="empty-icon">⌖</div><h3>${cidades.length ? "Nenhum resultado" : "Você ainda não adicionou cidades"}</h3><p>${cidades.length ? "Tente outra pesquisa." : "Adicione sua primeira cidade para consultar a previsão."}</p><a class="button button-primary" href="/cidade/nova">Adicionar cidade</a></div>`;
    return;
  }
  lista.innerHTML = filtradas.map(c => `
    <article class="city-card">
      <div class="city-icon">☀</div>
      <h3>${escapar(c.nome)}</h3>
      <p>${escapar([c.estado, c.pais].filter(Boolean).join(", "))}</p>
      <small>${Number(c.latitude).toFixed(3)}, ${Number(c.longitude).toFixed(3)}</small>
      <a class="button button-primary card-link" href="/cidade/${encodeURIComponent(c.id)}">Ver previsão <span>→</span></a>
    </article>`).join("");
}
function escapar(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
busca.addEventListener("input", renderizarCidades);
carregarCidades();
