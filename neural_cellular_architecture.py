"""
Sistema de Arquitectura Celular Neuronal para Mi-cochinito
===========================================================
Implementa una arquitectura neuronal multi-relacional donde cada nodo:
- Tiene relaciones HIJO, PADRE, HERMANO
- Comunica bidireccionalmente (extremo ↔ centro)
- Comparte línea temporal sincronizada
- Células coordinadoras actúan como gateways
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
import json
from collections import deque

# Importar clases base del sistema original
from cellular_architecture import (
    RiskLevel, CellState, ValueSource, RiskMetrics, RegulationRules
)


class MessageType(Enum):
    """Tipos de mensajes en el sistema neuronal"""
    DIRECTIVE = "directive"  # Centro → Extremo (backpropagation)
    REPORT = "report"  # Extremo → Centro (forward)
    QUERY = "query"  # Solicitud de información
    RESPONSE = "response"  # Respuesta a query
    ALERT = "alert"  # Alerta de riesgo
    COORDINATION = "coordination"  # Entre hermanos (lateral)


@dataclass
class Message:
    """Mensaje entre nodos del sistema"""
    msg_id: str
    msg_type: MessageType
    sender_id: str
    receiver_id: str
    timestamp: datetime
    content: Dict
    priority: int = 1  # 1=low, 5=critical


@dataclass
class NodeRelation:
    """Define relación entre dos nodos (conexión neuronal)"""
    relation_id: str
    node_a_id: str
    node_b_id: str
    relation_type: str  # "parent", "child", "sibling", "coordinator"
    weight: float = 1.0  # Peso de la conexión (como en red neuronal)
    is_active: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def adjust_weight(self, delta: float):
        """Ajusta peso de la conexión (aprendizaje)"""
        self.weight = max(0.0, min(2.0, self.weight + delta))


class GlobalTimeline:
    """Línea temporal global compartida por todos los nodos"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.current_month = 0
            cls._instance.current_timestamp = datetime.now()
            cls._instance.history = []
            cls._instance.events = deque(maxlen=1000)
        return cls._instance
    
    def advance_month(self):
        """Avanza un mes en el sistema completo"""
        self.current_month += 1
        self.current_timestamp = datetime.now()
        self.events.append({
            'month': self.current_month,
            'timestamp': self.current_timestamp,
            'type': 'month_advance'
        })
    
    def log_event(self, event_type: str, entity_id: str, data: Dict):
        """Registra evento en la línea temporal global"""
        self.events.append({
            'month': self.current_month,
            'timestamp': datetime.now(),
            'type': event_type,
            'entity': entity_id,
            'data': data
        })
    
    def get_history(self, months: int = None) -> List[Dict]:
        """Obtiene historial de N meses"""
        if months is None:
            return list(self.events)
        return list(self.events)[-months:]
    
    def get_current_state(self) -> Dict:
        """Estado actual del timeline"""
        return {
            'month': self.current_month,
            'timestamp': self.current_timestamp,
            'total_events': len(self.events)
        }


