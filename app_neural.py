"""
Interfaz Streamlit para el Sistema de Arquitectura Celular NEURONAL
=====================================================================
Muestra las relaciones multi-relacionales y comunicación bidireccional
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Importar sistema neuronal
from neural_cellular_architecture import (
    NeuralMasterNode,
    NeuralConsolidatorNode,
    NeuralSavingsCell,
    create_neural_example_system,
    MessageType,
    GlobalTimeline
)
from cellular_architecture import ValueSource, CellState
from temporal_persistence import TemporalSequenceStore, TemporalNeuralSystem

# Configuración de página
st.set_page_config(
    page_title="Mi-cochinito Neuronal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .relation-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    .parent-relation { background-color: #ff6b6b; }
    .child-relation { background-color: #4ecdc4; }
    .sibling-relation { background-color: #45b7d1; }
    .coordinator-relation { background-color: #f9ca24; color: #000; }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'neural_system' not in st.session_state:
    st.session_state.neural_system = None
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = []
if 'timeline' not in st.session_state:
    st.session_state.timeline = GlobalTimeline()
if 'temporal_system' not in st.session_state:
    st.session_state.temporal_system = None

def main():
    # Header
    st.markdown('<div class="main-header">🧠 Mi-cochinito - Sistema Neuronal</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Control")
        
        st.markdown("### 📊 Sistema")
        
        if st.button("🚀 Cargar Sistema de Ejemplo", use_container_width=True):
            with st.spinner("Creando sistema neuronal con trazabilidad temporal..."):
                neural = create_neural_example_system()
                st.session_state.neural_system = neural
                st.session_state.temporal_system = TemporalNeuralSystem(neural, f"sidepe_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                st.session_state.simulation_results = []
                st.success("✅ Sistema cargado con historial temporal")
        
        st.markdown("---")
        
        if st.session_state.neural_system:
            st.markdown("### ⚙️ Información del Sistema")
            system = st.session_state.neural_system
            st.metric("Consolidadores", len(system.consolidator_nodes))
            st.metric("Células Totales", system.get_total_cells())
            st.metric("Células Activas", system.get_active_cells())
            st.metric("Mes Actual", system.timeline.current_month)
            
            st.markdown("---")
            st.markdown("### 🎯 Navegación")
            
        page = st.radio(
            "Selecciona Vista:",
            [
                "🏠 Dashboard",
                "🧬 Relaciones Neuronales",
                "⏰ Timeline Global",
                "💬 Sistema de Mensajería",
                "▶️ Simulación",
                "� Histórico Temporal",
                "�📊 Análisis Avanzado"
            ],
            label_visibility="collapsed"
        )
    
    # Contenido principal
    if not st.session_state.neural_system:
        show_welcome()
    else:
        if page == "🏠 Dashboard":
            show_dashboard()
        elif page == "🧬 Relaciones Neuronales":
            show_neural_relations()
        elif page == "⏰ Timeline Global":
            show_timeline()
        elif page == "💬 Sistema de Mensajería":
            show_messaging_system()
        elif page == "▶️ Simulación":
            show_simulation()
        elif page == "� Histórico Temporal":
            show_temporal_history()
        elif page == "�📊 Análisis Avanzado":
            show_advanced_analysis()


def show_welcome():
    """Pantalla de bienvenida"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🎓 Bienvenido al Sistema Neuronal")
        st.markdown("""
        ### ¿Qué es diferente?
        
        Este sistema implementa **arquitectura neuronal multi-relacional**:
        
        ✅ **Relaciones Bidireccionales**
        - Extremo → Centro (agregación)
        - Centro → Extremo (retroalimentación)
        
        ✅ **Células Coordinadoras**
        - Actúan como gateways
        - Reducen complejidad de comunicación
        
        ✅ **Timeline Global Sincronizado**
        - Todos los nodos comparten el mismo "ahora"
        - Causalidad temporal garantizada
        
        ✅ **Sistema de Mensajería**
        - Directivas, reportes, alertas, coordinación
        - Comunicación asíncrona entre nodos
        
        ✅ **Control Adaptativo**
        - Feedback loop automático
        - Ajuste de riesgo en tiempo real
        
        ---
        
        ### 🚀 Para Empezar
        
        1. Click en **"Cargar Sistema de Ejemplo"** en el menú lateral
        2. Explora las **Relaciones Neuronales**
        3. Ejecuta una **Simulación**
        4. Revisa el **Timeline Global**
        """)


