import math
from typing import Optional

import requests
from smolagents import DuckDuckGoSearchTool, Tool, tool

from retriever import clientes


# ---------- Clientes: filtros EXACTOS (para no depender del buscador aproximado) ----------

@tool
def filtrar_clientes(ciudad: Optional[str] = None, etapa: Optional[str] = None, tarifa: Optional[str] = None) -> str:
    """
    Regresa la lista EXACTA de clientes que cumplen todos los filtros dados. Úsala para preguntas como
    "¿qué clientes de Durango están en cotización enviada?" o "¿quiénes tienen tarifa DAC?".
    Para preguntas abiertas sobre un cliente (qué le preocupa, notas) usa buscar_clientes.
    Args:
        ciudad: ciudad del cliente, por ejemplo "Aguascalientes", "Durango" o "Zacatecas" (opcional)
        etapa: etapa de venta: "Primer contacto", "Cotización enviada", "Negociación", "Cerrado - ganado" o "Cerrado - perdido" (opcional)
        tarifa: tarifa de CFE, por ejemplo "1", "DAC", "PDBT" o "GDMTO" (opcional)
    Returns:
        Texto con un renglón por cliente (nombre, ciudad, etapa, tarifa, consumo), o un aviso si no hay ninguno.
    """
    encontrados = [
        c for c in clientes
        if (ciudad is None or c["ciudad"].lower() == ciudad.lower())
        and (etapa is None or c["etapa"].lower() == etapa.lower())
        and (tarifa is None or c["tarifa"].lower() == tarifa.lower())
    ]
    if not encontrados:
        return "Ningún cliente cumple esos filtros."
    renglones = [
        f"- {c['nombre']} | {c['ciudad']} | {c['etapa']} | tarifa {c['tarifa']} | {c['consumo_bimestral_kwh']} kWh/bimestre"
        for c in encontrados
    ]
    return f"{len(encontrados)} cliente(s):\n" + "\n".join(renglones)


# ---------- Horas sol pico reales (Open-Meteo, gratis y sin llave) ----------

class HorasSolTool(Tool):
    name = "horas_sol_pico"
    description = (
        "Calcula las horas sol pico promedio por día de una ciudad de México con datos reales de radiación "
        "solar de los últimos 60 días. Úsala antes de calcular_cotizacion para dimensionar los paneles. "
        'Regresa un diccionario: {"horas_sol": float, "fuente": "real" o "estimado"}. '
        'Si la fuente es "estimado", avísale al usuario que la cotización usa un promedio.'
    )
    inputs = {"ciudad": {"type": "string", "description": "Nombre de la ciudad, por ejemplo 'Durango'."}}
    output_type = "object"

    def forward(self, ciudad: str) -> dict:
        try:
            return {"horas_sol": self._consultar(ciudad), "fuente": "real"}
        except Exception as e:
            # Respaldo: si la API falla, usa el promedio de México, pero AVISA que es estimado
            print(f"Aviso: no pude obtener la radiación de {ciudad} ({e}); uso 5.5 horas estimadas.")
            return {"horas_sol": 5.5, "fuente": "estimado"}

    def _consultar(self, ciudad: str) -> float:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1, "language": "es", "countryCode": "MX"},
            timeout=15,
        ).json()
        if not geo.get("results"):
            raise ValueError(f"No encontré la ciudad '{ciudad}'.")
        lugar = geo["results"][0]

        clima = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lugar["latitude"],
                "longitude": lugar["longitude"],
                "daily": "shortwave_radiation_sum",  # energía solar del día, en MJ/m²
                "past_days": 60,
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=15,
        ).json()
        radiacion = [r for r in clima["daily"]["shortwave_radiation_sum"] if r is not None]
        # 1 kWh/m² = 3.6 MJ/m², y 1 kWh/m² al día = 1 hora sol pico
        return round(sum(radiacion) / len(radiacion) / 3.6, 2)


# ---------- Cotizador (del agente solar, ahora con horas de sol reales) ----------

@tool
def calcular_cotizacion(consumo_bimestral_kwh: float, precio_por_panel: float, horas_sol: float = 5.5) -> dict:
    """
    Calcula cuántos paneles solares de 550 W necesita un cliente y el costo total, a partir de su recibo de CFE.
    Args:
        consumo_bimestral_kwh: consumo de luz en kWh del recibo bimestral de CFE
        precio_por_panel: precio de un panel instalado, en MXN
        horas_sol: horas sol pico promedio por día de la ciudad (usa horas_sol_pico); si no se sabe, 5.5
    Returns:
        Un diccionario con "paneles" (int) y "costo_total" (float, MXN). Ejemplo:
        r = calcular_cotizacion(800, 6500, 5.8); r["paneles"]; r["costo_total"]
    """
    consumo_diario = consumo_bimestral_kwh / 60
    energia_panel_dia = 0.55 * horas_sol * 0.8  # 550 W × horas sol pico × 80 % de eficiencia
    paneles = math.ceil(consumo_diario / energia_panel_dia)
    return {"paneles": paneles, "costo_total": paneles * precio_por_panel}


@tool
def calcular_ahorro_anual(consumo_bimestral_kwh: float, tarifa_kwh: float) -> float:
    """
    Calcula el ahorro anual estimado al instalar paneles solares.
    Args:
        consumo_bimestral_kwh: consumo de luz en kWh del recibo bimestral de CFE
        tarifa_kwh: precio del kWh en MXN
    Returns:
        ahorro anual estimado en MXN
    """
    return consumo_bimestral_kwh * 6 * tarifa_kwh


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


busqueda_web = DuckDuckGoSearchTool(max_results=4)
horas_sol_pico = HorasSolTool()


if __name__ == "__main__":
    print(filtrar_clientes(tarifa="DAC"))
    print(filtrar_clientes(ciudad="Durango", etapa="Cotización enviada"))
    for ciudad in ["Aguascalientes", "Durango", "Zacatecas"]:
        print(ciudad, horas_sol_pico(ciudad), "horas sol pico")
    print("Ciudad inventada:", horas_sol_pico("Ciudadquenoexiste"))
    hs = horas_sol_pico("Durango")
    print(calcular_cotizacion(780, 6500, hs["horas_sol"]))
