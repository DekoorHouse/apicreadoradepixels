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

# --- INICIALIZACIÓN DE LA APLICACIÓN FLASK ---
app = Flask(__name__)

# --- PLANTILLA HTML CON TAILWIND CSS Y JAVASCRIPT ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Activos de Meta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        .tab-active { border-color: #3b82f6; color: #3b82f6; }
        .tab-inactive { border-color: transparent; }
        .log-output { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body class="bg-gray-100 text-gray-800">

    <div class="container mx-auto p-4 md:p-8 max-w-3xl">
        <div class="bg-white rounded-lg shadow-lg">
            <div class="p-6 md:p-8 border-b">
                <div class="flex items-center">
                    <svg class="h-8 w-8 text-blue-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.627 48.627 0 0 1 12 20.904a48.627 48.627 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.57 50.57 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.906 59.906 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5" /></svg>
                    <h1 class="text-2xl font-bold">Gestor de Activos de Meta</h1>
                </div>
            </div>
            
            <!-- Pestañas -->
            <div class="flex border-b">
                <button id="tab-create" class="flex-1 py-4 px-2 text-center font-medium border-b-2 tab-active">Crear Nuevo</button>
                <button id="tab-connect" class="flex-1 py-4 px-2 text-center font-medium border-b-2 tab-inactive">Conectar Existente</button>
            </div>

            <div class="p-6 md:p-8">
                <!-- Contenido Pestaña Crear -->
                <div id="content-create">
                    <form id="form-create">
                        <div class="space-y-4">
                            <p class="text-sm text-gray-600">Crea un nuevo conjunto de datos y conéctalo a un WABA.</p>
                            <div>
                                <label for="create_dataset_name" class="block text-sm font-medium text-gray-700">Nombre del Nuevo Conjunto de Datos</label>
                                <input type="text" id="create_dataset_name" name="dataset_name" class="mt-1 block w-full input-field" value="Mi Conjunto de Datos (App)" required>
                            </div>
                            <div>
                                <label for="create_access_token" class="block text-sm font-medium text-gray-700">Access Token</label>
                                <input type="password" id="create_access_token" name="access_token" class="mt-1 block w-full input-field" required>
                            </div>
                            <div>
                                <label for="create_business_id" class="block text-sm font-medium text-gray-700">Business ID (Portafolio Comercial)</label>
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
                            <button type="submit" class="w-full submit-btn bg-blue-600 hover:bg-blue-700">Crear y Conectar</button>
                        </div>
                    </form>
                </div>

                <!-- Contenido Pestaña Conectar -->
                <div id="content-connect" class="hidden">
                     <form id="form-connect">
                        <div class="space-y-4">
                            <p class="text-sm text-gray-600">Selecciona un conjunto de datos y un WABA existentes para conectarlos.</p>
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
                                    <label for="select_dataset" class="block text-sm font-medium text-gray-700">Seleccionar Conjunto de Datos</label>
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
            </div>
        </div>
    </div>

    <script>
        // Utilidades y Clases CSS
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

        // Lógica de Formularios
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
                logOutput.textContent = result.logs || `Error: ${result.error}\\n${result.details || ''}`;
            } catch (error) {
                logOutput.textContent = `Error de red: ${error.message}`;
            } finally {
                button.disabled = false;
                button.textContent = button.dataset.originalText;
            }
        }
        
        // Formulario CREAR
        const formCreate = document.getElementById('form-create');
        formCreate.querySelector('button[type="submit"]').dataset.originalText = 'Crear y Conectar';
        formCreate.addEventListener('submit', (e) => {
            e.preventDefault();
            handleFormSubmit(formCreate, '/create-new', e.target.querySelector('button[type="submit"]'));
        });

        // Formulario CONECTAR
        const formConnect = document.getElementById('form-connect');
        formConnect.querySelector('button[type="submit"]').dataset.originalText = 'Conectar Activos';
        formConnect.addEventListener('submit', (e) => {
            e.preventDefault();
            handleFormSubmit(formConnect, '/connect-existing', e.target.querySelector('button[type="submit"]'));
        });

        // Botón Cargar Activos
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
                    
                    selectDataset.innerHTML = '<option value="">-- Selecciona un Conjunto de Datos --</option>';
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
"""

# --- LÓGICA DEL BACKEND ---
API_VERSION = 'v20.0'
BASE_URL = f'https://graph.facebook.com/{API_VERSION}'

# --- Funciones de la API ---
def create_dataset_pixel(ad_account_id, dataset_name, access_token, logs):
    logs.append(f"1. Creando Conjunto de Datos '{dataset_name}'...")
    url = f'{BASE_URL}/{ad_account_id}/adspixels'
    params = {'name': dataset_name, 'access_token': access_token}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        dataset_id = data.get('id')
        if dataset_id:
            logs.append(f"   ✅ Éxito. ID del Conjunto de Datos: {dataset_id}")
            return dataset_id
        else:
            logs.append(f"   ❌ Error: No se pudo obtener el ID. Respuesta: {json.dumps(data)}")
            return None
    except requests.exceptions.RequestException as e:
        logs.append(f"   ❌ Error en la API: {e.response.text if e.response else e}")
        return None

def share_dataset_with_ad_account(dataset_id, ad_account_to_share, access_token, logs):
    logs.append(f"\n2. Compartiendo {dataset_id} con la cuenta {ad_account_to_share}...")
    url = f'{BASE_URL}/{dataset_id}/shared_accounts'
    params = {'account_id': ad_account_to_share, 'access_token': access_token}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            logs.append(f"   ✅ Activo compartido con éxito.")
        else:
            logs.append(f"   ❌ Problema al compartir. Respuesta: {json.dumps(data)}")
    except requests.exceptions.RequestException as e:
        logs.append(f"   ❌ Error en la API: {e.response.text if e.response else e}")

def connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs):
    logs.append(f"\nConectando WABA ({waba_id}) al Conjunto de Datos ({dataset_id})...")
    url = f'{BASE_URL}/{business_id}/whatsapp_business_accounts_to_pixels'
    params = {'pixel_id': dataset_id, 'whatsapp_business_account_id': waba_id, 'access_token': access_token}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            logs.append(f"   ✅ WABA conectado con éxito.")
        else:
            logs.append(f"   ❌ Problema al conectar WABA. Respuesta: {json.dumps(data)}")
    except requests.exceptions.RequestException as e:
        logs.append(f"   ❌ Error en la API: {e.response.text if e.response else e}")

# --- RUTAS DE LA APLICACIÓN (ENDPOINTS) ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-assets', methods=['POST'])
def get_assets():
    data = request.json
    access_token = data.get('access_token')
    business_id = data.get('business_id')

    if not all([access_token, business_id]):
        return jsonify({'error': 'Access Token y Business ID son requeridos.'}), 400

    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        # Obtener Conjuntos de Datos (Píxeles)
        pixels_url = f'{BASE_URL}/{business_id}/owned_adspixels?fields=id,name'
        pixels_response = requests.get(pixels_url, headers=headers)
        pixels_response.raise_for_status()
        datasets = pixels_response.json().get('data', [])

        # Obtener WABAs
        wabas_url = f'{BASE_URL}/{business_id}/owned_whatsapp_business_accounts?fields=id,name'
        wabas_response = requests.get(wabas_url, headers=headers)
        wabas_response.raise_for_status()
        wabas = wabas_response.json().get('data', [])
        
        return jsonify({'datasets': datasets, 'wabas': wabas})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Error al contactar la API de Meta.', 'details': e.response.text if e.response else str(e)}), 500

@app.route('/create-new', methods=['POST'])
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

    dataset_id = create_dataset_pixel(ad_account_id, dataset_name, access_token, logs)
    
    if dataset_id:
        if ad_account_to_share:
            share_dataset_with_ad_account(dataset_id, ad_account_to_share, access_token, logs)
        connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs)
        logs.append("\n🎉 Proceso de creación completado.")
    else:
        logs.append("\n❌ El proceso falló. Revisa los logs de arriba.")

    return jsonify({'logs': "\n".join(logs)})

@app.route('/connect-existing', methods=['POST'])
def connect_existing():
    data = request.json
    logs = []
    access_token = data.get('access_token')
    business_id = data.get('connect_business_id')
    dataset_id = data.get('dataset_id')
    waba_id = data.get('waba_id')

    if not all([access_token, business_id, dataset_id, waba_id]):
        return jsonify({'logs': 'Error: Debes seleccionar un conjunto de datos y un WABA.'}), 400
    
    # En la conexión, el paso 1 y 2 no existen, solo el 3.
    connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs)
    logs.append("\n🎉 Proceso de conexión completado.")

    return jsonify({'logs': "\n".join(logs)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
