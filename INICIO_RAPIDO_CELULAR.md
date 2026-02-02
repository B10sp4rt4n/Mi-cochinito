# 🚀 Inicio Rápido - Sistema de Arquitectura Celular

## ⚡ 3 Formas de Empezar

---

## 1️⃣ Interfaz Web (Más Fácil)

### Ejecutar
```bash
streamlit run app_cellular.py
```

### Acceder
Abre tu navegador en: **http://localhost:8501**

### Primeros Pasos
1. Click en **"📋 Ejemplo Pre-configurado"** en el sidebar
2. Ve a **"📊 Vista General"**
3. Click en **"▶️ Simulación"**
4. Ejecuta 12 meses
5. ¡Explora los resultados!

---

## 2️⃣ Script Python (Rápido)

### Código Mínimo
```python
from cellular_architecture import create_example_system

# Cargar sistema pre-configurado
system = create_example_system()

# Simular 12 meses
results = system.simulate_multiple_months(12)

# Ver reporte
report = system.get_system_report()
print(f"Balance: ${report['summary']['total_balance']:,.2f}")
print(f"Ganancia: ${report['summary']['total_profit']:,.2f}")
print(f"Health: {report['summary']['system_health']:.1f}/100")
```

### Ejecutar
```bash
python -c "from cellular_architecture import create_example_system; s=create_example_system(); s.simulate_multiple_months(12); print(s.get_system_report())"
```

---

## 3️⃣ Demo Automática (Instant)

### Ejecutar
```bash
python cellular_architecture.py
```

### Output Esperado
```
============================================================
Sistema de Arquitectura Celular - Mi-cochinito
============================================================

Simulando 12 meses...

============================================================
REPORTE FINAL DEL SISTEMA
============================================================
Balance Total: $1,460,594.18
Ganancia Total: $176,594.18
Health Score: 61.0/100
Células Activas: 3/3

Riesgo Global: 27.1% (LOW)
```

---

## 🎓 Tutorial: Crear Tu Primer Sistema

### Paso 1: Crear Sistema Maestro
```python
from cellular_architecture import MasterNode

master = MasterNode("Mi Sistema de Ahorro")
```

### Paso 2: Crear Consolidador (Región/Grupo)
```python
from cellular_architecture import ConsolidatorNode

consolidator = ConsolidatorNode(
    node_id="CON-001",
    name="Región Norte"
)
```

### Paso 3: Crear Célula (Grupo de Ahorro)
```python
from cellular_architecture import SavingsCell

cell = SavingsCell(
    cell_id="CELL-001",
    name="Grupo A",
    num_members=50  # 50 personas
)
```

### Paso 4: Agregar Fuentes de Valor
```python
from cellular_architecture import ValueSource

# Fondo de Emergencia (5%)
cell.add_value_source(ValueSource(
    source_id="SRC-FEE",
    name="Fondo Emergencia",
    initial_capital=0,
    monthly_contribution=2500,  # 50 personas * $50
    gpm_rate=0.5,  # 0.5% mensual
    utilization_rate=30.0  # 30% se utiliza
))

# Núcleo Productivo (85%)
cell.add_value_source(ValueSource(
    source_id="SRC-NUCLEUS",
    name="Núcleo Productivo",
    initial_capital=0,
    monthly_contribution=42500,  # 50 * $850
    gpm_rate=2.5,  # 2.5% mensual
    utilization_rate=85.0,  # 85% se utiliza
    risk_factor=0.95  # 5% riesgo de default
))

# Fondo de Inversión (10%)
cell.add_value_source(ValueSource(
    source_id="SRC-FIC",
    name="Fondo Inversión Colectiva",
    initial_capital=0,
    monthly_contribution=5000,  # 50 * $100
    gpm_rate=1.8,  # 1.8% mensual
    utilization_rate=90.0
))
```

### Paso 5: Ensamblar Sistema
```python
# Agregar célula al consolidador
consolidator.add_cell(cell)

# Agregar consolidador al master
master.add_consolidator(consolidator)
```

### Paso 6: Simular
```python
# Simular 12 meses
results = master.simulate_multiple_months(12)

# Ver último mes
print(results[-1])
```

