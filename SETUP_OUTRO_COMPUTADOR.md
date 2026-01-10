# Executar o CathoLeads em outro computador

Este guia mostra como preparar o ambiente e executar o script do projeto em outro computador.

## Pré-requisitos

- **Python 3.10+** (recomendado 3.11/3.12)
- **Git** (opcional, se for clonar o repositório)
- Acesso à internet (para instalar dependências e baixar navegadores do Playwright)

> Observação: o Playwright precisa baixar os navegadores (Chromium/Firefox/WebKit) via `playwright install`.

---

## 1) Obter o projeto

### Opção A — via Git
```bash
git clone <URL_DO_REPOSITORIO>
cd CathoLeads
```

### Opção B — via ZIP
- Baixe o ZIP do projeto
- Extraia
- Abra um terminal na pasta extraída `CathoLeads`

---

## 2) Configurar o arquivo de configuração

Edite o arquivo [config/config.json](config/config.json) e ajuste:
- `username` / `password`
- `search_term` (termo de busca)
- `search_url` (URL base da busca, sem o `q=`)
- `num_candidatos` (quantos candidatos coletar)
- `headless`:
  - `true` = não abre janela do navegador
  - `false` = abre a janela (bom para depuração)

---

## 3) Instalar dependências e executar

### Windows (PowerShell)

Na pasta do projeto:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install
python .\src\catho_leads.py
```

Se o PowerShell bloquear o `Activate.ps1`, rode (uma vez):
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Windows (CMD)

Na pasta do projeto:
```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
playwright install
python src\catho_leads.py
```

### Linux / macOS (bash/zsh)

Na pasta do projeto:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
python src/catho_leads.py
```

---

## 4) Saída gerada

O script salva os resultados em `output/candidates/`:
- `output/candidates/json/curriculos_coletados.json`
- `output/candidates/csv/curriculos_coletados.csv`
- `output/candidates/excel/curriculos_coletados.xlsx`

---

## (Opcional) Rodar testes

Se você quiser validar rapidamente a instalação:
```bash
python -m pytest -q
```

---

## Troubleshooting rápido

- **`playwright` não encontrado**: confirme que o venv está ativo (`.venv` ativado) e rode `pip install -r requirements.txt`.
- **Navegador não abre / erro de browser**: rode `playwright install` novamente.
- **Ambiente sem interface gráfica (servidor)**: use `"headless": true` no config.
