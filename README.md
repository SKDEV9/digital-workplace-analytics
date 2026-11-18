# Digital Workplace Analytics

Projeto de estudo e portfólio focado em **Data Analytics**, **Business Intelligence** e **Transformação Digital**. O objetivo é avaliar a adoção, o engajamento e o suporte de ferramentas digitais em uma organização fictícia do setor industrial e de aviação.

> **Nota de Transparência:** Todos os dados, departamentos, ferramentas e registros utilizados neste repositório são **100% sintéticos**, gerados exclusivamente para fins de estudo analítico e demonstração técnica. Não representam sistemas ou métricas de nenhuma empresa real.

## Estrutura do Repositório

- `data/`: Datasets sintéticos brutos (`raw/`) e processados (`processed/`).
- `sql/`: Modelagem relacional, validações de integridade, consultas analíticas e views em PostgreSQL.
- `python/`: Script gerador de dados sintéticos com semente fixa (`seed=42`).
- `notebooks/`: Análise exploratória, tratamento com Pandas e visualizações com Matplotlib.
- `ai-powered-digital-support/`: Prova de conceito de triagem de chamados internos utilizando IA generativa, engenharia de prompts e governança.
- `docs/`: Guia prático de interpretação de indicadores digitais para público não técnico.

## Definição Formal da Métrica Principal

### Taxa de Adoção Ativa (%)

$$\text{Taxa de Adoção Ativa} = \left( \frac{\text{Usuários Ativos Elegíveis}}{\text{Funcionários Elegíveis com Acesso}} \right) \times 100$$

- **Numerador (Usuários Ativos Elegíveis):** Funcionários elegíveis que utilizaram a ferramenta em **pelo menos $N = 3$ dias distintos** dentro do mês analisado. O corte de 3 dias filtra cliques acidentais e captura recorrência de uso na rotina. *(Serão realizados testes de sensibilidade com $N = 1$ e $N = 5$ dias).*
- **Denominador (Funcionários Elegíveis com Acesso):** Total de funcionários que possuíram permissão ativa para a ferramenta durante **todo o mês analisado**, respeitando cumulativamente:
  1. Contratação anterior ou igual ao primeiro dia do mês (`hire_date`).
  2. Ferramenta já lançada no início do mês (`launch_date`).
  3. Acesso concedido até o primeiro dia do mês (`access_granted_date`) e não revogado antes do último dia do mês (`access_revoked_date`).
- **Tratamento de Exceção:** Caso não haja funcionários elegíveis no denominador em determinado mês/departamento, a taxa é registrada como `NULL` (indefinida), nunca como `0%`.