Playwright Login Automations

Project structure and quick start

- `src/playwright_login.py`: script principal que lê `config/login_config.json` e executa o login usando Playwright.
- `config/login_config.json`: arquivo de configuração (url, username, password, headless).
- `tests/`: testes pytest básicos.

Quick start

1. Criar um virtualenv e ativar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências

```powershell
pip install -r requirements.txt
python -m playwright install
```

3. Configurar `config/login_config.json` com suas credenciais.

4. Executar script

```powershell
python src\playwright_login.py
```

5. Rodar testes

```powershell
pytest -q
```

Notes

- `playwright_login.log` e `playwright_debug.png` serão gerados ao lado do script para ajudar na depuração.
- Não inclua credenciais sensíveis no repositório público; use variáveis de ambiente ou segredos do GitHub Actions para CI.
