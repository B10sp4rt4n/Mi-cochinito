"""
Tests para Sistema de Arquitectura Celular
==========================================
Validación de componentes y flujos del sistema
"""

import pytest
import numpy as np
from cellular_architecture import (
    ValueSource, SavingsCell, ConsolidatorNode, MasterNode,
    RiskMetrics, RegulationRules, RiskLevel, CellState,
    create_example_system
)


class TestValueSource:
    """Tests para ValueSource"""
    
    def test_value_source_creation(self):
        """Test creación básica"""
        source = ValueSource(
            source_id="TEST-001",
            name="Test Source",
            initial_capital=1000,
            monthly_contribution=500,
            gpm_rate=2.0,
            utilization_rate=85.0
        )
        
        assert source.source_id == "TEST-001"
        assert source.current_balance == 1000
        assert source.total_profit == 0
    
    def test_calculate_growth(self):
        """Test cálculo de crecimiento"""
        source = ValueSource(
            source_id="TEST-002",
            name="Growth Test",
            initial_capital=10000,
            monthly_contribution=0,
            gpm_rate=2.0,
            utilization_rate=100.0,
            risk_factor=1.0
        )
        
        growth = source.calculate_growth()
        expected = 10000 * 0.02  # 2% de 10000
        
        assert abs(growth - expected) < 0.01
    
    def test_add_contribution(self):
        """Test agregar contribución"""
        source = ValueSource(
            source_id="TEST-003",
            name="Contribution Test",
            initial_capital=1000,
            monthly_contribution=500,
            gpm_rate=0
        )
        
        initial_balance = source.current_balance
        source.add_contribution(500)
        
        assert source.current_balance == initial_balance + 500
    
    def test_apply_growth(self):
        """Test aplicar crecimiento"""
        source = ValueSource(
            source_id="TEST-004",
            name="Apply Growth Test",
            initial_capital=1000,
            monthly_contribution=0,
            gpm_rate=0
        )
        
        growth = 50
        initial_balance = source.current_balance
        source.apply_growth(growth)
        
        assert source.current_balance == initial_balance + growth
        assert source.total_profit == growth


class TestRiskMetrics:
    """Tests para RiskMetrics"""
    
    def test_risk_metrics_creation(self):
        """Test creación de métricas"""
        metrics = RiskMetrics(
            default_rate=5.0,
            volatility=10.0,
            concentration_risk=30.0,
            liquidity_risk=15.0,
            operational_risk=5.0
        )
        
        assert metrics.default_rate == 5.0
        assert metrics.volatility == 10.0
    
    def test_composite_risk_calculation(self):
        """Test cálculo de riesgo compuesto"""
        metrics = RiskMetrics(
            default_rate=10.0,
            volatility=20.0,
            concentration_risk=30.0,
            liquidity_risk=15.0,
            operational_risk=10.0
        )
        
        composite, level = metrics.calculate_composite_risk()
        
        # Verificar que está en rango válido
        assert 0 <= composite <= 100
        assert isinstance(level, RiskLevel)
    
    def test_risk_level_very_low(self):
        """Test nivel de riesgo muy bajo"""
        metrics = RiskMetrics(
            default_rate=2.0,
            volatility=3.0,
            concentration_risk=5.0,
            liquidity_risk=2.0,
            operational_risk=1.0
        )
        
        composite, level = metrics.calculate_composite_risk()
        assert level == RiskLevel.VERY_LOW
    
    def test_risk_level_critical(self):
        """Test nivel de riesgo crítico"""
        metrics = RiskMetrics(
            default_rate=100.0,
            volatility=100.0,
            concentration_risk=100.0,
            liquidity_risk=100.0,
            operational_risk=100.0
        )
        
        composite, level = metrics.calculate_composite_risk()
        assert level == RiskLevel.CRITICAL


