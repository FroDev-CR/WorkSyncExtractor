# 🔐 Solución al Error de Login

## ❌ El error que tenías:

```
El login falló. Verifica las credenciales en config.py
```

## ✅ Lo que arreglé:

### El problema:
Las credenciales estaban **hardcodeadas** en el archivo `config.py`, lo que significa:
- ❌ Solo funcionaban si las credenciales eran exactamente las del código
- ❌ Si las credenciales cambiaban, había que modificar el código
- ❌ No era flexible para diferentes usuarios
- ❌ No era seguro tener credenciales en el código

### La solución:
Ahora **cada usuario ingresa sus propias credenciales** directamente en la interfaz web:

✅ **Campos de usuario/contraseña en la interfaz**
✅ **Las credenciales NO se guardan permanentemente**
✅ **Funciona para cualquier persona con acceso a SupplyPro**
✅ **No hay que modificar ningún archivo**

## 🎯 Cómo usar la nueva versión:

### 1. Acceder a la app
- Ingresa tu clave de acceso (por defecto: `X30XH3-S9JH34`)

### 2. Ingresar credenciales de SupplyPro
Verás dos campos nuevos:
- **Usuario de SupplyPro**: Tu usuario para acceder a SupplyPro
- **Contraseña de SupplyPro**: Tu contraseña para acceder a SupplyPro

### 3. Seleccionar configuración
- ShineAndBright o Apex

### 4. Exportar órdenes
- Click en "🚀 Exportar órdenes de SupplyPro"

## 🔒 Seguridad

**¿Mis credenciales se guardan?**
- ❌ NO se guardan en ninguna base de datos
- ❌ NO se almacenan en el servidor
- ✅ Solo se usan durante tu sesión actual
- ✅ Si cierras sesión, se eliminan de la memoria

**¿Es seguro ingresar mis credenciales?**
- ✅ Las credenciales se transmiten directamente al sitio de SupplyPro
- ✅ La conexión es a través de HTTPS (encriptada)
- ✅ Streamlit Cloud usa HTTPS por defecto
- ⚠️ Solo úsalo en redes confiables

## 📝 Cambios en los archivos:

### `app.py` - Modificado:
- ✅ Añadidos campos de entrada para usuario/contraseña
- ✅ Eliminada dependencia de credenciales hardcodeadas
- ✅ Las credenciales se guardan en `session_state` (temporal)
- ✅ Se borran al cerrar sesión

### `config.py` - YA NO SE USA para credenciales:
- El archivo sigue existiendo pero las credenciales ya no se usan
- Solo contiene las reglas de transformación de datos

## 🚀 Actualizar la app:

```bash
# Windows
actualizar_repo.bat

# Mac/Linux
./actualizar_repo.sh

# Manual
git add .
git commit -m "Fix: Permitir credenciales personalizadas por usuario"
git push
```

Espera 2-3 minutos para que Streamlit Cloud redesplegue.

## 🎨 Así se ve ahora:

```
📦 SupplyPro Extractor
========================

⚪ ShineAndBright  ⚪ Apex

---

🔑 Credenciales de SupplyPro

[Usuario de SupplyPro]    [Contraseña de SupplyPro]
   (tu_usuario)               (••••••••••)

---

[🚀 Exportar órdenes de SupplyPro]
```

## 💡 Ventajas de este cambio:

✅ **Cualquier persona puede usarlo** - Solo necesita sus credenciales de SupplyPro
✅ **No hay que modificar código** - Todo desde la interfaz
✅ **Más seguro** - No hay credenciales en el código fuente
✅ **Flexible** - Cada usuario usa sus propias credenciales
✅ **Fácil de usar** - Interfaz intuitiva

## ❓ Preguntas Frecuentes

**P: ¿Dónde consigo mis credenciales de SupplyPro?**
R: Son las mismas que usas para acceder a [SupplyPro](https://www.hyphensolutions.com/MH2Supply/Login.asp)

**P: ¿Qué pasa si ingreso credenciales incorrectas?**
R: Verás un error: "El login falló. Verifica las credenciales"

**P: ¿Las credenciales se guardan entre sesiones?**
R: Durante la sesión sí (mientras no cierres el navegador). Si cierras sesión o recargas la página, deberás ingresarlas nuevamente.

**P: ¿Puedo usar diferentes credenciales para ShineAndBright y Apex?**
R: Sí, solo cambia las credenciales antes de hacer la extracción.

**P: ¿Qué es la "clave de acceso"?**
R: Es una clave para acceder a la aplicación (no confundir con las credenciales de SupplyPro). Por defecto es `X30XH3-S9JH34`.

## 🐛 Si sigue sin funcionar:

1. **Verifica que las credenciales sean correctas**:
   - Prueba iniciar sesión manualmente en SupplyPro
   - Asegúrate de que no haya espacios extra

2. **Verifica que SupplyPro esté accesible**:
   - Abre [SupplyPro](https://www.hyphensolutions.com/MH2Supply/Login.asp) en tu navegador
   - Confirma que puedes acceder

3. **Revisa el error específico**:
   - Si dice "element is not visible": Puede ser un problema de red o timeout
   - Si dice "Error de autenticación": Las credenciales están mal
   - Si dice "No se encontró la tabla": Puede que no haya órdenes

---

**Desarrollado por FroDev**