class NeuralSavingsCell:
    """
    Célula de Ahorro Neuronal
    - Puede actuar como coordinadora de grupo
    - Comunica bidireccionalmente
    - Mantiene relaciones con hermanos y padre
    """
    
    def __init__(
        self,
        cell_id: str,
        name: str,
        num_members: int = 1,
        regulation_rules: Optional[RegulationRules] = None,
        is_coordinator: bool = False
    ):
        self.cell_id = cell_id
        self.name = name
        self.num_members = num_members
        self.is_coordinator = is_coordinator
        
        # Timeline global compartida
        self.timeline = GlobalTimeline()
        
        # Fuentes de valor
        self.value_sources: Dict[str, ValueSource] = {}
        
        # Estado y regulación
        self.state = CellState.ACTIVE
        self.regulation_rules = regulation_rules or RegulationRules()
        self.risk_metrics = RiskMetrics()
        
        # Relaciones neuronales
        self.parent_id: Optional[str] = None  # Consolidador
        self.sibling_cells: Set[str] = set()  # Células hermanas
        self.managed_cells: Set[str] = set()  # Si es coordinadora
        self.relations: Dict[str, NodeRelation] = {}  # Todas las relaciones
        
        # Sistema de mensajería (como sinapsis)
        self.inbox: deque = deque(maxlen=100)
        self.outbox: deque = deque(maxlen=100)
        
        # Historial
        self.monthly_history: List[Dict] = []
        self.violations_log: List[Dict] = []
        
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # Log creación
        self.timeline.log_event('cell_created', self.cell_id, {
            'name': self.name,
            'is_coordinator': self.is_coordinator
        })
    
    def add_value_source(self, source: ValueSource):
        """Agrega una fuente de valor"""
        self.value_sources[source.source_id] = source
    
    def set_as_coordinator(self, managed_cell_ids: List[str]):
        """Convierte esta célula en coordinadora de un grupo"""
        self.is_coordinator = True
        self.managed_cells = set(managed_cell_ids)
        self.sibling_cells.update(managed_cell_ids)
        
        # Crear relaciones
        for cell_id in managed_cell_ids:
            relation = NodeRelation(
                relation_id=f"{self.cell_id}_manages_{cell_id}",
                node_a_id=self.cell_id,
                node_b_id=cell_id,
                relation_type="coordinator",
                weight=1.0
            )
            self.relations[relation.relation_id] = relation
        
        self.timeline.log_event('coordinator_assigned', self.cell_id, {
            'managed_cells': list(managed_cell_ids)
        })
    
    def add_sibling(self, cell_id: str, weight: float = 1.0):
        """Agrega una célula hermana con peso de conexión"""
        self.sibling_cells.add(cell_id)
        
        relation = NodeRelation(
            relation_id=f"{self.cell_id}_sibling_{cell_id}",
            node_a_id=self.cell_id,
            node_b_id=cell_id,
            relation_type="sibling",
            weight=weight
        )
        self.relations[relation.relation_id] = relation
    
    def set_parent(self, parent_id: str):
        """Establece nodo padre"""
        self.parent_id = parent_id
        
        relation = NodeRelation(
            relation_id=f"{self.cell_id}_parent_{parent_id}",
            node_a_id=self.cell_id,
            node_b_id=parent_id,
            relation_type="parent",
            weight=1.0
        )
        self.relations[relation.relation_id] = relation
    
    # ==================== COMUNICACIÓN ====================
    
    def send_message(self, msg: Message):
        """Envía mensaje (señal neuronal)"""
        self.outbox.append(msg)
        self.timeline.log_event('message_sent', self.cell_id, {
            'msg_id': msg.msg_id,
            'to': msg.receiver_id,
            'type': msg.msg_type.value
        })
    
    def receive_message(self, msg: Message):
        """Recibe mensaje"""
        self.inbox.append(msg)
        self.timeline.log_event('message_received', self.cell_id, {
            'msg_id': msg.msg_id,
            'from': msg.sender_id,
            'type': msg.msg_type.value
        })
    
    def process_messages(self) -> List[str]:
        """Procesa todos los mensajes en inbox"""
        processed = []
        
        while self.inbox:
            msg = self.inbox.popleft()
            
            if msg.msg_type == MessageType.DIRECTIVE:
                self._handle_directive(msg)
            elif msg.msg_type == MessageType.QUERY:
                self._handle_query(msg)
            elif msg.msg_type == MessageType.ALERT:
                self._handle_alert(msg)
            elif msg.msg_type == MessageType.COORDINATION:
                self._handle_coordination(msg)
            
            processed.append(msg.msg_id)
        
        return processed
    
    def _handle_directive(self, msg: Message):
        """Maneja directiva del centro (backpropagation)"""
        directive_type = msg.content.get('directive_type')
        
        if directive_type == 'adjust_utilization':
            new_rate = msg.content.get('new_utilization_rate')
            for source in self.value_sources.values():
                source.utilization_rate = new_rate
            self.timeline.log_event('directive_applied', self.cell_id, {
                'type': 'adjust_utilization',
                'new_rate': new_rate
            })
        
        elif directive_type == 'suspend_operations':
            self.state = CellState.SUSPENDED
            self.timeline.log_event('state_change', self.cell_id, {
                'new_state': 'suspended',
                'reason': 'directive'
            })
        
        elif directive_type == 'resume_operations':
            if self.state == CellState.SUSPENDED:
                self.state = CellState.ACTIVE
                self.timeline.log_event('state_change', self.cell_id, {
                    'new_state': 'active',
                    'reason': 'directive'
                })
        
        elif directive_type == 'adjust_risk_factor':
            new_factor = msg.content.get('risk_factor')
            for source in self.value_sources.values():
                source.risk_factor = new_factor
        
        # Si es coordinadora, propaga a células gestionadas
        if self.is_coordinator and self.managed_cells:
            self._propagate_to_managed_cells(msg)
    
    def _propagate_to_managed_cells(self, original_msg: Message):
        """Propaga directiva a células gestionadas (efecto cascada)"""
        for cell_id in self.managed_cells:
            # Ajustar mensaje por peso de relación
            relation_key = f"{self.cell_id}_manages_{cell_id}"
            weight = self.relations.get(relation_key, NodeRelation("", "", "", "", 1.0)).weight
            
            propagated_msg = Message(
                msg_id=f"{original_msg.msg_id}_prop_{cell_id}",
                msg_type=MessageType.DIRECTIVE,
                sender_id=self.cell_id,
                receiver_id=cell_id,
                timestamp=datetime.now(),
                content={**original_msg.content, 'propagation_weight': weight},
                priority=original_msg.priority
            )
            self.send_message(propagated_msg)
    
    def _handle_query(self, msg: Message):
        """Responde a consulta"""
        response = Message(
            msg_id=f"resp_{msg.msg_id}",
            msg_type=MessageType.RESPONSE,
            sender_id=self.cell_id,
            receiver_id=msg.sender_id,
            timestamp=datetime.now(),
            content={
                'query_id': msg.msg_id,
                'balance': self.get_total_balance(),
                'profit': self.get_total_profit(),
                'risk': self.risk_metrics.calculate_composite_risk()[0],
                'state': self.state.value,
                'is_coordinator': self.is_coordinator
            }
        )
        self.send_message(response)
    
    def _handle_alert(self, msg: Message):
        """Maneja alerta de otro nodo (propagación lateral)"""
        alert_type = msg.content.get('alert_type')
        
        if alert_type == 'high_risk_sibling':
            # Ajustar propio riesgo preventivamente (contagio de riesgo)
            for source in self.value_sources.values():
                source.risk_factor *= 0.95
            
            self.timeline.log_event('risk_adjusted', self.cell_id, {
                'reason': 'sibling_alert',
                'from': msg.sender_id
            })
    
    def _handle_coordination(self, msg: Message):
        """Maneja mensaje de coordinación entre hermanos"""
        coord_type = msg.content.get('coordination_type')
        
        if coord_type == 'share_resources':
            # Lógica de compartir recursos entre hermanos
            pass
        elif coord_type == 'sync_state':
            # Sincronizar estado con hermanos
            pass
    
    # ==================== AGREGACIÓN Y REPORTE ====================
    
    def aggregate_group_state(self, sibling_states: List[Dict]) -> Dict:
        """Agrega estado del grupo si es coordinadora"""
        if not self.is_coordinator:
            return {}
        
        total_balance = self.get_total_balance()
        total_profit = self.get_total_profit()
        group_risk = self.risk_metrics.calculate_composite_risk()[0]
        
        for sibling_state in sibling_states:
            total_balance += sibling_state.get('balance', 0)
            total_profit += sibling_state.get('profit', 0)
            group_risk += sibling_state.get('risk', 0)
        
        avg_risk = group_risk / (len(sibling_states) + 1) if sibling_states else group_risk
        
        return {
            'coordinator_id': self.cell_id,
            'group_size': len(self.managed_cells) + 1,
            'total_balance': total_balance,
            'total_profit': total_profit,
            'average_risk': avg_risk,
            'active_cells': sum(1 for s in sibling_states if s.get('state') == 'active') + (1 if self.state == CellState.ACTIVE else 0)
        }
    
    def report_to_parent(self) -> Message:
        """Genera reporte para el nodo padre (forward propagation)"""
        content = {
            'cell_id': self.cell_id,
            'balance': self.get_total_balance(),
            'profit': self.get_total_profit(),
            'risk': self.risk_metrics.calculate_composite_risk()[0],
            'state': self.state.value,
            'health': self.get_health_score(),
            'month': self.timeline.current_month
        }
        
        if self.is_coordinator:
            content['is_coordinator'] = True
            content['managed_cells_count'] = len(self.managed_cells)
        
        msg = Message(
            msg_id=f"report_{self.cell_id}_{self.timeline.current_month}",
            msg_type=MessageType.REPORT,
            sender_id=self.cell_id,
            receiver_id=self.parent_id or "unknown",
            timestamp=self.timeline.current_timestamp,
            content=content
        )
        
        return msg
    
    # ==================== SIMULACIÓN ====================
    
    def simulate_month(self, external_shocks: Optional[Dict] = None) -> Dict:
        """Simula un mes de operación"""
        month = self.timeline.current_month
        
        results = {
            'month': month,
            'cell_id': self.cell_id,
            'state': self.state.value,
            'violations': []
        }
        
        # Procesar mensajes pendientes
        self.process_messages()
        
        # Verificar si está suspendida
        if self.state == CellState.SUSPENDED:
            results['message'] = "Célula suspendida, no opera este mes"
            return results
        
        # Aplicar shocks externos si hay
        if external_shocks:
            self._apply_external_shocks(external_shocks)
        
        # Procesar cada fuente de valor
        total_growth = 0.0
        source_details = []
        
        for source_id, source in self.value_sources.items():
            if not source.is_active:
                continue
            
            # Agregar contribución mensual
            source.add_contribution(source.monthly_contribution)
            
            # Calcular y aplicar crecimiento
            growth = source.calculate_growth()
            source.apply_growth(growth)
            total_growth += growth
            
            source_details.append({
                'source_id': source_id,
                'balance': source.current_balance,
                'growth': growth,
                'profit': source.total_profit
            })
        
        # Actualizar métricas de riesgo
        self._update_risk_metrics()
        composite_risk, risk_level = self.risk_metrics.calculate_composite_risk()
        
        # Verificar violaciones de reglas
        cell_data = {
            'utilization': self._calculate_average_utilization(),
            'total_balance': self.get_total_balance()
        }
        violations = self.regulation_rules.check_violation(self.risk_metrics, cell_data)
        
        # Auto-regulación: tomar acciones si hay violaciones
        if violations:
            self._auto_regulate(violations, risk_level)
            results['violations'] = violations
            self.violations_log.append({
                'month': month,
                'violations': violations,
                'action_taken': self.state.value
            })
        
        # Guardar en historial
        results.update({
            'total_balance': self.get_total_balance(),
            'total_profit': self.get_total_profit(),
            'total_growth': total_growth,
            'composite_risk': composite_risk,
            'risk_level': risk_level.name,
            'sources': source_details
        })
        
        self.monthly_history.append(results)
        self.last_updated = datetime.now()
        
        # Log evento en timeline global
        self.timeline.log_event('month_simulated', self.cell_id, {
            'balance': results['total_balance'],
            'risk': composite_risk
        })
        
        return results
    
    def _apply_external_shocks(self, shocks: Dict):
        """Aplica shocks externos a la célula"""
        if 'default_shock' in shocks:
            self.risk_metrics.default_rate += shocks['default_shock']
        
        if 'volatility_shock' in shocks:
            self.risk_metrics.volatility += shocks['volatility_shock']
    
    def _calculate_average_utilization(self) -> float:
        """Calcula tasa de utilización promedio"""
        if not self.value_sources:
            return 0.0
        return np.mean([s.utilization_rate for s in self.value_sources.values()])
    
    def _update_risk_metrics(self):
        """Actualiza las métricas de riesgo"""
        if not self.value_sources:
            return
        
        # Calcular concentración de riesgo
        total_balance = self.get_total_balance()
        if total_balance > 0:
            concentrations = [
                (source.current_balance / total_balance) * 100
                for source in self.value_sources.values()
            ]
            self.risk_metrics.concentration_risk = max(concentrations)
        
        # Volatilidad (basada en variación de crecimiento)
        if len(self.monthly_history) > 3:
            recent_growths = [h['total_growth'] for h in self.monthly_history[-3:]]
            self.risk_metrics.volatility = np.std(recent_growths) / np.mean(recent_growths) * 100 if np.mean(recent_growths) != 0 else 0
        
        # Liquidez (porcentaje no utilizado)
        avg_util = self._calculate_average_utilization()
        self.risk_metrics.liquidity_risk = max(0, 100 - avg_util)
    
    def _auto_regulate(self, violations: List[str], risk_level: RiskLevel):
        """Auto-regulación basada en violaciones"""
        if risk_level == RiskLevel.CRITICAL:
            self.state = CellState.SUSPENDED
            self.timeline.log_event('auto_regulation', self.cell_id, {
                'action': 'suspended',
                'reason': 'critical_risk'
            })
        elif risk_level == RiskLevel.HIGH:
            if self.state == CellState.ACTIVE:
                self.state = CellState.RECOVERING
                # Reducir utilización
                for source in self.value_sources.values():
                    source.utilization_rate *= 0.8
                self.timeline.log_event('auto_regulation', self.cell_id, {
                    'action': 'recovering',
                    'reason': 'high_risk'
                })
        elif self.state == CellState.RECOVERING and risk_level <= RiskLevel.LOW:
            self.state = CellState.ACTIVE
            self.timeline.log_event('auto_regulation', self.cell_id, {
                'action': 'reactivated',
                'reason': 'risk_normalized'
            })
    
    # ==================== MÉTRICAS ====================
    
    def get_total_balance(self) -> float:
        """Balance total de todas las fuentes"""
        return sum(source.current_balance for source in self.value_sources.values())
    
    def get_total_profit(self) -> float:
        """Ganancia total"""
        return sum(source.total_profit for source in self.value_sources.values())
    
    def get_health_score(self) -> float:
        """Health score de la célula (0-100)"""
        composite_risk, _ = self.risk_metrics.calculate_composite_risk()
        
        # Factores positivos
        utilization = self._calculate_average_utilization()
        utilization_score = 100 * (utilization / 85.0) if utilization <= 85 else 100
        
        # Penalizaciones por riesgo
        risk_penalty = composite_risk
        
        # Score final
        health = (utilization_score * 0.4) + ((100 - risk_penalty) * 0.6)
        
        return max(0, min(100, health))
    
    def export_state(self) -> Dict:
        """Exporta estado completo de la célula"""
        return {
            'cell_id': self.cell_id,
            'name': self.name,
            'is_coordinator': self.is_coordinator,
            'managed_cells': list(self.managed_cells),
            'sibling_cells': list(self.sibling_cells),
            'parent_id': self.parent_id,
            'state': self.state.value,
            'num_members': self.num_members,
            'total_balance': self.get_total_balance(),
            'total_profit': self.get_total_profit(),
            'health_score': self.get_health_score(),
            'risk': {
                'composite': self.risk_metrics.calculate_composite_risk()[0],
                'level': self.risk_metrics.calculate_composite_risk()[1].name
            },
            'sources': [
                {
                    'source_id': s.source_id,
                    'name': s.name,
                    'balance': s.current_balance,
                    'profit': s.total_profit
                }
                for s in self.value_sources.values()
            ]
        }


