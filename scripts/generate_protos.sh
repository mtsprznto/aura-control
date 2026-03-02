#!/bin/bash
set -e

# Directorios de salida
PY_OUT="./aura-ai/generated"
mkdir -p $PY_OUT

echo "🐍 Generando stubs de gRPC para Python (Aura-AI)..."

# Usamos el módulo de python directamente. 
# Esto es mucho más seguro en Windows porque 'uv' gestiona los paths internos.
uv run python -m grpc_tools.protoc \
    -I ./proto \
    --python_out=$PY_OUT \
    --grpc_python_out=$PY_OUT \
    ./proto/actuators.proto

# Crear __init__.py para que el directorio sea un módulo válido
touch $PY_OUT/__init__.py

echo "✅ Stubs de Python generados en: $PY_OUT"