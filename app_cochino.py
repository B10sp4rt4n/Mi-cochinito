import streamlit as st
import pandas as pd

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
st.title("Simulador de Escenarios SIDEPE")
st.markdown("Utiliza los controles en la barra lateral para definir las variables del sistema y ver el impacto en los resultados a 12 meses.")

# --- BARRA LATERAL CON CONTROLES ---
st.sidebar.header("Parámetros del Sistema")

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
# (1 + GAT_anual)^(1/12) - 1
nucleus_gpm = ((1 + nucleus_annual_gpm / 100)**(1/12) - 1) * 100
fic_gpm = ((1 + fic_annual_gpm / 100)**(1/12) - 1) * 100

if fee_dist + nucleus_dist + fic_dist == 100:
    # Correr la simulación
    df_results = run_simulation(
        num_users, monthly_contribution,
        utilization_rate, default_rate,
        admin_fee_type, admin_fee_pct, admin_fee_fixed,
        nucleus_gpm, fic_gpm,
        fee_dist, nucleus_dist, fic_dist
    )

    # Mostrar resultados
    st.header("Resultados de la Simulación a 12 Meses")
    
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
        chart_data = df_results[['Mes', 'Aportaciones Acumuladas', 'Valor Total del Sistema']].set_index('Mes')
        st.line_chart(chart_data)

        # Tabla detallada mes a mes
        with st.expander("Ver tabla detallada de crecimiento mensual"):
            st.dataframe(df_results.style.format({
                "Aportaciones Acumuladas": "${:,.2f}",
                "Crecimiento Neto del Mes": "${:,.2f}",
                "Valor Total del Sistema": "${:,.2f}",
                "Rendimiento Neto Acumulado": "${:,.2f}"
            }))
    else:
        st.error("No se pudieron generar resultados. Revisa los parámetros.")
else:
    st.warning("Ajusta la distribución del fondo en la barra lateral para que sume 100%.")