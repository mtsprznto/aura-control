cmake_minimum_required(VERSION 3.20)
project(AuraCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- SOLUCIÓN 1: Forzar LLD (evita el error 116 de memoria) ---
# Solo si lld está instalado en tu sistema
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=lld")

# --- SOLUCIÓN 2: Coherencia DLL ---
# gRPC en MSYS2 suele ser dinámico. Forzamos a que Protobuf no intente buscar estáticas.
set(Protobuf_USE_STATIC_LIBS OFF)
add_definitions(-DPROTOBUF_USE_DLLS)

find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf CONFIG REQUIRED)

# (Rutas y generación igual que antes...)
set(PROTO_FILE "${CMAKE_CURRENT_SOURCE_DIR}/../proto/actuators.proto")
set(GEN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/generated")
file(MAKE_DIRECTORY ${GEN_DIR})
set(PROTO_SRCS "${GEN_DIR}/actuators.pb.cc")
set(PROTO_HDRS "${GEN_DIR}/actuators.pb.h")
set(GRPC_SRCS "${GEN_DIR}/actuators.grpc.pb.cc")
set(GRPC_HDRS "${GEN_DIR}/actuators.grpc.pb.h")

add_custom_command(
    OUTPUT "${PROTO_SRCS}" "${PROTO_HDRS}" "${GRPC_SRCS}" "${GRPC_HDRS}"
    COMMAND protobuf::protoc
    ARGS --cpp_out "${GEN_DIR}"
         --grpc_out "${GEN_DIR}"
         --plugin=protoc-gen-grpc=$<TARGET_FILE:gRPC::grpc_cpp_plugin>
         -I "${CMAKE_CURRENT_SOURCE_DIR}/../proto"
         "${PROTO_FILE}"
    DEPENDS "${PROTO_FILE}"
    VERBATIM
)

add_executable(aura_server src/server.cpp ${PROTO_SRCS} ${GRPC_SRCS})
target_include_directories(aura_server PRIVATE ${GEN_DIR})

# --- SOLUCIÓN 3: Subsystem Linking Completo ---
target_link_libraries(aura_server 
    PRIVATE 
    gRPC::grpc++ 
    protobuf::libprotobuf
    ws2_32       # Sockets
    crypt32      # SSL/TLS
    iphlpapi     # Networking avanzado
    bcrypt       # Criptografía moderna
    secur32      # Seguridad de Windows
)