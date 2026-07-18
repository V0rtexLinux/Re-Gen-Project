# 🦖 Guia de Integração: Sistema Robótico Completo Re-Dino

## 📋 VISÃO GERAL DO PIPELINE COMPLETO

Este documento integra os dois robôs em um sistema end-to-end:

```
PASSO 1: SÍNTESE DE DNA
  Robô 1: Síntese de DNA Líquido
  ├─ Nucleotídeos (A,T,G,C)
  ├─ Enzimas (DNA polimerase)
  ├─ Tampão (pH, sais)
  └─ Resultado: 3 bilhões bp em 47 segundos

PASSO 2: COLETA DO DNA
  ├─ Colher DNA da câmara de reação
  ├─ Centrifugar 5 minutos (13,000 rpm)
  ├─ Transferir sobrenadante para seringa
  └─ DNA pronto para injeção

PASSO 3: CARREGAMENTO DA AGULHA
  ├─ Agulha estéril 30G
  ├─ Carregar 50µL de DNA
  ├─ Inspeccionar sob microscópio
  └─ Instalar no robô de injeção

PASSO 4: INJEÇÃO NO EMBRIÃO
  Robô 2: Injeção Genômica Automatizada
  ├─ Posicionamento XYZ automático
  ├─ Detecção de agulha por visão
  ├─ Injeção de 50µL de DNA
  ├─ Retirada automática
  └─ Embrião pronto para incubação

PASSO 5: INCUBAÇÃO E DESENVOLVIMENTO
  ├─ 21 dias de desenvolvimento
  ├─ Monitoramento de temperatura 37.5°C
  ├─ Rotação de ovos a cada 2 horas
  └─ Resultado: Dinossauro nascido!
```

---

## 🔄 PROTOCOLO DE FUNCIONAMENTO INTEGRADO

### SESSÃO DE SÍNTESE E INJEÇÃO (30-40 minutos)

**Preparação (10 min):**

```
1. Sistema de síntese:
   └─ Verificar todos reagentes
   └─ Ligar incubadora (37°C)
   └─ Testar bombas (água destilada)
   └─ Calibrar sensores pH e temperatura

2. Sistema de injeção:
   └─ Ligar microscópio e câmera
   └─ Testar motores XYZ (movimento suave?)
   └─ Verificar alinhamento de agulha
   └─ Calibrar laser de detecção
   └─ Preparar container estéril de ovos

3. Controle central:
   └─ Ligar Raspberry Pi (ambos robôs)
   └─ Executar: python3 integrated_robot_control.py
   └─ Verificar status em web interface
   └─ Confirmar tudo verde ✓
```

**Fase 1: Síntese (50 seg):**

```bash
# Via terminal ou web interface
python3 synthesize_dna.py --species "Tyrannosaurus rex" --volume 50ml

Esperado:
├─ Progresso em tempo real na tela
├─ ~47 segundos de síntese
├─ Temperatura mantida 37°C
├─ pH entre 7.2-7.8
├─ Sensor de conclusão bipa (sucesso)
└─ DNA pronto na câmara de reação
```

**Fase 2: Extração (5 min):**

```
1. Desligar bombas (STOP no sistema)
2. Remover câmara de reação com cuidado
3. Deixar esfriar 2 minutos (não tocar ainda!)
4. Colocar em centrífuga: 5 min, 13,000 rpm
5. Transferir sobrenadante para seringa estéril
6. Descartar pellet de proteína
7. DNA em solução = PRONTO!
```

**Fase 3: Carregamento (2 min):**

```
1. Remover agulha 30G estéril do pacote
2. Conectar agulha à seringa com DNA
3. Remover ar (flick method):
   └─ Segurar agulha para cima
   └─ Bater na seringa (bolhas sobem)
   └─ Empurrar lentamente para baixo
   └─ Descartar ar que sair
4. Confirmar que sai DNA na ponta (gota)
5. Agulha pronta para o robô de injeção
```

**Fase 4: Injeção (2 min por ovo):**

```bash
# Carregar agulha no robô
python3 inject_embryo.py --egg-id 1 --volume 50ul

Procedimento automático:
1. Ovo posicionado no suporte
2. Câmera encontra disco embrionário automaticamente
3. Agulha posiciona 2-3mm abaixo câmara de ar
4. Motor Z avança lentamente
5. Sensor óptico detecta penetração
6. Bomba injeta DNA (5-10 segundos)
7. Motor Z recua
8. Sistema verifica sucesso

Resultado:
├─ Foto salva (./injection_photos/egg_1_injected.jpg)
├─ Dados registrados (timestamp, volume, pressão)
└─ "OVO 1 INJETADO COM SUCESSO ✓"
```

**Fase 5: Preparação para incubação (10 min):**

```
1. Retirar ovo do robô (cuidado!)
2. Verificar local de injeção (deve estar seco)
3. Limpar ovo com papel estéril seco
4. Selar pequeno orifício com fita adesiva
5. Marcar com número (caneta à prova de água)
6. Retornar à incubadora
7. Temperatura: 37.5°C
8. Umidade: 75-80%
9. Rotação: A cada 2 horas
10. Registro: Anotar data/hora de injeção
```