class TestRegulationRules:
    """Tests para RegulationRules"""
    
    def test_regulation_rules_creation(self):
        """Test creación de reglas"""
        rules = RegulationRules(
            max_default_rate=5.0,
            min_utilization=70.0,
            max_utilization=95.0
        )
        
        assert rules.max_default_rate == 5.0
        assert rules.min_utilization == 70.0
    
    def test_check_violation_default_rate(self):
        """Test violación de default rate"""
        rules = RegulationRules(max_default_rate=5.0)
        metrics = RiskMetrics(default_rate=10.0)
        
        violations = rules.check_violation(metrics, {'utilization': 80})
        
        assert len(violations) > 0
        assert any('Default rate' in v for v in violations)
    
    def test_check_violation_utilization_low(self):
        """Test violación de utilización baja"""
        rules = RegulationRules(min_utilization=70.0)
        metrics = RiskMetrics()
        
        violations = rules.check_violation(metrics, {'utilization': 60})
        
        assert len(violations) > 0
        assert any('Utilización' in v for v in violations)
    
    def test_check_violation_emergency(self):
        """Test violación de umbral de emergencia"""
        rules = RegulationRules(emergency_stop_threshold=50.0)
        metrics = RiskMetrics(
            default_rate=100.0,
            volatility=100.0,
            concentration_risk=100.0,
            liquidity_risk=100.0,
            operational_risk=100.0
        )
        
        violations = rules.check_violation(metrics, {'utilization': 80})
        
        assert len(violations) > 0
        assert any('EMERGENCIA' in v for v in violations)


class TestSavingsCell:
    """Tests para SavingsCell"""
    
    def test_cell_creation(self):
        """Test creación de célula"""
        cell = SavingsCell(
            cell_id="CELL-TEST-001",
            name="Test Cell",
            num_members=50
        )
        
        assert cell.cell_id == "CELL-TEST-001"
        assert cell.name == "Test Cell"
        assert cell.num_members == 50
        assert cell.state == CellState.ACTIVE
    
    def test_add_value_source(self):
        """Test agregar fuente de valor"""
        cell = SavingsCell("CELL-001", "Test", 50)
        
        source = ValueSource(
            source_id="SRC-001",
            name="Source 1",
            initial_capital=1000,
            monthly_contribution=500,
            gpm_rate=2.0
        )
        
        cell.add_value_source(source)
        
        assert "SRC-001" in cell.value_sources
        assert len(cell.value_sources) == 1
    
    def test_remove_value_source(self):
        """Test remover fuente de valor"""
        cell = SavingsCell("CELL-001", "Test", 50)
        
        source = ValueSource("SRC-001", "Source 1", 1000, 500, 2.0)
        cell.add_value_source(source)
        cell.remove_value_source("SRC-001")
        
        assert "SRC-001" not in cell.value_sources
        assert len(cell.value_sources) == 0
    
    def test_get_total_balance(self):
        """Test obtener balance total"""
        cell = SavingsCell("CELL-001", "Test", 50)
        
        source1 = ValueSource("SRC-001", "S1", 1000, 0, 0)
        source2 = ValueSource("SRC-002", "S2", 2000, 0, 0)
        
        cell.add_value_source(source1)
        cell.add_value_source(source2)
        
        assert cell.get_total_balance() == 3000
    
    def test_simulate_month_basic(self):
        """Test simulación básica de un mes"""
        cell = SavingsCell("CELL-001", "Test", 50)
        
        source = ValueSource(
            source_id="SRC-001",
            name="Source 1",
            initial_capital=10000,
            monthly_contribution=1000,
            gpm_rate=2.0,
            utilization_rate=100.0,
            risk_factor=1.0
        )
        
        cell.add_value_source(source)
        
        result = cell.simulate_month(1)
        
        assert result['month'] == 1
        assert result['cell_id'] == "CELL-001"
        assert result['total_balance'] > 10000  # Debe crecer
        assert len(result['sources']) == 1
    
    def test_cell_auto_regulation(self):
        """Test autorregulación de célula"""
        # Crear célula con reglas estrictas
        strict_rules = RegulationRules(
            max_default_rate=1.0,  # Muy estricto
            emergency_stop_threshold=10.0
        )
        
        cell = SavingsCell(
            "CELL-001",
            "Test",
            50,
            regulation_rules=strict_rules
        )
        
        # Agregar fuente con alto riesgo
        source = ValueSource(
            source_id="SRC-001",
            name="High Risk",
            initial_capital=10000,
            monthly_contribution=1000,
            gpm_rate=2.0,
            utilization_rate=100.0,
            risk_factor=0.5  # 50% de riesgo = alto default
        )
        
        cell.add_value_source(source)
        
        # Simular varios meses para acumular historial
        for month in range(1, 6):
            cell.simulate_month(month)
        
        # La célula debería haberse autorregulado
        # (estado cambiado o utilización reducida)
        assert len(cell.violations_log) > 0 or cell.state != CellState.ACTIVE
    
    def test_health_score(self):
        """Test cálculo de health score"""
        cell = SavingsCell("CELL-001", "Test", 50)
        
        source = ValueSource("SRC-001", "S1", 10000, 1000, 2.0)
        cell.add_value_source(source)
        
        # Simular para generar historial
        cell.simulate_month(1)
        
        health = cell.get_health_score()
        
        assert 0 <= health <= 100
    
    def test_export_state(self):
        """Test exportar estado de célula"""
        cell = SavingsCell("CELL-001", "Test Cell", 50)
        
        source = ValueSource("SRC-001", "Source 1", 10000, 1000, 2.0)
        cell.add_value_source(source)
        
        cell.simulate_month(1)
        
        state = cell.export_state()
        
        assert state['cell_id'] == "CELL-001"
        assert state['name'] == "Test Cell"
        assert 'total_balance' in state
        assert 'risk_metrics' in state
        assert len(state['sources']) == 1


