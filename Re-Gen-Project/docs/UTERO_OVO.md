# Útero-Ovo — do conceito especulativo ao controlador real

Este documento registra a origem do "Útero-Ovo": uma descrição de ficção
científica de uma cápsula de incubação, e como cada parte dela foi traduzida
(ou substituída) para algo que existe e funciona hoje, implementado em
`src/re_gen/hardware/utero_ovo_controller.py`.

Nada aqui foi descartado por desrespeito ao conceito original — pelo
contrário, o objetivo é honrar a ambição da ideia sendo honesto sobre o que
dela já é engenharia possível e o que ainda é ficção.

## Tabela de tradução

| # | Conceito original (Útero-Ovo) | Realidade em 2026 | O que foi implementado |
|---|---|---|---|
| 1 | Casca ovoidal em polímero + biovidro transparente | Chassi comum: qualquer laboratório de prototipagem constrói isso hoje | Sem mudança — é só um invólucro físico |
| 2 | Líquido conservante à base de perfluorocarbono com oxigênio líquido | Perfluorocarbonos carreadores de O2 existem e são usados experimentalmente em **ventilação líquida pulmonar** (não em imersão total de um embrião inteiro) | Circulação e filtração automatizadas ficaram no design, mas o controlador **não assume** que a imersão total do embrião em PFC já é um protocolo validado — isso continua sendo pesquisa em aberto |
| 3 | Membrana biomimética que muda de espessura/permeabilidade sozinha, "programada quimicamente" por fase | **Não existe.** Nenhum material muda sua própria estrutura em resposta ao estágio de um embrião | Substituído pelo filme de **polimetilpenteno (PMP)**, material real e publicado (Tahara & Obara, 2014), de permeabilidade fixa. A "mudança de fase" vira responsabilidade do controlador, que muda as condições **externas** (O2, temperatura) em dias específicos — não do material |
| 4 | RTOS bare-metal customizado do zero | Redundante para este problema: um firmware Arduino (C++ sobre microcontrolador) já entrega o timing determinístico necessário | Implementado como firmware compatível com o protocolo serial ASCII já usado no resto do projeto (`arduino_bridge.py`) |
| 5 | IA de borda lendo sinais biométricos em milissegundos e liberando hormônios instantaneamente | **Não existe** sensor não-invasivo que leia estado hormonal de um embrião em tempo real através de uma membrana fechada | Substituído por um **controlador PID clássico** (determinístico, sem IA, conhecido desde os anos 1920) atuando sobre variáveis mensuráveis de verdade: temperatura, umidade, O2, massa (evaporação) |

## O que o controlador real (`UteroOvoController`) faz hoje

Automatiza o protocolo publicado de cultura *ex-ovo* para embriões de ave
(Tahara & Obara, 2014), em 3 fases reais:

1. **Transferência** (dia 2,3 / 55-56h) — evento manual registrado pelo controlador.
2. **Cultura padrão** (dia 2,3 → dia 17) — temperatura 37,5 °C, reposição de
   água/lactato de cálcio por cronograma real, monitorada por perda de massa.
3. **Oxigenação pura** (a partir do dia 17) — troca real de válvula para O2
   quase puro, replicando os 57,1% de taxa de eclosão publicados.

## O que continua sendo apenas visão, não implementação

- Gestação de uma espécie **não-aviária** (réptil de grande porte, e muito
  menos um dinossauro) neste sistema: não há protocolo publicado equivalente.
- Imersão total do embrião em líquido perfluorocarbonado como meio de
  gestação completo (diferente de ventilação pulmonar): não validado.
- Qualquer forma de "IA que entende o embrião": não existe sensoriamento que
  permita isso hoje, com ou sem IA.

## Referências

- Tahara, Y. & Obara, K. (2014). *A Novel Shell-less Culture System for
  Chick Embryos Using a Plastic Film as Culture Vessels*. Journal of Poultry
  Science, 51(3), 307–312. https://doi.org/10.2141/jpsa.0130043
- Tahara, Y., Obara, K. & Kamihira, M. (2021). *Calcium carbonate
  supplementation to chorioallantoic membranes improves hatchability in
  shell-less chick embryo culture*. J. Biosci. Bioeng., 131, 314–319.