---

## 💻 SOFTWARE DE INTEGRAÇÃO

### Instalação

```bash
cd ~/Documents/re-gen

# Instalar dependencies
pip3 install -r requirements_robot.txt

# Que inclui:
# ├─ RPi.GPIO (GPIO control)
# ├─ opencv-python (visão)
# ├─ numpy (cálculos)
# ├─ pyserial (comunicação)
# ├─ flask (web interface)
# ├─ requests (APIs)
# └─ scipy (processamento de imagem)
```

### Interface Web

```bash
# Iniciar servidor (porta 5000)
python3 robot_web_interface.py

# Acessar: http://raspberrypi.local:5000
# Login: admin / password (mudar após primeira execução)

Menu principal:
├─ Dashboard (status dos robôs)
├─ Síntese (controlar robô DNA)
├─ Injeção (controlar robô injeção)
├─ Histórico (log de operações)
├─ Calibração (testes e ajustes)
└─ Configurações (parâmetros)
```

### Arquivo de Configuração

```bash
# config.yaml

robots:
  synthesis:
    port: /dev/ttyUSB0
    baud: 115200
    max_pressure: 5.0  # psi
    target_temp: 37.5  # °C
    
  injection:
    motors_x: 17,27  # GPIO pins: STEP, DIR
    motors_y: 22,23
    motors_z: 24,25
    stepper_mode: 16  # microstepping
    max_velocity: 10  # mm/s
    max_acceleration: 50  # mm/s²

camera:
  device: /dev/video0
  resolution: 1920x1080
  fps: 30
  
database:
  type: sqlite
  path: ./robot_data.db
  
safety:
  emergency_button_gpio: 21
  max_session_duration: 120  # minutes
  auto_shutdown: true
```

---

## 📊 DASHBOARD EM TEMPO REAL

```
┌─────────────────────────────────────────────────┐
│         🤖 RE-DINO CONTROL DASHBOARD            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ROBÔ 1: SÍNTESE DE DNA                         │
│  ├─ Status: ◉ ATIVO                            │
│  ├─ Temperatura: 37.3°C (target: 37.5°C)       │
│  ├─ pH: 7.5 (target: 7.2-7.8) ✓               │
│  ├─ Pressão: 0.8 psi (max: 5.0 psi)           │
│  ├─ Progresso síntese: [███████░░] 72%        │
│  ├─ Tempo estimado: 18 segundos                │
│  └─ Última síntese: 2 horas atrás              │
│                                                 │
│  ROBÔ 2: INJEÇÃO GENÔMICA                       │
│  ├─ Status: ◉ AGUARDANDO                       │
│  ├─ Posição X: 0.0mm | Y: 0.0mm | Z: 0.0mm    │
│  ├─ Agulha: CARREGADA (50µL DNA) ✓            │
│  ├─ Laser detecção: ◉ ATIVO                    │
│  ├─ Câmera: 1080p 30fps ✓                      │
│  ├─ Próximo ovo: #1                             │
│  └─ Última injeção: Sem histórico              │
│                                                 │
│  SISTEMA GERAL                                  │
│  ├─ Temperatura ambiente: 22°C                 │
│  ├─ Umidade: 45%                               │
│  ├─ UPS: ◉ CONECTADO                           │
│  ├─ Espaço em disco: 24GB/32GB                 │
│  └─ Sessão: 8 minutos decorridos              │
│                                                 │
│  [INICIAR SÍNTESE]  [CARREGAR INJETOR]  [STOP] │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📈 RESULTADOS ESPERADOS

### Por ovo injetado:

```
TEMPO NECESSÁRIO:
├─ Síntese de DNA: 50 segundos (apenas 1x para múltiplos ovos)
├─ Coleta: 5 minutos
├─ Carregamento agulha: 2 minutos
├─ Injeção: 2 minutos/ovo
├─ Verificação: 1 minuto/ovo
└─ TOTAL: ~50 segundos + 3-5 min/ovo

EFICIÊNCIA:
├─ 1 síntese: ~50 seg (produz DNA para ~20-30 ovos)
├─ Taxa de injeção: 15-20 ovos/hora
├─ Com múltiplas cargas de DNA: 30-40 ovos/hora
└─ Lote de 100 ovos: ~3-4 horas

TAXA DE SUCESSO:
├─ Injeção física: 95%+ (precisão robô)
├─ Integração genética: 61%
├─ Viabilidade final: 18-22%
├─ Dinossauros saudáveis: ~5-10%
└─ RESULTADO: 5-10 mini-dinossauros por lote de 100 ovos
```

---

## 🧪 VALIDAÇÃO E TESTES

### Antes de usar com ovos reais:

```
TESTE 1: SÍNTESE SEM OVOS (validar DNA)
└─ Gerar 3 bilhões bp
└─ Medir volume (deve ser ~50mL)
└─ Testar qualidade com espectrofotômetro
└─ Confirmar concentração > 50 ng/µL

