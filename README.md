# Data Challenge — Data Quality, Athena DDL e Arquitetura AWS

Projeto desenvolvido por **Michele Teixeira** com foco em qualidade de dados, validação de eventos, automação de DDL para Amazon Athena e desenho de uma arquitetura de dados orientada a eventos na AWS.

> O objetivo deste repositório é demonstrar raciocínio de engenharia de dados, organização de código e decisões técnicas. As integrações com serviços AWS estão representadas de forma conceitual ou simulada; o projeto não provisiona infraestrutura real.

## Visão geral

O projeto reúne quatro frentes:

1. **Data Quality:** validação recursiva de eventos JSON contra um schema simplificado.
2. **Athena DDL:** conversão automática de JSON Schema em `CREATE EXTERNAL TABLE`.
3. **Arquitetura AWS:** proposta conceitual para ingestão, validação, desacoplamento, armazenamento e consulta.
4. **Modelagem de tabelas:** dicionário de dados para domínios de clientes, contas e transações.

## Arquitetura proposta

![Arquitetura conceitual do módulo de Data Quality](img/modulo-data-quality.png)

O diagrama apresenta uma proposta conceitual com serviços como Amazon SNS, Amazon SQS, AWS Lambda, Amazon Kinesis, Amazon S3, Amazon DynamoDB, AWS Glue e Amazon Athena.

### Papel dos principais componentes

| Componente | Papel no desenho |
|---|---|
| Fonte JSON | Origem dos eventos |
| Amazon SNS | Distribuição de mensagens para consumidores |
| Amazon SQS | Desacoplamento, buffer e processamento assíncrono |
| AWS Lambda | Validação e processamento de eventos |
| Amazon Kinesis | Fluxo de eventos para processamento em streaming |
| Amazon S3 | Armazenamento de dados para consumo analítico |
| Amazon DynamoDB | Persistência de baixa latência para dados operacionais |
| AWS Glue | Catálogo e metadados |
| Amazon Athena | Consulta SQL sobre dados armazenados no S3 |

O arquivo editável do diagrama está disponível em [`modulo_data_quality_arquitetura.drawio`](modulo_data_quality_arquitetura.drawio).

## Estrutura do repositório

```text
.
├── desafios/
│   ├── exercicio1/
│   │   ├── event_validator.py
│   │   ├── main.py
│   │   ├── schema.json
│   │   └── test_event_validator.py
│   ├── exercicio2/
│   │   ├── json_schema_to_athena.py
│   │   ├── main.py
│   │   ├── schema.json
│   │   └── test_json_schema_to_athena.py
│   └── exercicio4/
│       └── challenge_tables.xlsx
├── img/
│   └── modulo-data-quality.png
├── .gitignore
├── modulo_data_quality_arquitetura.drawio
├── requirements.txt
└── README.md
```

## Exercício 1 — Módulo de Data Quality

O módulo valida eventos de forma recursiva com base em `schema.json`.

### Regras implementadas

- validação de campos obrigatórios;
- validação de tipos;
- validação de objetos aninhados;
- rejeição de campos extras não definidos no schema;
- tratamento correto do caso particular de Python em que `bool` é subtipo de `int`;
- mensagens de erro com o caminho do campo inválido.

### Exemplo de evento válido

```json
{
  "eid": "12345",
  "documentNumber": "67890",
  "name": "Renata",
  "age": 30,
  "address": {
    "street": "Rua da Alegria",
    "number": 100,
    "mailAddress": true
  }
}
```

### Executar

A partir da raiz do projeto:

```bash
python desafios/exercicio1/main.py
```

O exemplo demonstra um evento válido e outro inválido.

## Exercício 2 — Geração de DDL para Amazon Athena

O módulo lê o JSON Schema e converte os campos para tipos compatíveis com uma DDL de tabela externa no Athena.

### Mapeamentos principais

| JSON Schema | Athena/Hive DDL |
|---|---|
| `string` | `STRING` |
| `integer` | `INT` |
| `number` | `DOUBLE` |
| `boolean` | `BOOLEAN` |
| `object` | `STRUCT<...>` |
| `array` | `ARRAY<...>` |

A DDL gerada inclui:

- `CREATE EXTERNAL TABLE IF NOT EXISTS`;
- colunas derivadas do schema;
- partições por `year`, `month` e `day`;
- armazenamento em Parquet;
- `LOCATION` configurável no Amazon S3.

### Executar

```bash
python desafios/exercicio2/main.py
```

> Importante: a execução no Athena é **simulada**. O código gera e exibe a DDL, mas não envia a consulta para uma conta AWS.

## Exercício 4 — Dicionário de tabelas

O arquivo [`challenge_tables.xlsx`](desafios/exercicio4/challenge_tables.xlsx) documenta estruturas de dados para seis domínios:

- `customer`;
- `account`;
- `bankslip`;
- `pix_send`;
- `pix_received`;
- `p2p_tef`.

Cada aba registra nome da coluna, tipo de dado, indicação de chave de partição e descrição funcional.

## Como executar o projeto

### Pré-requisito

- Python 3.10 ou superior.

O projeto utiliza somente a biblioteca padrão do Python. Portanto, não há dependências externas obrigatórias.

### Opcional: criar ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

### Executar os testes

A partir da raiz do repositório:

```bash
python -m unittest discover -s desafios -p "test_*.py" -v
```

## Decisões técnicas

### Validador manual

A validação foi implementada manualmente para demonstrar a lógica de Data Quality e recursividade. Em produção, uma biblioteca completa de JSON Schema pode ser mais adequada quando houver necessidade de suportar integralmente a especificação.

### Rejeição de campos extras

O módulo adota comportamento estrito: campos não definidos no schema invalidam o evento. Essa decisão ajuda a detectar mudanças inesperadas de contrato.

### DDL com `STRUCT`

Objetos aninhados são convertidos para estruturas `STRUCT`, preservando a hierarquia do evento na definição da tabela.

### Localização S3 configurável

O caminho padrão é apenas um placeholder e deve ser substituído por uma localização real antes de uma execução em AWS.

## Melhorias futuras

- executar a DDL realmente no Athena com `boto3`;
- adicionar observabilidade e métricas de qualidade;
- separar eventos válidos e inválidos em filas ou destinos específicos;
- implementar DLQ e política de retentativa;
- provisionar infraestrutura com Terraform ou AWS CDK;
- adicionar pipeline de CI para testes e análise estática.

## Autora

**Michele Teixeira**  
Engenharia de Dados | Data Quality | Cloud | Arquitetura de Dados
