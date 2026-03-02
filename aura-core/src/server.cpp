#include <iostream>
#include <memory>
#include <thread>
#include <atomic>
#include <chrono>

#include <grpcpp/grpcpp.h>
#include "../generated/actuators.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReaderWriter;
using grpc::Status;
using aura::control::v1::MirrorControlService;
using aura::control::v1::ActuatorCommand;
using aura::control::v1::TelemetryStream;

class MirrorControlServiceImpl final : public MirrorControlService::Service {
    Status StreamActuators(ServerContext* context, 
                           ServerReaderWriter<TelemetryStream, ActuatorCommand>* stream) override {
        
        std::atomic<bool> keep_running{true};

        // Hilo de Telemetría de alta frecuencia (1kHz)
        std::jthread telemetry_thread([&](std::stop_token stoken) {
            while (!stoken.stop_requested() && keep_running) {
                TelemetryStream response;
                // Simular datos de actuadores
                auto* state = response.add_actuators();
                state->set_id(1);
                state->set_position_nm(150.25);
                state->set_timestamp_ns(std::chrono::system_clock::now().time_since_epoch().count());

                if (!stream->Write(response)) break;
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        });

        ActuatorCommand cmd;
        while (stream->Read(&cmd)) {
            // Aquí procesaríamos los comandos de la IA
        }
        keep_running = false;
        return Status::OK;
    }
};


int main() {
    MirrorControlServiceImpl service;
    ServerBuilder builder;
    builder.AddListeningPort("0.0.0.0:50051", grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    
    std::unique_ptr<Server> server(builder.BuildAndStart());
    
    if (!server) {
        std::cerr << "❌ ERROR: El servidor no pudo iniciar. ¿Puerto 50051 ocupado?" << std::endl;
        return 1;
    }

    std::cout << "🛰️ Servidor Aura-Core activo en puerto 50051" << std::endl;
    std::cout.flush(); // Fuerza la salida a la terminal
    
    server->Wait();
    return 0;
}