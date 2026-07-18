#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hibridizador de DNA - Script de Execução
Launcher para GUI ou modo terminal
Re-Dino Project v1.0
"""

import sys
import argparse
import time
import json
from datetime import datetime

from hibridizador_core import Hibridizador, ParametroReacao
from hibridizador_hardware import ControladorHardware, CorLED


def modo_terminal(args):
    """Executar hibridizador em modo terminal (sem GUI)"""
    print("\n" + "="*80)
    print("🧬 HIBRIDIZADOR DNA 3000 - MODO TERMINAL")
    print("="*80 + "\n")
    
    # Criar instâncias
    hibridizador = Hibridizador()
    hardware = ControladorHardware()
    hibridizador.set_hardware(hardware)
    
    # Iniciar
    hardware.iniciar()
    hibridizador.ligar()
    
    print("[✓] Sistema ligado")
    print("[✓] Aquecendo...")
    
    # Esperar aquecimento
    time.sleep(3)
    
    # Configurar parâmetros
    parametros = {
        "temperatura_alvo": args.temperatura,
        "duracao_reacao": args.duracao * 60,  # Converter minutos para segundos
        "velocidade_bomba": args.velocidade
    }
    
    hibridizador.configurar_parametros(parametros)
    print(f"\n[✓] Parâmetros configurados:")
    print(f"    - Temperatura: {args.temperatura}°C")
    print(f"    - Duração: {args.duracao} minutos")
    print(f"    - Velocidade bomba: {args.velocidade}%")
    
    # Iniciar reação
    print(f"\n[▶] Iniciando reação...")
    hibridizador.iniciar_reacao()
    
    # Monitorar
    print(f"\n[📊] Monitorando reação:\n")
    print(f"{'Tempo':<10} {'Temp':<10} {'pH':<10} {'Progresso':<15} {'DNA-H':<12}")
    print("-" * 60)
    
    tempo_inicio = time.time()
    tempo_total = parametros["duracao_reacao"]
    
    while hibridizador.reacao_ativa:
        status = hibridizador.obter_status()
        dados = status['dados_reacao']
        
        tempo_dec = int(time.time() - tempo_inicio)
        min_dec = tempo_dec // 60
        seg_dec = tempo_dec % 60
        
        print(f"{min_dec:02d}:{seg_dec:02d}    {status['temperatura']:.1f}°C    "
              f"{status['pH']:.1f}     {dados['progresso_percentual']:5.1f}%      "
              f"{dados['DNA_hibridizado']:6.2f} µM")
        
        if dados['progresso_percentual'] >= 99:
            hibridizador.reacao_ativa = False
        
        time.sleep(2)
    
    # Resultado final
    print("\n" + "="*60)
    print("✓ REAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    resultado = hibridizador.resultado_final
    if resultado:
        print(f"\n📋 RESULTADO FINAL:")
        print(f"  DNA Hibridizado: {resultado['DNA_hibridizado_final']:.2f} µM")
        print(f"  DNA-A Restante: {resultado['DNA_A_restante']:.2f} µM")
        print(f"  DNA-B Restante: {resultado['DNA_B_restante']:.2f} µM")
        print(f"  Temperatura Média: {resultado['temperatura_media']:.1f}°C")
        print(f"  pH Final: {resultado['pH_final']:.2f}")
    
    # Exportar dados
    print(f"\n[💾] Exportando dados...")
    dados_export = hibridizador.exportar_dados_reacao()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_saida = f"hibridizacao_{timestamp}.json"
    
    with open(arquivo_saida, 'w') as f:
        json.dump(dados_export, f, indent=2)
    
    print(f"[✓] Dados salvos em: {arquivo_saida}")
    
    # Limpeza
    print(f"\n[🧹] Iniciando ciclo de limpeza...")
    hibridizador.resetar_sistema()
    
    time.sleep(2)
    
    # Desligar
    hibridizador.desligar()
    hardware.parar()
    
    print(f"[✓] Sistema desligado\n")


def modo_diagnostico():
    """Modo diagnóstico - verificar hardware"""
    print("\n" + "="*80)
    print("🔧 MODO DIAGNÓSTICO")
    print("="*80 + "\n")
    
    hardware = ControladorHardware()
    hardware.iniciar()
    
    print("[✓] Hardware inicializado\n")
    
    # Teste de sensores
    print("📍 TESTE DE SENSORES:")
    for i in range(5):
        status = hardware.obter_status_completo()
        sensores = status['sensores']
        print(f"  [{i+1}] T: {sensores['temperatura']:.1f}°C | "
              f"pH: {sensores['pH']:.2f} | "
              f"Cond: {sensores['condutividade']:.1f} mS/cm | "
              f"Turb: {sensores['turbidez']:.1f} NTU")
        time.sleep(1)
    
    # Teste de atuadores
    print("\n📌 TESTE DE ATUADORES:")
    
    print("  [Aquecedor] Aquecendo para 40°C...")
    hardware.ligar_aquecedor(40)
    time.sleep(5)
    status = hardware.obter_status_completo()
    temp = status['atuadores']['aquecedor']['temperatura_atual']
    print(f"    Temperatura atual: {temp:.1f}°C")
    hardware.desligar_aquecedor()
    
    print("  [Bomba] Testando bomba...")
    hardware.set_velocidade_bomba(50)
    hardware.ligar_bomba()
    time.sleep(3)
    status = hardware.obter_status_completo()
    bomba = status['atuadores']['bomba']
    print(f"    Fluxo: {bomba['fluxo']:.1f} mL/min | Volume: {bomba['volume_dispensado']:.2f} mL")
    hardware.desligar_bomba()
    
    print("  [LED RGB] Testando cores...")
    cores = [CorLED.VERMELHO, CorLED.VERDE, CorLED.AZUL, CorLED.AMARELO]
    for cor in cores:
        hardware.set_cor_led(cor, 100)
        print(f"    {cor.name}: ✓")
        time.sleep(0.5)
    
    hardware.parar()
    print("\n[✓] Diagnóstico concluído\n")


def modo_calibracao():
    """Modo calibração - calibrar sensores"""
    print("\n" + "="*80)
    print("⚙️ MODO CALIBRAÇÃO")
    print("="*80 + "\n")
    
    print("Para calibrar sensores:")
    print("1. Temperatura: Coloque uma sonda conhecida")
    print("2. pH: Use solução de pH 7.0 e pH 4.0")
    print("3. Condutividade: Use solução padrão\n")
    
    hardware = ControladorHardware()
    hardware.iniciar()
    
    print("[✓] Sistema pronto para calibração\n")
    
    # Exemplo de leitura para calibração
    print("Leituras atuais (para calibração):")
    for i in range(10):
        status = hardware.obter_status_completo()
        sensores = status['sensores']
        print(f"  T: {sensores['temperatura']:.2f}°C | "
              f"pH: {sensores['pH']:.3f} | "
              f"Cond: {sensores['condutividade']:.2f} mS/cm")
        time.sleep(1)
    
    hardware.parar()
    print("\n[✓] Calibração finalizada\n")


def modo_gui():
    """Executar interface gráfica"""
    try:
        from hibridizador_gui import main
        print("[✓] Iniciando interface gráfica...")
        main()
    except ImportError as e:
        print(f"[✗] Erro ao importar PyQt5: {e}")
        print("Instale com: pip3 install PyQt5")
        sys.exit(1)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Hibridizador DNA 3000 - Sistema de Hibridização de DNA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python3 run_hibridizador.py --gui              # Iniciar GUI
  python3 run_hibridizador.py --terminal -t 37.5 -d 4 -v 75   # Modo terminal
  python3 run_hibridizador.py --diagnostico      # Modo diagnóstico
  python3 run_hibridizador.py --calibracao       # Modo calibração
        """
    )
    
    # Argumentos de modo
    parser.add_argument('--gui', action='store_true', 
                       help='Executar interface gráfica PyQt5')
    parser.add_argument('--terminal', action='store_true', 
                       help='Executar em modo terminal')
    parser.add_argument('--diagnostico', action='store_true', 
                       help='Modo diagnóstico do hardware')
    parser.add_argument('--calibracao', action='store_true', 
                       help='Modo calibração de sensores')
    
    # Argumentos de configuração
    parser.add_argument('-t', '--temperatura', type=float, default=37.5,
                       help='Temperatura alvo em °C (padrão: 37.5)')
    parser.add_argument('-d', '--duracao', type=int, default=4,
                       help='Duração da reação em minutos (padrão: 4)')
    parser.add_argument('-v', '--velocidade', type=float, default=75.0,
                       help='Velocidade da bomba em %% (padrão: 75)')
    
    args = parser.parse_args()
    
    # Se nenhum modo especificado, usar GUI como padrão
    if not any([args.gui, args.terminal, args.diagnostico, args.calibracao]):
        args.gui = True
    
    # Executar modo selecionado
    if args.gui:
        modo_gui()
    elif args.terminal:
        modo_terminal(args)
    elif args.diagnostico:
        modo_diagnostico()
    elif args.calibracao:
        modo_calibracao()


if __name__ == "__main__":
    main()