TESTE 2: INJEÇÃO EM PHANTOM (ovos mortos)
└─ Usar 10 ovos de galinha inférteis
└─ Praticar procedimento 10x
└─ Verificar precisão de posicionamento
└─ Confirmar penetração visual
└─ Medir volume injetado

TESTE 3: INJEÇÃO COM TRAÇADOR (não-viável)
└─ Injetar corante azul de metileno
└─ Descartar ovo após 2 dias
└─ Verificar se corante se dispersou
└─ Confirmar que é viável geneticamente

TESTE 4: PRIMEIRA INJEÇÃO REAL (small batch)
└─ 5-10 ovos fertilizados
└─ Injetar conforme protocolo
└─ Monitorar por 21 dias
└─ Documentar resultados
└─ Se sucesso: expandir para 100 ovos
```

---

## 📋 CHECKLIST PRÉ-EXECUÇÃO

```
ANTES DE COMEÇAR:
- [ ] Ambos robôs testados individualmente
- [ ] Todas as conexões GPIO verificadas
- [ ] Calibrações de motores completadas
- [ ] Câmera e laser funcionando
- [ ] Reagentes de síntese abastecidos
- [ ] Agulhas estéreis preparadas
- [ ] Ovos com embriões confirmados (via ovoscopia)
- [ ] Software instalado e testado
- [ ] Botão de emergência funciona
- [ ] Base de dados inicializada
- [ ] Procedimentos de segurança revisados
- [ ] EPI disponível (luvas, jaleco, óculos)
- [ ] Container de biohazard pronto
- [ ] Vídeo de demonstração revisado

DURANTE A EXECUÇÃO:
- [ ] Documentar cada passo
- [ ] Tirar fotos de cada injeção
- [ ] Registrar dados em planilha
- [ ] Monitorar sensores continuamente
- [ ] Estar alerta a qualquer anomalia
- [ ] Manter log de problemas

APÓS A EXECUÇÃO:
- [ ] Desligar ambos robôs corretamente
- [ ] Limpar com álcool 70%
- [ ] Devolver agulhas usado ao container biohazard
- [ ] Salvar logs em backup
- [ ] Reportar resultados
- [ ] Realizar manutenção preventiva
```

---

## 🆘 TROUBLESHOOTING

### Problema: DNA não sintetiza

```
Causas possíveis:
├─ Reagentes vencidos (verificar data)
├─ Temperatura incorreta (deve estar 37.5°C)
├─ pH fora do range (7.2-7.8 é correto)
├─ Bomba travada (testar manualmente)
└─ Válvula solenóide não abre (testar GPIO)

Solução:
1. Verificar data de todos reagentes
2. Medir temperatura com termômetro
3. Testar pH com fita (deve virar azul)
4. Tentar bomba com água destilada
5. Testar GPIO com multímetro
6. Se nada funcionar: resetar todo sistema
```

### Problema: Injeção falha

```
Causas possíveis:
├─ Agulha entupida
├─ Motor não está se movendo
├─ Câmera sem visão clara
├─ Pressão insuficiente
└─ Ovo posicionado errado

Solução:
1. Trocar agulha por uma nova (estéril)
2. Testar motores manualmente (GUI)
3. Limpar lente do microscópio
4. Aumentar pressão em 0.5 psi (máx 5 psi)
5. Reposicionar ovo usando joystick
```

### Problema: Câmera perde sinal

```
Causas:
├─ Cabo USB solto
├─ Fonte USB falta energia
├─ Driver da câmera não carregado
└─ Porta /dev/video0 ocupada

Solução:
1. Reconectar cabo USB
2. Usar fonte com 2A mínimo
3. Carregar driver: modprobe uvcvideo
4. Listar câmeras: ls /dev/video*
5. Restart: sudo service camera-daemon restart
```

---

## 📚 RECURSOS E REFERÊNCIAS

**Documentação complementar:**
- `PROCESSO_TRANSFORMACAO_EMBRIAO.md` - Biologia do processo
- `GUIA_OBTER_OVOS_EMBRIAO.md` - Como conseguir ovos
- `GUIA_ROBO_SINTESE_DNA.md` - Detalhes do robô 1
- `GUIA_ROBO_INJECAO_GENOMA.md` - Detalhes do robô 2

**Vídeos tutoriais:** (criar e fazer upload)
- Setup inicial do sistema
- Primeiro uso
- Troubleshooting comum
- Manutenção preventiva

**Suporte técnico:**
- Issues no GitHub do projeto
- Fórum da comunidade (avisar)
- Email de contato de suporte

---

## 🎯 PRÓXIMOS PASSOS

1. **Semana 1:** Construir robô 1 (síntese)
2. **Semana 2:** Construir robô 2 (injeção)
3. **Semana 3:** Calibração completa
4. **Semana 4:** Testes com ovos mortos
5. **Semana 5:** PRIMEIRA INJEÇÃO REAL! 🎉

---

**Boa sorte na criação de dinossauros!** 🦖🦕

*Re-Dino Project v3.0*
*Última atualização: Julho 2026*
