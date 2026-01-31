import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Importar módulo de OpenAI (opcional)
try:
    from openai_integration import OpenAIAnalyzer, is_openai_available, get_pricing_info
    OPENAI_MODULE_AVAILABLE = True
except ImportError:
    OPENAI_MODULE_AVAILABLE = False

# ==========================================
# MOTOR DE INTELIGENCIA ARTIFICIAL
# ==========================================

class SIDEPEIntelligence:
    """Motor de IA para análisis y optimización del sistema SIDEPE"""
    
    def __init__(self):
        self.thresholds = {
            'roi_target': 20.0,  # ROI objetivo mínimo (%)
            'utilization_optimal': 85.0,
            'default_max': 5.0,
            'nucleus_dist_optimal': 85.0
        }
        
    def analyze_performance(self, df_results, params):
        """Analiza el desempeño del sistema y genera métricas de salud"""
        if df_results.empty:
            return {}
            
        final = df_results.iloc[-1]
        total_invested = params['num_users'] * params['monthly_contribution'] * 12
        net_profit = final['Rendimiento Neto Acumulado']
        roi = (net_profit / total_invested * 100) if total_invested > 0 else 0
        
        # Calcular tendencias
        recent_months = df_results.tail(3)
        growth_trend = recent_months['Crecimiento Neto del Mes'].mean()
        
        # Score de salud (0-100)
        health_score = self._calculate_health_score(roi, params, growth_trend)
        
        return {
            'roi': roi,
            'health_score': health_score,
            'growth_trend': growth_trend,
            'total_profit': net_profit,
            'profit_per_user': net_profit / params['num_users'] if params['num_users'] > 0 else 0
        }
    
    def _calculate_health_score(self, roi, params, growth_trend):
        """Calcula un score de salud del sistema (0-100)"""
        score = 50  # Base
        
        # ROI performance
        if roi >= self.thresholds['roi_target']:
            score += 20
        else:
            score += (roi / self.thresholds['roi_target']) * 20
            
        # Utilización óptima
        util_diff = abs(params['utilization_rate'] - self.thresholds['utilization_optimal'])
        score += max(0, 15 - util_diff / 5)
        
        # Morosidad
        if params['default_rate'] <= self.thresholds['default_max']:
            score += 15
        else:
            score -= (params['default_rate'] - self.thresholds['default_max']) * 2
            
        # Tendencia de crecimiento
        if growth_trend > 0:
            score += 10
            
        return min(100, max(0, score))
    
    def generate_recommendations(self, performance, params):
        """Genera recomendaciones inteligentes basadas en análisis"""
        recommendations = []
        optimizations = {}
        
        roi = performance['roi']
        health = performance['health_score']
        
        # Recomendaciones de utilización
        if params['utilization_rate'] < 75:
            recommendations.append({
                'type': 'critical',
                'category': 'Utilización',
                'message': f"⚠️ Utilización baja ({params['utilization_rate']}%). Aumentar a 85% podría incrementar ganancias en {self._calculate_impact(params, 'utilization', 85):.1f}%",
                'action': 'Implementar sistema de pre-aprobación de préstamos'
            })
            optimizations['utilization_rate'] = 85
            
        # Recomendaciones de morosidad
        if params['default_rate'] > 5:
            recommendations.append({
                'type': 'critical',
                'category': 'Riesgo',
                'message': f"🚨 Morosidad alta ({params['default_rate']}%). Reducir a 3% recuperaría ${self._calculate_recovery(params):.2f} por usuario/año",
                'action': 'Activar sistema de scoring crediticio'
            })
            optimizations['default_rate'] = 3
            
        # Recomendaciones de distribución
        if params['nucleus_dist'] < 85:
            recommendations.append({
                'type': 'opportunity',
                'category': 'Distribución',
                'message': f"💡 Núcleo en {params['nucleus_dist']}%. Aumentar a 90% optimizaría capital productivo",
                'action': f"Ajustar: FEE 5% / Núcleo 90% / FIC 5%"
            })
            optimizations['nucleus_dist'] = 90
            optimizations['fee_dist'] = 5
            optimizations['fic_dist'] = 5
            
        # Recomendaciones de escala
        if params['num_users'] < 200:
            target_users = params['num_users'] * 2
            recommendations.append({
                'type': 'growth',
                'category': 'Escalamiento',
                'message': f"📈 Con {target_users} usuarios, el ROI podría aumentar a {roi * 1.3:.1f}% por economías de escala",
                'action': 'Campaña de adquisición de usuarios'
            })
            
        # Recomendaciones de comisiones
        if params['admin_fee_pct'] > 2.0:
            recommendations.append({
                'type': 'opportunity',
                'category': 'Comisiones',
                'message': f"💰 Modelo de comisión actual: {params['admin_fee_pct']}%. Considerar cobrar 20% sobre ganancias netas",
                'action': 'Cambiar a modelo basado en performance'
            })
            
        return recommendations, optimizations
    
    def _calculate_impact(self, params, variable, new_value):
        """Calcula el impacto de cambiar una variable"""
        if variable == 'utilization':
            current = params['utilization_rate']
            return ((new_value - current) / current) * 100
        return 0
    
    def _calculate_recovery(self, params):
        """Calcula recuperación potencial reduciendo morosidad"""
        annual_contribution = params['monthly_contribution'] * 12
        nucleus_portion = annual_contribution * (params['nucleus_dist'] / 100)
        potential_growth = nucleus_portion * (params['nucleus_annual_gpm'] / 100)
        current_loss = potential_growth * (params['default_rate'] / 100)
        target_loss = potential_growth * 0.03
        return current_loss - target_loss
    
    def predict_future_cycles(self, df_results, params, num_cycles=3):
        """Predice ciclos futuros basándose en tendencias"""
        if len(df_results) < 6:
            return None
            
        # Calcular tasa promedio de crecimiento
        recent = df_results.tail(6)
        avg_growth_rate = recent['Crecimiento Neto del Mes'].mean()
        
        predictions = []
        last_value = df_results.iloc[-1]['Valor Total del Sistema']
        
        for cycle in range(1, num_cycles + 1):
            months = cycle * 12
            predicted_value = last_value + (avg_growth_rate * months)
            total_contributions = params['num_users'] * params['monthly_contribution'] * months
            predicted_profit = predicted_value - total_contributions
            predicted_roi = (predicted_profit / total_contributions * 100) if total_contributions > 0 else 0
            
            predictions.append({
                'Ciclo': cycle,
                'Valor Proyectado': predicted_value,
                'Ganancia Proyectada': predicted_profit,
                'ROI Proyectado': predicted_roi
            })
            
        return pd.DataFrame(predictions)
    
    def auto_optimize(self, params):
        """Optimiza automáticamente los parámetros"""
        optimized = params.copy()
        
        # Aplicar optimizaciones basadas en mejores prácticas
        optimized['utilization_rate'] = min(88, optimized['utilization_rate'] * 1.2)
        optimized['default_rate'] = max(2, optimized['default_rate'] * 0.6)
        optimized['nucleus_dist'] = 90
        optimized['fee_dist'] = 5
        optimized['fic_dist'] = 5
        
        return optimized

