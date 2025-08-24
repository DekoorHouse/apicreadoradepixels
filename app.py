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
# Todo el frontend está dentro de esta plantilla.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creador de Activos de Meta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        .log-output { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body class="bg-gray-100 text-gray-800">

    <div class="container mx-auto p-4 md:p-8 max-w-2xl">
        <div class="bg-white rounded-lg shadow-lg p-6 md:p-8">
            <div class="flex items-center mb-6">
                <svg class="h-8 w-8 text-blue-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.627 48.627 0 0 1 12 20.904a48.627 48.627 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.57 50.57 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.906 59.906 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5" />
                </svg>
                <h1 class="text-2xl font-bold">Creador de Activos de Meta</h1>
            </div>

            <form id="asset-form">
                <div class="space-y-4">
                    <div>
                        <label for="dataset_name" class="block text-sm font-medium text-gray-700">Nombre del Conjunto de Datos</label>
                        <input type="text" id="dataset_name" name="dataset_name" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" value="Mi Conjunto de Datos (App)" required>
                    </div>
                    <div>
                        <label for="access_token" class="block text-sm font-medium text-gray-700">Access Token</label>
                        <input type="password" id="access_token" name="access_token" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" required>
                    </div>
                    <div>
                        <label for="business_id" class="block text-sm font-medium text-gray-700">Business ID (Portafolio Comercial)</label>
                        <input type="text" id="business_id" name="business_id" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" required>
                    </div>
                    <div>
                        <label for="ad_account_id" class="block text-sm font-medium text-gray-700">Ad Account ID (Propietaria)</label>
                        <input type="text" id="ad_account_id" name="ad_account_id" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="act_123456789" required>
                    </div>
                    <div>
                        <label for="waba_id" class="block text-sm font-medium text-gray-700">WABA ID</label>
                        <input type="text" id="waba_id" name="waba_id" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" required>
                    </div>
                    <div>
                        <label for="ad_account_id_to_share" class="block text-sm font-medium text-gray-700">Ad Account ID a Compartir (Opcional)</label>
                        <input type="text" id="ad_account_id_to_share" name="ad_account_id_to_share" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="act_987654321">
                    </div>
                </div>

                <div class="mt-6">
                    <button type="submit" id="submit-btn" class="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        Crear Activos
                    </button>
                </div>
            </form>

            <div id="results" class="mt-6 hidden">
                <h2 class="text-lg font-semibold mb-2">Resultados:</h2>
                <div class="bg-gray-900 text-white font-mono text-sm rounded-md p-4 max-h-96 overflow-y-auto">
                    <pre id="log-output" class="log-output"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('asset-form');
        const submitBtn = document.getElementById('submit-btn');
        const resultsDiv = document.getElementById('results');
        const logOutput = document.getElementById('log-output');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Procesando...';
            resultsDiv.classList.remove('hidden');
            logOutput.textContent = 'Iniciando proceso...';

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/create-assets', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    logOutput.textContent = result.logs;
                } else {
                    logOutput.textContent = `Error del servidor: ${result.error}\\n\\nDetalles:\\n${result.logs}`;
                }

            } catch (error) {
                logOutput.textContent = `Error de red o de conexión: ${error.message}`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Crear Activos';
            }
        });
    </script>

</body>
</html>
"""

# --- LÓGICA DEL BACKEND ---
API_VERSION = 'v20.0'
BASE_URL = f'https://graph.facebook.com/{API_VERSION}'

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
    logs.append(f"\n3. Conectando WABA ({waba_id}) al Conjunto de Datos ({dataset_id})...")
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

# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/create-assets', methods=['POST'])
def create_assets():
    data = request.json
    logs = []
    
    # Extraer datos del formulario
    access_token = data.get('access_token')
    business_id = data.get('business_id')
    ad_account_id = data.get('ad_account_id')
    waba_id = data.get('waba_id')
    dataset_name = data.get('dataset_name')
    ad_account_to_share = data.get('ad_account_id_to_share')

    if not all([access_token, business_id, ad_account_id, waba_id, dataset_name]):
        return jsonify({'error': 'Faltan campos requeridos.', 'logs': 'Por favor, completa todos los campos obligatorios.'}), 400

    # Ejecutar el flujo
    dataset_id = create_dataset_pixel(ad_account_id, dataset_name, access_token, logs)
    
    if dataset_id:
        if ad_account_to_share:
            share_dataset_with_ad_account(dataset_id, ad_account_to_share, access_token, logs)
        
        connect_waba_to_dataset(business_id, dataset_id, waba_id, access_token, logs)
        logs.append("\n🎉 Proceso completado.")
    else:
        logs.append("\n❌ El proceso falló en el primer paso. No se continuó.")

    return jsonify({'logs': "\n".join(logs)})

if __name__ == '__main__':
    # Usar el puerto que Render asigne, o 5000 para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
