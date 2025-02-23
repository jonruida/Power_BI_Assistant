import gzip
import io

def extract_gzip_data(file_path, output_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()

        # Definir los marcadores de inicio y fin
        start_marker = b"'content': b'\'"
        end_marker = b"'headers'"

        # Recorrer el archivo buscando múltiples bloques de contenido
        start_index = 0
        all_content = []

        while True:
            # Buscar el siguiente bloque de contenido
            start_index = data.find(start_marker, start_index)
            if start_index == -1:
                break
            start_index += len(start_marker)

            # Buscar el final del bloque
            end_index = data.find(end_marker, start_index)
            if end_index == -1:
                break

            # Extraer el contenido entre los marcadores y limpiar comillas
            block_data = data[start_index:end_index].replace(b"'", b"").strip()

            # Comprobar si el bloque tiene más de 100 caracteres
            if len(block_data) > 100:
                print("Bloque de más de 100 caracteres encontrado, descomprimiendo...")
                try:
                    with gzip.GzipFile(fileobj=io.BytesIO(block_data), mode='rb') as gzip_file:
                        decompressed_data = gzip_file.read()
                        utf8_data = decompressed_data.decode('utf-8')
                        all_content.append(utf8_data)
                except Exception as e:
                    print(f"Error al descomprimir el bloque GZIP: {e}")
            else:
                # Si el bloque tiene menos de 100 caracteres, se guarda tal cual
                print("Bloque con menos de 100 caracteres encontrado, guardando sin descomprimir.")
                all_content.append(block_data.decode('utf-8', errors='ignore'))

            start_index = end_index  # Avanzar el índice para continuar con el siguiente bloque

        # Guardar todo el contenido en el archivo de salida
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(all_content))

    except Exception as e:
        print(f"Error durante el procesamiento: {e}")

# Usar la función con tus rutas de archivo
extract_gzip_data("C:/Users/jon.ruizcarrillo/outfile_dec", "C:/Users/jon.ruizcarrillo/outfile_decod")

