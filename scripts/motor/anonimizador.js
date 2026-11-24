// Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
// Envolve window.fetch na página da gravação:
//   1) troca nomes de clientes por nomes fictícios coerentes e mascara telefones;
//   2) aplica ganchos de dados ilustrativos (window.__tutorDemo) — só no navegador;
//   3) guarda em cache rotas pesadas para trocar de aba sem tela de carregamento.
// Nada disso altera o servidor: as respostas reais continuam iguais no banco.
(() => {
  if (window.__tutorAnon) return;
  window.__tutorAnon = true;
  const CFG = (window.__TUTOR_CFG && window.__TUTOR_CFG.privacidade) || {};
  const ROTAS = (CFG.rotas || []).map((r) => new RegExp(r));
  const CACHE = (CFG.cache_rotas || []).map((r) => new RegExp(r));
  const KEYS = new Set(CFG.chaves_nome || []);
  const TEL = CFG.mascarar_telefones !== false;
  const PRIM = ["Mariana","Carlos","Fernanda","Ricardo","Juliana","Paulo","Beatriz","Rafael","Camila","Lucas","Patrícia","André","Renata","Gustavo","Aline","Diego","Larissa","Thiago","Vanessa","Bruno","Débora","Felipe","Natália","Rodrigo","Sabrina","Marcelo","Priscila","Vinícius","Tatiane","Eduardo","Cláudia","Fábio","Letícia","Gabriel","Simone","Leandro","Bianca","Márcio","Elaine","Sérgio"];
  const SOBR = ["Souza","Lima","Rocha","Alves","Costa","Mendes","Nunes","Teixeira","Ribeiro","Martins","Gomes","Barbosa","Dias","Pires","Moreira","Cardoso","Freitas","Moura","Castro","Araújo","Lopes","Ramos","Duarte","Campos","Vieira","Pinto","Reis","Correia","Melo","Farias","Batista","Cunha","Monteiro","Rezende","Prado","Macedo","Tavares","Fonseca","Queiroz","Siqueira"];
  const mapa = new Map();
  const fake = (o) => {
    const k = o.toLowerCase();
    if (!mapa.has(k)) {
      let h = 0; for (const ch of k) h = (h * 131 + ch.charCodeAt(0)) >>> 0;
      mapa.set(k, PRIM[h % PRIM.length] + " " + SOBR[Math.floor(h / PRIM.length) % SOBR.length]);
    }
    return mapa.get(k);
  };
  const ehNome = (k, v) => KEYS.has(k) && typeof v === "string" && v.trim() && v.trim().toLowerCase() !== "cliente";
  const telRe = /(^|[^\d.])(\+?55)?(\d{2})(9?\d{4})(\d{4})(?![\d.])/g;
  const mascara = (s) => (TEL ? s.replace(telRe, (m, p, c, d, e, f) => p + "•••••" + f) : s);
  const coletar = (o, acc) => {
    if (Array.isArray(o)) o.forEach((v) => coletar(v, acc));
    else if (o && typeof o === "object") for (const [k, v] of Object.entries(o)) { if (ehNome(k, v)) acc.add(v.trim()); else coletar(v, acc); }
  };
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const anon = (text) => {
    let data; try { data = JSON.parse(text); } catch (e) { return text; }
    if (text.length > 150000) {
      // respostas grandes: percorre o objeto (regex global por nome travaria a página)
      const walk = (o) => {
        if (Array.isArray(o)) o.forEach(walk);
        else if (o && typeof o === "object") for (const k of Object.keys(o)) {
          const v = o[k];
          if (ehNome(k, v)) o[k] = fake(v.trim());
          else if (typeof v === "string") o[k] = mascara(v);
          else walk(v);
        }
      };
      walk(data); return JSON.stringify(data);
    }
    const nomes = new Set(); coletar(data, nomes);
    const pares = [];
    for (const n of nomes) { const f = fake(n); pares.push([n, f]); const a = n.split(/\s+/)[0], b = f.split(" ")[0]; if (a.length >= 3) pares.push([a, b]); }
    pares.sort((x, y) => y[0].length - x[0].length);
    for (const [a, b] of pares) {
      const ja = JSON.stringify(a).slice(1, -1), jb = JSON.stringify(b).slice(1, -1);
      text = text.replace(new RegExp("(^|[^\\p{L}\\p{N}_])" + esc(ja) + "(?![\\p{L}\\p{N}_])", "giu"), (m, p) => p + jb);
    }
    return mascara(text);
  };
  window.__tutorDemo = window.__tutorDemo || [];   // ganchos: async (url, texto) => texto
  window.__tutorFake = fake;
  const cache = {};
  const orig = window.fetch.bind(window);
  window.fetch = async (input, init) => {
    const url = typeof input === "string" ? input : (input && input.url) || "";
    const metodo = ((init && init.method) || (input && input.method) || "GET").toUpperCase();
    if (metodo === "GET" && cache[url] && CACHE.some((r) => r.test(url))) {
      return new Response(cache[url], { status: 200, headers: { "content-type": "application/json" } });
    }
    const res = await orig(input, init);
    const alvo = ROTAS.some((r) => r.test(url));
    const temDemo = window.__tutorDemo.length > 0;
    if (!alvo && !temDemo) return res;
    if (!(res.headers.get("content-type") || "").includes("json")) return res;
    let out = await res.text();
    if (alvo) out = anon(out);
    for (const g of window.__tutorDemo) { try { out = await g(url, out); } catch (e) { console.warn("tutor demo", e); } }
    if (res.ok && CACHE.some((r) => r.test(url))) cache[url] = out;
    return new Response(out, { status: res.status, statusText: res.statusText, headers: res.headers });
  };
})();
