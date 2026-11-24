// Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
// GANCHO DE DADOS ILUSTRATIVOS · copie para <projeto>/demo/<nome>.js
// Roda só no navegador da gravação: o banco não é tocado. Avise o usuário na entrega.
// Cada gancho recebe (url, texto JSON já anonimizado) e devolve o texto final.
(() => {
  window.__tutorDemo = window.__tutorDemo || [];
  window.__tutorDemo.push(async (url, texto) => {
    // Exemplo: lista de tarefas vazia ganha 3 itens de demonstração, só nesta tela
    if (!/\/api\/v1\/tarefas(\?|$)/.test(url) || !location.pathname.startsWith("/tarefas")) return texto;
    const lista = JSON.parse(texto);
    if (lista.length) return texto;
    const h = 3600e3, agora = Date.now();
    // Dê ids próprios aos itens: muitos fronts recolocam o objeto original pelo id
    return JSON.stringify([
      { id: "demo-1", titulo: "Ligar para o cliente", status: "aberta", criadaEm: new Date(agora - 3 * h).toISOString() },
      { id: "demo-2", titulo: "Enviar proposta revisada", status: "em_andamento", criadaEm: new Date(agora - 20 * h).toISOString() },
      { id: "demo-3", titulo: "Confirmar entrega", status: "concluida", criadaEm: new Date(agora - 50 * h).toISOString() },
    ]);
  });
})();