# ==========================================
# SIMULACIÓN MULTI-CICLO
# ==========================================

def run_multi_cycle_simulation(params, num_cycles=3):
    """Ejecuta simulación de múltiples ciclos (años) con evolución"""
    all_cycles = []
    
    for cycle in range(num_cycles):
        # Ajustar parámetros con aprendizaje (mejora gradual)
        if cycle > 0:
            # Mejora natural: utilización aumenta, morosidad disminuye
            params['utilization_rate'] = min(95, params['utilization_rate'] * 1.05)
            params['default_rate'] = max(2, params['default_rate'] * 0.9)
        
        df_cycle = run_simulation(
            params['num_users'], params['monthly_contribution'],
            params['utilization_rate'], params['default_rate'],
            params['admin_fee_type'], params['admin_fee_pct'], params['admin_fee_fixed'],
            params['nucleus_gpm'], params['fic_gpm'],
            params['fee_dist'], params['nucleus_dist'], params['fic_dist'],
            duration_months=12
        )
        
        # Agregar columna de ciclo
        df_cycle['Ciclo'] = cycle + 1
        df_cycle['Mes_Global'] = df_cycle['Mes'] + (cycle * 12)
        all_cycles.append(df_cycle)
    
    return pd.concat(all_cycles, ignore_index=True)

