from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    # Filtrar solo las solicitudes JSON de Power BI
    if "api" in flow.request.pretty_url and "application/json" in flow.request.headers.get("Accept", ""):
        with open("captured_requests.json", "a") as f:
            f.write(f"URL: {flow.request.pretty_url}\n")
            f.write(f"Request Headers: {dict(flow.request.headers)}\n")
            f.write(f"Request Body: {flow.request.content.decode('utf-8', 'ignore')}\n")            
        
            f.write(f"Response Body: {flow.response.content.decode('utf-8', 'ignore')}\n")

            
            f.write("\n")