class TestConsolidatorNode:
    """Tests para ConsolidatorNode"""
    
    def test_consolidator_creation(self):
        """Test creación de consolidador"""
        consolidator = ConsolidatorNode(
            node_id="CON-001",
            name="Test Consolidator"
        )
        
        assert consolidator.node_id == "CON-001"
        assert consolidator.name == "Test Consolidator"
        assert len(consolidator.cells) == 0
    
    def test_add_cell(self):
        """Test agregar célula"""
        consolidator = ConsolidatorNode("CON-001", "Test")
        cell = SavingsCell("CELL-001", "Cell 1", 50)
        
        consolidator.add_cell(cell)
        
        assert "CELL-001" in consolidator.cells
        assert len(consolidator.cells) == 1
    
    def test_remove_cell(self):
        """Test remover célula"""
        consolidator = ConsolidatorNode("CON-001", "Test")
        cell = SavingsCell("CELL-001", "Cell 1", 50)
        
        consolidator.add_cell(cell)
        consolidator.remove_cell("CELL-001")
        
        assert "CELL-001" not in consolidator.cells
        assert len(consolidator.cells) == 0
    
    def test_simulate_month(self):
        """Test simulación de mes para consolidador"""
        consolidator = ConsolidatorNode("CON-001", "Test")
        
        # Agregar células con fuentes
        for i in range(3):
            cell = SavingsCell(f"CELL-{i}", f"Cell {i}", 50)
            source = ValueSource(f"SRC-{i}", f"Source {i}", 10000, 1000, 2.0)
            cell.add_value_source(source)
            consolidator.add_cell(cell)
        
        result = consolidator.simulate_month(1)
        
        assert result['month'] == 1
        assert len(result['cells_results']) == 3
        assert 'total_balance' in result
        assert 'average_health' in result
    
    def test_get_total_balance(self):
        """Test balance total del consolidador"""
        consolidator = ConsolidatorNode("CON-001", "Test")
        
        cell1 = SavingsCell("CELL-1", "C1", 50)
        cell1.add_value_source(ValueSource("S1", "S1", 10000, 0, 0))
        
        cell2 = SavingsCell("CELL-2", "C2", 50)
        cell2.add_value_source(ValueSource("S2", "S2", 20000, 0, 0))
        
        consolidator.add_cell(cell1)
        consolidator.add_cell(cell2)
        
        assert consolidator.get_total_balance() == 30000
    
    def test_get_cells_by_risk(self):
        """Test agrupar células por riesgo"""
        consolidator = ConsolidatorNode("CON-001", "Test")
        
        # Agregar células y simular para generar métricas
        for i in range(3):
            cell = SavingsCell(f"CELL-{i}", f"Cell {i}", 50)
            source = ValueSource(f"SRC-{i}", "S", 10000, 1000, 2.0, 85, 1.0)
            cell.add_value_source(source)
            cell.simulate_month(1)
            consolidator.add_cell(cell)
        
        consolidator.simulate_month(1)
        
        risk_groups = consolidator.get_cells_by_risk()
        
        assert isinstance(risk_groups, dict)
        # Verificar que todas las categorías existen
        for level in RiskLevel:
            assert level.name in risk_groups


