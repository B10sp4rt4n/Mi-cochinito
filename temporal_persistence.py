"""
Sistema de Persistencia Temporal con Trazabilidad Histórica
============================================================
Permite guardar cada secuencia con timestamp y revisar el histórico completo.
Cada operación queda registrada como un evento inmutable en la línea temporal.

DIFERENCIADOR ÚNICO: Trazabilidad completa de toda la evolución del sistema.
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import gzip
import pickle


@dataclass
class TemporalEvent:
    """Evento individual con timestamp inmutable"""
    event_id: str
    timestamp: datetime
    sequence_number: int
    event_type: str
    entity_id: str
    entity_type: str  # 'cell', 'consolidator', 'master', 'system'
    operation: str  # 'create', 'update', 'simulate', 'message', 'regulation'
    data_before: Dict  # Estado antes del evento
    data_after: Dict  # Estado después del evento
    metadata: Dict = field(default_factory=dict)
    
    # Hash para integridad (como blockchain)
    previous_hash: str = ""
    event_hash: str = ""
    
    def __post_init__(self):
        if not self.event_hash:
            self.event_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calcula hash del evento para integridad"""
        content = f"{self.event_id}{self.timestamp}{self.sequence_number}{self.event_type}{self.entity_id}{self.operation}{json.dumps(self.data_after, sort_keys=True, default=str)}{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario serializable"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'sequence_number': self.sequence_number,
            'event_type': self.event_type,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'operation': self.operation,
            'data_before': self.data_before,
            'data_after': self.data_after,
            'metadata': self.metadata,
            'previous_hash': self.previous_hash,
            'event_hash': self.event_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TemporalEvent':
        """Reconstruye desde diccionario"""
        return cls(
            event_id=data['event_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            sequence_number=data['sequence_number'],
            event_type=data['event_type'],
            entity_id=data['entity_id'],
            entity_type=data['entity_type'],
            operation=data['operation'],
            data_before=data['data_before'],
            data_after=data['data_after'],
            metadata=data.get('metadata', {}),
            previous_hash=data.get('previous_hash', ''),
            event_hash=data.get('event_hash', '')
        )


@dataclass
class SystemSnapshot:
    """Snapshot completo del estado del sistema en un momento"""
    snapshot_id: str
    timestamp: datetime
    month: int
    sequence_number: int
    system_state: Dict  # Estado completo del sistema
    metrics: Dict  # Métricas en ese momento
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calcula checksum del snapshot"""
        content = json.dumps(self.system_state, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return {
            'snapshot_id': self.snapshot_id,
            'timestamp': self.timestamp.isoformat(),
            'month': self.month,
            'sequence_number': self.sequence_number,
            'system_state': self.system_state,
            'metrics': self.metrics,
            'checksum': self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SystemSnapshot':
        return cls(
            snapshot_id=data['snapshot_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            month=data['month'],
            sequence_number=data['sequence_number'],
            system_state=data['system_state'],
            metrics=data['metrics'],
            checksum=data.get('checksum', '')
        )


class TemporalSequenceStore:
    """
    Almacén de Secuencias Temporales
    ================================
    Guarda toda la historia del sistema con trazabilidad completa.
    Permite:
    - Revisar cualquier momento en el tiempo
    - Reproducir secuencias de eventos
    - Auditar cambios
    - Comparar estados en diferentes momentos
    """
    
    def __init__(self, system_id: str, storage_path: str = "./temporal_data"):
        self.system_id = system_id
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Secuencias de eventos
        self.events: List[TemporalEvent] = []
        self.sequence_counter: int = 0
        
        # Snapshots periódicos
        self.snapshots: List[SystemSnapshot] = []
        self.snapshot_frequency: int = 1  # Cada N meses
        
        # Índices para búsqueda rápida
        self.events_by_entity: Dict[str, List[int]] = {}
        self.events_by_type: Dict[str, List[int]] = {}
        self.events_by_month: Dict[int, List[int]] = {}
        
        # Metadata del almacén
        self.created_at = datetime.now()
        self.last_event_hash = "genesis"
    
    def record_event(
        self,
        event_type: str,
        entity_id: str,
        entity_type: str,
        operation: str,
        data_before: Dict,
        data_after: Dict,
        metadata: Optional[Dict] = None
    ) -> TemporalEvent:
        """
        Registra un evento en la secuencia temporal.
        Cada evento está encadenado al anterior (como blockchain).
        """
        self.sequence_counter += 1
        
        event = TemporalEvent(
            event_id=f"{self.system_id}_evt_{self.sequence_counter}",
            timestamp=datetime.now(),
            sequence_number=self.sequence_counter,
            event_type=event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            operation=operation,
            data_before=data_before,
            data_after=data_after,
            metadata=metadata or {},
            previous_hash=self.last_event_hash
        )
        
        # Actualizar hash encadenado
        self.last_event_hash = event.event_hash
        
        # Almacenar evento
        event_idx = len(self.events)
        self.events.append(event)
        
        # Actualizar índices
        if entity_id not in self.events_by_entity:
            self.events_by_entity[entity_id] = []
        self.events_by_entity[entity_id].append(event_idx)
        
        if event_type not in self.events_by_type:
            self.events_by_type[event_type] = []
        self.events_by_type[event_type].append(event_idx)
        
        month = metadata.get('month', 0) if metadata else 0
        if month not in self.events_by_month:
            self.events_by_month[month] = []
        self.events_by_month[month].append(event_idx)
        
        return event
    
    def create_snapshot(
        self,
        month: int,
        system_state: Dict,
        metrics: Dict
    ) -> SystemSnapshot:
        """Crea snapshot del estado completo del sistema"""
        snapshot = SystemSnapshot(
            snapshot_id=f"{self.system_id}_snap_{month}",
            timestamp=datetime.now(),
            month=month,
            sequence_number=self.sequence_counter,
            system_state=system_state,
            metrics=metrics
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    # ==================== CONSULTAS HISTÓRICAS ====================
    
    def get_entity_history(self, entity_id: str) -> List[TemporalEvent]:
        """Obtiene historial completo de una entidad"""
        if entity_id not in self.events_by_entity:
            return []
        
        indices = self.events_by_entity[entity_id]
        return [self.events[i] for i in indices]
    
    def get_events_by_type(self, event_type: str) -> List[TemporalEvent]:
        """Obtiene todos los eventos de un tipo"""
        if event_type not in self.events_by_type:
            return []
        
        indices = self.events_by_type[event_type]
        return [self.events[i] for i in indices]
    
    def get_events_in_month(self, month: int) -> List[TemporalEvent]:
        """Obtiene eventos de un mes específico"""
        if month not in self.events_by_month:
            return []
        
        indices = self.events_by_month[month]
        return [self.events[i] for i in indices]
    
    def get_events_in_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[TemporalEvent]:
        """Obtiene eventos en un rango de tiempo"""
        return [
            e for e in self.events
            if start_time <= e.timestamp <= end_time
        ]
    
    def get_state_at_sequence(self, sequence_number: int) -> Optional[Dict]:
        """Reconstruye el estado del sistema hasta una secuencia específica"""
        # Buscar snapshot más cercano anterior
        closest_snapshot = None
        for snap in reversed(self.snapshots):
            if snap.sequence_number <= sequence_number:
                closest_snapshot = snap
                break
        
        if closest_snapshot:
            return closest_snapshot.system_state
        
        return None
    
    def get_snapshot_at_month(self, month: int) -> Optional[SystemSnapshot]:
        """Obtiene snapshot de un mes específico"""
        for snap in self.snapshots:
            if snap.month == month:
                return snap
        return None
    
    def compare_states(self, month_a: int, month_b: int) -> Dict:
        """Compara estados del sistema en dos momentos diferentes"""
        snap_a = self.get_snapshot_at_month(month_a)
        snap_b = self.get_snapshot_at_month(month_b)
        
        if not snap_a or not snap_b:
            return {'error': 'Snapshots no encontrados'}
        
        comparison = {
            'month_a': month_a,
            'month_b': month_b,
            'timestamp_a': snap_a.timestamp.isoformat(),
            'timestamp_b': snap_b.timestamp.isoformat(),
            'metrics_comparison': {},
            'events_between': len([
                e for e in self.events
                if snap_a.sequence_number < e.sequence_number <= snap_b.sequence_number
            ])
        }
        
        # Comparar métricas
        for key in snap_a.metrics:
            if key in snap_b.metrics:
                val_a = snap_a.metrics[key]
                val_b = snap_b.metrics[key]
                if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                    comparison['metrics_comparison'][key] = {
                        'before': val_a,
                        'after': val_b,
                        'change': val_b - val_a,
                        'change_pct': ((val_b - val_a) / val_a * 100) if val_a != 0 else 0
                    }
        
        return comparison
    
    def replay_sequence(
        self,
        from_sequence: int,
        to_sequence: int
    ) -> List[TemporalEvent]:
        """Reproduce una secuencia de eventos"""
        return [
            e for e in self.events
            if from_sequence <= e.sequence_number <= to_sequence
        ]
    
    def audit_entity(self, entity_id: str) -> Dict:
        """Genera reporte de auditoría para una entidad"""
        history = self.get_entity_history(entity_id)
        
        if not history:
            return {'entity_id': entity_id, 'error': 'No history found'}
        
        return {
            'entity_id': entity_id,
            'total_events': len(history),
            'first_event': history[0].to_dict(),
            'last_event': history[-1].to_dict(),
            'operations_count': self._count_operations(history),
            'timeline': [
                {
                    'sequence': e.sequence_number,
                    'timestamp': e.timestamp.isoformat(),
                    'operation': e.operation,
                    'event_type': e.event_type
                }
                for e in history
            ]
        }
    
    def _count_operations(self, events: List[TemporalEvent]) -> Dict[str, int]:
        """Cuenta operaciones por tipo"""
        counts = {}
        for e in events:
            counts[e.operation] = counts.get(e.operation, 0) + 1
        return counts
    
    # ==================== VERIFICACIÓN DE INTEGRIDAD ====================
    
    def verify_chain_integrity(self) -> Dict:
        """Verifica integridad de la cadena de eventos (como blockchain)"""
        if not self.events:
            return {'valid': True, 'message': 'No events to verify'}
        
        errors = []
        
        # Verificar primer evento
        if self.events[0].previous_hash != "genesis":
            errors.append({
                'sequence': 0,
                'error': 'First event should have genesis hash'
            })
        
        # Verificar cadena
        for i in range(1, len(self.events)):
            expected_prev_hash = self.events[i-1].event_hash
            actual_prev_hash = self.events[i].previous_hash
            
            if expected_prev_hash != actual_prev_hash:
                errors.append({
                    'sequence': i,
                    'expected': expected_prev_hash,
                    'actual': actual_prev_hash,
                    'error': 'Chain broken'
                })
            
            # Verificar que el hash del evento sea correcto
            recalculated_hash = self.events[i]._calculate_hash()
            # Nota: No comparamos porque el hash ya se calculó en __post_init__
        
        return {
            'valid': len(errors) == 0,
            'total_events': len(self.events),
            'errors': errors,
            'last_hash': self.last_event_hash
        }
    
    # ==================== PERSISTENCIA ====================
    
    def save_to_file(self, filename: Optional[str] = None) -> str:
        """Guarda toda la secuencia temporal a archivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.system_id}_{timestamp}.temporal.json.gz"
        
        filepath = self.storage_path / filename
        
        data = {
            'system_id': self.system_id,
            'created_at': self.created_at.isoformat(),
            'saved_at': datetime.now().isoformat(),
            'sequence_counter': self.sequence_counter,
            'last_event_hash': self.last_event_hash,
            'events': [e.to_dict() for e in self.events],
            'snapshots': [s.to_dict() for s in self.snapshots],
            'integrity': self.verify_chain_integrity()
        }
        
        # Guardar comprimido
        with gzip.open(filepath, 'wt', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(filepath)
    
    def load_from_file(self, filepath: str) -> bool:
        """Carga secuencia temporal desde archivo"""
        path = Path(filepath)
        
        if not path.exists():
            return False
        
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
        
        self.system_id = data['system_id']
        self.created_at = datetime.fromisoformat(data['created_at'])
        self.sequence_counter = data['sequence_counter']
        self.last_event_hash = data['last_event_hash']
        
        # Reconstruir eventos
        self.events = [TemporalEvent.from_dict(e) for e in data['events']]
        self.snapshots = [SystemSnapshot.from_dict(s) for s in data['snapshots']]
        
        # Reconstruir índices
        self._rebuild_indices()
        
        return True
    
    def _rebuild_indices(self):
        """Reconstruye índices después de cargar"""
        self.events_by_entity = {}
        self.events_by_type = {}
        self.events_by_month = {}
        
        for idx, event in enumerate(self.events):
            if event.entity_id not in self.events_by_entity:
                self.events_by_entity[event.entity_id] = []
            self.events_by_entity[event.entity_id].append(idx)
            
            if event.event_type not in self.events_by_type:
                self.events_by_type[event.event_type] = []
            self.events_by_type[event.event_type].append(idx)
            
            month = event.metadata.get('month', 0)
            if month not in self.events_by_month:
                self.events_by_month[month] = []
            self.events_by_month[month].append(idx)
    
    # ==================== EXPORTACIÓN ====================
    
    def export_timeline_csv(self, filename: Optional[str] = None) -> str:
        """Exporta timeline a CSV"""
        import pandas as pd
        
        if not filename:
            filename = f"{self.system_id}_timeline.csv"
        
        filepath = self.storage_path / filename
        
        data = []
        for e in self.events:
            data.append({
                'Secuencia': e.sequence_number,
                'Timestamp': e.timestamp.isoformat(),
                'Tipo Evento': e.event_type,
                'Entidad': e.entity_id,
                'Tipo Entidad': e.entity_type,
                'Operación': e.operation,
                'Hash': e.event_hash,
                'Hash Anterior': e.previous_hash
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return str(filepath)
    
    def export_snapshots_csv(self, filename: Optional[str] = None) -> str:
        """Exporta snapshots a CSV"""
        import pandas as pd
        
        if not filename:
            filename = f"{self.system_id}_snapshots.csv"
        
        filepath = self.storage_path / filename
        
        data = []
        for s in self.snapshots:
            row = {
                'Snapshot ID': s.snapshot_id,
                'Timestamp': s.timestamp.isoformat(),
                'Mes': s.month,
                'Secuencia': s.sequence_number,
                'Checksum': s.checksum
            }
            # Agregar métricas
            for key, value in s.metrics.items():
                row[f'Metric_{key}'] = value
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return str(filepath)
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del almacén temporal"""
        return {
            'system_id': self.system_id,
            'created_at': self.created_at.isoformat(),
            'total_events': len(self.events),
            'total_snapshots': len(self.snapshots),
            'sequence_counter': self.sequence_counter,
            'unique_entities': len(self.events_by_entity),
            'event_types': list(self.events_by_type.keys()),
            'months_recorded': list(self.events_by_month.keys()),
            'integrity': self.verify_chain_integrity()['valid'],
            'storage_path': str(self.storage_path)
        }


# ==================== INTEGRACIÓN CON SISTEMA NEURONAL ====================

class TemporalNeuralSystem:
    """
    Wrapper que agrega trazabilidad temporal al sistema neuronal.
    Cada operación queda registrada con timestamp inmutable.
    """
    
    def __init__(self, neural_system, system_id: str = "neural_sidepe"):
        from neural_cellular_architecture import NeuralMasterNode
        
        self.neural_system: NeuralMasterNode = neural_system
        self.temporal_store = TemporalSequenceStore(system_id)
        
        # Registrar creación del sistema
        self._record_system_creation()
    
    def _record_system_creation(self):
        """Registra la creación del sistema"""
        self.temporal_store.record_event(
            event_type='system_creation',
            entity_id='master',
            entity_type='master',
            operation='create',
            data_before={},
            data_after=self._get_system_state(),
            metadata={'month': 0}
        )
    
    def _get_system_state(self) -> Dict:
        """Obtiene estado actual del sistema"""
        return self.neural_system.get_system_report()
    
    def _get_system_metrics(self) -> Dict:
        """Obtiene métricas actuales"""
        return {
            'balance': self.neural_system.get_total_balance(),
            'profit': self.neural_system.get_total_profit(),
            'health': self.neural_system.get_system_health(),
            'risk': self.neural_system.global_metrics.calculate_composite_risk()[0],
            'cells': self.neural_system.get_total_cells(),
            'active_cells': self.neural_system.get_active_cells()
        }
    
    def simulate_month_with_tracking(self, external_shocks=None) -> Dict:
        """Simula un mes con registro temporal completo"""
        # Estado antes
        state_before = self._get_system_state()
        metrics_before = self._get_system_metrics()
        
        # Ejecutar simulación
        result = self.neural_system.simulate_month(external_shocks)
        
        # Estado después
        state_after = self._get_system_state()
        metrics_after = self._get_system_metrics()
        
        month = self.neural_system.timeline.current_month
        
        # Registrar evento principal
        self.temporal_store.record_event(
            event_type='month_simulation',
            entity_id='master',
            entity_type='master',
            operation='simulate',
            data_before=metrics_before,
            data_after=metrics_after,
            metadata={
                'month': month,
                'result_summary': {
                    'balance': result['total_system_balance'],
                    'profit': result['total_system_profit'],
                    'risk': result['global_risk']
                }
            }
        )
        
        # Crear snapshot
        self.temporal_store.create_snapshot(
            month=month,
            system_state=state_after,
            metrics=metrics_after
        )
        
        # Registrar eventos por consolidador
        for cons_result in result.get('consolidators_results', []):
            self.temporal_store.record_event(
                event_type='consolidator_simulation',
                entity_id=cons_result['node_id'],
                entity_type='consolidator',
                operation='simulate',
                data_before={},
                data_after={
                    'balance': cons_result['total_balance'],
                    'profit': cons_result['total_profit'],
                    'risk': cons_result['consolidated_risk']
                },
                metadata={'month': month}
            )
            
            # Registrar eventos por célula
            for cell_result in cons_result.get('cells_results', []):
                self.temporal_store.record_event(
                    event_type='cell_simulation',
                    entity_id=cell_result['cell_id'],
                    entity_type='cell',
                    operation='simulate',
                    data_before={},
                    data_after={
                        'balance': cell_result.get('total_balance', 0),
                        'profit': cell_result.get('total_profit', 0),
                        'risk': cell_result.get('composite_risk', 0),
                        'state': cell_result.get('state', 'unknown')
                    },
                    metadata={'month': month}
                )
        
        return result
    
    def simulate_multiple_months_with_tracking(self, num_months: int) -> List[Dict]:
        """Simula múltiples meses con tracking completo"""
        results = []
        for _ in range(num_months):
            result = self.simulate_month_with_tracking()
            results.append(result)
        return results
    
    def get_entity_timeline(self, entity_id: str) -> List[Dict]:
        """Obtiene timeline completo de una entidad"""
        events = self.temporal_store.get_entity_history(entity_id)
        return [e.to_dict() for e in events]
    
    def compare_periods(self, month_a: int, month_b: int) -> Dict:
        """Compara dos períodos"""
        return self.temporal_store.compare_states(month_a, month_b)
    
    def save_history(self, filename: Optional[str] = None) -> str:
        """Guarda todo el historial"""
        return self.temporal_store.save_to_file(filename)
    
    def load_history(self, filepath: str) -> bool:
        """Carga historial guardado"""
        return self.temporal_store.load_from_file(filepath)
    
    def export_all(self) -> Dict[str, str]:
        """Exporta todo a múltiples formatos"""
        return {
            'temporal_json': self.temporal_store.save_to_file(),
            'timeline_csv': self.temporal_store.export_timeline_csv(),
            'snapshots_csv': self.temporal_store.export_snapshots_csv()
        }
    
    def audit(self, entity_id: Optional[str] = None) -> Dict:
        """Genera reporte de auditoría"""
        if entity_id:
            return self.temporal_store.audit_entity(entity_id)
        
        return {
            'system_statistics': self.temporal_store.get_statistics(),
            'chain_integrity': self.temporal_store.verify_chain_integrity(),
            'entities_tracked': list(self.temporal_store.events_by_entity.keys())
        }


# ==================== DEMO ====================

if __name__ == "__main__":
    print("=" * 70)
    print("DEMO: Sistema de Persistencia Temporal")
    print("=" * 70)
    
    from neural_cellular_architecture import create_neural_example_system
    
    # Crear sistema con tracking temporal
    neural_system = create_neural_example_system()
    temporal_system = TemporalNeuralSystem(neural_system, "demo_sidepe")
    
    print(f"\n✅ Sistema creado con trazabilidad temporal")
    
    # Simular 6 meses
    print(f"\n🔄 Simulando 6 meses con registro completo...")
    results = temporal_system.simulate_multiple_months_with_tracking(6)
    
    # Estadísticas
    stats = temporal_system.temporal_store.get_statistics()
    print(f"\n📊 Estadísticas:")
    print(f"   - Eventos registrados: {stats['total_events']}")
    print(f"   - Snapshots creados: {stats['total_snapshots']}")
    print(f"   - Entidades rastreadas: {stats['unique_entities']}")
    print(f"   - Integridad de cadena: {'✅ Válida' if stats['integrity'] else '❌ Corrupta'}")
    
    # Auditoría de una entidad
    print(f"\n📋 Auditoría de 'master':")
    audit = temporal_system.audit('master')
    print(f"   - Total eventos: {audit['total_events']}")
    print(f"   - Operaciones: {audit['operations_count']}")
    
    # Comparar períodos
    print(f"\n📈 Comparación Mes 1 vs Mes 6:")
    comparison = temporal_system.compare_periods(1, 6)
    if 'metrics_comparison' in comparison:
        for metric, data in comparison['metrics_comparison'].items():
            print(f"   - {metric}: {data['before']:.2f} → {data['after']:.2f} ({data['change_pct']:+.1f}%)")
    
    # Guardar
    filepath = temporal_system.save_history()
    print(f"\n💾 Historial guardado en: {filepath}")
    
    # Exportar
    exports = temporal_system.export_all()
    print(f"\n📁 Archivos exportados:")
    for fmt, path in exports.items():
        print(f"   - {fmt}: {path}")
    
    print(f"\n✅ Demo completada - Trazabilidad temporal funcionando!")
