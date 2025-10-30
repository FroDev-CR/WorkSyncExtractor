# ⚠️ ACTUALIZACIÓN IMPORTANTE - Credenciales Personalizadas

## 🎯 Cambio Principal

**Ahora cada usuario ingresa sus propias credenciales de SupplyPro** directamente en la interfaz web.

## ✅ Por qué este cambio:

1. ❌ **Antes**: Las credenciales estaban hardcodeadas en `config.py`
   - Solo funcionaba con esas credenciales específicas
   - Si cambiaban, había que modificar el código
   - No era flexible ni seguro

2. ✅ **Ahora**: Cada usuario ingresa sus credenciales
   - Funciona para cualquier persona con acceso a SupplyPro
   - No hay que tocar código nunca más
   - Más seguro y flexible

## 📋 Qué cambió en la interfaz:

### Antes:
```
[Seleccionar: ShineAndBright o Apex]
[🚀 Exportar órdenes] ← Click directo
```

### Ahora:
```
[Seleccionar: ShineAndBright o Apex]

🔑 Credenciales de SupplyPro
[Usuario] [Contraseña]

[🚀 Exportar órdenes] ← Click después de ingresar credenciales
```

## 🚀 Cómo actualizar:

```bash
git add .
git commit -m "Fix: Permitir credenciales personalizadas"
git push
```

**Tiempo de deploy:** 2-3 minutos

## 📖 Cómo usar la nueva versión:

1. **Accede a la app** con tu clave (ej: `X30XH3-S9JH34`)

2. **Ingresa tus credenciales de SupplyPro**:
   - Usuario: Tu usuario de SupplyPro
   - Contraseña: Tu contraseña de SupplyPro

3. **Selecciona la configuración** (ShineAndBright o Apex)

4. **Click en "Exportar órdenes"**

5. **Descarga el resultado** en CSV o Excel

## 🔒 Seguridad:

- ✅ Las credenciales NO se guardan permanentemente
- ✅ Solo se usan durante tu sesión
- ✅ Se borran al cerrar sesión
- ✅ Conexión segura (HTTPS)

## 💡 Beneficios:

✅ **Universal** - Funciona para cualquier usuario de SupplyPro
✅ **Sin mantenimiento** - No hay que actualizar credenciales en el código
✅ **Más seguro** - No hay credenciales en el repositorio
✅ **Flexible** - Cada quien usa las suyas

## 📞 Soporte:

Si tienes problemas, lee: `SOLUCION_ERROR_LOGIN.md`

---

**Esta actualización resuelve el error de login que estabas experimentando.**
