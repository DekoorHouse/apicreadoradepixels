# --- IMPORTANTE PARA EL DESPLIEGUE ---
# Guarda este archivo con el nombre `app.py`.
# El comando de inicio de Render (`gunicorn app:app`) busca un archivo llamado `app.py`
# y dentro de él, una variable llamada `app`. Si el nombre del archivo es diferente,
# el despliegue fallará con un error "AppImportError".
# -----------------------------------------

from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
import time
from functools import wraps

# --- INICIALIZACIÓN DE LA APLICACIÓN FLASK ---
app = Flask(__name__)

# --- CONFIGURACIÓN ACTUALIZADA ---
API_VERSION = 'v22.0'  # ✅ Versión actualizada
BASE_URL = f'https://graph.facebook.com/{API_VERSION}'

# Rate limiting simple
REQUEST_COUNTS = {}

def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            if client_ip not in REQUEST_COUNTS:
                REQUEST_COUNTS[client_ip] = []
            
            # Limpiar requests antiguos
            REQUEST_COUNTS[client_ip] = [
                req_time for req_time in REQUEST_COUNTS[client_ip] 
                if current_time - req_time < window
            ]
            
            if len(REQUEST_COUNTS[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
            
            REQUEST_COUNTS[client_ip].append(current_time)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# --- PLANTILLA HTML (sin cambios, ya está bien) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Activos de Meta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .tab-active {{ border-color: #3b82f6; color: #3b82f6; }}
        .tab-inactive {{ border-color: transparent; }}
        .log-output {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body class="bg-gray-100 text-gray-800">

    <div class="container mx-auto p-4 md:p-8 max-w-3xl">
        <div class="bg-white rounded-lg shadow-lg">
            <div class="p-6 md:p-8 border-b">
                <div class="flex items-center">
                    <svg class="h-8 w-8 text-blue-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.627 48.627 0 0 1 12 20.904a48.627 48.627 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.57 50.57 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.906 59.906 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5" /></svg>
                    <h1 class="text-2xl font-bold">Gestor de Datasets de Meta</h1>
                </div>
                <p class="text-sm text-gray-600 mt-2">API Version: {api_version} | Los píxeles ahora se llaman Datasets</p>
            </div>
            
            <!-- Pestañas -->
            <div class="flex border-b">
                <button id="tab-create" class="flex-1 py-4 px-2 text-center font-medium border-b-2 tab-active">Crear Nuevo Dataset</button>
                <button id="tab-connect" class="flex-1 py-4 px-2 text-center font-medium border-b-2 tab-inactive">Conectar Existente</button>
            </div>

            <div class="p-6 md:p-8">
                <!-- Contenido Pestaña Crear -->
                <div id="content-create">
                    <form id="form-create">
                        <div class="space-y-4">
                            <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                                <p class="text-sm text-blue-800">
                                    ℹ️ <strong>Dataset (antes Píxel):</strong> Crea un nuevo conjunto de datos unificado para web, app y eventos offline.
                                </p>
                            </div>
                            <div>
                                <label for="create_dataset_name" class="block text-sm font-medium text-gray-700">Nombre del Nuevo Dataset</label>
                                <input type="text" id="create_dataset_name" name="dataset_name" class="mt-1 block w-full input-field" value="Mi Dataset (App)" required>
                            </div>
                            <div>
                                <label for="create_access_token" class="block text-sm font-medium text-gray-700">Access Token</label>
                                <input type="password" id="create_access_token" name="access_token" class="mt-1 block w-full input-field" required>
                            </div>
                            <div>
                                <label for="create_business_id" class="block text-sm font-medium text-gray-700">Business ID (Portfolio Comercial)</label>
                                <input type="text" id="create_business_id" name="business_id" class="mt-1 block w-full input-field" required>
                            </div>
                            <div>
                                <label for="create_ad_account_id" class="block text-sm font-medium text-gray-700">Ad Account ID (Propietaria)</label>
                                <input type="text" id="create_ad_account_id" name="ad_account_id" class="mt-1 block w-full input-field" placeholder="act_123456789" required>
                            </div>
                            <div>
                                <label for="create_waba_id" class="block text-sm font-medium text-gray-700">WABA ID a Conectar</label>
                                <input type="text" id="create_waba_id" name="waba_id" class="mt-1 block w-full input-field" required>
                            </div>
                            <div>
                                <label for="create_ad_account_id_to_share" class="block text-sm font-medium text-gray-700">Ad Account ID a Compartir (Opcional)</label>
                                <input type="text" id="create_ad_account_id_to_share" name="ad_account_id_to_share" class="mt-1 block w-full input-field" placeholder="act_987654321">
                            </div>
                        </div>
                        <div class="mt-6">
                            <button type="submit" class="w-full submit-btn bg-blue-600 hover:bg-blue-700">Crear Dataset y Conectar</button>
                        </div>
                    </form>
                </div>

                <!-- Contenido Pestaña Conectar -->
                <div id="content-connect" class="hidden">
                     <form id="form-connect">
                        <div class="space-y-4">
                            <div class="bg-green-50 border border-green-200 rounded-md p-3">
                                <p class="text-sm text-green-800">
                                    ✅ Conecta un Dataset existente con un WABA para tracking unificado.
                                </p>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label for="connect_access_token" class="block text-sm font-medium text-gray-700">Access Token</label>
                                    <input type="password" id="connect_access_token" class="mt-1 block w-full input-field" required>
                                </div>
                                <div>
                                    <label for="connect_business_id" class="block text-sm font-medium text-gray-700">Business ID</label>
                                    <input type="text" id="connect_business_id" class="mt-1 block w-full input-field" required>
                                </div>
                            </div>
                            <button type="button" id="load-assets-btn" class="w-full submit-btn bg-gray-600 hover:bg-gray-700 mt-2">Cargar Activos Existentes</button>
                            
                            <div id="selectors" class="hidden space-y-4 pt-4">
                                <div>
                                    <label for="select_dataset" class="block text-sm font-medium text-gray-700">Seleccionar Dataset</label>
                                    <select id="select_dataset" name="dataset_id" class="mt-1 block w-full input-field" required></select>
                                </div>
                                <div>
                                    <label for="select_waba" class="block text-sm font-medium text-gray-700">Seleccionar WABA</label>
                                    <select id="select_waba" name="waba_id" class="mt-1 block w-full input-field" required></select>
                                </div>
                                <div class="mt-6">
                                    <button type="submit" class="w-full submit-btn bg-blue-600 hover:bg-blue-700">Conectar Activos</button>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Resultados -->
            <div id="results" class="p-6 md:p-8 border-t hidden">
                <h2 class="text-lg font-semibold mb-2">Resultados:</h2>
                <div class="bg-gray-900 text-white font-mono text-sm rounded-md p-4 max-h-96 overflow-y-auto">
                    <pre id="log-output" class="log-output"></pre>
                </div>
                <div class="mt-4 text-xs text-gray-500">
                    <p>💡 <strong>Tip:</strong> Los Datasets permiten tracking unificado de web, app y eventos offline en un solo ID.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Mismo JavaScript que antes, sin cambios
        const INPUT_FIELD_CLASSES = "px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500";
        const SUBMIT_BTN_CLASSES = "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500";
        document.querySelectorAll('.input-field').forEach(el => el.className += ' ' + INPUT_FIELD_CLASSES);
        document.querySelectorAll('.submit-btn').forEach(el => el.className += ' ' + SUBMIT_BTN_CLASSES);
        
        // Lógica de Pestañas
        const tabCreate = document.getElementById('tab-create');
        const tabConnect = document.getElementById('tab-connect');
        const contentCreate = document.getElementById('content-create');
        const contentConnect = document.getElementById('content-connect');

        function switchTab(activeTab) {
            [tabCreate, tabConnect].forEach(tab => tab.classList.remove('tab-active', 'tab-inactive'));
            if (activeTab === 'create') {
                tabCreate.classList.add('tab-active');
                tabConnect.classList.add('tab-inactive');
                contentCreate.classList.remove('hidden');
                contentConnect.classList.add('hidden');
            } else {
                tabConnect.classList.add('tab-active');
                tabCreate.classList.add('tab-inactive');
                contentConnect.classList.remove('hidden');
                contentCreate.classList.add('hidden');
            }
            document.getElementById('results').classList.add('hidden');
        }
        tabCreate.addEventListener('click', () => switchTab('create'));
        tabConnect.addEventListener('click', () => switchTab('connect'));

        // Resto del JavaScript igual...
        const resultsDiv = document.getElementById('results');
        const logOutput = document.getElementById('log-output');

        async function handleFormSubmit(form, endpoint, button) {
            button.disabled = true;
            button.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Procesando...';
            resultsDiv.classList.remove('hidden');
            logOutput.textContent = 'Iniciando proceso...';

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (response.status === 429) {
                    logOutput.textContent = 'Error: Rate limit excedido. Intenta de nuevo en unos minutos.';
                } else {
                    logOutput.textContent = result.logs || `Error: ${result.error}\\n${result.details || ''}`;
                }
            } catch (error) {
                logOutput.textContent = `Error de red: ${error.message}`;
            } finally {
                button.disabled = false;
                button.textContent = button.dataset.originalText;
            }
        }
        
        // Formularios (mismo código)
        const formCreate = document.getElementById('form-create');
        formCreate.querySelector('button[type="submit"]').dataset.originalText = 'Crear Dataset y Conectar';
        formCreate.addEventListener('submit', (e) => {
            e.preventDefault();
            handleFormSubmit(formCreate, '/create-new', e.target.querySelector('button[type="submit"]'));
        });

        const formConnect = document.getElementById('form-connect');
        formConnect.querySelector('button[type="submit"]').dataset.originalText = 'Conectar Activos';
        formConnect.addEventListener('submit', (e) => {
            e.preventDefault();
            handleFormSubmit(formConnect, '/connect-existing', e.target.querySelector('button[type="submit"]'));
        });

        // Botón Cargar Activos (mismo código)
        const loadAssetsBtn = document.getElementById('load-assets-btn');
        const selectorsDiv = document.getElementById('selectors');
        const selectDataset = document.getElementById('select_dataset');
        const selectWaba = document.getElementById('select_waba');

        loadAssetsBtn.addEventListener('click', async () => {
            const token = document.getElementById('connect_access_token').value;
            const businessId = document.getElementById('connect_business_id').value;
            if (!token || !businessId) {
                alert('Por favor, ingresa el Access Token y el Business ID para cargar los activos.');
                return;
            }
            
            loadAssetsBtn.disabled = true;
            loadAssetsBtn.textContent = 'Cargando...';
            resultsDiv.classList.remove('hidden');
            logOutput.textContent = 'Cargando activos desde la API de Meta...';

            try {
                const response = await fetch('/get-assets', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token, business_id: businessId })
                });
                const result = await response.json();

                if (response.ok) {
                    logOutput.textContent = 'Activos cargados con éxito. Por favor, selecciona desde los menús desplegables.';
                    
                    selectDataset.innerHTML = '<option value="">-- Selecciona un Dataset --</option>';
                    result.datasets.forEach(d => selectDataset.innerHTML += `<option value="${d.id}">${d.name} (ID: ${d.id})</option>`);
                    
                    selectWaba.innerHTML = '<option value="">-- Selecciona un WABA --</option>';
                    result.wabas.forEach(w => selectWaba.innerHTML += `<option value="${w.id}">${w.name} (ID: ${w.id})</option>`);
                    
                    selectorsDiv.classList.remove('hidden');
                } else {
                    logOutput.textContent = `Error al cargar activos: ${result.error}\\n${result.details || ''}`;
                }
            } catch (error) {
                logOutput.textContent = `Error de red: ${error.message}`;
            } finally {
                loadAssetsBtn.disabled = false;
                loadAssetsBtn.textContent = 'Cargar Activos Existentes';
            }
        });
    </script>
