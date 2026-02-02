"""
Test rápido del sistema neuronal
"""
import sys
sys.path.insert(0, '/workspaces/Mi-cochinito')

from neural_cellular_architecture import create_neural_example_system

print("="*70)
print("TEST DEL SISTEMA NEURONAL")
print("="*70)

# Crear sistema
print("\n1️⃣ Creando sistema...")
system = create_neural_example_system()
print(f"   ✅ {system.system_name}")
print(f"   - Consolidadores: {len(system.consolidator_nodes)}")
print(f"   - Células: {system.get_total_cells()}")

# Simular 3 meses
print("\n2️⃣ Simulando 3 meses...")
for i in range(3):
    result = system.simulate_month()
    print(f"   Mes {result['month']}: Balance=${result['total_system_balance']:,.0f}, Riesgo={result['global_risk']:.1f}%")

# Reporte
print("\n3️⃣ Reporte Final:")
report = system.get_system_report()
print(f"   Balance: ${report['summary']['total_balance']:,.2f}")
print(f"   Ganancia: ${report['summary']['total_profit']:,.2f}")
print(f"   Health: {report['summary']['system_health']:.1f}/100")
print(f"   Timeline: Mes {report['current_month']}, {len(system.timeline.events)} eventos")

# Timeline events
print("\n4️⃣ Últimos 5 eventos en Timeline:")
recent_events = system.timeline.get_history(5)
for event in recent_events[-5:]:
    print(f"   - {event['type']}: {event.get('entity', 'N/A')}")

print("\n✅ Sistema neuronal funcionando correctamente!\n")