def show_dashboard():
    """Dashboard principal"""
    system = st.session_state.neural_system
    
    st.title("🏠 Dashboard del Sistema Neuronal")
    
    # Métricas principales - Primera fila
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        balance = system.get_total_balance()
        st.metric("💰 Balance Total", f"${balance:,.0f}")
    
    with col2:
        profit = system.get_total_profit()
        st.metric("📈 Ganancia Total", f"${profit:,.0f}")
    
    with col3:
        health = system.get_system_health()
        st.metric("❤️ Health Score", f"{health:.1f}/100")
    
    with col4:
        risk = system.global_metrics.calculate_composite_risk()[0]
        risk_level = system.global_metrics.calculate_composite_risk()[1].name
        st.metric("⚠️ Riesgo Global", f"{risk:.1f}%", delta=risk_level)
    
    # Métricas de rendimiento - Segunda fila
    if system.system_history:
        col1, col2, col3, col4 = st.columns(4)
        
        # Calcular capital inicial (total aportado)
        total_contributed = 0
        for consolidator in system.consolidator_nodes.values():
            for cell in consolidator.cells.values():
                for source in cell.value_sources.values():
                    months = system.timeline.current_month
                    total_contributed += source.monthly_contribution * months
        
        with col1:
            # ROI Total
            roi_total = (profit / total_contributed * 100) if total_contributed > 0 else 0
            st.metric("📊 ROI Total", f"{roi_total:.2f}%")
        
        with col2:
            # ROI Mensual Promedio
            roi_mensual = roi_total / system.timeline.current_month if system.timeline.current_month > 0 else 0
            st.metric("📅 ROI Mensual Promedio", f"{roi_mensual:.2f}%")
        
        with col3:
            # Rendimiento del último mes
            if len(system.system_history) >= 2:
                last_profit = system.system_history[-1]['total_system_profit']
                prev_profit = system.system_history[-2]['total_system_profit']
                monthly_growth = last_profit - prev_profit
                st.metric("💹 Rendimiento Último Mes", f"${monthly_growth:,.0f}")
            else:
                st.metric("💹 Rendimiento Último Mes", "$0")
        
        with col4:
            # Tasa de crecimiento mensual promedio
            if len(system.system_history) > 1:
                initial_balance = system.system_history[0]['total_system_balance']
                final_balance = system.system_history[-1]['total_system_balance']
                months = len(system.system_history)
                avg_growth = ((final_balance / initial_balance) ** (1/months) - 1) * 100 if initial_balance > 0 else 0
                st.metric("📈 Crecimiento Mensual Avg", f"{avg_growth:.2f}%")
            else:
                st.metric("📈 Crecimiento Mensual Avg", "0%")
    
    st.markdown("---")
    
    # Visualización de arquitectura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏗️ Estructura del Sistema")
        
        for cons_id, consolidator in system.consolidator_nodes.items():
            with st.expander(f"📦 {consolidator.name}", expanded=True):
                st.write(f"**Balance:** ${consolidator.get_total_balance():,.0f}")
                st.write(f"**Células:** {len(consolidator.cells)}")
                st.write(f"**Coordinadoras:** {len(consolidator.coordinator_cells)}")
                
                # Listar células
                for cell_id, cell in consolidator.cells.items():
                    icon = "🎯" if cell.is_coordinator else "📍"
                    role = "Coordinadora" if cell.is_coordinator else "Regular"
                    st.write(f"{icon} {cell.name} ({role}) - ${cell.get_total_balance():,.0f}")
    
    with col2:
        st.markdown("### ⚡ Estado en Tiempo Real")
        
        # Timeline info
        st.info(f"""
        **📅 Mes Actual:** {system.timeline.current_month}
        
        **🕐 Timestamp:** {system.timeline.current_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        
        **📝 Eventos Registrados:** {len(system.timeline.events)}
        """)
        
        # Distribución de células por estado
        st.markdown("#### 🔄 Estados de Células")
        states_count = {}
        for consolidator in system.consolidator_nodes.values():
            for cell in consolidator.cells.values():
                state = cell.state.value
                states_count[state] = states_count.get(state, 0) + 1
        
        for state, count in states_count.items():
            st.write(f"- **{state.upper()}:** {count} células")
    
    # Resultados de simulación si existen
    if st.session_state.simulation_results:
        st.markdown("---")
        st.markdown("### 📈 Evolución del Sistema")
        
        df = system.export_to_dataframe()
        
        if not df.empty:
            # Calcular rendimientos graduales
            df['Rendimiento Mensual'] = df['Ganancia Total'].diff().fillna(df['Ganancia Total'])
            
            # Calcular capital acumulado
            df['Capital Aportado'] = 0
            for consolidator in system.consolidator_nodes.values():
                for cell in consolidator.cells.values():
                    for source in cell.value_sources.values():
                        df['Capital Aportado'] += source.monthly_contribution * df['Mes']
            
            # Calcular ROI acumulado
            df['ROI Acumulado (%)'] = (df['Ganancia Total'] / df['Capital Aportado'] * 100).fillna(0)
            
            # Tabs para diferentes vistas
            tab1, tab2, tab3 = st.tabs(["💰 Balance", "📊 Rendimientos", "📈 ROI"])
            
            with tab1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Mes'],
                    y=df['Balance Total'],
                    mode='lines+markers',
                    name='Balance',
                    line=dict(color='#1f77b4', width=3),
                    fill='tozeroy'
                ))
                fig.update_layout(
                    title="Balance Total por Mes",
                    xaxis_title="Mes",
                    yaxis_title="Balance ($)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Gráfico de rendimientos mensuales
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['Mes'],
                    y=df['Rendimiento Mensual'],
                    name='Rendimiento Mensual',
                    marker_color='#2ca02c'
                ))
                fig.add_trace(go.Scatter(
                    x=df['Mes'],
                    y=df['Ganancia Total'],
                    mode='lines+markers',
                    name='Ganancia Acumulada',
                    line=dict(color='#ff7f0e', width=3),
                    yaxis='y2'
                ))
                fig.update_layout(
                    title="Rendimientos Graduales y Totales",
                    xaxis_title="Mes",
                    yaxis=dict(title="Rendimiento Mensual ($)"),
                    yaxis2=dict(title="Ganancia Acumulada ($)", overlaying='y', side='right'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabla de rendimientos
                st.markdown("#### 📋 Tabla de Rendimientos por Mes")
                render_df = df[['Mes', 'Rendimiento Mensual', 'Ganancia Total', 'Capital Aportado']].copy()
                render_df['Rendimiento Mensual'] = render_df['Rendimiento Mensual'].apply(lambda x: f"${x:,.2f}")
                render_df['Ganancia Total'] = render_df['Ganancia Total'].apply(lambda x: f"${x:,.2f}")
                render_df['Capital Aportado'] = render_df['Capital Aportado'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(render_df, use_container_width=True, hide_index=True)
            
            with tab3:
                # Gráfico de ROI
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Mes'],
                    y=df['ROI Acumulado (%)'],
                    mode='lines+markers',
                    name='ROI Acumulado',
                    line=dict(color='#9467bd', width=3),
                    fill='tozeroy'
                ))
                fig.update_layout(
                    title="ROI Acumulado por Mes",
                    xaxis_title="Mes",
                    yaxis_title="ROI (%)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Estadísticas de ROI
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ROI Inicial", f"{df['ROI Acumulado (%)'].iloc[0]:.2f}%")
                with col2:
                    st.metric("ROI Final", f"{df['ROI Acumulado (%)'].iloc[-1]:.2f}%")
                with col3:
                    roi_growth = df['ROI Acumulado (%)'].iloc[-1] - df['ROI Acumulado (%)'].iloc[0]
                    st.metric("Crecimiento ROI", f"{roi_growth:.2f}%")


def show_neural_relations():
    """Visualiza las relaciones neuronales del sistema"""
    system = st.session_state.neural_system
    
    st.title("🧬 Relaciones Neuronales Multi-Relacionales")
    
    st.markdown("""
    Este sistema implementa 5 tipos de relaciones:
    
    1. **HIJO → PADRE**: Agregación ascendente de valores
    2. **PADRE → HIJO**: Retroalimentación descendente (directivas)
    3. **HERMANO ↔ HERMANO**: Comunicación lateral entre células
    4. **COORDINADOR → GRUPO**: Gateway de comunicación
    5. **TIEMPO ⏰**: Sincronización temporal global
    """)
    
    st.markdown("---")
    
    # Mapa de relaciones
    st.markdown("### 🗺️ Mapa de Relaciones")
    
    # Crear diagrama de red con Plotly
    nodes_data = []
    edges_data = []
    
    # Nodo Master
    nodes_data.append({
        'id': 'master',
        'label': 'Master Node',
        'type': 'master',
        'x': 0,
        'y': 0
    })
    
    # Consolidadores
    x_cons = -1
    for cons_id, consolidator in system.consolidator_nodes.items():
        nodes_data.append({
            'id': cons_id,
            'label': consolidator.name,
            'type': 'consolidator',
            'x': x_cons,
            'y': 1
        })
        
        # Edge: Master → Consolidator
        edges_data.append({
            'from': 'master',
            'to': cons_id,
            'type': 'parent'
        })
        
        # Células del consolidador
        y_cell = 2
        for cell_id, cell in consolidator.cells.items():
            nodes_data.append({
                'id': cell_id,
                'label': cell.name,
                'type': 'coordinator' if cell.is_coordinator else 'cell',
                'x': x_cons,
                'y': y_cell
            })
            
            # Edge: Consolidator → Cell
            edges_data.append({
                'from': cons_id,
                'to': cell_id,
                'type': 'parent'
            })
            
            # Relaciones de coordinación
            if cell.is_coordinator:
                for managed_id in cell.managed_cells:
                    edges_data.append({
                        'from': cell_id,
                        'to': managed_id,
                        'type': 'coordinator'
                    })
            
            # Relaciones entre hermanos
            for sibling_id in cell.sibling_cells:
                if sibling_id in consolidator.cells:
                    edges_data.append({
                        'from': cell_id,
                        'to': sibling_id,
                        'type': 'sibling'
                    })
            
            y_cell += 0.3
        
        x_cons += 2
    
    # Visualizar con plotly
    fig = go.Figure()
    
    # Agregar edges
    for edge in edges_data:
        from_node = next(n for n in nodes_data if n['id'] == edge['from'])
        to_node = next(n for n in nodes_data if n['id'] == edge['to'])
        
        color = {
            'parent': '#ff6b6b',
            'coordinator': '#f9ca24',
            'sibling': '#45b7d1'
        }.get(edge['type'], '#95a5a6')
        
        fig.add_trace(go.Scatter(
            x=[from_node['x'], to_node['x']],
            y=[from_node['y'], to_node['y']],
            mode='lines',
            line=dict(color=color, width=2),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Agregar nodes
    for node_type in ['master', 'consolidator', 'coordinator', 'cell']:
        nodes_of_type = [n for n in nodes_data if n['type'] == node_type]
        if not nodes_of_type:
            continue
        
        color_map = {
            'master': '#e74c3c',
            'consolidator': '#3498db',
            'coordinator': '#f39c12',
            'cell': '#2ecc71'
        }
        
        fig.add_trace(go.Scatter(
            x=[n['x'] for n in nodes_of_type],
            y=[n['y'] for n in nodes_of_type],
            mode='markers+text',
            name=node_type.capitalize(),
            marker=dict(
                size=30 if node_type == 'master' else 20,
                color=color_map[node_type]
            ),
            text=[n['label'] for n in nodes_of_type],
            textposition='top center',
            hovertext=[n['label'] for n in nodes_of_type]
        ))
    
    fig.update_layout(
        title="Topología del Sistema Neuronal",
        showlegend=True,
        hovermode='closest',
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detalle de relaciones por célula
    st.markdown("### 🔗 Detalle de Relaciones por Célula")
    
    for cons_id, consolidator in system.consolidator_nodes.items():
        with st.expander(f"📦 {consolidator.name}"):
            for cell_id, cell in consolidator.cells.items():
                st.markdown(f"#### {cell.name}")
                
                # Badges de relaciones
                badges_html = ""
                
                if cell.parent_id:
                    badges_html += f'<span class="relation-badge parent-relation">↑ Padre: {cell.parent_id}</span>'
                
                if cell.is_coordinator:
                    badges_html += f'<span class="relation-badge coordinator-relation">🎯 Coordinadora ({len(cell.managed_cells)} células)</span>'
                
                if cell.sibling_cells:
                    badges_html += f'<span class="relation-badge sibling-relation">↔ {len(cell.sibling_cells)} hermanos</span>'
                
                st.markdown(badges_html, unsafe_allow_html=True)
                
                # Detalles
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Balance:** ${cell.get_total_balance():,.0f}")
                    st.write(f"**Health:** {cell.get_health_score():.1f}/100")
                
                with col2:
                    st.write(f"**Estado:** {cell.state.value}")
                    st.write(f"**Relaciones:** {len(cell.relations)}")


def show_timeline():
    """Muestra el timeline global"""
    system = st.session_state.neural_system
    timeline = system.timeline
    
    st.title("⏰ Timeline Global Sincronizado")
    
    st.info(f"""
    **Mes Actual:** {timeline.current_month}
    
    **Timestamp:** {timeline.current_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
    
    **Total de Eventos:** {len(timeline.events)}
    """)
    
    st.markdown("---")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        num_events = st.slider("Número de eventos a mostrar", 10, 100, 50)
    
    with col2:
        event_types = set(e['type'] for e in timeline.events)
        selected_types = st.multiselect(
            "Filtrar por tipo de evento",
            options=list(event_types),
            default=list(event_types)
        )
    
    # Obtener eventos
    events = timeline.get_history()
    
    # Filtrar
    filtered_events = [
        e for e in events
        if e['type'] in selected_types
    ][-num_events:]
    
    # Mostrar eventos
    st.markdown(f"### 📋 Últimos {len(filtered_events)} Eventos")
    
    for event in reversed(filtered_events):
        timestamp = event.get('timestamp', 'N/A')
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime('%H:%M:%S')
        
        entity = event.get('entity', 'N/A')
        event_type = event['type']
        data = event.get('data', {})
        
        # Icono según tipo
        icon_map = {
            'month_advance': '📅',
            'cell_created': '🆕',
            'consolidator_created': '📦',
            'master_created': '🏢',
            'message_sent': '📤',
            'message_received': '📥',
            'month_simulated': '⚙️',
            'directive_applied': '📋',
            'state_change': '🔄',
            'auto_regulation': '⚠️',
            'risk_adjusted': '⚖️'
        }
        
        icon = icon_map.get(event_type, '📌')
        
        with st.expander(f"{icon} [{timestamp}] {event_type} - {entity}"):
            st.json(data)
    
    # Gráfico de eventos por tipo
    st.markdown("---")
    st.markdown("### 📊 Distribución de Eventos")
    
    event_counts = {}
    for event in events:
        et = event['type']
        event_counts[et] = event_counts.get(et, 0) + 1
    
    df_events = pd.DataFrame(list(event_counts.items()), columns=['Tipo', 'Cantidad'])
    df_events = df_events.sort_values('Cantidad', ascending=False)
    
    fig = px.bar(df_events, x='Tipo', y='Cantidad', title="Eventos por Tipo")
    st.plotly_chart(fig, use_container_width=True)


def show_messaging_system():
    """Muestra el sistema de mensajería"""
    system = st.session_state.neural_system
    
    st.title("💬 Sistema de Mensajería Neuronal")
    
    st.markdown("""
    El sistema implementa comunicación asíncrona tipo red neuronal:
    - **Directivas:** Centro → Extremo (backpropagation)
    - **Reportes:** Extremo → Centro (forward propagation)
    - **Alertas:** Propagación lateral entre hermanos
    - **Coordinación:** Entre células del mismo grupo
    """)
    
    st.markdown("---")
    
    # Enviar directiva global
    st.markdown("### 📤 Enviar Directiva Global")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        directive_type = st.selectbox(
            "Tipo de Directiva",
            ['adjust_utilization', 'suspend_operations', 'resume_operations', 'adjust_risk_factor']
        )
    
    with col2:
        target = st.selectbox(
            "Objetivo",
            ['coordinators', 'all']
        )
    
    with col3:
        if directive_type == 'adjust_utilization':
            value = st.slider("Nueva Utilización (%)", 30, 100, 85)
            content = {'new_utilization_rate': value}
        elif directive_type == 'adjust_risk_factor':
            value = st.slider("Factor de Riesgo", 0.5, 1.5, 1.0, 0.05)
            content = {'risk_factor': value}
        else:
            content = {}
    
    if st.button("🚀 Enviar Directiva", type="primary"):
        system.broadcast_global_directive(directive_type, content, target)
        st.success(f"✅ Directiva '{directive_type}' enviada a '{target}'")
        
        # Log en timeline
        system.timeline.log_event('manual_directive', 'user', {
            'type': directive_type,
            'target': target,
            'content': content
        })
    
    st.markdown("---")
    
    # Estadísticas de mensajería
    st.markdown("### 📊 Estadísticas de Mensajería")
    
    total_inbox = 0
    total_outbox = 0
    
    for consolidator in system.consolidator_nodes.values():
        total_inbox += len(consolidator.inbox)
        total_outbox += len(consolidator.outbox)
        
        for cell in consolidator.cells.values():
            total_inbox += len(cell.inbox)
            total_outbox += len(cell.outbox)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📥 Mensajes en Inbox", total_inbox)
    
    with col2:
        st.metric("📤 Mensajes en Outbox", total_outbox)
    
    with col3:
        st.metric("📬 Total de Mensajes", total_inbox + total_outbox)
    
    # Detalle por nodo
    st.markdown("### 📋 Buzones por Nodo")
    
    for cons_id, consolidator in system.consolidator_nodes.items():
        with st.expander(f"📦 {consolidator.name}"):
            st.write(f"**Inbox:** {len(consolidator.inbox)} mensajes")
            st.write(f"**Outbox:** {len(consolidator.outbox)} mensajes")
            
            for cell_id, cell in consolidator.cells.items():
                role = "🎯 Coordinadora" if cell.is_coordinator else "📍 Regular"
                st.write(f"{role} {cell.name}: Inbox={len(cell.inbox)}, Outbox={len(cell.outbox)}")


def show_simulation():
    """Interfaz de simulación"""
    system = st.session_state.neural_system
    temporal = st.session_state.temporal_system
    
    st.title("▶️ Simulación del Sistema Neuronal")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        num_months = st.slider("Número de meses a simular", 1, 24, 12)
    
    with col2:
        if st.button("▶️ Ejecutar Simulación", type="primary", use_container_width=True):
            with st.spinner(f"Simulando {num_months} meses con registro temporal..."):
                # Usar sistema temporal si está disponible
                if temporal:
                    results = temporal.simulate_multiple_months_with_tracking(num_months)
                    events_count = len(temporal.temporal_store.events)
                    snapshots_count = len(temporal.temporal_store.snapshots)
                    st.success(f"✅ Simulación completada: {num_months} meses | 📊 {events_count} eventos | 📸 {snapshots_count} snapshots")
                else:
                    results = system.simulate_multiple_months(num_months)
                    st.success(f"✅ Simulación completada: {num_months} meses")
                st.session_state.simulation_results = results
    
    # Mostrar resultados
    if st.session_state.simulation_results:
        st.markdown("---")
        st.markdown("### 📊 Resultados de la Simulación")
        
        df = system.export_to_dataframe()
        
        if not df.empty:
            # Métricas finales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                final_balance = df['Balance Total'].iloc[-1]
                initial_balance = df['Balance Total'].iloc[0] if len(df) > 1 else 0
                delta = final_balance - initial_balance
                st.metric("Balance Final", f"${final_balance:,.0f}", f"+${delta:,.0f}")
            
            with col2:
                final_profit = df['Ganancia Total'].iloc[-1]
                st.metric("Ganancia Total", f"${final_profit:,.0f}")
            
            with col3:
                final_health = df['Health Score'].iloc[-1]
                st.metric("Health Final", f"{final_health:.1f}/100")
            
            with col4:
                final_risk = df['Riesgo Global'].iloc[-1]
                st.metric("Riesgo Final", f"{final_risk:.1f}%")
            
            # Gráficos
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Balance", "⚠️ Riesgo", "❤️ Health", "💹 Rendimientos"])
            
            with tab1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Mes'],
                    y=df['Balance Total'],
                    mode='lines+markers',
                    name='Balance',
                    fill='tozeroy',
                    line=dict(color='#1f77b4', width=3)
                ))
                fig.update_layout(title="Evolución del Balance", xaxis_title="Mes", yaxis_title="Balance ($)")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Mes'],
                    y=df['Riesgo Global'],
                    mode='lines+markers',
                    name='Riesgo',
                    line=dict(color='#ff7f0e', width=3)
                ))
                fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Umbral Alto")
                fig.update_layout(title="Evolución del Riesgo", xaxis_title="Mes", yaxis_title="Riesgo (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Mes'],
                    y=df['Health Score'],
                    mode='lines+markers',
                    name='Health',
                    line=dict(color='#2ca02c', width=3)
                ))
                fig.update_layout(title="Evolución del Health Score", xaxis_title="Mes", yaxis_title="Health")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                # Calcular rendimientos graduales y totales
                df_render = df.copy()
                df_render['Rendimiento Mensual'] = df_render['Ganancia Total'].diff().fillna(df_render['Ganancia Total'])
                
                # Gráfico combinado
                fig = go.Figure()
                
                # Barras para rendimiento mensual
                fig.add_trace(go.Bar(
                    x=df_render['Mes'],
                    y=df_render['Rendimiento Mensual'],
                    name='Rendimiento Mensual',
                    marker_color='#2ca02c',
                    yaxis='y'
                ))
                
                # Línea para ganancia acumulada
                fig.add_trace(go.Scatter(
                    x=df_render['Mes'],
                    y=df_render['Ganancia Total'],
                    mode='lines+markers',
                    name='Ganancia Acumulada',
                    line=dict(color='#ff7f0e', width=3),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title="Rendimientos Graduales y Acumulados",
                    xaxis_title="Mes",
                    yaxis=dict(title="Rendimiento Mensual ($)", side='left'),
                    yaxis2=dict(title="Ganancia Acumulada ($)", overlaying='y', side='right'),
                    hovermode='x unified',
                    legend=dict(x=0.01, y=0.99)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Estadísticas de rendimiento
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_monthly = df_render['Rendimiento Mensual'].mean()
                    st.metric("💰 Rendimiento Mensual Promedio", f"${avg_monthly:,.2f}")
                with col2:
                    max_monthly = df_render['Rendimiento Mensual'].max()
                    st.metric("🔝 Mejor Mes", f"${max_monthly:,.2f}")
                with col3:
                    min_monthly = df_render['Rendimiento Mensual'].min()
                    st.metric("⬇️ Peor Mes", f"${min_monthly:,.2f}")
            
            # Tabla de datos
            st.markdown("### 📋 Datos Detallados")
            st.dataframe(df, use_container_width=True)


def show_temporal_history():
    """
    Vista del Histórico Temporal - DIFERENCIADOR ÚNICO
    Permite revisar cada secuencia guardada con timestamp
    """
    st.title("📜 Histórico Temporal")
    st.markdown("""
    > **Diferenciador Único**: Cada secuencia se guarda con timestamp inmutable.
    > Permite revisar el histórico completo de toda la evolución del sistema.
    """)
    
    temporal = st.session_state.temporal_system
    
    if not temporal:
        st.warning("⚠️ Sistema temporal no inicializado")
        return
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Estadísticas",
        "📅 Timeline de Eventos",
        "🔍 Auditoría",
        "📈 Comparar Períodos",
        "💾 Exportar/Guardar"
    ])
    
    with tab1:
        show_temporal_statistics(temporal)
    
    with tab2:
        show_event_timeline(temporal)
    
    with tab3:
        show_entity_audit(temporal)
    
    with tab4:
        show_period_comparison(temporal)
    
    with tab5:
        show_export_options(temporal)