# Continúa en la siguiente sección...


class NeuralConsolidatorNode:
    """
    Nodo Consolidador Neuronal
    - Agrega múltiples células (algunas coordinadoras)
    - Comunica con MasterNode y con células
    - Propaga directivas hacia abajo
    """
    
    def __init__(
        self,
        node_id: str,
        name: str,
        regulation_rules: Optional[RegulationRules] = None
    ):
        self.node_id = node_id
        self.name = name
        self.cells: Dict[str, NeuralSavingsCell] = {}
        self.regulation_rules = regulation_rules or RegulationRules()
        
        # Timeline global
        self.timeline = GlobalTimeline()
        
        # Métricas consolidadas
        self.consolidated_metrics = RiskMetrics()
        self.monthly_consolidated_history: List[Dict] = []
        
        # Relaciones
        self.parent_id: Optional[str] = None  # MasterNode
        self.sibling_consolidators: Set[str] = set()
        self.coordinator_cells: Set[str] = set()  # Células coordinadoras
        
        # Mensajería
        self.inbox: deque = deque(maxlen=200)
        self.outbox: deque = deque(maxlen=200)
        
        self.created_at = datetime.now()
        
        self.timeline.log_event('consolidator_created', self.node_id, {
            'name': self.name
        })
    
    def add_cell(self, cell: NeuralSavingsCell):
        """Agrega una célula al consolidador"""
        self.cells[cell.cell_id] = cell
        cell.set_parent(self.node_id)
        
        if cell.is_coordinator:
            self.coordinator_cells.add(cell.cell_id)
        
        self.timeline.log_event('cell_added', self.node_id, {
            'cell_id': cell.cell_id,
            'is_coordinator': cell.is_coordinator
        })
    
    def remove_cell(self, cell_id: str):
        """Remueve una célula"""
        if cell_id in self.cells:
            del self.cells[cell_id]
            self.coordinator_cells.discard(cell_id)
    
    def set_parent(self, master_id: str):
        """Establece nodo maestro padre"""
        self.parent_id = master_id
    
    # ==================== MENSAJERÍA ====================
    
    def send_message(self, msg: Message):
        """Envía mensaje"""
        self.outbox.append(msg)
        self.timeline.log_event('message_sent', self.node_id, {
            'msg_id': msg.msg_id,
            'to': msg.receiver_id,
            'type': msg.msg_type.value
        })
    
    def receive_message(self, msg: Message):
        """Recibe mensaje"""
        self.inbox.append(msg)
    
    def process_messages(self) -> List[str]:
        """Procesa mensajes"""
        processed = []
        
        while self.inbox:
            msg = self.inbox.popleft()
            
            if msg.msg_type == MessageType.DIRECTIVE:
                self._handle_directive(msg)
            elif msg.msg_type == MessageType.REPORT:
                self._handle_report(msg)
            
            processed.append(msg.msg_id)
        
        return processed
    
    def _handle_directive(self, msg: Message):
        """Maneja directiva del MasterNode"""
        directive_type = msg.content.get('directive_type')
        target = msg.content.get('target', 'all')  # all, coordinators, specific_cell
        
        # Propagar solo a coordinadoras (eficiencia)
        if target == 'coordinators':
            for coord_id in self.coordinator_cells:
                if coord_id in self.cells:
                    cell_msg = Message(
                        msg_id=f"{msg.msg_id}_to_{coord_id}",
                        msg_type=MessageType.DIRECTIVE,
                        sender_id=self.node_id,
                        receiver_id=coord_id,
                        timestamp=datetime.now(),
                        content=msg.content,
                        priority=msg.priority
                    )
                    self.cells[coord_id].receive_message(cell_msg)
        
        # Propagar a todas
        elif target == 'all':
            for cell in self.cells.values():
                cell_msg = Message(
                    msg_id=f"{msg.msg_id}_to_{cell.cell_id}",
                    msg_type=MessageType.DIRECTIVE,
                    sender_id=self.node_id,
                    receiver_id=cell.cell_id,
                    timestamp=datetime.now(),
                    content=msg.content,
                    priority=msg.priority
                )
                cell.receive_message(cell_msg)
    
    def _handle_report(self, msg: Message):
        """Procesa reporte de célula"""
        # Almacenar información del reporte
        pass
    
    def broadcast_directive(self, directive_type: str, content: Dict, target: str = 'coordinators'):
        """Envía directiva a células"""
        msg = Message(
            msg_id=f"dir_{self.node_id}_{self.timeline.current_month}_{directive_type}",
            msg_type=MessageType.DIRECTIVE,
            sender_id=self.node_id,
            receiver_id="cells",
            timestamp=datetime.now(),
            content={
                'directive_type': directive_type,
                'target': target,
                **content
            },
            priority=3
        )
        
        self._handle_directive(msg)
    
    def collect_reports(self) -> List[Message]:
        """Solicita reportes a células coordinadoras"""
        reports = []
        for coord_id in self.coordinator_cells:
            if coord_id in self.cells:
                report = self.cells[coord_id].report_to_parent()
                reports.append(report)
        return reports
    
    def report_to_master(self) -> Message:
        """Genera reporte para MasterNode"""
        content = {
            'consolidator_id': self.node_id,
            'total_balance': self.get_total_balance(),
            'total_profit': self.get_total_profit(),
            'average_health': self.get_average_health(),
            'risk': self.consolidated_metrics.calculate_composite_risk()[0],
            'num_cells': len(self.cells),
            'active_cells': sum(1 for c in self.cells.values() if c.state == CellState.ACTIVE),
            'coordinator_cells': len(self.coordinator_cells),
            'month': self.timeline.current_month
        }
        
        msg = Message(
            msg_id=f"report_cons_{self.node_id}_{self.timeline.current_month}",
            msg_type=MessageType.REPORT,
            sender_id=self.node_id,
            receiver_id=self.parent_id or "unknown",
            timestamp=self.timeline.current_timestamp,
            content=content
        )
        
        return msg
    
    # ==================== SIMULACIÓN ====================
    
    def simulate_month(self, external_shocks: Optional[Dict] = None):
        """Simula un mes para todas las células"""
        month = self.timeline.current_month
        
        results = {
            'month': month,
            'node_id': self.node_id,
            'cells_results': []
        }
        
        # Procesar mensajes pendientes
        self.process_messages()
        
        # Simular cada célula
        for cell_id, cell in self.cells.items():
            cell_shocks = external_shocks.get(cell_id) if external_shocks else None
            cell_result = cell.simulate_month(cell_shocks)
            results['cells_results'].append(cell_result)
        
        # Consolidar métricas
        self._consolidate_metrics()
        
        # Agregar métricas consolidadas
        composite_risk, risk_level = self.consolidated_metrics.calculate_composite_risk()
        results.update({
            'total_balance': self.get_total_balance(),
            'total_profit': self.get_total_profit(),
            'average_health': self.get_average_health(),
            'consolidated_risk': composite_risk,
            'risk_level': risk_level.name,
            'active_cells': sum(1 for c in self.cells.values() if c.state == CellState.ACTIVE),
            'total_cells': len(self.cells),
            'coordinator_cells': len(self.coordinator_cells)
        })
        
        self.monthly_consolidated_history.append(results)
        
        self.timeline.log_event('consolidator_simulated', self.node_id, {
            'balance': results['total_balance'],
            'risk': composite_risk
        })
        
        return results
    
    def _consolidate_metrics(self):
        """Consolida métricas de riesgo de todas las células"""
        if not self.cells:
            return
        
        total_balance = self.get_total_balance()
        if total_balance == 0:
            return
        
        weighted_default = 0
        weighted_volatility = 0
        weighted_liquidity = 0
        
        for cell in self.cells.values():
            weight = cell.get_total_balance() / total_balance
            weighted_default += cell.risk_metrics.default_rate * weight
            weighted_volatility += cell.risk_metrics.volatility * weight
            weighted_liquidity += cell.risk_metrics.liquidity_risk * weight
        
        self.consolidated_metrics.default_rate = weighted_default
        self.consolidated_metrics.volatility = weighted_volatility
        self.consolidated_metrics.liquidity_risk = weighted_liquidity
        
        # Concentración a nivel de nodo
        if len(self.cells) > 0:
            cell_balances = [c.get_total_balance() for c in self.cells.values()]
            max_concentration = max(cell_balances) / total_balance * 100 if total_balance > 0 else 0
            self.consolidated_metrics.concentration_risk = max_concentration
    
    # ==================== MÉTRICAS ====================
    
    def get_total_balance(self) -> float:
        """Balance total de todas las células"""
        return sum(cell.get_total_balance() for cell in self.cells.values())
    
    def get_total_profit(self) -> float:
        """Ganancia total de todas las células"""
        return sum(cell.get_total_profit() for cell in self.cells.values())
    
    def get_average_health(self) -> float:
        """Health score promedio de las células"""
        if not self.cells:
            return 0.0
        return np.mean([cell.get_health_score() for cell in self.cells.values()])
    
    def export_state(self) -> Dict:
        """Exporta estado consolidado del nodo"""
        return {
            'node_id': self.node_id,
            'name': self.name,
            'total_balance': self.get_total_balance(),
            'total_profit': self.get_total_profit(),
            'average_health': self.get_average_health(),
            'num_cells': len(self.cells),
            'active_cells': sum(1 for c in self.cells.values() if c.state == CellState.ACTIVE),
            'coordinator_cells': len(self.coordinator_cells),
            'consolidated_risk': {
                'composite': self.consolidated_metrics.calculate_composite_risk()[0],
                'level': self.consolidated_metrics.calculate_composite_risk()[1].name
            },
            'cells': [cell.export_state() for cell in self.cells.values()]
        }


