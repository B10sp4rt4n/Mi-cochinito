"""
Módulo de integración con OpenAI GPT para análisis avanzado del simulador SIDEPE.
"""

import os
from typing import Dict, List, Optional
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIAnalyzer:
    """Analizador avanzado usando OpenAI GPT"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el analizador con OpenAI.
        
        Args:
            api_key: API key de OpenAI. Si no se proporciona, busca en variables de entorno.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI no está instalado. Ejecuta: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key de OpenAI no proporcionada")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Modelo más económico pero potente
    
    def analyze_deep(self, simulation_data: Dict, params: Dict) -> str:
        """
        Realiza un análisis profundo de los resultados de simulación.
        
        Args:
            simulation_data: Datos de la simulación (DataFrame convertido a dict)
            params: Parámetros de la simulación
            
        Returns:
            Análisis detallado en texto
        """
        prompt = self._build_analysis_prompt(simulation_data, params)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un experto en análisis financiero y microfinanzas con 20 años de experiencia. 
                        Analizas modelos de ahorro colectivo y cooperativas financieras. 
                        Tus análisis son profundos, prácticos y basados en datos.
                        Siempre proporcionas recomendaciones accionables con prioridades claras."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error al analizar con OpenAI: {str(e)}"
    
    def generate_report(self, simulation_data: Dict, params: Dict, format: str = "ejecutivo") -> str:
        """
        Genera un reporte profesional basado en los datos.
        
        Args:
            simulation_data: Datos de la simulación
            params: Parámetros de la simulación
            format: Tipo de reporte ('ejecutivo', 'tecnico', 'inversionista')
            
        Returns:
            Reporte formateado
        """
        prompts = {
            "ejecutivo": """Genera un reporte ejecutivo profesional de máximo 2 páginas para el CEO.
                         Incluye: Resumen ejecutivo, hallazgos clave, recomendaciones prioritarias, próximos pasos.""",
            
            "tecnico": """Genera un reporte técnico detallado para el equipo de operaciones.
                       Incluye: Análisis de métricas, identificación de cuellos de botella, 
                       optimizaciones técnicas, plan de implementación paso a paso.""",
            
            "inversionista": """Genera un reporte para presentar a inversionistas.
                             Incluye: Viabilidad del modelo, análisis de riesgo, proyecciones, 
                             comparación con benchmarks, retorno esperado."""
        }
        
        prompt = f"""{prompts.get(format, prompts['ejecutivo'])}

Datos de la simulación:
- Número de usuarios: {params.get('num_users')}
- Aportación mensual: ${params.get('monthly_contribution')}
- Utilización del capital: {params.get('utilization_rate')}%
- Tasa de morosidad: {params.get('default_rate')}%
- ROI proyectado: {simulation_data.get('roi', 0):.2f}%
- Valor final del sistema: ${simulation_data.get('final_value', 0):,.2f}
- Ganancia neta acumulada: ${simulation_data.get('net_profit', 0):,.2f}

Genera el reporte en formato Markdown profesional."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista financiero senior especializado en reportes ejecutivos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error al generar reporte: {str(e)}"
    
    def chat_advisor(self, user_question: str, context: Dict) -> str:
        """
        Responde preguntas del usuario sobre el simulador de forma conversacional.
        
        Args:
            user_question: Pregunta del usuario
            context: Contexto de la simulación actual
            
        Returns:
            Respuesta del asistente
        """
        prompt = f"""Contexto de la simulación actual:
{json.dumps(context, indent=2)}

Pregunta del usuario: {user_question}

Responde de forma clara, concisa y accionable. Si es relevante, sugiere ejecutar una simulación específica."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asistente financiero experto en el modelo SIDEPE.
                        Ayudas a usuarios a entender su simulación y tomar mejores decisiones.
                        Respondes preguntas de forma clara, educativa y práctica."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error en chat: {str(e)}"
    
    def optimize_with_constraints(self, params: Dict, constraints: str) -> Dict:
        """
        Optimiza parámetros considerando restricciones específicas del negocio.
        
        Args:
            params: Parámetros actuales
            constraints: Restricciones en lenguaje natural
            
        Returns:
            Parámetros optimizados
        """
        prompt = f"""Parámetros actuales del sistema SIDEPE:
{json.dumps(params, indent=2)}

