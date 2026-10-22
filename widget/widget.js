/*
 * PawConnect chat widget
 * Embed on any website with one line before </body>:
 *
 *   <script src="https://YOUR-API.onrender.com/widget/widget.js" defer></script>
 *
 * Optional attributes on the <script> tag:
 *   data-api="https://..."     API base URL (default: where this script is served from)
 *   data-title="..."           Header title
 *   data-color="#e8833a"       Accent color
 */
(function () {
  "use strict";
  if (window.__pawConnectLoaded) return;
  window.__pawConnectLoaded = true;

  var script = document.currentScript;
  var cfg = {
    api: (script && script.dataset.api) || (script ? new URL(script.src).origin : ""),
    title: (script && script.dataset.title) || "PlayStayTion Pet Resort",
    color: (script && script.dataset.color) || "#e8833a",
    welcome:
      "Hi! Welcome to PlayStayTion Pet Resort 🐾\n\n" +
      "I can help with bookings, prices, hours and services. How can I help today?",
  };

  // ─── Session id (kept per browser tab) ───
  var SESSION_KEY = "pawconnect_session";
  var sessionId = null;
  try { sessionId = sessionStorage.getItem(SESSION_KEY); } catch (e) {}
  function saveSession(id) {
    sessionId = id;
    try { sessionStorage.setItem(SESSION_KEY, id); } catch (e) {}
  }

  // ─── Build UI inside a shadow root so site CSS can't break it ───
  var host = document.createElement("div");
  host.id = "pawconnect-widget";
  document.body.appendChild(host);
  var root = host.attachShadow({ mode: "open" });

  root.innerHTML =
    "<style>" +
    ":host{--accent:" + cfg.color + ";all:initial}" +
    "*{box-sizing:border-box;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}" +
    ".bubble{position:fixed;right:20px;bottom:20px;width:60px;height:60px;border-radius:50%;border:none;" +
    "background:var(--accent);color:#fff;font-size:28px;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.25);z-index:2147483646}" +
    ".bubble:focus-visible{outline:3px solid #222;outline-offset:3px}" +
    ".panel{position:fixed;right:20px;bottom:92px;width:370px;max-width:calc(100vw - 32px);height:540px;max-height:calc(100vh - 120px);" +
    "background:#fff;color:#1f2328;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.25);display:none;flex-direction:column;overflow:hidden;z-index:2147483647}" +
    ".panel.open{display:flex}" +
    ".head{background:var(--accent);color:#fff;padding:14px 16px;display:flex;align-items:center;justify-content:space-between}" +
    ".head b{font-size:15px}.head small{display:block;font-size:12px;opacity:.9}" +
    ".close{background:none;border:none;color:#fff;font-size:22px;cursor:pointer;line-height:1}" +
    ".msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#f7f7f8}" +
    ".m{max-width:85%;padding:9px 12px;border-radius:14px;font-size:14px;line-height:1.45;white-space:pre-wrap;word-wrap:break-word}" +
    ".bot{background:#fff;border:1px solid #e5e5e5;align-self:flex-start;border-bottom-left-radius:4px}" +
    ".me{background:var(--accent);color:#fff;align-self:flex-end;border-bottom-right-radius:4px}" +
    ".typing{color:#777;font-style:italic}" +
    "form{display:flex;gap:8px;padding:10px;border-top:1px solid #eee;background:#fff}" +
    "input{flex:1;border:1px solid #ddd;border-radius:20px;padding:10px 14px;font-size:14px;outline:none;color:#1f2328;background:#fff}" +
    "input:focus{border-color:var(--accent)}" +
    "button.send{background:var(--accent);color:#fff;border:none;border-radius:20px;padding:0 16px;font-size:14px;cursor:pointer}" +
    "button.send:disabled{opacity:.5;cursor:default}" +
    ".foot{font-size:11px;color:#999;text-align:center;padding:0 0 8px;background:#fff}" +
    "@media (max-width:480px){.panel{right:0;bottom:0;width:100vw;max-width:100vw;height:100vh;max-height:100vh;border-radius:0}}" +
    "</style>" +
    '<button class="bubble" aria-label="Open chat">🐾</button>' +
    '<div class="panel" role="dialog" aria-label="Chat with ' + escapeAttr(cfg.title) + '">' +
    '  <div class="head"><div><b></b><small>Usually replies in seconds · 24/7</small></div>' +
    '    <button class="close" aria-label="Close chat">×</button></div>' +
    '  <div class="msgs" aria-live="polite"></div>' +
    '  <form><input type="text" placeholder="Type your message…" maxlength="1000" aria-label="Message" />' +
    '    <button class="send" type="submit">Send</button></form>' +
    '  <div class="foot">Powered by Paw Connect AI</div>' +
    "</div>";

  var bubble = root.querySelector(".bubble");
  var panel = root.querySelector(".panel");
  var msgs = root.querySelector(".msgs");
  var form = root.querySelector("form");
  var input = root.querySelector("input");
  var sendBtn = root.querySelector(".send");
  root.querySelector(".head b").textContent = cfg.title;

  function escapeAttr(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function add(text, who) {
    var el = document.createElement("div");
    el.className = "m " + who;
    // Support **bold** from the model, but never render replies as HTML:
    // every piece is inserted as a text node.
    String(text).split(/\*\*(.+?)\*\*/g).forEach(function (part, i) {
      if (i % 2) {
        var strong = document.createElement("strong");
        strong.textContent = part;
        el.appendChild(strong);
      } else if (part) {
        el.appendChild(document.createTextNode(part));
      }
    });
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
    return el;
  }

  var greeted = false;
  function toggle(open) {
    panel.classList.toggle("open", open);
    bubble.setAttribute("aria-label", open ? "Close chat" : "Open chat");
    if (open) {
      if (!greeted) { add(cfg.welcome, "bot"); greeted = true; }
      input.focus();
    }
  }
  bubble.addEventListener("click", function () { toggle(!panel.classList.contains("open")); });
  root.querySelector(".close").addEventListener("click", function () { toggle(false); });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text || sendBtn.disabled) return;
    add(text, "me");
    input.value = "";
    sendBtn.disabled = true;
    var typing = add("Typing…", "bot typing");

    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, 60000);

    fetch(cfg.api + "/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
      signal: ctrl.signal,
    })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        saveSession(data.session_id);
        typing.remove();
        add(data.reply, "bot");
      })
      .catch(function () {
        typing.remove();
        add("Sorry, I couldn't connect. Please call us at 903-207-4408!", "bot");
      })
      .finally(function () {
        clearTimeout(timer);
        sendBtn.disabled = false;
        input.focus();
      });
  });
})();
