import json
from pathlib import Path

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from smolagents import Tool

RUTA_CLIENTES = Path(__file__).parent / "data" / "clientes.json"

with open(RUTA_CLIENTES, encoding="utf-8") as f:
    clientes = json.load(f)

# 1. Cada cliente se vuelve un documento con TODOS sus campos (lo que no está aquí, el buscador no lo encuentra)
docs = [
    Document(
        page_content="\n".join([
            f"Nombre: {c['nombre']}",
            f"Ciudad: {c['ciudad']}",
            f"Tipo: {c['tipo']}",
            f"Consumo bimestral: {c['consumo_bimestral_kwh']} kWh",
            f"Tarifa CFE: {c['tarifa']}",
            f"Etapa de venta: {c['etapa']}",
            f"Última interacción: {c['ultima_interaccion']}",
            f"Notas: {c['notas']}",
            f"Email: {c['email']}",
        ]),
        metadata={"nombre": c["nombre"]},
    )
    for c in clientes
]


class ClientesRetrieverTool(Tool):
    name = "buscar_clientes"
    # 2. Descripción clara: qué busca y cuándo usarla
    description = (
        "Busca información de los clientes de la empresa solar: nombre, ciudad, tipo (casa o negocio), "
        "consumo de luz, tarifa de CFE, etapa de venta, última interacción, notas y email. "
        "Úsala para preguntas sobre un cliente específico o para filtrar por ciudad, etapa, tarifa o tipo."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Palabras a buscar: nombre del cliente, ciudad, etapa de venta, tarifa, etc.",
        }
    }
    output_type = "string"

    def __init__(self, docs):
        super().__init__()
        # 3. El retriever se crea UNA sola vez
        self.retriever = BM25Retriever.from_documents(docs, k=3)

    def forward(self, query: str) -> str:
        resultados = self.retriever.invoke(query)
        if not resultados:
            return "No se encontró ningún cliente con esa búsqueda."
        # 4. Regresa texto, no una lista de Document
        return "\n\n".join(doc.page_content for doc in resultados)


# 5. Una instancia, con sus docs
clientes_tool = ClientesRetrieverTool(docs)


if __name__ == "__main__":
    print(clientes_tool.forward("Durango"))
    print("-----")
    print(clientes_tool.forward("DAC"))
