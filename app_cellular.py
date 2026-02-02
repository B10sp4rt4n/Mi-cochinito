"""
Interfaz Streamlit para Sistema de Arquitectura Celular
========================================================
Visualización y control del sistema de ahorro con arquitectura celular fractal
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from cellular_architecture import (
    MasterNode, ConsolidatorNode, SavingsCell, ValueSource,
    RegulationRules, RiskLevel, CellState, create_example_system
)
import json
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Sistema Celular SIDEPE",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .big-metric { font-size: 24px; font-weight: bold; }
    .risk-critical { color: #dc3545; }
    .risk-high { color: #fd7e14; }
    .risk-medium { color: #ffc107; }
    .risk-low { color: #20c997; }
    .risk-very-low { color: #28a745; }
    .cell-active { background-color: #d4edda; padding: 10px; border-radius: 5px; }
    .cell-suspended { background-color: #f8d7da; padding: 10px; border-radius: 5px; }
    .cell-recovering { background-color: #fff3cd; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa el estado de la sesión"""
    if 'system' not in st.session_state:
        st.session_state.system = None
    if 'simulation_run' not in st.session_state:
        st.session_state.simulation_run = False
    if 'current_month' not in st.session_state:
        st.session_state.current_month = 0


def create_custom_system():
    """Interfaz para crear sistema personalizado"""
    st.subheader("🏗️ Crear Sistema Personalizado")
    
    system_name = st.text_input("Nombre del Sistema", "Mi Sistema de Ahorro")
    
    num_consolidators = st.number_input("Número de Consolidadores (Regiones/Grupos)", 1, 10, 2)
    
    consolidators_data = []
    
    for i in range(num_consolidators):
        with st.expander(f"⚙️ Configurar Consolidador {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                cons_name = st.text_input(f"Nombre Consolidador {i+1}", f"Grupo {i+1}", key=f"cons_name_{i}")
                num_cells = st.number_input(f"Número de Células", 1, 20, 3, key=f"num_cells_{i}")
            
            cells_data = []
            for j in range(num_cells):
                with st.expander(f"🔬 Célula {j+1}"):
                    cell_name = st.text_input(f"Nombre", f"Célula {chr(65+j)}", key=f"cell_name_{i}_{j}")
                    num_members = st.number_input(f"Miembros", 10, 1000, 50, key=f"members_{i}_{j}")
                    contribution = st.number_input(f"Aportación Mensual por Miembro ($)", 10, 10000, 1000, key=f"contrib_{i}_{j}")
                    
                    st.write("**Fuentes de Valor:**")
                    num_sources = st.number_input("Número de Fuentes", 1, 5, 3, key=f"sources_{i}_{j}")
                    
                    sources = []
                    for k in range(num_sources):
                        scol1, scol2, scol3 = st.columns(3)
                        with scol1:
                            src_name = st.text_input(f"Fuente {k+1}", f"Fuente {k+1}", key=f"src_name_{i}_{j}_{k}")
                            src_contrib_pct = st.slider(f"% Aportación", 0, 100, 30, key=f"src_pct_{i}_{j}_{k}")
                        with scol2:
                            src_gpm = st.slider(f"GPM %", 0.0, 10.0, 2.0, 0.1, key=f"src_gpm_{i}_{j}_{k}")
                            src_util = st.slider(f"Utilización %", 0, 100, 85, key=f"src_util_{i}_{j}_{k}")
                        with scol3:
                            src_risk = st.slider(f"Factor Riesgo", 0.5, 1.5, 1.0, 0.05, key=f"src_risk_{i}_{j}_{k}")
                        
                        sources.append({
                            'name': src_name,
                            'contrib_pct': src_contrib_pct,
                            'gpm': src_gpm,
                            'utilization': src_util,
                            'risk_factor': src_risk
                        })
                    
                    cells_data.append({
                        'name': cell_name,
                        'members': num_members,
                        'contribution': contribution,
                        'sources': sources
                    })
            
            consolidators_data.append({
                'name': cons_name,
                'cells': cells_data
            })
    
    if st.button("🚀 Crear Sistema", type="primary"):
        # Construir sistema
        master = MasterNode(system_name)
        
        for i, cons_data in enumerate(consolidators_data):
            consolidator = ConsolidatorNode(f"CON-{i+1}", cons_data['name'])
            
            for j, cell_data in enumerate(cons_data['cells']):
                cell = SavingsCell(f"CELL-{i+1}-{j+1}", cell_data['name'], cell_data['members'])
                
                # Agregar fuentes
                for k, src_data in enumerate(cell_data['sources']):
                    monthly_contrib = cell_data['contribution'] * cell_data['members'] * (src_data['contrib_pct'] / 100)
                    
                    source = ValueSource(
                        source_id=f"SRC-{i+1}-{j+1}-{k+1}",
                        name=src_data['name'],
                        initial_capital=0,
                        monthly_contribution=monthly_contrib,
                        gpm_rate=src_data['gpm'],
                        utilization_rate=src_data['utilization'],
                        risk_factor=src_data['risk_factor']
                    )
                    cell.add_value_source(source)
                
                consolidator.add_cell(cell)
            
            master.add_consolidator(consolidator)
        
        st.session_state.system = master
        st.session_state.simulation_run = False
        st.success(f"✅ Sistema '{system_name}' creado exitosamente!")
        st.rerun()


def display_simple_dashboard():
    """Dashboard simplificado para modo básico"""
    system = st.session_state.system
    
    st.subheader("🏠 Panel Principal")
    
    if not system.system_history:
        st.warning("⚠️ Aún no has ejecutado una simulación")
        st.info("👉 Ve a '▶️ Ejecutar Simulación' en el menú para empezar")
        
        # Mostrar info básica
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏢 Regiones", len(system.consolidator_nodes))
        with col2:
            st.metric("👥 Grupos", system.get_total_cells())
        with col3:
            total_members = sum(
                cell.num_members 
                for cons in system.consolidator_nodes.values() 
                for cell in cons.cells.values()
            )
            st.metric("🧑‍🤝‍🧑 Personas Total", total_members)
        
        return
    
    # Con simulación ejecutada
    last_record = system.system_history[-1]
    
    # Métricas principales en grande
    st.markdown("### 💰 Resultados de la Simulación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "💵 Dinero Total",
            f"${last_record['total_system_balance']:,.0f}",
            help="Todo el dinero acumulado en el sistema"
        )
        
        roi = (last_record['total_system_profit'] / (last_record['total_system_balance'] - last_record['total_system_profit']) * 100)
        st.metric(
            "📈 Rendimiento (ROI)",
            f"{roi:.1f}%",
            help="Porcentaje de ganancia sobre el dinero aportado"
        )
    
    with col2:
        st.metric(
            "💎 Ganancias",
            f"${last_record['total_system_profit']:,.0f}",
            help="Dinero ganado por intereses y rendimientos"
        )
        
        health = last_record['system_health_score']
        health_emoji = "🟢" if health > 70 else "🟡" if health > 50 else "🔴"
        st.metric(
            f"{health_emoji} Salud del Sistema",
            f"{health:.0f}/100",
            help="Qué tan saludable está el sistema (100 = perfecto)"
        )
    
    # Métricas de rendimiento gradual
    st.markdown("---")
    st.markdown("### 📊 Rendimientos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular rendimiento mensual
    df = system.export_to_dataframe()
    df['Rendimiento Mensual'] = df['Ganancia Total'].diff().fillna(df['Ganancia Total'])
    
    # Calcular capital aportado (estimación basada en contribuciones)
    total_monthly_contribution = sum(
        source.monthly_contribution
        for cons in system.consolidator_nodes.values()
        for cell in cons.cells.values()
        for source in cell.value_sources.values()
    )
    months = len(system.system_history)
    capital_aportado = total_monthly_contribution * months
    
    with col1:
        roi_total = (last_record['total_system_profit'] / capital_aportado * 100) if capital_aportado > 0 else 0
        st.metric(
            "📊 ROI Total",
            f"{roi_total:.2f}%",
            help="Rendimiento total sobre el capital aportado"
        )
    
    with col2:
        roi_mensual = roi_total / months if months > 0 else 0
        st.metric(
            "📅 ROI Mensual Promedio",
            f"{roi_mensual:.2f}%",
            help="ROI dividido entre los meses simulados"
        )
    
    with col3:
        ultimo_rendimiento = df['Rendimiento Mensual'].iloc[-1] if len(df) > 0 else 0
        st.metric(
            "💹 Último Mes",
            f"${ultimo_rendimiento:,.0f}",
            help="Rendimiento del mes más reciente"
        )
    
    with col4:
        promedio_mensual = df['Rendimiento Mensual'].mean() if len(df) > 0 else 0
        st.metric(
            "📈 Promedio Mensual",
            f"${promedio_mensual:,.0f}",
            help="Rendimiento promedio por mes"
        )
    
    # Gráfico simple
    st.markdown("---")
    st.markdown("### 📈 Crecimiento del Dinero")
    
    df = system.export_to_dataframe()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Balance Total'],
        mode='lines+markers',
        name='Dinero Total',
        line=dict(color='#1f77b4', width=3),
        fill='tozeroy',
        hovertemplate='<b>Mes %{x}</b><br>Dinero: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Dinero Total ($)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Resumen por grupos
    st.markdown("---")
    st.markdown("### 👥 Resumen por Grupos")
    
    for cons in system.consolidator_nodes.values():
        with st.expander(f"📍 {cons.name}"):
            cols = st.columns(len(cons.cells))
            for idx, (cell_id, cell) in enumerate(cons.cells.items()):
                with cols[idx]:
                    state_emoji = "✅" if cell.state.value == "active" else "⚠️"
                    st.markdown(f"**{state_emoji} {cell.name}**")
                    st.write(f"👥 {cell.num_members} personas")
                    st.write(f"💰 ${cell.get_total_balance():,.0f}")
                    health = cell.get_health_score()
                    health_emoji = "🟢" if health > 70 else "🟡" if health > 50 else "🔴"
                    st.write(f"{health_emoji} {health:.0f}/100")


def display_simple_results():
    """Vista simplificada de resultados"""
    system = st.session_state.system
    
    st.subheader("📊 Resultados Detallados")
    
    if not system.system_history:
        st.warning("⚠️ No hay simulación ejecutada")
        st.info("👉 Ve a '▶️ Ejecutar Simulación' primero")
        return
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Gráficos", "📊 ROI y Rendimientos", "📋 Tabla de Datos", "💡 Análisis"])
    
    with tab1:
        df = system.export_to_dataframe()
        
        # Gráfico de balance
        st.markdown("#### 💰 Evolución del Dinero")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['Mes'], y=df['Balance Total'],
            mode='lines+markers',
            name='Balance Total',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy'
        ))
        fig1.update_layout(
            xaxis_title="Mes",
            yaxis_title="Dinero ($)",
            height=350
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Calcular rendimiento mensual (diferencia)
        df['Rendimiento Mensual'] = df['Ganancia Total'].diff().fillna(df['Ganancia Total'])
        
        # Gráfico de rendimientos graduales y totales
        st.markdown("#### 💎 Rendimientos Graduales y Totales")
        fig2 = go.Figure()
        
        # Barras para rendimiento mensual
        fig2.add_trace(go.Bar(
            x=df['Mes'],
            y=df['Rendimiento Mensual'],
            marker_color='#28a745',
            name='Rendimiento Mensual',
            yaxis='y'
        ))
        
        # Línea para ganancia acumulada
        fig2.add_trace(go.Scatter(
            x=df['Mes'],
            y=df['Ganancia Total'],
            mode='lines+markers',
            name='Ganancia Acumulada',
            line=dict(color='#ff7f0e', width=3),
            yaxis='y2'
        ))
        
        fig2.update_layout(
            xaxis_title="Mes",
            yaxis=dict(title="Rendimiento Mensual ($)", side='left'),
            yaxis2=dict(title="Ganancia Acumulada ($)", overlaying='y', side='right'),
            height=400,
            legend=dict(x=0.01, y=0.99),
            hovermode='x unified'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Estadísticas de rendimiento
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Rendimiento Mensual Promedio", f"${df['Rendimiento Mensual'].mean():,.0f}")
        with col2:
            st.metric("🔝 Mejor Mes", f"${df['Rendimiento Mensual'].max():,.0f}")
        with col3:
            st.metric("⬇️ Peor Mes", f"${df['Rendimiento Mensual'].min():,.0f}")
    
    with tab2:
        df = system.export_to_dataframe()
        df['Rendimiento Mensual'] = df['Ganancia Total'].diff().fillna(df['Ganancia Total'])
        
        # Calcular capital aportado
        total_monthly_contribution = sum(
            source.monthly_contribution
            for cons in system.consolidator_nodes.values()
            for cell in cons.cells.values()
            for source in cell.value_sources.values()
        )
        df['Capital Aportado'] = total_monthly_contribution * df['Mes']
        df['ROI Acumulado (%)'] = (df['Ganancia Total'] / df['Capital Aportado'] * 100).fillna(0)
        
        st.markdown("#### 📊 ROI y Rendimientos por Mes")
        
        # Gráfico de ROI
        fig_roi = go.Figure()
        fig_roi.add_trace(go.Scatter(
            x=df['Mes'],
            y=df['ROI Acumulado (%)'],
            mode='lines+markers',
            name='ROI Acumulado',
            line=dict(color='#9467bd', width=3),
            fill='tozeroy'
        ))
        fig_roi.update_layout(
            title="ROI Acumulado por Mes",
            xaxis_title="Mes",
            yaxis_title="ROI (%)",
            height=350
        )
        st.plotly_chart(fig_roi, use_container_width=True)
        
        # Tabla de rendimientos
        st.markdown("#### 📋 Tabla de Rendimientos")
        render_df = df[['Mes', 'Rendimiento Mensual', 'Ganancia Total', 'Capital Aportado', 'ROI Acumulado (%)']].copy()
        st.dataframe(
            render_df.style.format({
                'Rendimiento Mensual': '${:,.2f}',
                'Ganancia Total': '${:,.2f}',
                'Capital Aportado': '${:,.2f}',
                'ROI Acumulado (%)': '{:.2f}%'
            }),
            use_container_width=True,
            height=300
        )
        
        # Métricas finales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ROI Inicial", f"{df['ROI Acumulado (%)'].iloc[0]:.2f}%")
        with col2:
            st.metric("ROI Final", f"{df['ROI Acumulado (%)'].iloc[-1]:.2f}%")
        with col3:
            roi_growth = df['ROI Acumulado (%)'].iloc[-1] - df['ROI Acumulado (%)'].iloc[0]
            st.metric("Crecimiento ROI", f"{roi_growth:.2f}%")
    
    with tab3:
        st.markdown("#### 📋 Tabla Completa de Resultados")
        df = system.export_to_dataframe()
        st.dataframe(
            df.style.format({
                'Balance Total': '${:,.2f}',
                'Ganancia Total': '${:,.2f}',
                'Health Score': '{:.1f}',
                'Riesgo Global': '{:.1f}%'
            }),
            use_container_width=True,
            height=400
        )
        
        # Botón de descarga
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Descargar CSV",
            csv,
            "resultados_simulacion.csv",
            "text/csv"
        )
    
    with tab4:
        last_record = system.system_history[-1]
        
        st.markdown("#### 💡 Análisis Rápido")
        
        # Análisis positivo/negativo
        roi = (last_record['total_system_profit'] / (last_record['total_system_balance'] - last_record['total_system_profit']) * 100)
        
        if roi > 15:
            st.success(f"✅ **Excelente rendimiento:** {roi:.1f}% de ROI")
        elif roi > 10:
            st.info(f"✓ **Buen rendimiento:** {roi:.1f}% de ROI")
        else:
            st.warning(f"⚠️ **Rendimiento bajo:** {roi:.1f}% de ROI")
        
        # Health
        health = last_record['system_health_score']
        if health > 70:
            st.success(f"✅ **Sistema saludable:** {health:.0f}/100")
        elif health > 50:
            st.info(f"⚠️ **Sistema aceptable:** {health:.0f}/100")
        else:
            st.error(f"❌ **Sistema en riesgo:** {health:.0f}/100")
        
        # Grupos activos
        active_pct = (last_record['active_cells'] / last_record['total_cells'] * 100)
        if active_pct == 100:
            st.success(f"✅ **Todos los grupos activos:** {last_record['active_cells']}/{last_record['total_cells']}")
        else:
            st.warning(f"⚠️ **Algunos grupos suspendidos:** {last_record['active_cells']}/{last_record['total_cells']} activos")


def display_system_overview():
    """Muestra vista general del sistema"""
    system = st.session_state.system
    
    if not system.system_history:
        st.warning("⚠️ No hay datos de simulación")
        st.info("👉 Ve a la página **'⚡ Simulación'** en el menú lateral y ejecuta una simulación primero")
        
        # Mostrar información básica del sistema sin simulación
        st.markdown("---")
        st.subheader("📊 Información del Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏢 Consolidadores", len(system.consolidator_nodes))
        
        with col2:
            st.metric("🔬 Células Totales", system.get_total_cells())
        
        with col3:
            balance = system.get_total_balance()
            st.metric("💰 Balance Inicial", f"${balance:,.2f}")
        
        return
    
    # Obtener último estado
    last_record = system.system_history[-1]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Balance Total",
            f"${last_record['total_system_balance']:,.2f}",
            f"+${last_record['total_system_profit']:,.2f}"
        )
    
    with col2:
        health_score = last_record['system_health_score']
        st.metric(
            "🏥 Health Score",
            f"{health_score:.1f}/100",
            delta=f"{health_score - 50:.1f}" if len(system.system_history) > 1 else None
        )
    
    with col3:
        risk_color_map = {
            'VERY_LOW': '🟢', 'LOW': '🟡', 'MEDIUM': '🟠', 'HIGH': '🔴', 'CRITICAL': '⚫'
        }
        risk_icon = risk_color_map.get(last_record['global_risk_level'], '⚪')
        st.metric(
            "⚠️ Riesgo Global",
            f"{risk_icon} {last_record['global_risk']:.1f}%",
            last_record['global_risk_level']
        )
    
    with col4:
        st.metric(
            "🔬 Células Activas",
            f"{last_record['active_cells']}/{last_record['total_cells']}",
            f"{(last_record['active_cells']/last_record['total_cells']*100):.0f}%"
        )
    
    # Gráficos
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de evolución de balance
        df = system.export_to_dataframe()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Mes'], y=df['Balance Total'],
            mode='lines+markers',
            name='Balance Total',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            title="📈 Evolución del Balance Total",
            xaxis_title="Mes",
            yaxis_title="Balance ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de riesgo vs health
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Mes'], y=df['Health Score'],
            mode='lines+markers',
            name='Health Score',
            line=dict(color='#28a745', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['Mes'], y=df['Riesgo Global'],
            mode='lines+markers',
            name='Riesgo Global',
            line=dict(color='#dc3545', width=2),
            yaxis='y2'
        ))
        fig.update_layout(
            title="🏥 Health Score vs Riesgo",
            xaxis_title="Mes",
            yaxis=dict(title="Health Score", side='left'),
            yaxis2=dict(title="Riesgo (%)", side='right', overlaying='y'),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)


