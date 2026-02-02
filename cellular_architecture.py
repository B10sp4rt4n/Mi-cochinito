"""
Sistema de Arquitectura Celular para Mi-cochinito
==================================================
Implementa una arquitectura fractal donde cada nodo de ahorro es una célula
autorregulada con capacidades de detección de riesgo e intercambio de valores.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
import json
from collections import deque


class MessageType(Enum):
    """Tipos de mensajes en el sistema"""
    DIRECTIVE = "directive"  # Centro → Extremo
    REPORT = "report"  # Extremo → Centro
    QUERY = "query"  # Solicitud de información
    RESPONSE = "response"  # Respuesta a query
    ALERT = "alert"  # Alerta de riesgo
    COORDINATION = "coordination"  # Entre hermanos


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
    """Define relación entre dos nodos"""
    relation_id: str
    node_a_id: str
    node_b_id: str
    relation_type: str  # "parent", "child", "sibling", "coordinator"
    weight: float = 1.0  # Peso de la conexión
    is_active: bool = True
    metadata: Dict = field(default_factory=dict)


class GlobalTimeline:
    """Línea temporal global compartida por todos los nodos"""
    def __init__(self):
        self.current_month: int = 0
        self.current_timestamp: datetime = datetime.now()
        self.history: List[Dict] = []
        self.events: deque = deque(maxlen=1000)
    
    def advance_month(self):
        """Avanza un mes en el sistema"""
        self.current_month += 1
        self.current_timestamp = datetime.now()
        self.events.append({
            'month': self.current_month,
            'timestamp': self.current_timestamp,
            'type': 'month_advance'
        })
    
    def log_event(self, event_type: str, entity_id: str, data: Dict):
        """Registra evento en la línea temporal"""
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


class RiskLevel(Enum):
    """Niveles de riesgo en el sistema"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class CellState(Enum):
    """Estados posibles de una célula"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    RECOVERING = "recovering"
    CLOSED = "closed"


@dataclass
class ValueSource:
    """Fuente de valor/aportación al sistema"""
    source_id: str
    name: str
    initial_capital: float
    monthly_contribution: float
    gpm_rate: float  # Tasa de crecimiento mensual
    utilization_rate: float = 85.0
    risk_factor: float = 1.0  # Factor de riesgo (1.0 = neutro)
    is_active: bool = True
    
    # Estado actual
    current_balance: float = 0.0
    total_profit: float = 0.0
    
    def __post_init__(self):
        if self.current_balance == 0.0:
            self.current_balance = self.initial_capital
    
    def calculate_growth(self) -> float:
        """Calcula crecimiento mensual de esta fuente"""
        utilized_capital = self.current_balance * (self.utilization_rate / 100)
        growth = utilized_capital * (self.gpm_rate / 100)
        return growth * self.risk_factor
    
    def add_contribution(self, amount: float):
        """Agrega contribución mensual"""
        self.current_balance += amount
    
    def apply_growth(self, growth: float):
        """Aplica crecimiento calculado"""
        self.current_balance += growth
        self.total_profit += growth


@dataclass
class RiskMetrics:
    """Métricas de riesgo de una célula"""
    default_rate: float = 0.0
    volatility: float = 0.0
    concentration_risk: float = 0.0
    liquidity_risk: float = 0.0
    operational_risk: float = 0.0
    
    def calculate_composite_risk(self) -> Tuple[float, RiskLevel]:
        """Calcula riesgo compuesto (0-100) y su nivel"""
        weights = {
            'default': 0.35,
            'volatility': 0.20,
            'concentration': 0.20,
            'liquidity': 0.15,
            'operational': 0.10
        }
        
        composite = (
            self.default_rate * weights['default'] +
            self.volatility * weights['volatility'] +
            self.concentration_risk * weights['concentration'] +
            self.liquidity_risk * weights['liquidity'] +
            self.operational_risk * weights['operational']
        )
        
        # Determinar nivel de riesgo
        if composite < 20:
            level = RiskLevel.VERY_LOW
        elif composite < 40:
            level = RiskLevel.LOW
        elif composite < 60:
            level = RiskLevel.MEDIUM
        elif composite < 80:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL
            
        return composite, level


@dataclass
class RegulationRules:
    """Reglas de autorregulación de una célula"""
    max_default_rate: float = 5.0
    min_utilization: float = 70.0
    max_utilization: float = 95.0
    min_liquidity_ratio: float = 10.0
    max_concentration_single_source: float = 40.0
    emergency_stop_threshold: float = 85.0  # Score de riesgo
    
    def check_violation(self, metrics: RiskMetrics, cell_data: Dict) -> List[str]:
        """Verifica violaciones de reglas"""
        violations = []
        
        if metrics.default_rate > self.max_default_rate:
            violations.append(f"Default rate {metrics.default_rate:.1f}% excede límite {self.max_default_rate}%")
        
        if cell_data.get('utilization', 0) < self.min_utilization:
            violations.append(f"Utilización {cell_data['utilization']:.1f}% bajo mínimo {self.min_utilization}%")
        
        if cell_data.get('utilization', 0) > self.max_utilization:
            violations.append(f"Utilización {cell_data['utilization']:.1f}% excede máximo {self.max_utilization}%")
        
        composite_risk, _ = metrics.calculate_composite_risk()
        if composite_risk > self.emergency_stop_threshold:
            violations.append(f"EMERGENCIA: Riesgo compuesto {composite_risk:.1f}% excede umbral {self.emergency_stop_threshold}%")
        
        return violations


class SavingsCell:
    """
    Célula de Ahorro Individual - Unidad básica autorregulada
    Puede contener múltiples fuentes de valor y se autoregula según su riesgo
    """
    
    def __init__(
        self,
        cell_id: str,
        name: str,
        num_members: int,
        regulation_rules: Optional[RegulationRules] = None
    ):
        self.cell_id = cell_id
        self.name = name
        self.num_members = num_members
        self.state = CellState.ACTIVE
        
        # Fuentes de valor
        self.value_sources: Dict[str, ValueSource] = {}
        
        # Sistema de regulación
        self.regulation_rules = regulation_rules or RegulationRules()
        self.risk_metrics = RiskMetrics()
        
        # Historial
        self.monthly_history: List[Dict] = []
        self.violations_log: List[Dict] = []
        
        # Metadata
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def add_value_source(self, source: ValueSource):
        """Agrega una fuente de valor a la célula"""
        self.value_sources[source.source_id] = source
        self._update_risk_metrics()
    
    def remove_value_source(self, source_id: str):
        """Remueve una fuente de valor"""
        if source_id in self.value_sources:
            del self.value_sources[source_id]
            self._update_risk_metrics()
    
    def get_total_balance(self) -> float:
        """Obtiene balance total de todas las fuentes"""
        return sum(source.current_balance for source in self.value_sources.values())
    
    def get_total_profit(self) -> float:
        """Obtiene ganancia total de todas las fuentes"""
        return sum(source.total_profit for source in self.value_sources.values())
    
    def simulate_month(self, month: int, external_shocks: Optional[Dict] = None):
        """
        Simula un mes de operación con autorregulación
        """
        results = {
            'month': month,
            'cell_id': self.cell_id,
            'state': self.state.value,
            'violations': []
        }
        
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
        
        return results
    
    def _calculate_average_utilization(self) -> float:
        """Calcula tasa de utilización promedio"""
        if not self.value_sources:
            return 0.0
        return np.mean([s.utilization_rate for s in self.value_sources.values()])
    
    def _update_risk_metrics(self):
        """Actualiza las métricas de riesgo basado en estado actual"""
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
        
        # Volatilidad (simplificada - basada en variación de fuentes)
        if len(self.monthly_history) > 3:
            recent_growths = [h['total_growth'] for h in self.monthly_history[-3:]]
            self.risk_metrics.volatility = np.std(recent_growths) / np.mean(recent_growths) * 100 if np.mean(recent_growths) != 0 else 0
        
        # Liquidez (porcentaje no utilizado)
        avg_util = self._calculate_average_utilization()
        self.risk_metrics.liquidity_risk = max(0, 100 - (100 - avg_util)) if avg_util < 90 else 10
        
        # Default rate (promedio ponderado por balance)
        total_bal = self.get_total_balance()
        if total_bal > 0:
            weighted_default = sum(
                (1 - source.risk_factor) * 5 * (source.current_balance / total_bal)
                for source in self.value_sources.values()
            )
            self.risk_metrics.default_rate = weighted_default
    
    def _apply_external_shocks(self, shocks: Dict):
        """Aplica shocks externos a las fuentes de valor"""
        for source_id, shock_data in shocks.items():
            if source_id in self.value_sources:
                source = self.value_sources[source_id]
                
                # Ajustar factor de riesgo
                if 'risk_factor_change' in shock_data:
                    source.risk_factor *= shock_data['risk_factor_change']
                
                # Ajustar tasa de crecimiento
                if 'gpm_change' in shock_data:
                    source.gpm_rate *= shock_data['gpm_change']
    
    def _auto_regulate(self, violations: List[str], risk_level: RiskLevel):
        """
        Sistema de autorregulación - toma acciones según violaciones
        """
        if risk_level == RiskLevel.CRITICAL:
            # Suspender operaciones
            self.state = CellState.SUSPENDED
            # Reducir utilización en todas las fuentes
            for source in self.value_sources.values():
                source.utilization_rate = min(source.utilization_rate, 50.0)
        
        elif risk_level == RiskLevel.HIGH:
            # Entrar en modo recuperación
            self.state = CellState.RECOVERING
            # Reducir utilización moderadamente
            for source in self.value_sources.values():
                source.utilization_rate *= 0.8
        
        elif risk_level == RiskLevel.MEDIUM:
            # Ajustes menores
            for source in self.value_sources.values():
                if source.risk_factor > 1.2:
                    source.utilization_rate *= 0.9
    
    def get_health_score(self) -> float:
        """Calcula score de salud de la célula (0-100)"""
        if not self.monthly_history:
            return 50.0
        
        composite_risk, _ = self.risk_metrics.calculate_composite_risk()
        
        # Score inverso al riesgo
        risk_score = 100 - composite_risk
        
        # Factor de estado
        state_multiplier = {
            CellState.ACTIVE: 1.0,
            CellState.RECOVERING: 0.8,
            CellState.SUSPENDED: 0.5,
            CellState.INACTIVE: 0.3,
            CellState.CLOSED: 0.0
        }
        
        return risk_score * state_multiplier[self.state]
    
    def export_state(self) -> Dict:
        """Exporta estado completo de la célula"""
        return {
            'cell_id': self.cell_id,
            'name': self.name,
            'state': self.state.value,
            'num_members': self.num_members,
            'total_balance': self.get_total_balance(),
            'total_profit': self.get_total_profit(),
            'health_score': self.get_health_score(),
            'risk_metrics': {
                'composite': self.risk_metrics.calculate_composite_risk()[0],
                'level': self.risk_metrics.calculate_composite_risk()[1].name,
                'default_rate': self.risk_metrics.default_rate,
                'volatility': self.risk_metrics.volatility,
                'concentration': self.risk_metrics.concentration_risk,
                'liquidity': self.risk_metrics.liquidity_risk
            },
            'num_sources': len(self.value_sources),
            'sources': [
                {
                    'id': s.source_id,
                    'name': s.name,
                    'balance': s.current_balance,
                    'profit': s.total_profit
                }
                for s in self.value_sources.values()
            ],
            'violations_count': len(self.violations_log)
        }


class ConsolidatorNode:
    """
    Nodo Consolidador - Agrupa múltiples células
    Monitorea y coordina un grupo de células de ahorro
    """
    
    def __init__(
        self,
        node_id: str,
        name: str,
        regulation_rules: Optional[RegulationRules] = None
    ):
        self.node_id = node_id
        self.name = name
        self.cells: Dict[str, SavingsCell] = {}
        self.regulation_rules = regulation_rules or RegulationRules()
        
        # Métricas consolidadas
        self.consolidated_metrics = RiskMetrics()
        self.monthly_consolidated_history: List[Dict] = []
        
        self.created_at = datetime.now()
    
    def add_cell(self, cell: SavingsCell):
        """Agrega una célula al nodo consolidador"""
        self.cells[cell.cell_id] = cell
    
    def remove_cell(self, cell_id: str):
        """Remueve una célula"""
        if cell_id in self.cells:
            del self.cells[cell_id]
    
    def simulate_month(self, month: int, external_shocks: Optional[Dict] = None):
        """Simula un mes para todas las células del nodo"""
        results = {
            'month': month,
            'node_id': self.node_id,
            'cells_results': []
        }
        
        # Simular cada célula
        for cell_id, cell in self.cells.items():
            cell_shocks = external_shocks.get(cell_id) if external_shocks else None
            cell_result = cell.simulate_month(month, cell_shocks)
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
            'total_cells': len(self.cells)
        })
        
        self.monthly_consolidated_history.append(results)
        return results
    
    def _consolidate_metrics(self):
        """Consolida métricas de riesgo de todas las células"""
        if not self.cells:
            return
        
        # Promedios ponderados por balance
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
    
    def get_cells_by_risk(self) -> Dict[str, List[str]]:
        """Agrupa células por nivel de riesgo"""
        risk_groups = {level.name: [] for level in RiskLevel}
        
        for cell in self.cells.values():
            _, risk_level = cell.risk_metrics.calculate_composite_risk()
            risk_groups[risk_level.name].append(cell.cell_id)
        
        return risk_groups
    
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
            'consolidated_risk': {
                'composite': self.consolidated_metrics.calculate_composite_risk()[0],
                'level': self.consolidated_metrics.calculate_composite_risk()[1].name
            },
            'cells_by_risk': self.get_cells_by_risk(),
            'cells': [cell.export_state() for cell in self.cells.values()]
        }


class MasterNode:
    """
    Nodo Maestro - Nivel superior que encapsula nodos consolidadores
    Sistema completo de arquitectura celular
    """
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.consolidator_nodes: Dict[str, ConsolidatorNode] = {}
        self.global_regulation_rules = RegulationRules()
        
        # Métricas globales
        self.global_metrics = RiskMetrics()
        self.system_history: List[Dict] = []
        
        self.created_at = datetime.now()
    
    def add_consolidator(self, consolidator: ConsolidatorNode):
        """Agrega un nodo consolidador al sistema"""
        self.consolidator_nodes[consolidator.node_id] = consolidator
    
    def simulate_month(self, month: int, external_shocks: Optional[Dict] = None):
        """Simula un mes para todo el sistema"""
        results = {
            'month': month,
            'system': self.system_name,
            'consolidators_results': []
        }
        
        # Simular cada consolidador
        for node_id, consolidator in self.consolidator_nodes.items():
            node_shocks = external_shocks.get(node_id) if external_shocks else None
            node_result = consolidator.simulate_month(month, node_shocks)
            results['consolidators_results'].append(node_result)
        
        # Consolidar métricas globales
        self._consolidate_global_metrics()
        
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
        return results
    
    def simulate_multiple_months(self, num_months: int, external_shocks_per_month: Optional[Dict[int, Dict]] = None):
        """Simula múltiples meses"""
        results = []
        for month in range(1, num_months + 1):
            shocks = external_shocks_per_month.get(month) if external_shocks_per_month else None
            month_result = self.simulate_month(month, shocks)
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


def create_example_system() -> MasterNode:
    """
    Crea un sistema de ejemplo con arquitectura celular completa
    """
    # Crear nodo maestro
    master = MasterNode("Sistema SIDEPE Celular")
    
    # Crear consolidadores (regiones o grupos)
    consolidator_norte = ConsolidatorNode("CON-NORTE", "Región Norte")
    consolidator_sur = ConsolidatorNode("CON-SUR", "Región Sur")
    
    # Crear células para región norte
    cell_norte_1 = SavingsCell("CELL-N1", "Grupo Norte A", num_members=50)
    
    # Agregar fuentes de valor a la célula
    cell_norte_1.add_value_source(ValueSource(
        source_id="SRC-FEE",
        name="Fondo de Emergencia",
        initial_capital=0,
        monthly_contribution=2500,  # 50 * 50
        gpm_rate=0.5,
        utilization_rate=30.0
    ))
    
    cell_norte_1.add_value_source(ValueSource(
        source_id="SRC-NUCLEUS",
        name="Núcleo Productivo",
        initial_capital=0,
        monthly_contribution=42500,  # 50 * 850
        gpm_rate=2.5,
        utilization_rate=85.0,
        risk_factor=0.95  # 5% morosidad
    ))
    
    cell_norte_1.add_value_source(ValueSource(
        source_id="SRC-FIC",
        name="Fondo Inversión Colectiva",
        initial_capital=0,
        monthly_contribution=2500,
        gpm_rate=1.8,
        utilization_rate=90.0
    ))
    
    # Crear más células
    cell_norte_2 = SavingsCell("CELL-N2", "Grupo Norte B", num_members=30)
    cell_norte_2.add_value_source(ValueSource(
        "SRC-NUCLEUS", "Núcleo", 0, 25500, 2.3, 80.0, 0.97
    ))
    
    cell_sur_1 = SavingsCell("CELL-S1", "Grupo Sur A", num_members=40)
    cell_sur_1.add_value_source(ValueSource(
        "SRC-NUCLEUS", "Núcleo", 0, 34000, 2.7, 88.0, 0.92
    ))
    
    # Ensamblar jerarquía
    consolidator_norte.add_cell(cell_norte_1)
    consolidator_norte.add_cell(cell_norte_2)
    consolidator_sur.add_cell(cell_sur_1)
    
    master.add_consolidator(consolidator_norte)
    master.add_consolidator(consolidator_sur)
    
    return master


if __name__ == "__main__":
    # Demo del sistema
    print("=" * 60)
    print("Sistema de Arquitectura Celular - Mi-cochinito")
    print("=" * 60)
    
    # Crear sistema de ejemplo
    system = create_example_system()
    
    # Simular 12 meses
    print("\nSimulando 12 meses...")
    results = system.simulate_multiple_months(12)
    
    # Mostrar reporte final
    report = system.get_system_report()
    
    print(f"\n{'='*60}")
    print("REPORTE FINAL DEL SISTEMA")
    print(f"{'='*60}")
    print(f"Balance Total: ${report['summary']['total_balance']:,.2f}")
    print(f"Ganancia Total: ${report['summary']['total_profit']:,.2f}")
    print(f"Health Score: {report['summary']['system_health']:.1f}/100")
    print(f"Células Activas: {report['summary']['active_cells']}/{report['summary']['total_cells']}")
    print(f"\nRiesgo Global: {report['global_risk']['composite']:.1f}% ({report['global_risk']['level']})")
    
    # Exportar a DataFrame
    df = system.export_to_dataframe()
    print(f"\n{df.to_string()}")
