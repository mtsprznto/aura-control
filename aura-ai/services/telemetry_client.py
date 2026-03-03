import time
import grpc
import sys
import os

# 🛠️ FIX DE PATHS: Añadimos las rutas necesarias para que los stubs se vean entre sí
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
generated_dir = os.path.abspath(os.path.join(current_dir, "../generated"))
if os.path.exists(generated_dir):
    sys.path.insert(0, generated_dir)

sys.path.insert(0, project_root)
sys.path.insert(0, generated_dir)

# Ahora los imports funcionarán
import actuators_pb2
import actuators_pb2_grpc

def run():
    print("============ Iniciando Cliente de Telemetría Aura-AI ============")
    server_address = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")
    with grpc.insecure_channel(server_address) as channel:
        stub = actuators_pb2_grpc.MirrorControlServiceStub(channel)
        
        def command_generator():
            # Enviamos un comando inicial de "CALIBRATE" o simplemente vacío
            yield actuators_pb2.ActuatorCommand(id=0, mode=actuators_pb2.ActuatorCommand.CALIBRATE)
            while True:
                time.sleep(1) # Mantener el canal abierto

        try:
            print("============ Suscribiéndose al flujo de actuadores (1kHz) ============")
            # Enviamos un iterador vacío para iniciar el stream
            responses = stub.StreamActuators(command_generator()) 
            
            for response in responses:
                for state in response.actuators:
                    # Formato profesional para telemetría
                    print(f"ID: {state.id:02} | Pos: {state.position_nm:8.2f} nm | TS: {state.timestamp_ns}")
                
        except grpc.RpcError as e:
            print(f"============ Error de gRPC: {e.code()} - {e.details()} ============")
        except KeyboardInterrupt:
            print("\n============ Cliente detenido. ============")

if __name__ == "__main__":
    run()