def display_consolidators_view():
    """Vista de consolidadores"""
    system = st.session_state.system
    
    st.subheader("🏢 Consolidadores del Sistema")
    
    if not system.system_history:
        st.info("💡 Ejecuta una simulación primero para ver métricas detalladas")
    
    for cons_id, consolidator in system.consolidator_nodes.items():
        with st.expander(f"📊 {consolidator.name} ({cons_id})", expanded=True):
            # Métricas del consolidador
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Balance", f"${consolidator.get_total_balance():,.2f}")
            with col2:
                profit = consolidator.get_total_profit()
                st.metric("Ganancia", f"${profit:,.2f}")
            with col3:
                health = consolidator.get_average_health()
                st.metric("Health Promedio", f"{health:.1f}")
            with col4:
                st.metric("Células", f"{len(consolidator.cells)}")
            
            # Si hay historial, mostrar distribución de riesgo
            if system.system_history:
                cells_by_risk = consolidator.get_cells_by_risk()
                
                st.write("**Distribución de Células por Riesgo:**")
                risk_data = {
                    'Nivel': [],
                    'Células': [],
                    'Color': []
                }
                color_map = {
                    'VERY_LOW': '#28a745',
                    'LOW': '#20c997',
                    'MEDIUM': '#ffc107',
                    'HIGH': '#fd7e14',
                    'CRITICAL': '#dc3545'
                }
                
                for risk_level, cell_ids in cells_by_risk.items():
                    if len(cell_ids) > 0:
                        risk_data['Nivel'].append(risk_level.replace('_', ' '))
                        risk_data['Células'].append(len(cell_ids))
                        risk_data['Color'].append(color_map.get(risk_level, '#6c757d'))
                
                if risk_data['Nivel']:
                    fig = go.Figure(data=[go.Bar(
                        x=risk_data['Nivel'],
                        y=risk_data['Células'],
                        marker_color=risk_data['Color'],
                        text=risk_data['Células'],
                        textposition='auto'
                    )])
                    fig.update_layout(
                        title=f"Células por Nivel de Riesgo - {consolidator.name}",
                        xaxis_title="Nivel de Riesgo",
                        yaxis_title="Número de Células",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Mostrar lista de células sin simulación
                st.write(f"**Células en este consolidador:** {len(consolidator.cells)}")
                for cell_id, cell in consolidator.cells.items():
                    st.write(f"- {cell.name} ({cell.num_members} miembros, {len(cell.value_sources)} fuentes)")



def display_cells_detail():
    """Vista detallada de células"""
    system = st.session_state.system
    
    st.subheader("🔬 Células del Sistema")
    
    # Recopilar todas las células
    all_cells = []
    for consolidator in system.consolidator_nodes.values():
        for cell in consolidator.cells.values():
            cell_state = cell.export_state()
            cell_state['consolidator'] = consolidator.name
            all_cells.append(cell_state)
    
    # Crear DataFrame
    cells_df = pd.DataFrame([
        {
            'ID': c['cell_id'],
            'Nombre': c['name'],
            'Consolidador': c['consolidator'],
            'Estado': c['state'],
            'Miembros': c['num_members'],
            'Balance': c['total_balance'],
            'Ganancia': c['total_profit'],
            'Health': c['health_score'],
            'Riesgo': c['risk_metrics']['composite'],
            'Nivel Riesgo': c['risk_metrics']['level'],
            'Fuentes': c['num_sources']
        }
        for c in all_cells
    ])
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_state = st.multiselect(
            "Filtrar por Estado",
            cells_df['Estado'].unique(),
            default=cells_df['Estado'].unique()
        )
    with col2:
        filter_risk = st.multiselect(
            "Filtrar por Nivel de Riesgo",
            cells_df['Nivel Riesgo'].unique(),
            default=cells_df['Nivel Riesgo'].unique()
        )
    
    # Aplicar filtros
    filtered_df = cells_df[
        (cells_df['Estado'].isin(filter_state)) &
        (cells_df['Nivel Riesgo'].isin(filter_risk))
    ]
    
    # Mostrar tabla con formato
    st.dataframe(
        filtered_df.style.format({
            'Balance': '${:,.2f}',
            'Ganancia': '${:,.2f}',
            'Health': '{:.1f}',
            'Riesgo': '{:.1f}%'
        }).background_gradient(subset=['Health'], cmap='RdYlGn')
        .background_gradient(subset=['Riesgo'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=400
    )
    
    # Gráfico de dispersión: Health vs Riesgo
    st.markdown("---")
    
    fig = px.scatter(
        filtered_df,
        x='Riesgo',
        y='Health',
        size='Balance',
        color='Nivel Riesgo',
        hover_data=['Nombre', 'Consolidador', 'Miembros'],
        title="🎯 Mapa de Riesgo vs Salud (tamaño = balance)",
        color_discrete_map={
            'VERY_LOW': '#28a745',
            'LOW': '#20c997',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
    )
    fig.update_layout(
        xaxis_title="Riesgo Compuesto (%)",
        yaxis_title="Health Score"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detalle de célula seleccionada
    st.markdown("---")
    st.subheader("🔍 Detalle de Célula")
    
    selected_cell_id = st.selectbox(
        "Seleccionar Célula",
        filtered_df['ID'].tolist()
    )
    
    if selected_cell_id:
        cell_detail = next(c for c in all_cells if c['cell_id'] == selected_cell_id)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {cell_detail['name']}")
            st.write(f"**Estado:** {cell_detail['state']}")
            st.write(f"**Miembros:** {cell_detail['num_members']}")
            
            # Fuentes de valor
            st.markdown("#### 💎 Fuentes de Valor")
            sources_df = pd.DataFrame(cell_detail['sources'])
            st.dataframe(
                sources_df.style.format({
                    'balance': '${:,.2f}',
                    'profit': '${:,.2f}'
                }),
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 📊 Métricas de Riesgo")
            risk_metrics = cell_detail['risk_metrics']
            
            st.metric("Riesgo Compuesto", f"{risk_metrics['composite']:.1f}%")
            st.metric("Nivel", risk_metrics['level'])
            st.write(f"**Default Rate:** {risk_metrics['default_rate']:.2f}%")
            st.write(f"**Volatilidad:** {risk_metrics['volatility']:.2f}%")
            st.write(f"**Concentración:** {risk_metrics['concentration']:.2f}%")
            st.write(f"**Liquidez:** {risk_metrics['liquidity']:.2f}%")


def run_simulation_interface():
    """Interfaz de simulación"""
    st.subheader("⚡ Ejecutar Simulación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_months = st.slider("Número de Meses a Simular", 1, 60, 12)
    
    with col2:
        add_shocks = st.checkbox("Agregar Shocks Externos", False)
    
    shocks_data = None
    if add_shocks:
        st.markdown("#### 🌪️ Configurar Shocks Externos")
        shock_month = st.number_input("Mes del Shock", 1, num_months, 6)
        
        st.write("Seleccionar células afectadas:")
        # Aquí se podría expandir para configurar shocks específicos
        st.info("Funcionalidad de shocks en desarrollo avanzado")
    
    if st.button("▶️ EJECUTAR SIMULACIÓN", type="primary"):
        with st.spinner("Simulando sistema celular..."):
            # Ejecutar simulación
            system = st.session_state.system
            results = system.simulate_multiple_months(num_months, shocks_data)
            
            st.session_state.simulation_run = True
            st.session_state.current_month = num_months
            
        st.success(f"✅ Simulación completada: {num_months} meses")
        st.rerun()


def export_data_interface():
    """Interfaz de exportación de datos"""
    st.subheader("💾 Exportar Datos")
    
    system = st.session_state.system
    
    export_format = st.radio(
        "Formato de Exportación",
        ["JSON", "CSV", "Reporte Completo"]
    )
    
    if st.button("📥 Exportar"):
        if export_format == "JSON":
            report = system.get_system_report()
            json_str = json.dumps(report, indent=2, default=str)
            st.download_button(
                "Descargar JSON",
                json_str,
                "sistema_celular_reporte.json",
                "application/json"
            )
        
        elif export_format == "CSV":
            df = system.export_to_dataframe()
            csv = df.to_csv(index=False)
            st.download_button(
                "Descargar CSV",
                csv,
                "sistema_celular_historial.csv",
                "text/csv"
            )
        
        elif export_format == "Reporte Completo":
            report = system.get_system_report()
            
            # Crear reporte markdown
            md_report = f"""# Reporte Sistema Celular: {report['system_name']}
            
**Fecha**: {report['timestamp']}

## Resumen Ejecutivo

- **Balance Total**: ${report['summary']['total_balance']:,.2f}
- **Ganancia Total**: ${report['summary']['total_profit']:,.2f}
- **Health Score**: {report['summary']['system_health']:.1f}/100
- **Células Activas**: {report['summary']['active_cells']}/{report['summary']['total_cells']}

## Riesgo Global

- **Riesgo Compuesto**: {report['global_risk']['composite']:.1f}%
- **Nivel**: {report['global_risk']['level']}
- **Default Rate**: {report['global_risk']['default_rate']:.2f}%
- **Volatilidad**: {report['global_risk']['volatility']:.2f}%

---

*Generado por Sistema de Arquitectura Celular Mi-cochinito*
"""
            
            st.download_button(
                "Descargar Reporte MD",
                md_report,
                "reporte_completo.md",
                "text/markdown"
            )


def main():
    """Función principal de la aplicación"""
    initialize_session_state()
    
    # Header
    st.title("� Mi-cochinito - Simulador de Ahorro")
    st.markdown("**Sistema Inteligente de Ahorro Colectivo con Múltiples Grupos**")
    
    # Ayuda contextual
    with st.expander("❓ ¿Cómo funciona?"):
        st.markdown("""
        ### 🎯 Pasos Simples:
        
        1. **Cargar Ejemplo** → Click en "📋 Ejemplo Pre-configurado" en el menú
        2. **Ejecutar Simulación** → Ve a "▶️ Ejecutar Simulación" y simula 12 meses
        3. **Ver Resultados** → Revisa gráficos y métricas
        
        ### 💡 ¿Qué es esto?
        
        Este simulador te permite:
        - **Simular múltiples grupos** de ahorro a la vez
        - **Ver cómo crece el dinero** mes a mes
        - **Detectar riesgos** automáticamente
        - **Comparar diferentes escenarios**
        
        Cada **grupo de ahorro** tiene:
        - Miembros que aportan dinero
        - Diferentes fondos (emergencia, inversión, etc.)
        - Reglas de seguridad automáticas
        """)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=SIDEPE", use_container_width=True)
        
        st.markdown("---")
        
        # Modo de vista
        view_mode = st.radio(
            "Modo de Vista",
            ["📊 Simple", "🔬 Avanzada"],
            help="Simple: para usuarios básicos. Avanzada: con análisis detallado"
        )
        
        st.markdown("---")
        
        if view_mode == "📊 Simple":
            page = st.radio(
                "Navegación",
                [
                    "🏠 Inicio",
                    "▶️ Ejecutar Simulación",
                    "📊 Ver Resultados",
                    "💾 Descargar Datos"
                ]
            )
        else:
            page = st.radio(
                "Navegación",
                [
                    "🏠 Inicio",
                    "📊 Resumen General",
                    "🏢 Por Región/Grupo",
                    "🔬 Detalle de Grupos",
                    "⚡ Ejecutar Simulación",
                    "💾 Exportar Datos"
                ]
            )
        
        st.markdown("---")
        
        # Acciones rápidas
        st.markdown("### 🚀 Acciones Rápidas")
        
        if st.button("📋 Ejemplo Pre-configurado"):
            st.session_state.system = create_example_system()
            st.session_state.simulation_run = False
            st.session_state.show_welcome = True
            st.success("✅ Sistema cargado! Ahora ve a '⚡ Simulación' para ejecutar")
            st.rerun()
        
        if st.session_state.system and st.button("🔄 Resetear Sistema"):
            st.session_state.system = None
            st.session_state.simulation_run = False
            st.rerun()
        
        # Info del sistema
        if st.session_state.system:
            st.markdown("---")
            st.markdown("### ℹ️ Sistema Actual")
            st.write(f"**Nombre:** {st.session_state.system.system_name}")
            st.write(f"**Consolidadores:** {len(st.session_state.system.consolidator_nodes)}")
            st.write(f"**Células:** {st.session_state.system.get_total_cells()}")
            if st.session_state.simulation_run:
                st.write(f"**Mes Actual:** {st.session_state.current_month}")
    
    # Contenido principal
    if not st.session_state.system:
        st.info("👈 **Empieza aquí:** Click en '📋 Ejemplo Pre-configurado' en el menú lateral")
        st.markdown("---")
        st.markdown("### 🎓 Tutorial Rápido")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 1️⃣ Cargar")
            st.write("Click en 'Ejemplo Pre-configurado' en el menú")
        
        with col2:
            st.markdown("#### 2️⃣ Simular")
            st.write("Ve a 'Ejecutar Simulación' y simula 12 meses")
        
        with col3:
            st.markdown("#### 3️⃣ Ver")
            st.write("Revisa los resultados en gráficos")
    
    else:
        # Banner de bienvenida para sistema nuevo
        if st.session_state.get('show_welcome', False):
            st.success("✅ Sistema cargado exitosamente")
            st.info("🎯 **Siguiente paso:** Ve a '▶️ Ejecutar Simulación' en el menú")
            if st.button("🚀 Ir a Simulación"):
                st.session_state.show_welcome = False
                st.rerun()
            st.markdown("---")
        
        # Modo Simple
        if view_mode == "📊 Simple":
            if page == "🏠 Inicio":
                display_simple_dashboard()
            elif page == "▶️ Ejecutar Simulación":
                run_simulation_interface()
            elif page == "📊 Ver Resultados":
                display_simple_results()
            elif page == "💾 Descargar Datos":
                export_data_interface()
        
        # Modo Avanzado
        else:
            if page == "🏠 Inicio":
                display_simple_dashboard()
            elif page == "📊 Resumen General":
                display_system_overview()
            elif page == "🏢 Por Región/Grupo":
                display_consolidators_view()
            elif page == "🔬 Detalle de Grupos":
                display_cells_detail()
            elif page == "⚡ Ejecutar Simulación":
                run_simulation_interface()
            elif page == "💾 Exportar Datos":
                export_data_interface()


if __name__ == "__main__":
    main()