class TestMasterNode:
    """Tests para MasterNode"""
    
    def test_master_creation(self):
        """Test creación de nodo maestro"""
        master = MasterNode("Test System")
        
        assert master.system_name == "Test System"
        assert len(master.consolidator_nodes) == 0
    
    def test_add_consolidator(self):
        """Test agregar consolidador"""
        master = MasterNode("Test System")
        consolidator = ConsolidatorNode("CON-001", "Consolidator 1")
        
        master.add_consolidator(consolidator)
        
        assert "CON-001" in master.consolidator_nodes
        assert len(master.consolidator_nodes) == 1
    
    def test_simulate_month(self):
        """Test simulación completa del sistema"""
        master = MasterNode("Test System")
        
        # Crear estructura completa
        consolidator = ConsolidatorNode("CON-001", "Cons 1")
        
        cell = SavingsCell("CELL-001", "Cell 1", 50)
        source = ValueSource("SRC-001", "Source 1", 10000, 1000, 2.0)
        cell.add_value_source(source)
        
        consolidator.add_cell(cell)
        master.add_consolidator(consolidator)
        
        result = master.simulate_month(1)
        
        assert result['month'] == 1
        assert result['system'] == "Test System"
        assert len(result['consolidators_results']) == 1
        assert 'total_system_balance' in result
        assert 'system_health_score' in result
    
    def test_simulate_multiple_months(self):
        """Test simulación de múltiples meses"""
        master = MasterNode("Test System")
        
        consolidator = ConsolidatorNode("CON-001", "Cons 1")
        cell = SavingsCell("CELL-001", "Cell 1", 50)
        source = ValueSource("SRC-001", "Source 1", 10000, 1000, 2.0)
        
        cell.add_value_source(source)
        consolidator.add_cell(cell)
        master.add_consolidator(consolidator)
        
        results = master.simulate_multiple_months(6)
        
        assert len(results) == 6
        assert results[0]['month'] == 1
        assert results[5]['month'] == 6
    
    def test_get_total_balance(self):
        """Test balance total del sistema"""
        master = MasterNode("Test System")
        
        # Crear 2 consolidadores con 2 células cada uno
        for i in range(2):
            consolidator = ConsolidatorNode(f"CON-{i}", f"Cons {i}")
            
            for j in range(2):
                cell = SavingsCell(f"CELL-{i}-{j}", f"Cell {j}", 50)
                source = ValueSource(f"SRC-{i}-{j}", "S", 5000, 0, 0)
                cell.add_value_source(source)
                consolidator.add_cell(cell)
            
            master.add_consolidator(consolidator)
        
        # 2 consolidadores * 2 células * 5000 = 20000
        assert master.get_total_balance() == 20000
    
    def test_get_system_report(self):
        """Test generación de reporte del sistema"""
        master = MasterNode("Test System")
        
        consolidator = ConsolidatorNode("CON-001", "Cons 1")
        cell = SavingsCell("CELL-001", "Cell 1", 50)
        source = ValueSource("SRC-001", "Source 1", 10000, 1000, 2.0)
        
        cell.add_value_source(source)
        consolidator.add_cell(cell)
        master.add_consolidator(consolidator)
        
        master.simulate_month(1)
        
        report = master.get_system_report()
        
        assert report['system_name'] == "Test System"
        assert 'summary' in report
        assert 'global_risk' in report
        assert 'consolidators' in report
        assert len(report['consolidators']) == 1
    
    def test_export_to_dataframe(self):
        """Test exportación a DataFrame"""
        master = MasterNode("Test System")
        
        consolidator = ConsolidatorNode("CON-001", "Cons 1")
        cell = SavingsCell("CELL-001", "Cell 1", 50)
        source = ValueSource("SRC-001", "Source 1", 10000, 1000, 2.0)
        
        cell.add_value_source(source)
        consolidator.add_cell(cell)
        master.add_consolidator(consolidator)
        
        master.simulate_multiple_months(3)
        
        df = master.export_to_dataframe()
        
        assert len(df) == 3
        assert 'Mes' in df.columns
        assert 'Balance Total' in df.columns
        assert 'Ganancia Total' in df.columns
        assert 'Health Score' in df.columns


