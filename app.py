import os
from flask import Flask, request, jsonify, render_template_string
import requests

APP_TITLE = "Gestor de Activos de Meta (verificado)"

TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{{ title }}</title>
  <script>
    async function cargarActivos() {
      const access_token = document.getElementById('connect_access_token').value.trim();
      const business_id  = document.getElementById('connect_business_id').value.trim();
      const out = document.getElementById('resultados');
      out.textContent = "Cargando...";
      try {
        const resp = await fetch(`/api/assets?access_token=${encodeURIComponent(access_token)}&business_id=${encodeURIComponent(business_id)}`);
        const data = await resp.json();
        if (!resp.ok) throw data;
        const dsSel = document.getElementById('dataset_select');
        const wbSel = document.getElementById('waba_select');
        dsSel.innerHTML = "";
        wbSel.innerHTML = "";
        (data.datasets || []).forEach(d => {
          const opt = document.createElement('option');
          opt.value = d.id;
          opt.textContent = `${d.name} (${d.id})`;
          dsSel.appendChild(opt);
        });
        (data.wabas || []).forEach(w => {
          const opt = document.createElement('option');
          opt.value = w.id;
          opt.textContent = `${w.name || 'WABA'} (${w.id})`;
          wbSel.appendChild(opt);
        });
        out.textContent = "Activos cargados. Selecciona y pulsa Conectar Activos.";
      } catch (e) {
        out.textContent = "Error al cargar activos: " + (e && e.error && e.error.message ? e.error.message : JSON.stringify(e));
      }
    }
    async function conectarExistente() {
      const form = document.getElementById('form_conectar');
      const fd = new FormData(form);
      const out = document.getElementById('resultados');
      out.textContent = "Conectando...";
      try {
        const resp = await fetch('/connect-existing', { method: 'POST', body: fd });
        const data = await resp.json();
        if (!resp.ok) throw data;
        // Mensaje amigable
        if (data.message) {
          out.textContent = data.message;
        } else {
          out.textContent = "Conexión realizada: " + JSON.stringify(data);
        }
      } catch (e) {
        out.textContent = "Error al conectar: " + (e && e.error && e.error.message ? e.error.message : JSON.stringify(e));
      }
    }
  </script>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background: #f6f7fb; margin: 0; padding: 0; }
    .container { max-width: 980px; margin: 24px auto; padding: 0 16px; }
    .card { background: white; border-radius: 14px; box-shadow: 0 6px 24px rgba(0,0,0,0.06); }
    .card-header { padding: 18px 24px; border-bottom: 1px solid #eee; font-weight: 700; font-size: 20px; display: flex; align-items: center; gap: 10px; }
    .tabs { display: flex; gap: 18px; padding: 14px 24px; border-bottom: 1px solid #eee; }
    .tab { cursor: pointer; padding: 4px 0; }
    .tab.active { color: #2563eb; border-bottom: 2px solid #2563eb; }
    .content { padding: 20px 24px 28px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px; }
    label { font-size: 13px; color: #374151; }
    input, select { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 10px; }
    button { padding: 10px 14px; border: 0; border-radius: 12px; background: #111827; color: white; cursor: pointer; }
    button.secondary { background: #374151; }
    pre { background: #0b1020; color: #d1e3ff; padding: 16px; border-radius: 12px; overflow: auto; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="card-header">Gestor de Activos de Meta</div>
      <div class="tabs">
        <div class="tab active" id="tab-conectar" onclick="document.getElementById('pane-conectar').style.display='block';document.getElementById('pane-crear').style.display='none';this.classList.add('active');document.getElementById('tab-crear').classList.remove('active');">Conectar Existente</div>
        <div class="tab" id="tab-crear" onclick="document.getElementById('pane-crear').style.display='block';document.getElementById('pane-conectar').style.display='none';this.classList.add('active');document.getElementById('tab-conectar').classList.remove('active');">Crear Nuevo</div>
      </div>

      <div class="content" id="pane-conectar">
        <p>Selecciona un conjunto de datos existente y un WABA para conectarlos.</p>
        <form id="form_conectar">
          <div class="row">
            <div>
              <label>Access Token</label>
              <input type="password" id="connect_access_token" name="access_token" value="{{ access_token or '' }}" required />
            </div>
            <div>
              <label>Business ID</label>
              <input type="text" id="connect_business_id" name="connect_business_id" value="{{ business_id or '' }}" required />
            </div>
          </div>

          <div class="row">
            <div>
              <label>Conjunto de datos (pixel/dataset)</label>
              <select id="dataset_select" name="dataset_id" required></select>
            </div>
            <div>
              <label>WABA</label>
              <select id="waba_select" name="waba_id" required></select>
            </div>
          </div>

          <div class="row">
            <button type="button" class="secondary" onclick="cargarActivos()">Cargar Activos Existentes</button>
            <button type="button" onclick="conectarExistente()">Conectar Activos</button>
          </div>
        </form>
        <h3>Resultados:</h3>
        <pre id="resultados"></pre>
      </div>

      <div class="content" id="pane-crear" style="display:none;">
        <p>Crea un nuevo conjunto de datos y conéctalo a un WABA.</p>
        <form method="post" action="/create-and-connect">
          <div class="row">
            <div>
              <label>Nombre del Conjunto</label>
              <input type="text" name="dataset_name" placeholder="Mi Dataset" required />
            </div>
            <div>
              <label>Access Token</label>
              <input type="password" name="access_token" value="{{ access_token or '' }}" required />
            </div>
          </div>
          <div class="row">
            <div>
              <label>Business ID</label>
              <input type="text" name="business_id" value="{{ business_id or '' }}" required />
            </div>
            <div>
              <label>Ad Account ID (act_123...)</label>
              <input type="text" name="ad_account_id" value="{{ ad_account_id or '' }}" placeholder="act_1234567890" required />
            </div>
          </div>
          <div class="row">
            <div>
              <label>WABA ID</label>
              <input type="text" name="waba_id" placeholder="XXXXXXXXXXXXXXXX" required />
            </div>
            <div>
              <label>Ad Account a compartir (opcional)</label>
              <input type="text" name="share_ad_account_id" placeholder="act_12345678 (opcional)" />
            </div>
          </div>
          <div class="row">
            <button type="submit">Crear y Conectar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</body>
</html>
"""

def graph_get(url, params, token):
    params = dict(params or {})
    params["access_token"] = token
    r = requests.get(url, params=params, timeout=60)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = {"error": {"message": r.text}}
        e = requests.HTTPError(f"{r.status_code} {r.reason}")
        e.detail = detail
        raise e
    return r.json()

def graph_post(url, payload, token):
    payload = dict(payload or {})
    payload["access_token"] = token
    r = requests.post(url, data=payload, timeout=60)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = {"error": {"message": r.text}}
        e = requests.HTTPError(f"{r.status_code} {r.reason}")
        e.detail = detail
        raise e
    return r.json()

def _extract_id(obj):
    if not obj:
        return None
    if isinstance(obj, dict):
        # If returns an object with id
        if "id" in obj:
            return obj["id"]
        # Or a list under data
        if "data" in obj and isinstance(obj["data"], list) and obj["data"]:
            # Return first id
            if isinstance(obj["data"][0], dict) and "id" in obj["data"][0]:
                return obj["data"][0]["id"]
    return None

app = Flask(__name__)

@app.route("/")
def index():
    access_token = request.args.get("access_token") or os.getenv("ACCESS_TOKEN", "")
    business_id = request.args.get("business_id") or os.getenv("BUSINESS_ID", "")
    ad_account_id = request.args.get("ad_account_id") or os.getenv("AD_ACCOUNT_ID", "")
    return render_template_string(TEMPLATE, title=APP_TITLE, access_token=access_token, business_id=business_id, ad_account_id=ad_account_id)

@app.route("/api/assets")
def api_assets():
    token = request.args.get("access_token")
    biz   = request.args.get("business_id")
    if not token or not biz:
        return jsonify({"error": {"message": "Faltan access_token o business_id"}}), 400
    try:
        base = f"https://graph.facebook.com/v20.0/{biz}"
        pixels = graph_get(base + "/adspixels", {"fields": "id,name", "limit": 200}, token)
        owned = graph_get(base + "/owned_whatsapp_business_accounts", {"fields": "id,name", "limit": 200}, token)
        try:
            client = graph_get(base + "/client_whatsapp_business_accounts", {"fields": "id,name", "limit": 200}, token)
        except requests.HTTPError:
            client = {"data": []}
        datasets = pixels.get("data", [])
        wabas = (owned.get("data", []) or []) + (client.get("data", []) or [])
        return jsonify({"datasets": datasets, "wabas": wabas})
    except requests.HTTPError as e:
        return jsonify(getattr(e, "detail", {"error": {"message": str(e)}})), 400

@app.route("/connect-existing", methods=["POST"])
def connect_existing():
    token = request.form.get("access_token")
    biz   = request.form.get("connect_business_id") or request.form.get("business_id")
    dataset_id = request.form.get("dataset_id")
    waba_id    = request.form.get("waba_id")
    if not all([token, biz, dataset_id, waba_id]):
        return jsonify({"error": {"message": "Faltan campos: access_token, business_id, dataset_id, waba_id"}}), 400

    # 1) Hacer el POST para conectar
    post_error = None
    connected = None
    try:
        connected = graph_post(f"https://graph.facebook.com/v20.0/{waba_id}/dataset", {"dataset_id": dataset_id}, token)
    except requests.HTTPError as e:
        post_error = getattr(e, "detail", {"error": {"message": str(e)}})

    # 2) Verificar leyendo el edge
    try:
        verification = graph_get(f"https://graph.facebook.com/v20.0/{waba_id}/dataset", {"fields": "id,name"}, token)
    except requests.HTTPError as e:
        # Si ni siquiera podemos leer, devolvemos el error del GET
        return jsonify({"ok": False, "error": getattr(e, "detail", {"error": {"message": str(e)}})}), 400

    current_id = _extract_id(verification)
    is_connected = (str(current_id) == str(dataset_id))

    # Mensaje legible
    if is_connected:
        message = f"✅ Conexión verificada: el WABA {waba_id} tiene conectado el dataset {dataset_id}."
    else:
        if post_error:
            message = f"⚠️ No se pudo verificar la conexión. Error al conectar: {post_error.get('error',{}).get('message','(sin detalle)')}"
        else:
            message = "⚠️ No se pudo verificar la conexión. El dataset leído no coincide."

    resp = {
        "ok": is_connected,
        "message": message,
        "connected": connected,
        "verification": verification,
        "waba_id": waba_id,
        "dataset_id": dataset_id,
        "post_error": post_error
    }
    status = 200 if is_connected else 400
    return jsonify(resp), status

@app.route("/create-and-connect", methods=["POST"])
def create_and_connect():
    token = request.form.get("access_token")
    biz   = request.form.get("business_id")
    name  = request.form.get("dataset_name")
    ad_ac = request.form.get("ad_account_id")
    waba_id = request.form.get("waba_id")
    share_ad_ac = request.form.get("share_ad_account_id")

    if not all([token, biz, name, ad_ac, waba_id]):
        return jsonify({"error": {"message": "Faltan campos obligatorios"}}), 400
    try:
        create = graph_post(f"https://graph.facebook.com/v20.0/{ad_ac}/adspixels", {"name": name}, token)
        dataset_id = create.get("id")
        # Conectar recién creado
        connected = graph_post(f"https://graph.facebook.com/v20.0/{waba_id}/dataset", {"dataset_id": dataset_id}, token)
        # Verificar
        verification = graph_get(f"https://graph.facebook.com/v20.0/{waba_id}/dataset", {"fields": "id,name"}, token)
        current_id = _extract_id(verification)
        is_connected = (str(current_id) == str(dataset_id))
        message = "✅ Creado y verificado." if is_connected else "⚠️ Creado pero no verificado."
        return jsonify({
            "ok": is_connected,
            "message": message,
            "created_dataset_id": dataset_id,
            "connect_result": connected,
            "verification": verification
        }), (200 if is_connected else 400)
    except requests.HTTPError as e:
        return jsonify(getattr(e, "detail", {"error": {"message": str(e)}})), 400

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
