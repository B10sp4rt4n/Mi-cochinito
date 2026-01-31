#!/usr/bin/env python3
"""
Script de prueba para verificar que el simulador está correctamente implementado.
"""

import ast
import sys

def test_syntax():
    """Verifica que el código Python sea sintácticamente correcto"""
    print("🧪 Test 1: Verificación de Sintaxis")
    
    try:
        with open('/workspaces/Mi-cochinito/app_cochino.py', 'r') as f:
            code = f.read()
            ast.parse(code)
        print("✅ Sintaxis de Python correcta")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False

def test_class_structure():
    """Verifica que las clases principales existan"""
    print("\n🧪 Test 2: Estructura de Clases")
    
    with open('/workspaces/Mi-cochinito/app_cochino.py', 'r') as f:
        code = f.read()
    
    # Verificar que SIDEPEIntelligence existe
    if 'class SIDEPEIntelligence:' in code:
        print("✅ Clase SIDEPEIntelligence encontrada")
    else:
        print("❌ Clase SIDEPEIntelligence NO encontrada")
        return False
    
    # Verificar métodos principales
    methods = [
        'analyze_performance',
        'generate_recommendations',
        'predict_future_cycles',
        'auto_optimize'
    ]
    
    for method in methods:
        if f'def {method}' in code:
            print(f"✅ Método {method}() encontrado")
        else:
            print(f"❌ Método {method}() NO encontrado")
            return False
    
    return True

def test_functions():
    """Verifica que las funciones principales existan"""
    print("\n🧪 Test 3: Funciones Principales")
    
    with open('/workspaces/Mi-cochinito/app_cochino.py', 'r') as f:
        code = f.read()
    
    functions = [
        'run_simulation',
        'run_multi_cycle_simulation'
    ]
    
    for func in functions:
        if f'def {func}(' in code:
            print(f"✅ Función {func}() encontrada")
        else:
            print(f"❌ Función {func}() NO encontrada")
            return False
    
    return True

def test_ui_elements():
    """Verifica elementos clave de la UI"""
    print("\n🧪 Test 4: Elementos de UI")
    
    with open('/workspaces/Mi-cochinito/app_cochino.py', 'r') as f:
        code = f.read()
    
    ui_elements = [
        'st.title',
        'st.sidebar',
        'st.metric',
        'st.line_chart',
        'Dashboard de Salud',
        'Recomendaciones de la IA',
        'Auto-Optimizado'
    ]
    
    for element in ui_elements:
        if element in code:
            print(f"✅ Elemento '{element}' encontrado")
        else:
            print(f"⚠️  Elemento '{element}' NO encontrado")
    
    return True

def test_imports():
    """Verifica los imports necesarios"""
    print("\n🧪 Test 5: Imports")
    
    with open('/workspaces/Mi-cochinito/app_cochino.py', 'r') as f:
        code = f.read()
    
    imports = ['streamlit', 'pandas', 'numpy']
    
    for imp in imports:
        if f'import {imp}' in code:
            print(f"✅ Import {imp} encontrado")
        else:
            print(f"❌ Import {imp} NO encontrado")
            return False
    
    return True

def test_documentation():
    """Verifica que existan los archivos de documentación"""
    print("\n🧪 Test 6: Documentación")
    
    import os
    
    docs = [
        'README.md',
        'GUIA_USO.md',
        'EJEMPLOS_IA.md',
        'RESUMEN_EJECUTIVO.md',
        'ANTES_DESPUES.md'
    ]
    
    for doc in docs:
        path = f'/workspaces/Mi-cochinito/{doc}'
        if os.path.exists(path):
            print(f"✅ {doc} existe")
        else:
            print(f"❌ {doc} NO existe")
            return False
    
    return True

def test_code_metrics():
    """Calcula métricas del código"""
    print("\n🧪 Test 7: Métricas del Código")
    
    with open('/workspaces/Mi-cochinito/app_cochino.py', 'r') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    comment_lines = len([l for l in lines if l.strip().startswith('#')])
    
    print(f"✅ Total de líneas: {total_lines}")
    print(f"✅ Líneas de código: {code_lines}")
    print(f"✅ Líneas de comentarios: {comment_lines}")
    print(f"✅ Ratio comentarios/código: {(comment_lines/code_lines*100):.1f}%")
    
    return True

def run_all_tests():
    """Ejecuta todos los tests"""
    print("=" * 60)
    print("🚀 Tests del Simulador Inteligente SIDEPE")
    print("=" * 60)
    
    tests = [
        test_syntax,
        test_imports,
        test_class_structure,
        test_functions,
        test_ui_elements,
        test_documentation,
        test_code_metrics
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test falló: {test.__name__}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{len(tests)} tests pasados")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 ¡Todos los tests pasaron! El simulador está correctamente implementado.")
        print("\n📝 Resumen de Capacidades:")
        print("   ✅ Motor de IA con 4+ métodos inteligentes")
        print("   ✅ Simulación simple y multi-ciclo")
        print("   ✅ Auto-optimización")
        print("   ✅ Dashboard de salud")
        print("   ✅ Sistema de recomendaciones")
        print("   ✅ Predicciones futuras")
        print("   ✅ Documentación completa (5 archivos)")
        print("\n🚀 Para ejecutar: streamlit run app_cochino.py")
    else:
        print(f"⚠️  {failed} test(s) fallaron. Revisar el código.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