</body>
</html>
""".format(api_version=API_VERSION)

# --- FUNCIONES DE LA API MEJORADAS ---
def validate_token_and_permissions(access_token, logs):
    """Valida el token y permisos básicos"""
    url = f'{BASE_URL}/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            logs.append("✅ Token validado correctamente")
            return True
        else:
            logs.append(f"❌ Token inválido: {response.status_code}")
            return False
    except Exception as e:
        logs.append(f"❌ Error validando token: {str(e)}")
        return False

def create_dataset_pixel(ad_account_id, dataset_name, access_token, logs):
    """Crea un nuevo dataset (antes píxel)"""
    logs.append(f"1. Creando Dataset '{dataset_name}'...")
    
    # Validar token primero
    if not validate_token_and_permissions(access_token, logs):
        return None
    
    url = f'{BASE_URL}/{ad_account_id}/adspixels'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'name': dataset_name}
    
    try:
        response = requests.post(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        dataset_id = data.get('id')
        if dataset_id:
            logs.append(f"   ✅ Éxito. ID del Dataset: {dataset_id}")
            logs.append(f"   ℹ️  Este ID ahora funciona como Dataset unificado")
            return dataset_id
        else:
            logs.append(f"   ❌ Error: No se pudo obtener el ID. Respuesta: {json.dumps(data)}")
            return None
    except requests.exceptions.RequestException as e:
        error_detail = e.response.text if hasattr(e, 'response') and e.response else str(e)
        logs.append(f"   ❌ Error en la API: {error_detail}")
        return None

def share_dataset_with_ad_account(dataset_id, ad_account_to_share, access_token, logs):
    """Comparte dataset con otra cuenta publicitaria"""
    logs.append(f"\n2. Compartiendo Dataset {dataset_id} con la cuenta {ad_account_to_share}...")
    url = f'{BASE_URL}/{dataset_id}/shared_accounts'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'account_id': ad_account_to_share}
    
    try:
        response = requests.post(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            logs.append(f"   ✅ Dataset compartido con éxito.")
        else:
            logs.append(f"   ⚠️  Respuesta inesperada: {json.dumps(data)}")
    except requests.exceptions.RequestException as e:
        error_detail = e.response.text if hasattr(e, 'response') and e.response else str(e)
        logs.append(f"   ❌ Error en la API: {error_detail}")

def connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs):
    """Conecta WABA al dataset - ENDPOINT CRÍTICO QUE PUEDE HABER CAMBIADO"""
    logs.append(f"\n3. Conectando WABA ({waba_id}) al Dataset ({dataset_id})...")
    
    # Endpoint actual - puede necesitar verificación
    endpoint_v1 = f'{BASE_URL}/{business_id}/whatsapp_business_accounts_to_pixels'
    # Posibles endpoints alternativos
    endpoint_v2 = f'{BASE_URL}/{business_id}/whatsapp_business_accounts/{waba_id}/data_sources'
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'pixel_id': dataset_id, 'whatsapp_business_account_id': waba_id}
    
    # Intentar con el endpoint original primero
    try:
        logs.append("   🔄 Intentando conexión con endpoint principal...")
        response = requests.post(endpoint_v1, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            logs.append(f"   ✅ WABA conectado al Dataset con éxito.")
            logs.append(f"   📊 Ahora puedes usar el Dataset ID {dataset_id} para tracking unificado")
            return True
        else:
            logs.append(f"   ⚠️  Respuesta inesperada: {json.dumps(data)}")
            return False
            
    except requests.exceptions.RequestException as e:
        error_detail = e.response.text if hasattr(e, 'response') and e.response else str(e)
        logs.append(f"   ❌ Error con endpoint principal: {error_detail}")
        
        # Si hay error 404 o similar, el endpoint puede haber cambiado
        if hasattr(e, 'response') and e.response and e.response.status_code == 404:
            logs.append("   ⚠️  ADVERTENCIA: El endpoint puede haber cambiado en la nueva versión de la API")
            logs.append("   💡 Recomendación: Verificar documentación oficial de Meta para el endpoint actualizado")
        
        return False

# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-assets', methods=['POST'])
@rate_limit(max_requests=5, window=60)  # ✅ Rate limiting añadido
def get_assets():
    data = request.json
    access_token = data.get('access_token')
    business_id = data.get('business_id')

    if not all([access_token, business_id]):
        return jsonify({'error': 'Access Token y Business ID son requeridos.'}), 400

    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        # Obtener Datasets (Píxeles)
        pixels_url = f'{BASE_URL}/{business_id}/owned_adspixels?fields=id,name'
        pixels_response = requests.get(pixels_url, headers=headers, timeout=15)
        pixels_response.raise_for_status()
        datasets = pixels_response.json().get('data', [])

        # Obtener WABAs
        wabas_url = f'{BASE_URL}/{business_id}/owned_whatsapp_business_accounts?fields=id,name'
        wabas_response = requests.get(wabas_url, headers=headers, timeout=15)
        wabas_response.raise_for_status()
        wabas = wabas_response.json().get('data', [])
        
        return jsonify({'datasets': datasets, 'wabas': wabas})

    except requests.exceptions.RequestException as e:
        error_detail = e.response.text if hasattr(e, 'response') and e.response else str(e)
        return jsonify({'error': 'Error al contactar la API de Meta.', 'details': error_detail}), 500

@app.route('/create-new', methods=['POST'])
@rate_limit(max_requests=3, window=300)  # ✅ Rate limiting más restrictivo para creación
def create_new_and_connect():
    data = request.json
    logs = []
    access_token = data.get('access_token')
    business_id = data.get('business_id')
    ad_account_id = data.get('ad_account_id')
    waba_id = data.get('waba_id')
    dataset_name = data.get('dataset_name')
    ad_account_to_share = data.get('ad_account_id_to_share')

    if not all([access_token, business_id, ad_account_id, waba_id, dataset_name]):
        return jsonify({'logs': 'Error: Faltan campos requeridos.'}), 400

    logs.append(f"🚀 Iniciando creación de Dataset con API {API_VERSION}")
    
    dataset_id = create_dataset_pixel(ad_account_id, dataset_name, access_token, logs)
    
    if dataset_id:
        if ad_account_to_share:
            share_dataset_with_ad_account(dataset_id, ad_account_to_share, access_token, logs)
        
        # Conexión WABA - parte crítica
        success = connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs)
        
        if success:
            logs.append("\n🎉 Proceso de creación completado exitosamente.")
            logs.append("📋 Resumen:")
            logs.append(f"   • Dataset ID: {dataset_id}")
            logs.append(f"   • WABA conectado: {waba_id}")
            logs.append(f"   • API Version: {API_VERSION}")
        else:
            logs.append("\n⚠️  Dataset creado pero la conexión WABA falló.")
            logs.append("💡 Puedes intentar conectar manualmente desde Meta Events Manager.")
    else:
        logs.append("\n❌ El proceso falló. Revisa los logs de arriba.")

    return jsonify({'logs': "\n".join(logs)})

@app.route('/connect-existing', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def connect_existing():
    data = request.json
    logs = []
    access_token = data.get('access_token')
    business_id = data.get('connect_business_id')
    dataset_id = data.get('dataset_id')
    waba_id = data.get('waba_id')

    if not all([access_token, business_id, dataset_id, waba_id]):
        return jsonify({'logs': 'Error: Debes seleccionar un dataset y un WABA.'}), 400
    
    logs.append(f"🔗 Conectando activos existentes con API {API_VERSION}")
    success = connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs)
    
    if success:
        logs.append("\n🎉 Proceso de conexión completado exitosamente.")
    else:
        logs.append("\n⚠️  La conexión falló. Verifica logs arriba.")

    return jsonify({'logs': "\n".join(logs)})

# ✅ Manejo de errores global
@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': 60}), 429

@app.errorhandler(500)
def server_error_handler(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