Restricciones y contexto:
{constraints}

Analiza y sugiere parámetros optimizados que:
1. Maximicen el ROI
2. Respeten todas las restricciones
3. Sean realistas de implementar

Responde SOLO con un objeto JSON con los parámetros optimizados (misma estructura que parámetros actuales)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un optimizador financiero experto. Respondes SOLO con JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            optimized = json.loads(response.choices[0].message.content)
            return optimized
        
        except Exception as e:
            return {"error": str(e)}
    
    def explain_metric(self, metric_name: str, value: float, context: Dict) -> str:
        """
        Explica una métrica específica en detalle educativo.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor actual
            context: Contexto adicional
            
        Returns:
            Explicación detallada
        """
        prompt = f"""Explica de forma educativa la métrica: {metric_name}

Valor actual: {value}
Contexto: {json.dumps(context, indent=2)}

Explica:
1. Qué significa esta métrica
2. Por qué tiene este valor
3. Cómo impacta el negocio
4. Cómo mejorarla (si aplica)

Usa lenguaje simple, ejemplos prácticos y bullets."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un educador financiero. Explicas conceptos complejos de forma simple."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_analysis_prompt(self, simulation_data: Dict, params: Dict) -> str:
        """Construye el prompt para análisis profundo"""
        return f"""Analiza en profundidad este modelo de ahorro colectivo SIDEPE:

PARÁMETROS DE OPERACIÓN:
- Usuarios: {params.get('num_users')}
- Aportación mensual: ${params.get('monthly_contribution')}
- Utilización del capital: {params.get('utilization_rate')}%
- Tasa de morosidad: {params.get('default_rate')}%
- Distribución: FEE {params.get('fee_dist')}% / Núcleo {params.get('nucleus_dist')}% / FIC {params.get('fic_dist')}%
- Comisión administrativa: {params.get('admin_fee_pct')}% anual

RESULTADOS:
- ROI: {simulation_data.get('roi', 0):.2f}%
- Score de salud: {simulation_data.get('health_score', 0):.0f}/100
- Valor final: ${simulation_data.get('final_value', 0):,.2f}
- Ganancia neta: ${simulation_data.get('net_profit', 0):,.2f}
- Ganancia por usuario: ${simulation_data.get('profit_per_user', 0):,.2f}

Proporciona:
1. DIAGNÓSTICO: Evaluación profunda del modelo (3-4 párrafos)
2. FACTORES CRÍTICOS: Los 3 factores que más impactan el resultado
3. ANÁLISIS DE RIESGO: Riesgos principales y cómo mitigarlos
4. PLAN DE ACCIÓN: 5 pasos concretos priorizados con timeline
5. POTENCIAL: ¿Cuál es el ROI máximo alcanzable y cómo?

Sé específico, práctico y basado en datos."""

    def test_connection(self) -> bool:
        """Prueba la conexión con OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return True
        except:
            return False


def is_openai_available() -> bool:
    """Verifica si OpenAI está disponible"""
    return OPENAI_AVAILABLE


def get_pricing_info() -> str:
    """Retorna información de precios"""
    return """
### 💰 Precios de OpenAI (GPT-4o-mini)

**Costos aproximados:**
- Análisis profundo: ~$0.01-0.02 USD por análisis
- Reporte ejecutivo: ~$0.02-0.03 USD por reporte
- Chat (respuesta): ~$0.005-0.01 USD por pregunta
- Optimización: ~$0.01-0.02 USD por optimización

**Estimado mensual:**
- Uso ligero (10 análisis/mes): ~$0.50 USD
- Uso moderado (50 análisis/mes): ~$2-3 USD
- Uso intensivo (200 análisis/mes): ~$10-15 USD

**Cómo obtener API key:**
1. Regístrate en https://platform.openai.com
2. Ve a API keys: https://platform.openai.com/api-keys
3. Crea una nueva key (recibes $5 gratis)
4. Copia la key y pégala en el simulador
"""
