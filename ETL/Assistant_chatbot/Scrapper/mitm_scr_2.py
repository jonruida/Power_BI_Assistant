from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    # Filtrar las respuestas JSON de Power BI
    if "api" in flow.request.pretty_url and "application/json" in flow.request.headers.get("Accept", ""):
        with open("captured_responses1.json", "a") as f:
            f.write(f"{flow.response.content.decode('utf-8', 'ignore')}\n")  # Aquí también flow.response para el cuerpo de la respuesta
