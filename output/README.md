# Output Directory

Esta pasta contém todos os arquivos gerados pelo script de coleta de dados do Catho.

## Estrutura

```
output/
├── candidates/
│   ├── json/
│   │   └── curriculos_coletados.json    # Dados dos candidatos em formato JSON
│   ├── csv/
│   │   └── curriculos_coletados.csv     # Dados dos candidatos em formato CSV
│   └── excel/
│       └── curriculos_coletados.xlsx    # Dados dos candidatos em formato Excel
├── logs/
│   └── playwright_login.log             # Arquivo de log das execuções
└── screenshots/
    ├── playwright_debug.png             # Screenshot de debug (em caso de erro no login)
    └── search_results.png               # Screenshot da página de resultados
```

## Descrição dos Arquivos

- **curriculos_coletados.json**: Contém os dados extraídos dos currículos em formato estruturado JSON
- **curriculos_coletados.csv**: Mesmos dados em formato CSV para facilitar análise em planilhas
- **curriculos_coletados.xlsx**: Dados dos candidatos em formato Excel para melhor visualização e compatibilidade com Microsoft Office
- **playwright_login.log**: Log detalhado de todas as execuções do script
- **Screenshots**: Capturas de tela para debug e verificação visual

## Campos Coletados

Cada registro contém:
- `nome`: Nome completo do candidato
- `info_basica`: Idade, estado civil, cidade e bairro
- `telefone`: Número(s) de telefone
- `email`: Endereço de email