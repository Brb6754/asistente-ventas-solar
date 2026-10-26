from smolagents import CodeAgent, LiteLLMModel

from retriever import clientes_tool
from tools import (
    busqueda_web,
    calcular_ahorro_anual,
    calcular_cotizacion,
    calcular_recuperacion,
    filtrar_clientes,
    horas_sol_pico,
)

model = LiteLLMModel(model_id="groq/qwen/qwen3.8-27b")  # Gemini pidió activar cobro; Groq gratis funciona (límite por minuto)

asistente = CodeAgent(
    tools=[
        clientes_tool,
        filtrar_clientes,
        horas_sol_pico,
        calcular_cotizacion,
        calcular_ahorro_anual,
        calcular_recuperacion,
        busqueda_web,
    ],
    model=model,
    max_steps=8,
    planning_interval=3,
    instructions=(
        "Eres el asistente de ventas de una empresa de paneles solares en México. Responde siempre en español. "
        "Para listas o filtros de clientes (ciudad, etapa, tarifa) usa filtrar_clientes; "
        "para detalles o notas de un cliente usa buscar_clientes. "
        "Para cotizar: primero horas_sol_pico de la ciudad del cliente y luego calcular_cotizacion con esas horas. "
        "Nunca inventes fórmulas ni datos: usa siempre las herramientas. "
        "Si horas_sol_pico regresa fuente 'estimado', avísalo en la respuesta. "
        "Usa la búsqueda web solo para datos actuales de internet, como tarifas de CFE. "
        "Cuando tengas la respuesta, llama final_answer con un resumen claro para el vendedor."
    ),
)


if __name__ == "__main__":
    pregunta_1 = (
        "¿Qué clientes de Durango tienen la cotización enviada? "
        "Actualízale la cotización a Roberto Gálvez con las horas de sol reales de su ciudad, "
        "con paneles de 6,500 pesos instalados."
    )
    print("RESPUESTA 1:", asistente.run(pregunta_1))

    # Memoria: la segunda pregunta se refiere a "él" sin decir el nombre
    pregunta_2 = "¿Y qué le preocupaba a él según sus notas? Dame un consejo para cerrar la venta."
    print("RESPUESTA 2:", asistente.run(pregunta_2, reset=False))