### Paso 7: Exportar Resultados
```python
# Exportar a DataFrame
df = master.export_to_dataframe()
print(df)

# Exportar reporte completo
report = master.get_system_report()

# Guardar en JSON
import json
with open("reporte.json", "w") as f:
    json.dump(report, f, indent=2, default=str)
```

---

## 📊 Código Completo del Tutorial

```python
from cellular_architecture import (
    MasterNode, ConsolidatorNode, SavingsCell, ValueSource
)

# 1. Crear estructura
master = MasterNode("Mi Sistema de Ahorro")
consolidator = ConsolidatorNode("CON-001", "Región Norte")
cell = SavingsCell("CELL-001", "Grupo A", 50)

# 2. Agregar fuentes
cell.add_value_source(ValueSource(
    "SRC-FEE", "Fondo Emergencia", 0, 2500, 0.5, 30
))
cell.add_value_source(ValueSource(
    "SRC-NUCLEUS", "Núcleo Productivo", 0, 42500, 2.5, 85, 0.95
))
cell.add_value_source(ValueSource(
    "SRC-FIC", "Fondo Inversión", 0, 5000, 1.8, 90
))

# 3. Ensamblar
consolidator.add_cell(cell)
master.add_consolidator(consolidator)

# 4. Simular
results = master.simulate_multiple_months(12)

# 5. Analizar
report = master.get_system_report()
print(f"\n{'='*60}")
print("RESULTADOS DE LA SIMULACIÓN")
print(f"{'='*60}")
print(f"Balance Total: ${report['summary']['total_balance']:,.2f}")
print(f"Ganancia Total: ${report['summary']['total_profit']:,.2f}")
print(f"Health Score: {report['summary']['system_health']:.1f}/100")
print(f"Riesgo Global: {report['global_risk']['composite']:.1f}% ({report['global_risk']['level']})")

# 6. Exportar
df = master.export_to_dataframe()
df.to_csv("simulacion.csv")
print(f"\n✅ Datos exportados a simulacion.csv")
```

---

## 🎯 Casos de Uso Rápidos

### Caso 1: Sistema Multi-regional
```python
master = MasterNode("Sistema Nacional")

# Crear 3 regiones
for region in ["Norte", "Centro", "Sur"]:
    consolidator = ConsolidatorNode(f"CON-{region}", f"Región {region}")
    
    # 3 grupos por región
    for i in range(3):
        cell = SavingsCell(f"CELL-{region}-{i}", f"Grupo {i}", 40)
        
        # 3 fuentes estándar
        cell.add_value_source(ValueSource(f"FEE-{i}", "FEE", 0, 2000, 0.5, 30))
        cell.add_value_source(ValueSource(f"NUC-{i}", "Núcleo", 0, 34000, 2.5, 85, 0.95))
        cell.add_value_source(ValueSource(f"FIC-{i}", "FIC", 0, 2000, 1.8, 90))
        
        consolidator.add_cell(cell)
    
    master.add_consolidator(consolidator)

# Simular sistema completo (9 grupos, 360 miembros)
results = master.simulate_multiple_months(12)
```

### Caso 2: Fondo Multi-activo
```python
cell = SavingsCell("FUND-001", "Fondo Diversificado", 100)

# Múltiples tipos de activos
cell.add_value_source(ValueSource("CASH", "Efectivo", 50000, 25000, 1.5, 70, 1.0))
cell.add_value_source(ValueSource("CRYPTO", "Cripto", 30000, 10000, 5.0, 80, 0.85))
cell.add_value_source(ValueSource("BONDS", "Bonos", 100000, 5000, 1.2, 95, 1.0))
cell.add_value_source(ValueSource("STOCKS", "Acciones", 20000, 8000, 3.5, 75, 0.90))

# Auto-balanceo según riesgo
for month in range(1, 13):
    result = cell.simulate_month(month)
    print(f"Mes {month}: Balance=${result['total_balance']:,.2f}, Riesgo={result['composite_risk']:.1f}%")
```

### Caso 3: Sistema Cerrado
```python
# Capital fijo, sin nuevas aportaciones
cell = SavingsCell("CLOSED-001", "Fondo Cerrado", 0)

cell.add_value_source(ValueSource(
    "PRINCIPAL", "Capital Inicial",
    initial_capital=1000000,  # $1M
    monthly_contribution=0,   # Sin aportes mensuales
    gpm_rate=2.0,
    utilization_rate=80
))

# Solo crece por rendimientos internos
for month in range(1, 13):
    cell.simulate_month(month)

print(f"Balance final: ${cell.get_total_balance():,.2f}")
print(f"Ganancia: ${cell.get_total_profit():,.2f}")
```