class NeuralMasterNode:
    """
    Nodo Maestro Neuronal
    - Centro del sistema completo
    - Coordina todos los consolidadores
    - Implementa feedback loop completo
    """
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.consolidator_nodes: Dict[str, NeuralConsolidatorNode] = {}
        self.global_regulation_rules = RegulationRules()
        
        # Timeline global (singleton)
        self.timeline = GlobalTimeline()
        
        # Métricas globales
        self.global_metrics = RiskMetrics()
        self.system_history: List[Dict] = []
        
        # Mensajería
        self.inbox: deque = deque(maxlen=500)
        self.outbox: deque = deque(maxlen=500)
        
        self.created_at = datetime.now()
        
        self.timeline.log_event('master_created', 'master', {
            'system_name': system_name
        })
    
    def add_consolidator(self, consolidator: NeuralConsolidatorNode):
        """Agrega un nodo consolidador al sistema"""
        self.consolidator_nodes[consolidator.node_id] = consolidator
        consolidator.set_parent('master')
        
        self.timeline.log_event('consolidator_added', 'master', {
            'consolidator_id': consolidator.node_id
        })
    
    # ==================== DIRECTIVAS GLOBALES ====================
    
    def broadcast_global_directive(self, directive_type: str, content: Dict, target: str = 'coordinators'):
        """Envía directiva global a todos los consolidadores"""
        for consolidator in self.consolidator_nodes.values():
            msg = Message(
                msg_id=f"global_dir_{directive_type}_{self.timeline.current_month}",
                msg_type=MessageType.DIRECTIVE,
                sender_id='master',
                receiver_id=consolidator.node_id,
                timestamp=datetime.now(),
                content={
                    'directive_type': directive_type,
                    'target': target,
                    **content
                },
                priority=5
            )
            consolidator.receive_message(msg)
        
        self.timeline.log_event('global_directive', 'master', {
            'type': directive_type,
            'target': target
        })
    
    def adaptive_risk_control(self):
        """Control adaptativo de riesgo (feedback loop)"""
        composite_risk, risk_level = self.global_metrics.calculate_composite_risk()
        
        if risk_level == RiskLevel.CRITICAL:
            # Reducir utilización drásticamente
            self.broadcast_global_directive(
                'adjust_utilization',
                {'new_utilization_rate': 50.0},
                target='all'
            )
            self.timeline.log_event('adaptive_control', 'master', {
                'action': 'emergency_reduction',
                'risk': composite_risk
            })
        
        elif risk_level == RiskLevel.HIGH:
            # Reducir utilización moderadamente
            self.broadcast_global_directive(
                'adjust_utilization',
                {'new_utilization_rate': 70.0},
                target='coordinators'
            )
        
        elif risk_level == RiskLevel.LOW:
            # Permitir mayor utilización
            self.broadcast_global_directive(
                'adjust_utilization',
                {'new_utilization_rate': 90.0},
                target='coordinators'
            )
    
    # ==================== SIMULACIÓN ====================
    
    def simulate_month(self, external_shocks: Optional[Dict] = None):
        """Simula un mes para todo el sistema"""
        # Avanzar timeline global
        self.timeline.advance_month()
        month = self.timeline.current_month
        
        results = {
            'month': month,
            'system': self.system_name,
            'timestamp': self.timeline.current_timestamp,
            'consolidators_results': []
        }
        
        # Simular cada consolidador
        for node_id, consolidator in self.consolidator_nodes.items():
            node_shocks = external_shocks.get(node_id) if external_shocks else None
            node_result = consolidator.simulate_month(node_shocks)
            results['consolidators_results'].append(node_result)
        
        # Consolidar métricas globales
        self._consolidate_global_metrics()
        
        # Aplicar control adaptativo de riesgo
        self.adaptive_risk_control()
        
        composite_risk, risk_level = self.global_metrics.calculate_composite_risk()
        results.update({
            'total_system_balance': self.get_total_balance(),
            'total_system_profit': self.get_total_profit(),
            'system_health_score': self.get_system_health(),
            'global_risk': composite_risk,
            'global_risk_level': risk_level.name,
            'total_consolidators': len(self.consolidator_nodes),
            'total_cells': self.get_total_cells(),
            'active_cells': self.get_active_cells()
        })
        
        self.system_history.append(results)
        
        self.timeline.log_event('system_simulated', 'master', {
            'balance': results['total_system_balance'],
            'risk': composite_risk
        })
        
        return results
    
    def simulate_multiple_months(self, num_months: int, external_shocks_per_month: Optional[Dict[int, Dict]] = None):
        """Simula múltiples meses"""
        results = []
        for month_num in range(1, num_months + 1):
            shocks = external_shocks_per_month.get(month_num) if external_shocks_per_month else None
            month_result = self.simulate_month(shocks)
            results.append(month_result)
        return results
    
    def _consolidate_global_metrics(self):
        """Consolida métricas a nivel de sistema completo"""
        if not self.consolidator_nodes:
            return
        
        total_balance = self.get_total_balance()
        if total_balance == 0:
            return
        
        weighted_default = 0
        weighted_volatility = 0
        weighted_liquidity = 0
        
        for consolidator in self.consolidator_nodes.values():
            weight = consolidator.get_total_balance() / total_balance
            weighted_default += consolidator.consolidated_metrics.default_rate * weight
            weighted_volatility += consolidator.consolidated_metrics.volatility * weight
            weighted_liquidity += consolidator.consolidated_metrics.liquidity_risk * weight
        
        self.global_metrics.default_rate = weighted_default
        self.global_metrics.volatility = weighted_volatility
        self.global_metrics.liquidity_risk = weighted_liquidity
        
        # Concentración a nivel global
        consolidator_balances = [c.get_total_balance() for c in self.consolidator_nodes.values()]
        max_concentration = max(consolidator_balances) / total_balance * 100 if total_balance > 0 else 0
        self.global_metrics.concentration_risk = max_concentration
    
    # ==================== MÉTRICAS ====================
    
    def get_total_balance(self) -> float:
        """Balance total del sistema"""
        return sum(c.get_total_balance() for c in self.consolidator_nodes.values())
    
    def get_total_profit(self) -> float:
        """Ganancia total del sistema"""
        return sum(c.get_total_profit() for c in self.consolidator_nodes.values())
    
    def get_total_cells(self) -> int:
        """Número total de células en el sistema"""
        return sum(len(c.cells) for c in self.consolidator_nodes.values())
    
    def get_active_cells(self) -> int:
        """Número de células activas"""
        return sum(
            sum(1 for cell in c.cells.values() if cell.state == CellState.ACTIVE)
            for c in self.consolidator_nodes.values()
        )
    
    def get_system_health(self) -> float:
        """Health score del sistema completo"""
        if not self.consolidator_nodes:
            return 0.0
        
        avg_consolidator_health = np.mean([c.get_average_health() for c in self.consolidator_nodes.values()])
        
        # Ajustar por riesgo global
        composite_risk, _ = self.global_metrics.calculate_composite_risk()
        risk_penalty = composite_risk / 100
        
        return avg_consolidator_health * (1 - risk_penalty * 0.3)
    
    def get_system_report(self) -> Dict:
        """Genera reporte completo del sistema"""
        return {
            'system_name': self.system_name,
            'timestamp': datetime.now().isoformat(),
            'current_month': self.timeline.current_month,
            'summary': {
                'total_balance': self.get_total_balance(),
                'total_profit': self.get_total_profit(),
                'system_health': self.get_system_health(),
                'total_consolidators': len(self.consolidator_nodes),
                'total_cells': self.get_total_cells(),
                'active_cells': self.get_active_cells()
            },
            'global_risk': {
                'composite': self.global_metrics.calculate_composite_risk()[0],
                'level': self.global_metrics.calculate_composite_risk()[1].name,
                'default_rate': self.global_metrics.default_rate,
                'volatility': self.global_metrics.volatility,
                'concentration': self.global_metrics.concentration_risk,
                'liquidity': self.global_metrics.liquidity_risk
            },
            'timeline': self.timeline.get_current_state(),
            'consolidators': [c.export_state() for c in self.consolidator_nodes.values()]
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Exporta historial del sistema a DataFrame"""
        if not self.system_history:
            return pd.DataFrame()
        
        flat_data = []
        for record in self.system_history:
            flat_data.append({
                'Mes': record['month'],
                'Balance Total': record['total_system_balance'],
                'Ganancia Total': record['total_system_profit'],
                'Health Score': record['system_health_score'],
                'Riesgo Global': record['global_risk'],
                'Nivel de Riesgo': record['global_risk_level'],
                'Células Activas': record['active_cells'],
                'Total Células': record['total_cells']
            })
        
        return pd.DataFrame(flat_data)


def create_neural_example_system() -> NeuralMasterNode:
    """
    Crea sistema neuronal de ejemplo con células coordinadoras
    """
    # Crear nodo maestro
    master = NeuralMasterNode("Sistema SIDEPE Neuronal")
    
    # Crear consolidadores (regiones)
    consolidator_norte = NeuralConsolidatorNode("CON-NORTE", "Región Norte")
    consolidator_sur = NeuralConsolidatorNode("CON-SUR", "Región Sur")
    
    # ===== REGIÓN NORTE =====
    
    # Crear célula coordinadora Norte
    cell_norte_coord = NeuralSavingsCell("CELL-N-COORD", "Coordinadora Norte", 50, is_coordinator=True)
    cell_norte_coord.add_value_source(ValueSource(
        source_id="SRC-NUCLEUS",
        name="Núcleo Productivo",
        initial_capital=0,
        monthly_contribution=42500,
        gpm_rate=2.5,
        utilization_rate=85.0,
        risk_factor=0.95
    ))
    
    # Células gestionadas por coordinadora
    cell_norte_1 = NeuralSavingsCell("CELL-N1", "Grupo Norte A", 30)
    cell_norte_1.add_value_source(ValueSource(
        "SRC-NUCLEUS", "Núcleo", 0, 25500, 2.3, 80.0, 0.97
    ))
    
    cell_norte_2 = NeuralSavingsCell("CELL-N2", "Grupo Norte B", 25)
    cell_norte_2.add_value_source(ValueSource(
        "SRC-NUCLEUS", "Núcleo", 0, 21250, 2.4, 82.0, 0.96
    ))
    
    # Establecer coordinación
    cell_norte_coord.set_as_coordinator(["CELL-N1", "CELL-N2"])
    cell_norte_1.add_sibling("CELL-N-COORD")
    cell_norte_2.add_sibling("CELL-N-COORD")
    
    # ===== REGIÓN SUR =====
    
    # Crear célula coordinadora Sur
    cell_sur_coord = NeuralSavingsCell("CELL-S-COORD", "Coordinadora Sur", 40, is_coordinator=True)
    cell_sur_coord.add_value_source(ValueSource(
        "SRC-NUCLEUS", "Núcleo", 0, 34000, 2.7, 88.0, 0.92
    ))
    
    cell_sur_1 = NeuralSavingsCell("CELL-S1", "Grupo Sur A", 20)
    cell_sur_1.add_value_source(ValueSource(
        "SRC-NUCLEUS", "Núcleo", 0, 17000, 2.6, 85.0, 0.93
    ))
    
    # Establecer coordinación
    cell_sur_coord.set_as_coordinator(["CELL-S1"])
    cell_sur_1.add_sibling("CELL-S-COORD")
    
    # ===== ENSAMBLAR JERARQUÍA =====
    
    consolidator_norte.add_cell(cell_norte_coord)
    consolidator_norte.add_cell(cell_norte_1)
    consolidator_norte.add_cell(cell_norte_2)
    
    consolidator_sur.add_cell(cell_sur_coord)
    consolidator_sur.add_cell(cell_sur_1)
    
    master.add_consolidator(consolidator_norte)
    master.add_consolidator(consolidator_sur)
    
    return master


if __name__ == "__main__":
    print("=" * 70)
    print("Sistema de Arquitectura Celular NEURONAL - Mi-cochinito")
    print("=" * 70)
    
    # Crear sistema
    system = create_neural_example_system()
    
    print(f"\n✅ Sistema creado: {system.system_name}")
    print(f"   - Consolidadores: {len(system.consolidator_nodes)}")
    print(f"   - Células totales: {system.get_total_cells()}")
    
    # Simular 12 meses
    print("\n🔄 Simulando 12 meses...")
    results = system.simulate_multiple_months(12)
    
    # Reporte final
    report = system.get_system_report()
    
    print(f"\n{'='*70}")
    print("REPORTE FINAL DEL SISTEMA NEURONAL")
    print(f"{'='*70}")
    print(f"Balance Total: ${report['summary']['total_balance']:,.2f}")
    print(f"Ganancia Total: ${report['summary']['total_profit']:,.2f}")
    print(f"Health Score: {report['summary']['system_health']:.1f}/100")
    print(f"Células Activas: {report['summary']['active_cells']}/{report['summary']['total_cells']}")
    print(f"\nRiesgo Global: {report['global_risk']['composite']:.1f}% ({report['global_risk']['level']})")
    print(f"Timeline: Mes {report['current_month']}, {len(system.timeline.events)} eventos registrados")
    
    # DataFrame
    df = system.export_to_dataframe()
    print(f"\n{df.to_string()}")
    
    print("\n✅ Sistema Neuronal Operacional")

print("Neural Cellular Architecture module loaded successfully")
