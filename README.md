# ☀️ Asistente de ventas solar — Agentic RAG

Agente de IA para una empresa de paneles solares en México. Responde preguntas sobre clientes, consulta datos reales de radiación solar y genera cotizaciones (paneles, costo, ahorro y años de recuperación).

Proyecto de la **Unidad 3 (Agentic RAG)** del [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course), adaptado de la gala de ejemplo del curso a un caso de negocio real.

```
Vendedor: "¿Qué clientes de Durango tienen la cotización enviada?
           Actualízale la cotización a Roberto Gálvez con las horas de sol reales."

Agente:   filtrar_clientes(ciudad="Durango", etapa="Cotización enviada")
          → buscar_clientes("Roberto Gálvez")
          → horas_sol_pico("Durango")          # 5.34 h, datos reales
          → calcular_cotizacion(780, 6500, 5.34)
          → calcular_ahorro_anual(...) → calcular_recuperacion(...)
```

## Herramientas del agente

| Tool | Tipo | Qué hace |
|---|---|---|
| `buscar_clientes` | RAG (BM25) | Preguntas abiertas sobre un cliente: notas, preocupaciones, historial |
| `filtrar_clientes` | Código | Filtros **exactos** por ciudad, etapa de venta o tarifa de CFE |
| `horas_sol_pico` | API ([Open-Meteo](https://open-meteo.com/)) | Horas sol pico reales de los últimos 60 días por ciudad |
| `calcular_cotizacion` | Código | Número de paneles de 550 W y costo total |
| `calcular_ahorro_anual` | Código | Ahorro anual según consumo y tarifa |
| `calcular_recuperacion` | Código | Años para recuperar la inversión |
| `web_search` | DuckDuckGo | Datos actuales de internet (tarifas de CFE, precios) |

## Decisiones de diseño

- **El LLM decide, el código calcula.** Todas las cuentas viven en tools deterministas; el modelo solo elige qué herramienta usar y redacta. En pruebas anteriores, cuando el agente hacía las cuentas él mismo, inventaba fórmulas (por ejemplo, tomar el consumo bimestral como mensual).
- **RAG para preguntas abiertas, código para filtros exactos.** BM25 con `k=3` siempre regresa 3 resultados aunque solo 2 coincidan; por eso los filtros por ciudad, etapa o tarifa usan una tool exacta.
- **Horas sol pico, no horas con sol.** Open-Meteo da la radiación diaria en MJ/m²; dividida entre 3.6 da kWh/m², que equivale a horas sol pico (Aguascalientes 5.81, Zacatecas 5.72, Durango 5.34).
- **Respaldo que avisa.** Si la API de clima falla, se usa 5.5 h con `fuente: "estimado"`, y el agente lo informa en lugar de esconderlo.
- **Tipos y descripciones claros.** Lo único que ve el LLM de cada tool es su nombre, sus tipos y su descripción; un tipo de retorno incorrecto (`-> str` en una tool que regresaba un `dict`) rompía al agente.

## Estructura

```
data/clientes.json   10 clientes de ejemplo (datos inventados)
retriever.py         RAG de clientes con BM25
tools.py             filtros, horas sol pico, cotizador y búsqueda web
app.py               el agente (smolagents CodeAgent, planeación cada 3 pasos, memoria entre preguntas)
agente.py            primera versión: agente cotizador con 3 tools
search.py            prueba de agente con búsqueda web
```

## Cómo correrlo

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
setx GROQ_API_KEY "tu_llave"    # https://console.groq.com — abre una terminal nueva después
python app.py
```

El modelo se cambia en una línea de `app.py` (`LiteLLMModel`): funciona con Groq, Ollama local, Hugging Face, Anthropic, OpenAI, etc.

## Estado y siguientes pasos

- [x] RAG de clientes, filtros exactos, horas sol reales y cotizador probados por separado
- [x] El agente planea y elige las herramientas correctas
- [ ] Corrida completa de punta a punta (el plan gratuito de Groq limita los tokens por minuto)
- [ ] Búsqueda semántica con embeddings en lugar de BM25
- [ ] Rehacerlo como workflow (LlamaIndex o LangGraph) para más control

## Autor

Bruno Rueda Betancourt — Ingeniería en Inteligencia Artificial, Universidad Panamericana