def show_temporal_statistics(temporal):
    """Estadísticas del almacén temporal"""
    stats = temporal.temporal_store.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Eventos", stats['total_events'])
    with col2:
        st.metric("📸 Snapshots", stats['total_snapshots'])
    with col3:
        st.metric("🏷️ Entidades", stats['unique_entities'])
    with col4:
        integrity_icon = "✅" if stats['integrity'] else "❌"
        st.metric("🔐 Integridad", f"{integrity_icon} {'Válida' if stats['integrity'] else 'Corrupta'}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Tipos de Eventos Registrados")
        event_types = stats.get('event_types', [])
        if event_types:
            for et in event_types:
                events = temporal.temporal_store.get_events_by_type(et)
                st.write(f"• **{et}**: {len(events)} eventos")
        else:
            st.info("Sin eventos registrados aún")
    
    with col2:
        st.markdown("### 📅 Meses Registrados")
        months = stats.get('months_recorded', [])
        if months:
            for month in sorted(months):
                events = temporal.temporal_store.get_events_in_month(month)
                st.write(f"• **Mes {month}**: {len(events)} eventos")
        else:
            st.info("Sin meses registrados aún")
    
    # Verificación de integridad de cadena
    st.markdown("---")
    st.markdown("### 🔗 Verificación de Cadena (Blockchain-like)")
    
    integrity = temporal.temporal_store.verify_chain_integrity()
    
    if integrity['valid']:
        st.success(f"✅ Cadena de {integrity['total_events']} eventos verificada - Integridad 100%")
        st.code(f"Último Hash: {integrity['last_hash']}", language="text")
    else:
        st.error(f"❌ Cadena corrupta - {len(integrity['errors'])} errores encontrados")
        for error in integrity['errors'][:5]:
            st.write(f"• Secuencia {error['sequence']}: {error['error']}")