def run_simulation(
    num_users, monthly_contribution,
    utilization_rate, default_rate,
    admin_fee_type, admin_fee_pct, admin_fee_fixed,
    nucleus_gpm, fic_gpm,
    fee_dist, nucleus_dist, fic_dist,
    duration_months=12
):
    """
    Corre la simulación financiera mes a mes con las variables dadas.
    (Versión Final Corregida y Robusta)
    """
    # Convertir porcentajes de UI a decimales para el cálculo
    utilization_rate /= 100
    default_rate /= 100
    admin_fee_monthly_pct = (admin_fee_pct / 100) / 12
    nucleus_monthly_rate = nucleus_gpm / 100
    fic_monthly_rate = fic_gpm / 100
    fee_dist /= 100
    nucleus_dist /= 100
    fic_dist /= 100

    # Inicializar fondos y listas para guardar resultados
    total_fee_fund, total_nucleus_fund, total_fic_fund = 0, 0, 0
    records = []
    total_group_contribution = num_users * monthly_contribution

    for month in range(1, duration_months + 1):
        last_month_value = total_fee_fund + total_nucleus_fund + total_fic_fund

        # 1. Calcular crecimiento del capital existente (LÓGICA CORREGIDA)
        # El crecimiento solo ocurre en la porción utilizada del núcleo
        utilized_nucleus_capital = total_nucleus_fund * utilization_rate
        gross_nucleus_growth = utilized_nucleus_capital * nucleus_monthly_rate
        
        # La morosidad se aplica solo a la ganancia generada
        default_loss = gross_nucleus_growth * default_rate
        net_nucleus_growth = gross_nucleus_growth - default_loss
        
        fic_growth = total_fic_fund * fic_monthly_rate
        
        # 2. Sumar crecimiento y nuevas aportaciones
        total_fee_fund += total_group_contribution * fee_dist
        total_nucleus_fund += net_nucleus_growth + (total_group_contribution * nucleus_dist)
        total_fic_fund += fic_growth + (total_group_contribution * fic_dist)

        # 3. Calcular valor total antes de comisiones
        total_system_value_before_fee = total_fee_fund + total_nucleus_fund + total_fic_fund
        
        # 4. Deducir comisión de administración
        fee_amount = (total_system_value_before_fee * admin_fee_monthly_pct) if admin_fee_type == 'Porcentual' else admin_fee_fixed
        
        if total_system_value_before_fee > 0:
            # Deducir la comisión proporcionalmente para mantener la distribución
            factor_descuento = 1 - (fee_amount / total_system_value_before_fee)
            total_fee_fund *= factor_descuento
            total_nucleus_fund *= factor_descuento
            total_fic_fund *= factor_descuento

        # 5. Calcular valores finales del mes
        total_system_value = total_fee_fund + total_nucleus_fund + total_fic_fund
        total_contributions = total_group_contribution * month
        net_profit_accumulated = total_system_value - total_contributions
        net_growth_this_month = total_system_value - last_month_value - total_group_contribution
        
        records.append({
            "Mes": month,
            "Aportaciones Acumuladas": total_contributions,
            "Crecimiento Neto del Mes": net_growth_this_month,
            "Valor Total del Sistema": total_system_value,
            "Rendimiento Neto Acumulado": net_profit_accumulated
        })
        
    return pd.DataFrame(records)


# --- Interfaz de Usuario de Streamlit ---

st.set_page_config(layout="wide")

# Inicializar IA
ai_engine = SIDEPEIntelligence()

# Inicializar OpenAI en session state
if 'openai_enabled' not in st.session_state:
    st.session_state.openai_enabled = False
if 'openai_analyzer' not in st.session_state:
    st.session_state.openai_analyzer = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Título con indicador de IA
col_title, col_ai = st.columns([4, 1])
with col_title:
    st.title("🤖 Simulador Inteligente SIDEPE")
    st.markdown("**Sistema de análisis con IA que evalúa ciclos recurrentes y optimiza automáticamente**")

