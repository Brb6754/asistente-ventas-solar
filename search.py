# Create a CodeAgent with DuckDuckGo search capability
from smolagents import tool
from smolagents import CodeAgent,LiteLLMModel,DuckDuckGoSearchTool,InferenceClientModel

model = LiteLLMModel(model_id="groq/qwen/qwen3.8-27b")

agent = CodeAgent(
    tools=[DuckDuckGoSearchTool(max_results=4)],
    model=model,
    max_steps=6,
    instructions=(
        "Responde siempre en español. "
        "Usa SIEMPRE la herramienta de búsqueda para obtener información; "
        "nunca inventes tus propias respuestas. "
        "En cuanto encuentres la respuesta en los resultados, llama final_answer() con la respuesta y la fuente. "
        "Si no encuentras información relevante, responde con 'No se encontró información relevante.'"
    ),
)

respuesta = agent.run("¿Cuál es la canción más escuchada de México en 2026?")
print("RESPUESTA:", respuesta)