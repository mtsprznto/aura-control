# ------------------------------------------
# ------------------------------------------
# ------------------------------------------
# --- Etapa 1: Construcción (Builder) ---
# ------------------------------------------
# ------------------------------------------
# ------------------------------------------
FROM ubuntu:24.04 AS builder
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake ninja-build git \
    libgrpc++-dev libprotobuf-dev protobuf-compiler-grpc \
    pkg-config

WORKDIR /app
COPY . .

RUN mkdir -p aura-ai/generated

# Forzar la generación de stubs de Python manualmente para estar seguros
RUN protoc -I proto \
    --python_out=aura-ai/generated \
    --grpc_python_out=aura-ai/generated \
    --plugin=protoc-gen-grpc_python=/usr/bin/grpc_python_plugin \
    proto/actuators.proto

# Ahora compilar el Core C++ como antes
RUN rm -rf aura-core/build && \
    mkdir -p aura-core/build && \
    cd aura-core/build && \
    cmake -G Ninja .. && \
    ninja -v



# ------------------------------------------
# ------------------------------------------
# ------------------------------------------
# --- Etapa 2: Runtime Final (Ubuntu 24.04 para Python 3.12 Nativo) ---
# ------------------------------------------
# ------------------------------------------
# ------------------------------------------

FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# DEBUG: Listar qué paquetes de gRPC y Python existen en esta nueva distro
RUN apt-get update && \
    echo "🔍 DEBUG: Buscando paquetes en Ubuntu 24.04..." && \
    apt-cache search python3.12 && \
    apt-cache search libgrpc++ && \
    apt-cache search libprotobuf

# Instalación corregida para Ubuntu 24.04
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    libgrpc++1.51t64 \
    libprotobuf32t64 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar artefactos

COPY --from=builder /app/aura-core/build/aura_server /app/aura_server
COPY --from=builder /app/aura-ai/generated /app/aura-ai/generated
COPY . .

# Herramientas de Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvbin/uv

# Sincronizar (uv detectará python 3.12 de la distro)
ENV UV_SYSTEM_PYTHON=1
RUN /uvbin/uv sync --frozen --no-cache && \
    echo "🔍 DEBUG: Verificando paquetes instalados en el sistema:" && \
    python3.12 -m pip list

EXPOSE 50051
CMD ["./aura_server"]