def show_event_timeline(temporal):
    """Muestra timeline de todos los eventos"""
    st.markdown("### 📅 Timeline Completo de Eventos")
    
    events = temporal.temporal_store.events
    
    if not events:
        st.info("📭 Sin eventos registrados. Ejecuta una simulación para generar historial.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        entity_types = list(set(e.entity_type for e in events))
        selected_entity_type = st.selectbox("Filtrar por Tipo Entidad", ["Todos"] + entity_types)
    
    with col2:
        operations = list(set(e.operation for e in events))
        selected_operation = st.selectbox("Filtrar por Operación", ["Todos"] + operations)
    
    with col3:
        event_types = list(set(e.event_type for e in events))
        selected_event_type = st.selectbox("Filtrar por Tipo Evento", ["Todos"] + event_types)
    
    # Aplicar filtros
    filtered = events
    if selected_entity_type != "Todos":
        filtered = [e for e in filtered if e.entity_type == selected_entity_type]
    if selected_operation != "Todos":
        filtered = [e for e in filtered if e.operation == selected_operation]
    if selected_event_type != "Todos":
        filtered = [e for e in filtered if e.event_type == selected_event_type]
    
    st.info(f"📊 Mostrando {len(filtered)} de {len(events)} eventos")
    
    # Mostrar como DataFrame
    if filtered:
        data = []
        for e in filtered[-100:]:  # Últimos 100
            data.append({
                'Seq': e.sequence_number,
                'Timestamp': e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'Tipo': e.event_type,
                'Entidad': e.entity_id,
                'Operación': e.operation,
                'Hash': e.event_hash[:8] + "...",
                'Hash Ant': e.previous_hash[:8] + "..." if e.previous_hash != "genesis" else "genesis"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Visualización de cadena
        st.markdown("### 🔗 Visualización de Cadena de Hashes")
        
        # Crear gráfico de cadena
        fig = go.Figure()
        
        # Mostrar últimos 10 eventos como nodos conectados
        recent = filtered[-10:]
        for i, e in enumerate(recent):
            fig.add_trace(go.Scatter(
                x=[i],
                y=[0],
                mode='markers+text',
                marker=dict(size=30, color='#667eea'),
                text=[f"#{e.sequence_number}"],
                textposition="middle center",
                textfont=dict(color='white', size=10),
                hovertext=f"Seq: {e.sequence_number}<br>Hash: {e.event_hash}<br>Op: {e.operation}",
                hoverinfo='text',
                showlegend=False
            ))
            
            if i > 0:
                fig.add_annotation(
                    x=i-0.5, y=0,
                    text="→",
                    showarrow=False,
                    font=dict(size=20, color='#764ba2')
                )
        
        fig.update_layout(
            title="Últimos 10 Eventos Encadenados",
            height=200,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_entity_audit(temporal):
    """Auditoría de entidades específicas"""
    st.markdown("### 🔍 Auditoría por Entidad")
    
    entities = list(temporal.temporal_store.events_by_entity.keys())
    
    if not entities:
        st.info("📭 Sin entidades registradas. Ejecuta una simulación primero.")
        return
    
    selected_entity = st.selectbox("Seleccionar Entidad para Auditar", entities)
    
    if selected_entity:
        audit = temporal.temporal_store.audit_entity(selected_entity)
        
        if 'error' in audit:
            st.warning(audit['error'])
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Eventos", audit['total_events'])
        with col2:
            first_ts = audit['first_event']['timestamp']
            st.metric("Primer Registro", first_ts[:10])
        with col3:
            last_ts = audit['last_event']['timestamp']
            st.metric("Último Registro", last_ts[:10])
        
        # Operaciones realizadas
        st.markdown("#### 📋 Operaciones Realizadas")
        ops = audit['operations_count']
        cols = st.columns(len(ops))
        for i, (op, count) in enumerate(ops.items()):
            with cols[i]:
                st.metric(op.capitalize(), count)
        
        # Timeline de la entidad
        st.markdown("#### 📅 Timeline de la Entidad")
        
        timeline_data = []
        for item in audit['timeline']:
            timeline_data.append({
                'Secuencia': item['sequence'],
                'Timestamp': item['timestamp'][:19],
                'Operación': item['operation'],
                'Tipo Evento': item['event_type']
            })
        
        st.dataframe(pd.DataFrame(timeline_data), use_container_width=True)
        
        # Gráfico de actividad
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(timeline_data))),
            y=[1] * len(timeline_data),
            mode='markers',
            marker=dict(
                size=15,
                color=list(range(len(timeline_data))),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Secuencia")
            ),
            text=[f"{d['Operación']}" for d in timeline_data],
            hoverinfo='text'
        ))
        
        fig.update_layout(
            title=f"Actividad de {selected_entity}",
            height=200,
            xaxis=dict(title="Orden Cronológico"),
            yaxis=dict(showticklabels=False),
            margin=dict(l=20, r=20, t=50, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_period_comparison(temporal):
    """Comparación entre períodos"""
    st.markdown("### 📈 Comparar Períodos")
    
    snapshots = temporal.temporal_store.snapshots
    
    if len(snapshots) < 2:
        st.warning("⚠️ Se necesitan al menos 2 snapshots para comparar. Simula varios meses primero.")
        return
    
    months = [s.month for s in snapshots]
    
    col1, col2 = st.columns(2)
    
    with col1:
        month_a = st.selectbox("Mes Inicial", months, index=0)
    with col2:
        month_b = st.selectbox("Mes Final", months, index=len(months)-1)
    
    if month_a >= month_b:
        st.warning("El mes final debe ser mayor que el inicial")
        return
    
    comparison = temporal.compare_periods(month_a, month_b)
    
    if 'error' in comparison:
        st.error(comparison['error'])
        return
    
    # Resumen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📅 Período", f"Mes {month_a} → {month_b}")
    with col2:
        st.metric("📊 Eventos Entre Períodos", comparison['events_between'])
    with col3:
        delta_months = month_b - month_a
        st.metric("⏱️ Meses Transcurridos", delta_months)
    
    # Comparación de métricas
    st.markdown("#### 📊 Evolución de Métricas")
    
    metrics = comparison.get('metrics_comparison', {})
    
    if metrics:
        data = []
        for metric, values in metrics.items():
            data.append({
                'Métrica': metric.replace('_', ' ').title(),
                f'Mes {month_a}': f"{values['before']:.2f}",
                f'Mes {month_b}': f"{values['after']:.2f}",
                'Cambio': f"{values['change']:+.2f}",
                'Cambio %': f"{values['change_pct']:+.1f}%"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Gráfico de barras comparativo
        fig = go.Figure()
        
        metric_names = [m.replace('_', ' ').title() for m in metrics.keys()]
        before_values = [m['before'] for m in metrics.values()]
        after_values = [m['after'] for m in metrics.values()]
        
        fig.add_trace(go.Bar(
            name=f'Mes {month_a}',
            x=metric_names,
            y=before_values,
            marker_color='#667eea'
        ))
        
        fig.add_trace(go.Bar(
            name=f'Mes {month_b}',
            x=metric_names,
            y=after_values,
            marker_color='#764ba2'
        ))
        
        fig.update_layout(
            title="Comparación Visual de Métricas",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin métricas para comparar")


def show_export_options(temporal):
    """Opciones de exportación y guardado"""
    st.markdown("### 💾 Exportar y Guardar Historial")
    
    st.markdown("""
    > **Nota**: Todos los datos se guardan con integridad verificable (como blockchain).
    > Cada archivo incluye checksums para garantizar que no ha sido modificado.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📁 Exportar Historial Completo")
        
        if st.button("💾 Guardar Historial (JSON comprimido)", use_container_width=True):
            try:
                filepath = temporal.save_history()
                st.success(f"✅ Guardado en: `{filepath}`")
                
                # Verificación de integridad post-guardado
                integrity = temporal.temporal_store.verify_chain_integrity()
                if integrity['valid']:
                    st.info(f"🔐 Integridad verificada - Hash final: `{integrity['last_hash']}`")
            except Exception as e:
                st.error(f"Error al guardar: {str(e)}")
        
        if st.button("📊 Exportar Timeline (CSV)", use_container_width=True):
            try:
                filepath = temporal.temporal_store.export_timeline_csv()
                st.success(f"✅ Exportado a: `{filepath}`")
            except Exception as e:
                st.error(f"Error al exportar: {str(e)}")
        
        if st.button("📸 Exportar Snapshots (CSV)", use_container_width=True):
            try:
                filepath = temporal.temporal_store.export_snapshots_csv()
                st.success(f"✅ Exportado a: `{filepath}`")
            except Exception as e:
                st.error(f"Error al exportar: {str(e)}")
    
    with col2:
        st.markdown("#### 📥 Cargar Historial")
        
        # Listar archivos disponibles
        from pathlib import Path
        storage_path = temporal.temporal_store.storage_path
        
        if storage_path.exists():
            files = list(storage_path.glob("*.temporal.json.gz"))
            
            if files:
                st.markdown("**Archivos disponibles:**")
                for f in files[-5:]:  # Últimos 5
                    st.code(f.name, language="text")
                
                selected_file = st.selectbox(
                    "Seleccionar archivo",
                    [f.name for f in files]
                )
                
                if st.button("📥 Cargar Historial", use_container_width=True):
                    try:
                        success = temporal.load_history(str(storage_path / selected_file))
                        if success:
                            st.success("✅ Historial cargado exitosamente")
                            st.rerun()
                        else:
                            st.error("No se pudo cargar el archivo")
                    except Exception as e:
                        st.error(f"Error al cargar: {str(e)}")
            else:
                st.info("No hay archivos de historial guardados")
        else:
            st.info("Directorio de almacenamiento no existe aún")
    
    # Estadísticas del almacén
    st.markdown("---")
    st.markdown("#### 📊 Resumen del Almacén")
    
    stats = temporal.temporal_store.get_statistics()
    
    st.json({
        'system_id': stats['system_id'],
        'created_at': stats['created_at'],
        'total_events': stats['total_events'],
        'total_snapshots': stats['total_snapshots'],
        'unique_entities': stats['unique_entities'],
        'integrity': "✅ Válida" if stats['integrity'] else "❌ Corrupta",
        'storage_path': stats['storage_path']
    })


def show_advanced_analysis():
    """Análisis avanzado del sistema"""
    system = st.session_state.neural_system
    
    st.title("📊 Análisis Avanzado")
    
    if not st.session_state.simulation_results:
        st.warning("⚠️ Ejecuta primero una simulación para ver análisis avanzados")
        return
    
    # Reporte completo del sistema
    report = system.get_system_report()
    
    tab1, tab2, tab3 = st.tabs(["🎯 Resumen", "🔍 Consolidadores", "📊 Métricas de Riesgo"])
    
    with tab1:
        st.json(report['summary'])
    
    with tab2:
        for cons in report['consolidators']:
            with st.expander(f"📦 {cons['name']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Balance", f"${cons['total_balance']:,.0f}")
                    st.metric("Ganancia", f"${cons['total_profit']:,.0f}")
                
                with col2:
                    st.metric("Health Promedio", f"{cons['average_health']:.1f}/100")
                    st.metric("Células", f"{cons['active_cells']}/{cons['num_cells']}")
                
                # Células del consolidador
                st.markdown("**Células:**")
                for cell in cons['cells']:
                    role = "🎯" if cell['is_coordinator'] else "📍"
                    st.write(f"{role} {cell['name']} - ${cell['total_balance']:,.0f} (Health: {cell['health_score']:.1f})")
    
    with tab3:
        st.markdown("### ⚠️ Métricas de Riesgo Global")
        
        risk_data = report['global_risk']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Riesgo Compuesto", f"{risk_data['composite']:.1f}%")
            st.metric("Nivel", risk_data['level'])
        
        with col2:
            st.metric("Default Rate", f"{risk_data['default_rate']:.2f}%")
            st.metric("Volatilidad", f"{risk_data['volatility']:.2f}%")
        
        # Gráfico de radar para métricas de riesgo
        categories = ['Default', 'Volatilidad', 'Concentración', 'Liquidez']
        values = [
            risk_data['default_rate'],
            risk_data['volatility'],
            risk_data['concentration'],
            risk_data['liquidity']
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Riesgo'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Perfil de Riesgo del Sistema"
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
