import gzip
import io

def extract_gzip_data(file_path, output_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()

        # Definir los marcadores de inicio y fin con contrabarra incluida
        start_marker = b"'content': b'"
        end_marker = b"'headers'"

       
        # Recorrer el archivo buscando múltiples bloques de contenido
        start_index = 0
        all_content = []

        while True:
            # Buscar el siguiente bloque que empieza con el marcador de inicio
            start_index = data.find(start_marker, start_index)
            if start_index == -1:
                break

            # Buscar el final del bloque
            end_index = data.find(end_marker, start_index)
            if end_index == -1:
                end_index = len(data)  # Si no se encuentra el fin, usar el final del archivo

            # Extraer el contenido entre los marcadores
            block_data = data[start_index + len(start_marker):end_index]
            print(f"Bloque encontrado de tamaño {len(block_data)} bytes.")
            # Si el archivo contiene secuencias de escape \x, lo convertimos a bytes
            # compressed_data_bytes = bytes.fromhex(compressed_data_str.replace("\\x", ""))
            print(block_data[0:10])

            try:
            
                with gzip.GzipFile(fileobj=io.BytesIO(block_data), mode='r') as gzip_file:
                    decompressed_data = gzip_file.read()
                    
                    utf8_data = decompressed_data.decode('utf-8')
                    all_content.append(utf8_data)
            
                all_content.append(block_data.decode('utf-8', errors='ignore'))
            except Exception as e:
                print(f"Error al descomprimir el bloque GZIP: {e}")


            start_index = end_index  # Avanzar el índice para continuar con el siguiente bloque

        # Guardar todo el contenido en el archivo de salida
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(all_content))

    except Exception as e:
        print(f"Error durante el procesamiento: {e}")

# Usar la función con tus rutas de archivo
extract_gzip_data("C:/Users/jon.ruizcarrillo/outfile_dec", "C:/Users/jon.ruizcarrillo/outfile_decod")
