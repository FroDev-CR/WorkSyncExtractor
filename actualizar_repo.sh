#!/bin/bash
echo "========================================"
echo "Actualizando repositorio de GitHub"
echo "========================================"
echo ""

git add .
git commit -m "Fix: Corregir error de deploy en Streamlit Cloud"
git push

echo ""
echo "========================================"
echo "¡Listo! Cambios subidos a GitHub"
echo "Streamlit Cloud detectará los cambios automáticamente"
echo "========================================"
