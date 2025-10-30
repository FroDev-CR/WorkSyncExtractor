#!/bin/bash
echo "========================================"
echo "Actualizando repositorio de GitHub"
echo "========================================"
echo ""

git add .
git commit -m "Simplificar app para uso universal sin autenticacion"
git push

echo ""
echo "========================================"
echo "¡Listo! Cambios subidos a GitHub"
echo ""
echo "VERSIÓN FINAL SIMPLIFICADA:"
echo "- Sin autenticación ni claves"
echo "- Solo: Seleccionar empresa y click"
echo "- Cualquier persona puede usar la app"
echo ""
echo "Streamlit Cloud redesplegará en 2-3 minutos"
echo "========================================"
