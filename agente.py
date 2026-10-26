import math

from smolagents import CodeAgent, LiteLLMModel, tool


# 1. Las tools: tus funciones, con @tool, tipos y docstring
@tool
def calcular_cotizacion(consumo_bimestral_kwh: float, precio_por_panel: float) -> dict:
    """Calcula cuántos paneles solares necesita una casa o negocio en Aguascalientes
    y estima el costo total, a partir de su recibo de luz de CFE.
    Args:
        consumo_bimestral_kwh: consumo de luz en kWh que aparece en el recibo bimestral de CFE
        precio_por_panel: precio de un panel instalado, en pesos mexicanos (MXN)
    Returns:
        Un diccionario con dos llaves: "paneles" (número de paneles, int) y
        "costo_total" (costo en MXN, float). Ejemplo de uso:
        r = calcular_cotizacion(800, 6500); r["paneles"]; r["costo_total"]
    """
    consumo_diario = consumo_bimestral_kwh / 60
    panel_dia = 0.55 * 5.5 * 0.8
    paneles = math.ceil(consumo_diario / panel_dia)
    costo = paneles * precio_por_panel
    return {"paneles": paneles, "costo_total": costo}


@tool
def calcular_ahorro_anual(consumo_bimestral_kwh: float, tarifa_kwh: float) -> float:
    """
    Calcula el ahorro anual estimado al instalar paneles solares, a partir del consumo bimestral de luz y la tarifa por kWh.
    Args:
        consumo_bimestral_kwh: consumo de luz en kWh que aparece en el recibo bimestral de CFE
        tarifa_kwh: tarifa por kWh en pesos mexicanos (MXN)
    Returns:
        ahorro anual estimado en MXN
    """
    consumo_anual = consumo_bimestral_kwh * 6
    ahorro = consumo_anual * tarifa_kwh
    return ahorro


@tool
def calcular_recuperacion(costo_total: float, ahorro_anual: float) -> float:
    """
    Calcula en cuántos años se recupera la inversión en paneles solares.
    Args:
        costo_total: costo total de la instalación en MXN
        ahorro_anual: ahorro anual estimado en MXN
    Returns:
        número de años para recuperar la inversión
    """
    return costo_total / ahorro_anual


# 2. El cerebro: tu modelo local en Ollama
model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5-coder:7b",
    api_base="http://localhost:11434",
    num_ctx=8192,
    temperature=0,
)

# 3. El agente: cerebro + herramientas
agent = CodeAgent(
    tools=[calcular_cotizacion, calcular_ahorro_anual, calcular_recuperacion],
    model=model,
    max_steps=6,
    instructions=(
        "Responde siempre en español. "
        "Usa SIEMPRE las herramientas para calcular paneles, costo, ahorro y años de recuperación; "
        "nunca inventes tus propias fórmulas. "
        "Si una herramienta da un resultado raro, revisa cómo la usaste y vuelve a llamarla. "
        "En el código usa nombres de variables cortos y sin espacios, por ejemplo: cot, ahorro, anios."
    ),
    additional_authorized_imports=["math"],
)

agent.run(
    "Mi recibo de luz dice 800 kWh en el bimestre y cada panel cuesta 6,500 pesos instalado. "
    "¿Cuántos paneles necesito, cuánto me cuesta y cuánto estaría ahorrando al año si la tarifa es de 5 pesos por kWh? "
    "¿Y en cuántos años recupero la inversión?"
)
