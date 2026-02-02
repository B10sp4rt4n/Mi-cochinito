#!/usr/bin/env python3
"""Test del sistema de persistencia temporal"""

from temporal_persistence import TemporalSequenceStore, TemporalEvent

# Test básico
store = TemporalSequenceStore("test")

# Registrar eventos
for i in range(5):
    event = store.record_event(
        event_type='simulation',
        entity_id=f'cell_{i}',
        entity_type='cell',
        operation='simulate',
        data_before={'balance': i * 100},
        data_after={'balance': (i + 1) * 100},
        metadata={'month': i + 1}
    )
    print(f"Evento {event.sequence_number}: {event.event_hash}")

# Verificar integridad
integrity = store.verify_chain_integrity()
print(f"\n✅ Cadena válida: {integrity['valid']}")
print(f"📊 Total eventos: {integrity['total_events']}")

# Estadísticas
stats = store.get_statistics()
print(f"\n📈 Entidades únicas: {stats['unique_entities']}")
print(f"📅 Meses registrados: {stats['months_recorded']}")

# Guardar
filepath = store.save_to_file("test_sequence.temporal.json.gz")
print(f"\n💾 Guardado en: {filepath}")

print("\n✅ Test completado!")