class TestIntegration:
    """Tests de integración del sistema completo"""
    
    def test_create_example_system(self):
        """Test crear sistema de ejemplo"""
        system = create_example_system()
        
        assert isinstance(system, MasterNode)
        assert system.system_name == "Sistema SIDEPE Celular"
        assert len(system.consolidator_nodes) == 2  # Norte y Sur
    
    def test_full_simulation_flow(self):
        """Test flujo completo de simulación"""
        system = create_example_system()
        
        # Simular 12 meses
        results = system.simulate_multiple_months(12)
        
        assert len(results) == 12
        
        # Verificar que el balance crece
        initial_balance = results[0]['total_system_balance']
        final_balance = results[-1]['total_system_balance']
        
        assert final_balance > initial_balance
        
        # Verificar que hay ganancia
        final_profit = results[-1]['total_system_profit']
        assert final_profit > 0
    
    def test_system_with_shocks(self):
        """Test sistema con shocks externos"""
        system = create_example_system()
        
        # Definir shock en mes 6
        shocks = {
            6: {
                "CON-NORTE": {
                    "CELL-N1": {
                        "SRC-NUCLEUS": {
                            "risk_factor_change": 0.5,  # Duplica el riesgo
                            "gpm_change": 0.8  # Reduce rendimiento 20%
                        }
                    }
                }
            }
        }
        
        results = system.simulate_multiple_months(12, shocks)
        
        # Verificar que el sistema sigue operando
        assert len(results) == 12
        
        # Puede haber cambios de estado en células afectadas
        assert results[-1]['total_system_balance'] > 0
    
    def test_risk_escalation(self):
        """Test escalamiento de riesgo en jerarquía"""
        system = create_example_system()
        
        # Simular para generar datos
        system.simulate_multiple_months(3)
        
        # Verificar métricas en cada nivel
        
        # Nivel célula
        for consolidator in system.consolidator_nodes.values():
            for cell in consolidator.cells.values():
                composite_risk, level = cell.risk_metrics.calculate_composite_risk()
                assert 0 <= composite_risk <= 100
                assert isinstance(level, RiskLevel)
        
        # Nivel consolidador
        for consolidator in system.consolidator_nodes.values():
            composite_risk, level = consolidator.consolidated_metrics.calculate_composite_risk()
            assert 0 <= composite_risk <= 100
        
        # Nivel global
        composite_risk, level = system.global_metrics.calculate_composite_risk()
        assert 0 <= composite_risk <= 100


# Ejecutar tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
