# ✅ Qué necesitas hacer de tu parte

## 1. Probar localmente (5 minutos)

```bash
# Instalar dependencias
pip install -r requirements.txt
playwright install chromium

# Ejecutar la app
streamlit run app.py
```

Abre tu navegador en `http://localhost:8501` y usa la clave: `X30XH3-S9JH34`

## 2. Deploy online (10 minutos) - OPCIÓN RECOMENDADA

### A. Crear cuenta en GitHub (si no tienes)
- Ve a [github.com](https://github.com) y créate una cuenta gratuita

### B. Subir el código
1. Crea un nuevo repositorio (puede ser privado)
2. Sube todos los archivos de esta carpeta (excepto Python/ si quieres)

**Método fácil con GitHub Desktop:**
- Descarga GitHub Desktop
- Arrastra esta carpeta
- Haz commit y push

**Método con comandos:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### C. Deploy en Streamlit Cloud (GRATIS)

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Sign in con tu cuenta de GitHub
3. Click en "New app"
4. Selecciona tu repositorio
5. Main file: `app.py`
6. Click en "Advanced settings" → "Secrets"
7. Pega esto:
```toml
license_keys = ["X30XH3-S9JH34", "TU-LLAVE-2"]
```
8. Click "Deploy"

**¡Listo!** Tu app estará online en 2-3 minutos

## 3. Personalizar (opcional)

### Cambiar las claves de acceso
Edita `.streamlit/secrets.toml`:
```toml
license_keys = ["TU_NUEVA_CLAVE_1", "TU_NUEVA_CLAVE_2"]
```

### Cambiar credenciales de SupplyPro
Edita `config.py` líneas 37-40

### Cambiar colores
Edita `.streamlit/config.toml`

## 🎉 Resultado final

Tu app web estará accesible desde:
- 📱 Tu celular
- 💻 Tu laptop
- 🖥️ Cualquier computadora
- 🌍 Desde cualquier lugar con internet

**URL ejemplo:** `https://tu-app.streamlit.app`

## ❓ Si tienes problemas

**La app no inicia localmente:**
- Asegúrate de tener Python 3.9 o superior
- Ejecuta `pip install -r requirements.txt` de nuevo

**Error al hacer deploy:**
- Verifica que todos los archivos estén en el repo
- Revisa que `requirements.txt` y `packages.txt` estén presentes
- En Streamlit Cloud, revisa los logs de deploy

**La extracción no funciona:**
- Verifica las credenciales en `config.py`
- Prueba manualmente en SupplyPro que las credenciales funcionen

## 📞 ¿Necesitas ayuda?

Revisa el README.md completo o contacta con FroDev.
