cmake_minimum_required(VERSION 3.20)
project(AuraCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(WIN32)
    # Evita el error 116 de memoria en ld de Windows
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=lld")
    # Coherencia para usar DLLs en lugar de estáticas
    set(Protobuf_USE_STATIC_LIBS OFF)
    add_definitions(-DPROTOBUF_USE_DLLS)
endif()

find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf REQUIRED)

if(Protobuf_FOUND)
    message(STATUS "Protobuf encontrado v${Protobuf_VERSION}")
else()
    # Si falla en Linux, intentamos vía PkgConfig como último recurso
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(PROTOBUF REQUIRED protobuf)
endif()

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

if(WIN32)
    target_link_libraries(aura_server 
        PRIVATE 
        gRPC::grpc++ 
        protobuf::libprotobuf
        ws2_32 crypt32 iphlpapi bcrypt secur32
    )
else()
    # En Linux (Docker), las dependencias se gestionan vía pkg-config/cmake automáticamente
    target_link_libraries(aura_server 
        PRIVATE 
        gRPC::grpc++ 
        protobuf::libprotobuf
        pthread
    )
endif()