// Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
// Cursor desenhado no DOM (o cursor do X não acompanha o mouse do CDP) + anel de clique.
(() => {
  if (window.__tutorCursor) return;
  window.__tutorCursor = true;
  const COR = (window.__TUTOR_CFG && window.__TUTOR_CFG.cor) || "#1D4E9E";
  const mk = () => {
    if (document.getElementById("__tutor_cur") || !document.documentElement) return;
    const c = document.createElement("div");
    c.id = "__tutor_cur";
    c.setAttribute("data-azvor", "tutor");
    c.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.5 15 L11.5 22 L14.5 20.7 L11.5 14 L17.5 14 Z" fill="#111" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, { position: "fixed", left: "0", top: "0", zIndex: 2147483647, pointerEvents: "none", filter: "drop-shadow(0 2px 3px rgba(0,0,0,.35))" });
    const p = window.__tutorPos || [-200, -200];
    c.style.transform = `translate(${p[0] - 4}px,${p[1] - 3}px)`;
    document.documentElement.appendChild(c);
  };
  document.addEventListener("mousemove", (e) => {
    window.__tutorPos = [e.clientX, e.clientY];
    mk();
    const c = document.getElementById("__tutor_cur");
    if (c) c.style.transform = `translate(${e.clientX - 4}px,${e.clientY - 3}px)`;
  }, true);
  document.addEventListener("mousedown", (e) => {
    const r = document.createElement("div");
    Object.assign(r.style, {
      position: "fixed", left: e.clientX - 24 + "px", top: e.clientY - 24 + "px", width: "48px", height: "48px",
      borderRadius: "50%", background: COR + "40", border: "2px solid " + COR + "a6", zIndex: 2147483646,
      pointerEvents: "none", transition: "transform .5s ease-out, opacity .5s ease-out", transform: "scale(.3)", opacity: "1",
    });
    document.documentElement.appendChild(r);
    requestAnimationFrame(() => requestAnimationFrame(() => { r.style.transform = "scale(1.25)"; r.style.opacity = "0"; }));
    setTimeout(() => r.remove(), 700);
  }, true);
  const css = () => {
    const st = document.createElement("style");
    st.textContent = "*{cursor:none !important} ::-webkit-scrollbar{width:0 !important;height:0 !important} *{scrollbar-width:none !important}";
    (document.head || document.documentElement).appendChild(st);
    mk();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", css); else css();
})();
