# 📦 SupplyPro Extractor - Versión Web

Aplicación web para extraer y procesar órdenes de SupplyPro automáticamente.

## 🚀 Características

- ✅ Extracción automatizada de órdenes de SupplyPro
- ✅ Procesamiento y transformación según reglas de negocio
- ✅ Interfaz web accesible desde cualquier dispositivo
- ✅ Exportación a CSV y Excel
- ✅ Autenticación simple con clave de acceso
- ✅ Deploy gratuito en la nube

## 📋 Requisitos locales

```bash
Python 3.9+
```

## 🔧 Instalación local

1. Clonar el repositorio o descargar los archivos

2. Instalar dependencias:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Configurar secrets:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Editar secrets.toml con tus claves de acceso
```

4. Ejecutar la aplicación:
```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## ☁️ Deploy en la nube (GRATIS)

### Opción 1: Streamlit Cloud (Recomendado)

**Pasos:**

1. Sube tu código a GitHub (privado o público)

2. Ve a [share.streamlit.io](https://share.streamlit.io)

3. Conecta tu cuenta de GitHub

4. Selecciona el repositorio y la rama

5. Configura los secrets:
   - En el panel de configuración, agrega:
   ```toml
   license_keys = ["X30XH3-S9JH34", "TU-LLAVE-2"]
   ```

6. Click en "Deploy"

**Ventajas:**
- Completamente gratis
- Setup super rápido (5 minutos)
- Actualización automática al hacer push

**Limitaciones:**
- 1 GB de RAM
- Puede dormirse después de 7 días sin uso

### Opción 2: Railway.app

**Pasos:**

1. Sube tu código a GitHub

2. Ve a [railway.app](https://railway.app) y crea una cuenta

3. Click en "New Project" → "Deploy from GitHub repo"

4. Selecciona tu repositorio

5. Railway detectará automáticamente que es una app Streamlit

6. Configura las variables de entorno:
   - En Settings → Variables, agrega:
   ```
   LICENSE_KEYS=["X30XH3-S9JH34", "TU-LLAVE-2"]
   ```

7. Deploy automático

**Ventajas:**
- $5 de crédito gratis al mes
- Mejor rendimiento
- No se duerme

**Limitaciones:**
- Después de los $5 gratis, se cobra por uso

### Opción 3: Render

1. Sube tu código a GitHub

2. Ve a [render.com](https://render.com)

3. Click en "New +" → "Web Service"

4. Conecta tu repositorio

5. Configura:
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

6. Agrega secrets en "Environment"

**Ventajas:**
- Plan gratuito disponible
- Buena estabilidad

**Limitaciones:**
- Se duerme después de 15 min de inactividad (tarda ~30s en despertar)

## 📝 Configuración

### Credenciales de SupplyPro

Las credenciales están en `config.py`. Si necesitas cambiarlas:

```python
CREDENTIALS = {
    'ShineAndBright': {
        'username': 'TU_USUARIO',
        'password': 'TU_PASSWORD'
    },
    'Apex': {
        'username': 'TU_USUARIO',
        'password': 'TU_PASSWORD'
    }
}
```

### Claves de acceso

Puedes agregar o modificar las claves de acceso en `.streamlit/secrets.toml`:

```toml
license_keys = ["CLAVE1", "CLAVE2", "CLAVE3"]
```

## 🏗️ Estructura del proyecto

```
extractor/
├── app.py                  # Aplicación principal Streamlit
├── config.py              # Configuración y credenciales
├── requirements.txt       # Dependencias Python
├── packages.txt          # Dependencias del sistema
├── .streamlit/
│   ├── config.toml       # Configuración de Streamlit
│   └── secrets.toml      # Claves de acceso (no subir a Git)
├── utils/
│   ├── scraper.py        # Lógica de extracción con Playwright
│   └── transformer.py    # Lógica de transformación
└── Python/
    └── SupplyProExtractor.py  # Versión original (desktop)
```

## 🎯 Uso

1. Accede a la aplicación web
2. Ingresa tu clave de acceso
3. Selecciona la configuración (ShineAndBright o Apex)
4. Click en "Exportar órdenes de SupplyPro"
5. Espera a que se procesen las órdenes
6. Descarga el archivo CSV o Excel

## 🔒 Seguridad

- Las credenciales de SupplyPro están en el código (considera usar variables de entorno)
- Las claves de acceso se manejan vía `secrets.toml`
- La autenticación es simple pero efectiva para uso interno
- Para producción, considera implementar un sistema de auth más robusto

## 🐛 Troubleshooting

**Error: "No module named playwright"**
```bash
pip install playwright
playwright install chromium
```

**Error en deploy: "Browser not found"**
- Asegúrate de tener `packages.txt` con `chromium` y `chromium-driver`
- En Railway/Render, agrega el buildpack de Chromium

**La app se queda en "Connecting to SupplyPro..."**
- Verifica que las credenciales sean correctas en `config.py`
- Revisa que SupplyPro esté accesible
- Aumenta los timeouts en `utils/scraper.py` si la red es lenta

## 📞 Soporte

Desarrollado por **FroDev**

## 📄 Licencia

Uso interno - Todos los derechos reservados
