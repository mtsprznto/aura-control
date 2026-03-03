import subprocess
import time
import os
import sys

def run_aura_system():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    # Asegúrate de que esta ruta sea exacta
    server_bin = os.path.normpath(os.path.join(curr_dir, "aura-core/build/aura_server.exe"))
    client_script = os.path.normpath(os.path.join(curr_dir, "aura-ai/services/telemetry_client.py"))
    
    if not os.path.exists(server_bin):
        print(f" ERROR: No se encuentra el binario en {server_bin}. ¿Compilaste con Ninja?")
        return

    # Inyectamos el PATH de MSYS2 UCRT64
    msys_path = r"D:\msys64\ucrt64\bin"
    env = os.environ.copy()
    env["PATH"] = f"{msys_path};{env.get('PATH', '')}"

    print("\n --- Iniciando Ecosistema Aura-Control ---")

    server_proc = None
    client_proc = None

    try:
        # 2. Lanzar el Servidor C++
        print(f"Lanzando Servidor C++ desde: {server_bin}")
        # Quitamos stdout=PIPE para que los errores salgan directos a la consola
        server_proc = subprocess.Popen(
            [server_bin],
            env=env
        )

        # Esperamos a que el servidor imprima su mensaje de "Activo"
        time.sleep(2)

        # 3. Lanzar el Cliente de IA
        if server_proc.poll() is None:
            print("Lanzando Cliente de Telemetría (Python)...")
            client_proc = subprocess.Popen(
                ["uv", "run", "python", client_script],
                env=env
            )
        else:
            print("El servidor falló al arrancar inmediatamente.")
            return

        # 4. Monitoreo
        while True:
            if server_proc.poll() is not None:
                print("El servidor C++ se ha cerrado.")
                break
            if client_proc and client_proc.poll() is not None:
                print("El cliente Python se ha cerrado.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo sistema por el usuario...")
    finally:
        if client_proc: client_proc.terminate()
        if server_proc: server_proc.terminate()
        print("Sistema Aura-Control apagado.\n")

if __name__ == "__main__":
    run_aura_system()