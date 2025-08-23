import requests
import json

# --- CONFIGURACIÓN ---
# Reemplaza estos valores con los tuyos
ACCESS_TOKEN = 'TU_TOKEN_DE_ACCESO_AQUI'

# ID del Portafolio Comercial que es dueño de todos los activos
# Lo encuentras en la URL de tu Business Manager: business.facebook.com/settings/?business_id=AQUI_ESTA_EL_ID
BUSINESS_ID = 'TU_ID_DE_PORTAFolio_COMERCIAL_AQUI'

# ID de la cuenta publicitaria que será la PROPIETARIA del conjunto de datos
AD_ACCOUNT_ID = 'act_TU_ID_DE_CUENTA_PUBLICITARIA_AQUI' 

# ID de la cuenta de WhatsApp Business (WABA) que quieres conectar
# Lo encuentras en el Administrador de WhatsApp de tu Business Manager
WABA_ID = 'TU_ID_DE_WABA_AQUI'

# (Opcional) ID de otra cuenta publicitaria con la que quieres COMPARTIR el conjunto de datos
AD_ACCOUNT_ID_TO_SHARE = 'act_ID_DE_LA_OTRA_CUENTA_PUBLICITARIA'

API_VERSION = 'v20.0' # Usa la versión más reciente de la API
BASE_URL = f'https://graph.facebook.com/{API_VERSION}'

def create_dataset_pixel(ad_account_id, dataset_name):
    """
    Crea un nuevo Conjunto de Datos (Píxel) en tu cuenta publicitaria.
    """
    print(f"1. Creando un nuevo Conjunto de Datos llamado '{dataset_name}'...")
    url = f'{BASE_URL}/{ad_account_id}/adspixels'
    params = {'name': dataset_name, 'access_token': ACCESS_TOKEN}
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        dataset_data = response.json()
        dataset_id = dataset_data.get('id')
        
        if dataset_id:
            print(f"   ✅ Conjunto de Datos creado con éxito. ID: {dataset_id}")
            return dataset_id
        else:
            print("   ❌ Error: No se pudo obtener el ID del nuevo conjunto de datos.")
            print("   Respuesta de la API:", json.dumps(dataset_data, indent=2))
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en la llamada a la API para crear el conjunto de datos: {e}")
        if e.response:
            print("   Detalles del error:", json.dumps(e.response.json(), indent=2))
        return None

def share_dataset_with_ad_account(dataset_id, ad_account_to_share):
    """
    Comparte un Conjunto de Datos (Píxel) con otra cuenta publicitaria.
    """
    print(f"\n2. Compartiendo el Conjunto de Datos {dataset_id} con la cuenta {ad_account_to_share}...")
    url = f'{BASE_URL}/{dataset_id}/shared_accounts'
    params = {'account_id': ad_account_to_share, 'access_token': ACCESS_TOKEN}
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        share_data = response.json()
        
        if share_data.get('success'):
            print(f"   ✅ Activo compartido con éxito.")
        else:
            print("   ❌ Ocurrió un problema al compartir el activo.")
            print("   Respuesta de la API:", json.dumps(share_data, indent=2))
        return share_data
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en la llamada a la API para compartir el activo: {e}")
        if e.response:
            print("   Detalles del error:", json.dumps(e.response.json(), indent=2))
        return None

def connect_waba_to_dataset(business_id, dataset_id, waba_id):
    """
    Conecta una Cuenta de WhatsApp Business (WABA) a un Conjunto de Datos (Píxel).
    """
    print(f"\n3. Conectando WABA ({waba_id}) al Conjunto de Datos ({dataset_id})...")
    
    # Este endpoint especial asocia un WABA a un Píxel dentro de un Business Manager
    url = f'{BASE_URL}/{business_id}/whatsapp_business_accounts_to_pixels'
    params = {
        'pixel_id': dataset_id,
        'whatsapp_business_account_id': waba_id,
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        connect_data = response.json()
        
        if connect_data.get('success'):
            print(f"   ✅ WABA conectado con éxito al conjunto de datos.")
        else:
            print("   ❌ Ocurrió un problema al conectar el WABA.")
            print("   Respuesta de la API:", json.dumps(connect_data, indent=2))
        return connect_data
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en la llamada a la API para conectar el WABA: {e}")
        if e.response:
            print("   Detalles del error:", json.dumps(e.response.json(), indent=2))
        return None

if __name__ == '__main__':
    new_dataset_name = "Mi Conjunto de Datos con WABA (API)"
    
    # Paso 1: Crear el conjunto de datos
    dataset_id = create_dataset_pixel(AD_ACCOUNT_ID, new_dataset_name)
    
    if dataset_id:
        # Paso 2 (Opcional): Compartirlo con otra cuenta publicitaria
        if AD_ACCOUNT_ID_TO_SHARE and AD_ACCOUNT_ID_TO_SHARE != 'act_ID_DE_LA_OTRA_CUENTA_PUBLICITARIA':
             share_dataset_with_ad_account(dataset_id, AD_ACCOUNT_ID_TO_SHARE)
        
        # Paso 3: Conectarlo con la cuenta de WhatsApp Business
        if BUSINESS_ID and WABA_ID:
            connect_waba_to_dataset(BUSINESS_ID, dataset_id, WABA_ID)

