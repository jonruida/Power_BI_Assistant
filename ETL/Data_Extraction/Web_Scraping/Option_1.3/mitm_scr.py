from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    # Filtrar solo las solicitudes JSON de Power BI
    # if "api" in flow.request.pretty_url and "application/json" in flow.request.headers.get("Accept", ""):
        with open("captured_requests.json", "a") as f:
            f.write(f"URL: {flow.request.pretty_url}\n")
            f.write(f"Request Headers: {dict(flow.request.headers)}\n")
            f.write(f"Request Body: {flow.request.content.decode('utf-8', 'ignore')}\n")
            f.write("\n")

def response(flow: http.HTTPFlow) -> None:
    # Filtrar las respuestas JSON de Power BI
    if "api" in flow.request.pretty_url and "application/json" in flow.request.headers.get("Accept", ""):
        with open("captured_responses1.json", "a") as f:
            f.write(f"URL: {flow.request.pretty_url}\n")  # Aquí puede seguir siendo flow.request porque es la URL de la solicitud
            if flow.response:
                f.write(f"Response Headers: {dict(flow.response.headers)}\n")  # Aquí usas flow.response para obtener los encabezados de la respuesta
                f.write(f"Response Body: {flow.response.content.decode('utf-8', 'ignore')}\n")  # Aquí también flow.response para el cuerpo de la respuesta
            else:
                f.write("Response not available. Check if the response was received or if there was an issue.\n")
            f.write("\n")