@echo off
echo ========================================
echo Actualizando repositorio de GitHub
echo ========================================
echo.

git add .
git commit -m "Fix: Mover modulos a raiz para evitar error de importacion"
git push

echo.
echo ========================================
echo Listo! Cambios subidos a GitHub
echo.
echo VERSION FINAL SIMPLIFICADA:
echo - Sin autenticacion ni claves
echo - Solo: Seleccionar empresa y click
echo - Cualquier persona puede usar la app
echo.
echo Streamlit Cloud redesplegara en 2-3 minutos
echo ========================================
pause