---

## 🧪 Ejecutar Tests

### Todos los Tests
```bash
pytest test_cellular.py -v
```

### Tests Específicos
```bash
# Tests de ValueSource
pytest test_cellular.py::TestValueSource -v

# Tests de SavingsCell
pytest test_cellular.py::TestSavingsCell -v

# Tests de Integración
pytest test_cellular.py::TestIntegration -v
```

### Con Coverage
```bash
pytest test_cellular.py --cov=cellular_architecture --cov-report=html
```

---

## 📚 Próximos Pasos

### 1. Lee la Documentación
- **[ARQUITECTURA_CELULAR.md](ARQUITECTURA_CELULAR.md)**: Guía técnica completa
- **[RESUMEN_ARQUITECTURA_CELULAR.md](RESUMEN_ARQUITECTURA_CELULAR.md)**: Resumen ejecutivo
- **[COMPARACION_SISTEMAS.md](COMPARACION_SISTEMAS.md)**: Tradicional vs Celular

### 2. Experimenta
- Modifica parámetros en el código
- Crea tus propias células y fuentes
- Simula diferentes escenarios

### 3. Personaliza
- Ajusta reglas de regulación
- Define tus propias métricas de riesgo
- Crea tipos de fuentes personalizadas

### 4. Contribuye
- Reporta bugs en GitHub
- Sugiere mejoras
- Comparte tus casos de uso

---

## 🆘 Solución de Problemas

### Error: Module not found
```bash
pip install -r requirements.txt
```

### Error: Streamlit not found
```bash
pip install streamlit plotly
```

### Error: pytest not found
```bash
pip install pytest
```

### Los tests fallan
```bash
# Asegúrate de estar en el directorio correcto
cd /workspaces/Mi-cochinito

# Ejecuta los tests
python -m pytest test_cellular.py -v
```

### La interfaz no carga
```bash
# Verifica que Streamlit esté instalado
streamlit --version

# Si no está:
pip install streamlit

# Ejecuta nuevamente
streamlit run app_cellular.py
```

---

## 💡 Tips Rápidos

### Tip 1: Usa el Sistema Pre-configurado
```python
from cellular_architecture import create_example_system
system = create_example_system()
# Ya tienes un sistema completo listo para simular
```

### Tip 2: Exporta a CSV para Excel
```python
df = master.export_to_dataframe()
df.to_csv("resultados.csv", index=False)
# Abre en Excel para análisis adicional
```

### Tip 3: Revisa los Logs de Violaciones
```python
for cell in consolidator.cells.values():
    if cell.violations_log:
        print(f"\n{cell.name}:")
        for violation in cell.violations_log:
            print(f"  Mes {violation['month']}: {violation['violations']}")
```

### Tip 4: Monitorea Salud de Células
```python
for cell in consolidator.cells.values():
    health = cell.get_health_score()
    status = "✅" if health > 70 else "⚠️" if health > 50 else "❌"
    print(f"{status} {cell.name}: {health:.1f}/100")
```

### Tip 5: Compara Escenarios
```python
# Escenario 1: Conservador
system1 = create_system(utilization=70, risk=0.98)
results1 = system1.simulate_multiple_months(12)

# Escenario 2: Agresivo
system2 = create_system(utilization=90, risk=0.92)
results2 = system2.simulate_multiple_months(12)

# Comparar
print(f"Conservador: ${results1[-1]['total_system_profit']:,.2f}")
print(f"Agresivo: ${results2[-1]['total_system_profit']:,.2f}")
```

---

## 📞 Contacto y Soporte

**Repositorio**: [github.com/B10sp4rt4n/Mi-cochinito](https://github.com/B10sp4rt4n/Mi-cochinito)  
**Documentación**: Ver archivos `*.md` en el repositorio  
**Issues**: Reporta problemas en GitHub Issues  

---

**¡Listo para comenzar!** 🚀

Elige cualquiera de los 3 métodos arriba y empieza a simular tu sistema de ahorro celular en minutos.
