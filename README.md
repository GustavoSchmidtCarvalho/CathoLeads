CathoLeads (Playwright)

Estrutura e uso rápido

- `src/catho_leads.py`: script principal (login + busca + coleta e exportação).
- `config/config.json`: configuração (sem credenciais reais no repositório).
- `config/config.user.json`: (opcional) sua configuração local, não versionada.
- `output/`: onde os resultados são gerados.
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

3. Configure sua execução:

- Edite `config/config.json` **ou** crie `config/config.user.json` (recomendado para não versionar credenciais).

4. Executar script

```powershell
python src\catho_leads.py
```

5. Rodar testes

```powershell
pytest -q
```

Notes

- Logs e screenshots ficam em `output/`.
- Evite commitar credenciais; prefira `config/config.user.json` (ignorado pelo git).

## Gerar executável (Windows)

Você pode gerar um `.exe` usando PyInstaller.

No PowerShell, na raiz do projeto:

```powershell
./scripts/build_exe_windows.ps1
```

O resultado fica em `dist/CathoLeads/`.

Para facilitar, você também pode dar duplo clique em `dist/CathoLeads/run_catholeads.bat` (ele executa o `.exe` e abre o log ao final).
