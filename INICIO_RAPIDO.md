# 🚀 Inicio Rápido - SupplyPro Extractor Web

## Paso 1: Instalar dependencias

Abre tu terminal en esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
```

Luego instala Chromium para Playwright:

```bash
playwright install chromium
```

## Paso 2: Probar la aplicación localmente

Ejecuta:

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`

**Clave de acceso por defecto:** `X30XH3-S9JH34`

## Paso 3: Usar la aplicación

1. Ingresa la clave de acceso
2. Selecciona ShineAndBright o Apex
3. Click en "Exportar órdenes de SupplyPro"
4. Descarga el CSV o Excel generado

## 🌐 Deploy en la nube

Para tener tu app online 24/7:

### Opción más fácil: Streamlit Cloud (100% gratis)

1. Sube este código a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo
4. En Settings → Secrets, pega:
```toml
license_keys = ["X30XH3-S9JH34", "TU-LLAVE-2"]
```
5. Deploy!

**Tu app estará online en 5 minutos** ✅

Lee el README.md completo para más opciones de deploy.