with col_ai:
    if OPENAI_MODULE_AVAILABLE:
        st.markdown("### 🔮 IA Avanzada")
        if st.session_state.openai_enabled:
            st.success("✅ Conectado")
        else:
            st.info("💤 Desactivado")

# Selector de modo
mode = st.radio(
    "Modo de Simulación:",
    ["📊 Ciclo Simple (12 meses)", "🔄 Multi-Ciclo (3 años)", "🚀 Auto-Optimizado"],
    horizontal=True
)

# --- BARRA LATERAL CON CONTROLES ---
st.sidebar.header("Parámetros del Sistema")

# === CONFIGURACIÓN DE OPENAI ===
if OPENAI_MODULE_AVAILABLE:
    with st.sidebar.expander("🔮 IA Avanzada (OpenAI)", expanded=False):
        st.markdown("**Análisis profundo con GPT**")
        
        api_key_input = st.text_input(
            "API Key de OpenAI",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Obtén tu API key en: https://platform.openai.com/api-keys"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔌 Conectar"):
                if api_key_input:
                    try:
                        analyzer = OpenAIAnalyzer(api_key=api_key_input)
                        if analyzer.test_connection():
                            st.session_state.openai_analyzer = analyzer
                            st.session_state.openai_enabled = True
                            st.success("✅ Conectado")
                        else:
                            st.error("❌ No se pudo conectar")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Ingresa tu API key")
        
        with col2:
            if st.button("🔌 Desconectar"):
                st.session_state.openai_enabled = False
                st.session_state.openai_analyzer = None
                st.info("Desconectado")
        
        if st.session_state.openai_enabled:
            st.success("✅ IA Avanzada activada")
            st.caption("Costos: ~$0.01-0.03 por análisis")
        else:
            st.info("💡 Obtén análisis profundo con GPT")
            with st.expander("Ver información de precios"):
                st.markdown(get_pricing_info())

st.sidebar.markdown("---")

# Variables de Participación
st.sidebar.subheader("1. Participación")
num_users = st.sidebar.number_input("Número de Ahorradores", min_value=1, value=100)
monthly_contribution = st.sidebar.slider("Aportación Mensual por Ahorrador ($)", 100, 5000, 400, 10)

# Variables de Costo
st.sidebar.subheader("2. Costo de Administración")
admin_fee_type = st.sidebar.radio("Tipo de Comisión", ('Porcentual', 'Fija Mensual'))
admin_fee_pct = 0.0
admin_fee_fixed = 0.0
if admin_fee_type == 'Porcentual':
    admin_fee_pct = st.sidebar.slider("Comisión de Administración Anual (%)", 0.0, 10.0, 2.5, 0.1)
else:
    admin_fee_fixed = st.sidebar.number_input("Costo Fijo Mensual ($)", min_value=0, value=500000)

# Variables de Rendimiento (Realista)
st.sidebar.subheader("3. Variables de Rendimiento (Realista)")
utilization_rate = st.sidebar.slider("Tasa de Utilización del Capital (%)", 0, 100, 65)
default_rate = st.sidebar.slider("Tasa de Morosidad (sobre ganancias) (%)", 0, 100, 8)

# Expander para configuración avanzada
with st.sidebar.expander("Configuración Avanzada del Fondo"):
    st.markdown("**Rendimiento Bruto Anual (Ideal)**")
    # Usamos el GAT del doc como base
    nucleus_annual_gpm = st.slider("Rendimiento Anual del Núcleo (%)", 10.0, 60.0, 42.6, 0.1) 
    fic_annual_gpm = st.slider("Rendimiento Anual del FIC (%)", 0.0, 30.0, 14.0, 0.1)

    st.markdown("**Distribución de la Aportación**")
    fee_dist = st.slider("Porcentaje para Fondo de Estabilidad (FEE) (%)", 0, 20, 10)
    nucleus_dist = st.slider("Porcentaje para Núcleo SIDEPE (%)", 50, 100, 80)
    fic_dist = st.slider("Porcentaje para Fondo de Inversión (FIC) (%)", 0, 30, 10)
    
    if fee_dist + nucleus_dist + fic_dist != 100:
        st.sidebar.error("La suma de la distribución debe ser 100%.")

# --- LÓGICA PRINCIPAL Y VISUALIZACIÓN ---

# Convertir rendimientos anuales a mensuales para el cálculo
nucleus_gpm = ((1 + nucleus_annual_gpm / 100)**(1/12) - 1) * 100
fic_gpm = ((1 + fic_annual_gpm / 100)**(1/12) - 1) * 100

# Empaquetar parámetros
params = {
    'num_users': num_users,
    'monthly_contribution': monthly_contribution,
    'utilization_rate': utilization_rate,
    'default_rate': default_rate,
    'admin_fee_type': admin_fee_type,
    'admin_fee_pct': admin_fee_pct,
    'admin_fee_fixed': admin_fee_fixed,
    'nucleus_gpm': nucleus_gpm,
    'fic_gpm': fic_gpm,
    'fee_dist': fee_dist,
    'nucleus_dist': nucleus_dist,
    'fic_dist': fic_dist,
    'nucleus_annual_gpm': nucleus_annual_gpm
}

if fee_dist + nucleus_dist + fic_dist == 100:
    
    # ============================================
    # EJECUTAR SIMULACIÓN SEGÚN MODO SELECCIONADO
    # ============================================
    
    if mode == "🚀 Auto-Optimizado":
        st.info("🤖 **Modo Auto-Optimizado Activado**: La IA está ajustando parámetros para maximizar rentabilidad...")
        optimized_params = ai_engine.auto_optimize(params)
        
        # Mostrar cambios
        with st.expander("Ver Optimizaciones Aplicadas por la IA"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Parámetros Originales:**")
                st.write(f"- Utilización: {params['utilization_rate']:.1f}%")
                st.write(f"- Morosidad: {params['default_rate']:.1f}%")
                st.write(f"- Distribución: FEE {params['fee_dist']}% / Núcleo {params['nucleus_dist']}% / FIC {params['fic_dist']}%")
            with col2:
                st.markdown("**Parámetros Optimizados:**")
                st.write(f"- Utilización: {optimized_params['utilization_rate']:.1f}% ✨")
                st.write(f"- Morosidad: {optimized_params['default_rate']:.1f}% ✨")
                st.write(f"- Distribución: FEE {optimized_params['fee_dist']}% / Núcleo {optimized_params['nucleus_dist']}% / FIC {optimized_params['fic_dist']}% ✨")
        
        params = optimized_params
        df_results = run_simulation(
            params['num_users'], params['monthly_contribution'],
            params['utilization_rate'], params['default_rate'],
            params['admin_fee_type'], params['admin_fee_pct'], params['admin_fee_fixed'],
            params['nucleus_gpm'], params['fic_gpm'],
            params['fee_dist'], params['nucleus_dist'], params['fic_dist']
        )
        
    elif mode == "🔄 Multi-Ciclo (3 años)":
        st.info("🔄 **Simulación Multi-Ciclo**: Evaluando 3 años con mejora continua del sistema...")
        df_results = run_multi_cycle_simulation(params, num_cycles=3)
        
    else:
        df_results = run_simulation(
            params['num_users'], params['monthly_contribution'],
            params['utilization_rate'], params['default_rate'],
            params['admin_fee_type'], params['admin_fee_pct'], params['admin_fee_fixed'],
            params['nucleus_gpm'], params['fic_gpm'],
            params['fee_dist'], params['nucleus_dist'], params['fic_dist']
        )
    
    # ============================================
    # ANÁLISIS DE IA Y RECOMENDACIONES
    # ============================================
    
    performance = ai_engine.analyze_performance(df_results, params)
    recommendations, optimizations = ai_engine.generate_recommendations(performance, params)
    
    # Dashboard de Salud del Sistema
    st.header("📊 Dashboard de Salud del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    health_color = "🟢" if performance['health_score'] >= 70 else "🟡" if performance['health_score'] >= 50 else "🔴"
    col1.metric("Score de Salud", f"{health_color} {performance['health_score']:.0f}/100")
    col2.metric("ROI Actual", f"{performance['roi']:.2f}%")
    col3.metric("Ganancia por Usuario", f"${performance['profit_per_user']:,.2f}")
    col4.metric("Tendencia", f"${performance['growth_trend']:,.2f}/mes")
    
    # Recomendaciones de la IA
    if recommendations:
        st.header("🤖 Recomendaciones de la IA")
        
        critical = [r for r in recommendations if r['type'] == 'critical']
        opportunities = [r for r in recommendations if r['type'] in ['opportunity', 'growth']]
        
        if critical:
            st.subheader("⚠️ Acciones Críticas")
            for rec in critical:
                with st.expander(f"**{rec['category']}**: {rec['message']}", expanded=True):
                    st.write(f"**Acción recomendada:** {rec['action']}")
                    if st.button(f"✨ Aplicar Optimización: {rec['category']}", key=f"apply_{rec['category']}"):
                        st.success(f"Optimización aplicada. Actualiza los parámetros en la barra lateral.")
        
        if opportunities:
            st.subheader("💡 Oportunidades de Mejora")
            for rec in opportunities:
                with st.expander(f"**{rec['category']}**: {rec['message']}"):
                    st.write(f"**Acción recomendada:** {rec['action']}")
    
    # Mostrar resultados
    st.header("📈 Resultados de la Simulación")
    
    # Asegurarse de que el dataframe no está vacío antes de calcular
    if not df_results.empty:
        final_results = df_results.iloc[-1]
        total_invested_per_person = (monthly_contribution * 12)
        net_profit_per_person = final_results["Rendimiento Neto Acumulado"] / num_users if num_users > 0 else 0
        
        if total_invested_per_person > 0:
            roi_pct = (net_profit_per_person / total_invested_per_person) * 100
        else:
            roi_pct = 0

        # Métricas principales por persona
        col1, col2, col3 = st.columns(3)
        col1.metric("Inversión Total por Persona", f"${total_invested_per_person:,.2f}")
        col2.metric("Ganancia Neta por Persona", f"${net_profit_per_person:,.2f}")
        col3.metric("Rendimiento sobre Inversión", f"{roi_pct:.2f}%")

        # Gráfico de crecimiento
        st.subheader("Crecimiento del Fondo vs. Aportaciones")
        if mode == "🔄 Multi-Ciclo (3 años)":
            chart_data = df_results[['Mes_Global', 'Aportaciones Acumuladas', 'Valor Total del Sistema']].set_index('Mes_Global')
            st.line_chart(chart_data)
            
            # Agregar gráfico de ciclos
            st.subheader("Análisis por Ciclo Anual")
            cycle_summary = df_results.groupby('Ciclo').agg({
                'Valor Total del Sistema': 'last',
                'Rendimiento Neto Acumulado': 'last'
            }).reset_index()
            cycle_summary.columns = ['Año', 'Valor Final', 'Ganancia Neta']
            st.bar_chart(cycle_summary.set_index('Año'))
        else:
            chart_data = df_results[['Mes', 'Aportaciones Acumuladas', 'Valor Total del Sistema']].set_index('Mes')
            st.line_chart(chart_data)
        
        # Predicciones futuras
        st.subheader("🔮 Predicción de Ciclos Futuros")
        predictions = ai_engine.predict_future_cycles(df_results, params, num_cycles=3)
        if predictions is not None:
            col1, col2, col3 = st.columns(3)
            for idx, pred in predictions.iterrows():
                with [col1, col2, col3][idx]:
                    st.metric(
                        f"Año {int(pred['Ciclo'])}",
                        f"${pred['Valor Proyectado']:,.0f}",
                        f"ROI: {pred['ROI Proyectado']:.1f}%"
                    )
        
        # Comparativa de escenarios
        if mode == "🚀 Auto-Optimizado":
            st.subheader("📊 Comparativa: Original vs Optimizado")
            
            # Ejecutar simulación original para comparar
            df_original = run_simulation(
                num_users, monthly_contribution,
                utilization_rate, default_rate,
                admin_fee_type, admin_fee_pct, admin_fee_fixed,
                nucleus_gpm, fic_gpm,
                fee_dist, nucleus_dist, fic_dist
            )
            
            if not df_original.empty:
                original_final = df_original.iloc[-1]
                optimized_final = df_results.iloc[-1]
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Escenario", "Original", "")
                col1.metric("Valor Final", f"${original_final['Valor Total del Sistema']:,.2f}")
                col1.metric("Ganancia", f"${original_final['Rendimiento Neto Acumulado']:,.2f}")
                
                col2.metric("Escenario", "Optimizado ✨", "")
                col2.metric("Valor Final", f"${optimized_final['Valor Total del Sistema']:,.2f}")
                col2.metric("Ganancia", f"${optimized_final['Rendimiento Neto Acumulado']:,.2f}")
                
                improvement = ((optimized_final['Rendimiento Neto Acumulado'] - original_final['Rendimiento Neto Acumulado']) / original_final['Rendimiento Neto Acumulado'] * 100) if original_final['Rendimiento Neto Acumulado'] > 0 else 0
                col3.metric("Mejora", f"+{improvement:.1f}%", "Por optimización IA")
                col3.metric("Ganancia Extra", f"${optimized_final['Rendimiento Neto Acumulado'] - original_final['Rendimiento Neto Acumulado']:,.2f}")

        # Tabla detallada mes a mes
        with st.expander("Ver tabla detallada de crecimiento mensual"):
            display_cols = ['Mes', 'Aportaciones Acumuladas', 'Crecimiento Neto del Mes', 
                          'Valor Total del Sistema', 'Rendimiento Neto Acumulado']
            if 'Ciclo' in df_results.columns:
                display_cols.insert(0, 'Ciclo')
            
            st.dataframe(df_results[display_cols].style.format({
                "Aportaciones Acumuladas": "${:,.2f}",
                "Crecimiento Neto del Mes": "${:,.2f}",
                "Valor Total del Sistema": "${:,.2f}",
                "Rendimiento Neto Acumulado": "${:,.2f}"
            }))
        
        # Información adicional de IA
        with st.expander("🧠 Análisis Detallado de la IA"):
            st.markdown(f"""
            **Métricas de Performance:**
            - Score de salud del sistema: {performance['health_score']:.1f}/100
            - ROI anual: {performance['roi']:.2f}%
            - Tendencia de crecimiento mensual: ${performance['growth_trend']:,.2f}
            - Ganancia total: ${performance['total_profit']:,.2f}
            - Ganancia por usuario: ${performance['profit_per_user']:,.2f}
            
            **Recomendaciones aplicadas:** {len(recommendations)}
            """)
            
            if optimizations:
                st.markdown("**Parámetros que la IA recomienda ajustar:**")
                for key, value in optimizations.items():
                    st.write(f"- {key}: {value}")
        
        # ============================================
        # FUNCIONALIDADES AVANZADAS CON OPENAI
        # ============================================
        
        if st.session_state.openai_enabled and st.session_state.openai_analyzer:
            st.markdown("---")
            st.header("🔮 Análisis Avanzado con IA (OpenAI GPT)")
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Análisis Profundo", 
                "📄 Generar Reporte", 
                "💬 Chat Asistente",
                "🎯 Optimización Personalizada"
            ])
            
            # Tab 1: Análisis Profundo
            with tab1:
                st.subheader("Análisis Profundo con GPT")
                st.markdown("GPT analizará todos los datos y contexto para dar insights que el sistema de reglas no puede detectar.")
                
                if st.button("🔍 Analizar con GPT", key="deep_analysis"):
                    with st.spinner("🤖 Analizando con GPT..."):
                        # Preparar datos
                        final_row = df_results.iloc[-1] if not df_results.empty else {}
                        analysis_data = {
                            'roi': performance.get('roi', 0),
                            'health_score': performance.get('health_score', 0),
                            'final_value': final_row.get('Valor Total del Sistema', 0),
                            'net_profit': final_row.get('Rendimiento Neto Acumulado', 0),
                            'profit_per_user': performance.get('profit_per_user', 0)
                        }
                        
                        analysis = st.session_state.openai_analyzer.analyze_deep(analysis_data, params)
                        st.markdown(analysis)
                        st.caption("💡 Análisis generado por GPT-4o-mini")
            
            # Tab 2: Generar Reporte
            with tab2:
                st.subheader("Generador de Reportes Profesionales")
                
                report_type = st.selectbox(
                    "Tipo de reporte:",
                    ["ejecutivo", "tecnico", "inversionista"],
                    format_func=lambda x: {
                        "ejecutivo": "📊 Ejecutivo (CEO/Directores)",
                        "tecnico": "🔧 Técnico (Operaciones)",
                        "inversionista": "💰 Inversionista (Pitch)"
                    }[x]
                )
                
                if st.button("📄 Generar Reporte", key="generate_report"):
                    with st.spinner("📝 Generando reporte profesional..."):
                        final_row = df_results.iloc[-1] if not df_results.empty else {}
                        report_data = {
                            'roi': performance.get('roi', 0),
                            'final_value': final_row.get('Valor Total del Sistema', 0),
                            'net_profit': final_row.get('Rendimiento Neto Acumulado', 0)
                        }
                        
                        report = st.session_state.openai_analyzer.generate_report(
                            report_data, params, format=report_type
                        )
                        st.markdown(report)
                        
                        # Botón para descargar
                        st.download_button(
                            label="💾 Descargar Reporte (MD)",
                            data=report,
                            file_name=f"reporte_sidepe_{report_type}_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )
            
            # Tab 3: Chat Asistente
            with tab3:
                st.subheader("💬 Chat con Asistente Financiero")
                st.markdown("Pregunta lo que quieras sobre tu simulación. GPT responderá basándose en tus datos.")
                
                # Mostrar historial
                for i, (question, answer) in enumerate(st.session_state.chat_history):
                    with st.chat_message("user"):
                        st.write(question)
                    with st.chat_message("assistant"):
                        st.write(answer)
                
                # Input de pregunta
                user_question = st.text_input(
                    "Tu pregunta:",
                    placeholder="Ej: ¿Por qué mi ROI es bajo? ¿Cómo puedo duplicar usuarios?"
                )
                
                if st.button("💬 Enviar", key="chat_send") and user_question:
                    with st.spinner("🤔 GPT está pensando..."):
                        context = {
                            'params': params,
                            'performance': performance,
                            'recommendations_count': len(recommendations)
                        }
                        
                        answer = st.session_state.openai_analyzer.chat_advisor(user_question, context)
                        
                        # Agregar al historial
                        st.session_state.chat_history.append((user_question, answer))
                        st.rerun()
                
                if st.button("🗑️ Limpiar Chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Tab 4: Optimización Personalizada
            with tab4:
                st.subheader("🎯 Optimización con Restricciones Personalizadas")
                st.markdown("Describe tus restricciones y GPT optimizará los parámetros considerándolas.")
                
                constraints = st.text_area(
                    "Describe tus restricciones:",
                    placeholder="""Ejemplo:
- Solo puedo tener máximo 150 usuarios (capacidad operativa)
- Capital inicial: $80,000
- Equipo de 2 personas
- No puedo aprobar más de 30 préstamos/mes
- Clientes: micro-empresarios zona rural""",
                    height=150
                )
                
                if st.button("🚀 Optimizar con GPT", key="optimize_gpt") and constraints:
                    with st.spinner("🧮 Optimizando parámetros..."):
                        optimized_params = st.session_state.openai_analyzer.optimize_with_constraints(
                            params, constraints
                        )
                        
                        if 'error' not in optimized_params:
                            st.success("✅ Parámetros optimizados:")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Parámetros Actuales:**")
                                st.json(params)
                            with col2:
                                st.markdown("**Parámetros Optimizados:**")
                                st.json(optimized_params)
                            
                            st.info("💡 Ajusta los parámetros en la barra lateral y ejecuta una nueva simulación")
                        else:
                            st.error(f"Error: {optimized_params['error']}")
        
    else:
        st.error("No se pudieron generar resultados. Revisa los parámetros.")
else:
    st.warning("Ajusta la distribución del fondo en la barra lateral para que sume 100%.")

# Footer con info
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("💡 **Tip**: Usa el modo Auto-Optimizado para que la IA ajuste automáticamente los parámetros hacia el mejor rendimiento.")
with col2:
    if OPENAI_MODULE_AVAILABLE and st.session_state.openai_enabled:
        st.success("🔮 IA Avanzada: Activada | Análisis profundo disponible")
    elif OPENAI_MODULE_AVAILABLE:
        st.info("🔮 IA Avanzada: Disponible | Configura tu API key en la barra lateral")
    else:
        st.caption("Sistema de reglas activado (sin OpenAI)")