import json
from pathlib import Path
from typing import Iterable
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from playwright.sync_api import sync_playwright


LOG_FILE = Path(__file__).resolve().parent.parent / "output" / "logs" / "catho_leads.log"


def log(msg: str) -> None:
    ts = datetime.now().isoformat(sep=" ", timespec="seconds")
    line = f"[{ts}] {msg}\n"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(line, end="")


def load_creds(path: str | Path = "../config/config.json") -> dict:
    script_dir = Path(__file__).resolve().parent
    candidates = []
    p = Path(path)
    if p.is_absolute():
        candidates.append(p)
    else:
        candidates.append(script_dir / p)
        candidates.append(Path.cwd() / p)

    for candidate in candidates:
        if candidate.exists():
            with candidate.open(encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(
        "Credenciais não encontradas. Procurei em: " + ", ".join(str(c.resolve()) for c in candidates)
    )


def try_selectors(page, selectors: Iterable[str], fill_value: str | None = None, click: bool = False) -> tuple[bool, str | None]:
    for sel in selectors:
        log(f"Trying selector: {sel}")
        try:
            if sel.startswith("label="):
                locator = page.get_by_label(sel.split("=", 1)[1])
            elif sel.startswith("xpath=") or sel.startswith("//"):
                xpath = sel if sel.startswith("xpath=") else f"xpath={sel}"
                locator = page.locator(xpath)
            else:
                locator = page.locator(sel)

            locator.wait_for(state="visible", timeout=5000)

            if fill_value is not None:
                locator.fill(fill_value)
                log(f"Filled selector: {sel}")
            if click:
                locator.click()
                log(f"Clicked selector: {sel}")

            log(f"Selector succeeded: {sel}")
            return True, sel
        except Exception as e:
            log(f"Selector failed: {sel} -> {e}")
            continue
    log("No selector matched from provided list.")
    return False, None


def with_search_term(search_url: str, search_term: str) -> str:
    parts = urlsplit(search_url)
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)

    replaced = False
    new_pairs: list[tuple[str, str]] = []
    for key, value in query_pairs:
        if key == "q" and not replaced:
            new_pairs.append((key, search_term))
            replaced = True
        else:
            new_pairs.append((key, value))

    if not replaced:
        new_pairs.append(("q", search_term))

    new_query = urlencode(new_pairs, doseq=True, safe="[]")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def main():
    creds = load_creds("../config/config.json")
    url = creds.get("url")
    username = creds.get("username")
    password = creds.get("password")
    search_url = creds.get("search_url")
    search_term = str(creds.get("search_term", "")).strip()
    num_candidatos = int(creds.get("num_candidatos", 10))
    headless = bool(creds.get("headless", True))

    if not url:
        raise ValueError("Arquivo de configuração deve conter 'url' com a página de login.")
    if not username or not password:
        raise ValueError("Arquivo de configuração deve conter 'username' e 'password'.")
    if not search_url:
        raise ValueError("Arquivo de configuração deve conter 'search_url' com a página de busca.")
    if num_candidatos <= 0:
        raise ValueError("'num_candidatos' deve ser um número maior que 0.")

    if search_term:
        search_url = with_search_term(search_url, search_term)
        log(f"Termo de busca aplicado (q): {search_term}")

    username_selectors = [
        "xpath=/html/body/div[3]/div/main/div/div/div/div/article/div[1]/form/div[1]/div/input",
        "input[type=\"email\"]",
        "input[name*=\"email\"]",
        "input[name*=\"user\"]",
        "input[placeholder*=\"email\"]",
        "label=E-mail",
        "label=Email",
        "xpath=//input[@type=\"email\"]",
        "xpath=//input[contains(@name, 'email')]",
    ]

    password_selectors = [
        "xpath=/html/body/div[3]/div/main/div/div/div/div/article/div[1]/form/div[2]/div/input",
        "input[type=\"password\"]",
        "input[name*=\"pass\"]",
        "input[placeholder*=\"senha\"]",
        "label=Senha",
        "xpath=//input[@type=\"password\"]",
        "xpath=//input[contains(@name, 'pass')]",
    ]

    submit_selectors = [
        "xpath=/html/body/div[3]/div/main/div/div/div/div/article/div[1]/form/button",
        "button[type=\"submit\"]",
        "button:has-text(\"Entrar\")",
        "button:has-text(\"Login\")",
        "xpath=//button[contains(., 'Entrar') or contains(., 'Login')]",
    ]

    if isinstance(creds.get("username_selector"), list):
        username_selectors = creds.get("username_selector") + username_selectors
    if isinstance(creds.get("password_selector"), list):
        password_selectors = creds.get("password_selector") + password_selectors
    if isinstance(creds.get("submit_selector"), list):
        submit_selectors = creds.get("submit_selector") + submit_selectors

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=50)
        page = browser.new_page()

        page.goto(url)
        try:
            page.wait_for_load_state('domcontentloaded', timeout=6000)
        except Exception:
            pass

        # Tentativa rápida de aguardar requisições principais assentarem (sem atrasar muito)
        try:
            page.wait_for_load_state('networkidle', timeout=2000)
        except Exception:
            pass

        ok_user, user_sel = try_selectors(page, username_selectors, fill_value=username)
        ok_pass, pass_sel = try_selectors(page, password_selectors, fill_value=password)
        ok_submit, submit_sel = try_selectors(page, submit_selectors, click=True)

        log(f"username filled: {ok_user} (selector: {user_sel})")
        log(f"password filled: {ok_pass} (selector: {pass_sel})")
        log(f"submit clicked: {ok_submit} (selector: {submit_sel})")

        # Aguardar um tempo para a página processar o login
        try:
            page.wait_for_load_state('domcontentloaded', timeout=10000)
        except Exception as e:
            log(f"Wait for load state failed: {e}")

        if not (ok_user and ok_pass and ok_submit):
            try:
                page.screenshot(path=str(Path(__file__).resolve().parent.parent / 'output' / 'screenshots' / 'playwright_debug.png'))
            except Exception:
                pass
        else:
            # Aguardar mais tempo para garantir que o login foi processado
            import time
            log("Aguardando 5 segundos para completar o login...")
            time.sleep(5)
            
            # Navegar para a página de busca após login bem-sucedido
            log(f"Navegando para: {search_url}")
            try:
                page.goto(search_url, timeout=30000, wait_until='load')
            except Exception as e:
                log(f"Erro ao navegar para search_url: {e}")
            
            try:
                page.wait_for_load_state('domcontentloaded', timeout=10000)
            except Exception:
                pass
            
            log("Página de busca carregada com sucesso!")
            
            # Ordenar por Data de Atualização antes de coletar
            try:
                log("Ordenando por Data de Atualização...")
                # Clicar no botão de ordenação (Relevância)
                sort_button_selectors = [
                    'button[aria-label="open menu"]',
                    '.Dropdown__DropInput-sc-xoew8d-0',
                    'button:has-text("Relevância")',
                    '#dropdown-204762'
                ]
                
                sort_button = None
                for sel in sort_button_selectors:
                    try:
                        locator = page.locator(sel).first
                        locator.wait_for(state="visible", timeout=3000)
                        sort_button = locator
                        log(f"Botão de ordenação encontrado com seletor: {sel}")
                        break
                    except Exception:
                        continue
                
                if sort_button:
                    sort_button.click()
                    page.wait_for_timeout(1000)  # Aguardar o menu aparecer
                    
                    # Selecionar "Data de Atualização"
                    update_options = [
                        'text=Data de Atualização',
                        'text=/Data de Atualização/',
                        'li:has-text("Data de Atualização")',
                        'button:has-text("Data de Atualização")'
                    ]
                    
                    option_found = False
                    for opt_sel in update_options:
                        try:
                            option = page.locator(opt_sel).first
                            option.wait_for(state="visible", timeout=3000)
                            option.click()
                            log(f"Opção 'Data de Atualização' selecionada com seletor: {opt_sel}")
                            option_found = True
                            break
                        except Exception:
                            continue
                    
                    if option_found:
                        # Aguardar a página recarregar com a nova ordenação (pode ser AJAX)
                        try:
                            page.wait_for_load_state('networkidle', timeout=5000)
                        except Exception:
                            log("Página não recarregou completamente, mas ordenação pode ter sido aplicada via AJAX")
                        log("Ordenação por Data de Atualização aplicada com sucesso!")
                    else:
                        log("Opção 'Data de Atualização' não encontrada, continuando sem ordenação")
                else:
                    log("Botão de ordenação não encontrado, continuando sem ordenação")
                
            except Exception as e:
                log(f"Erro ao ordenar por Data de Atualização: {e}")
            
            # Coletar dados dos currículos
            try:
                def go_to_next_page() -> bool:
                    next_selectors = [
                        'a[rel="next"]',
                        'button:has-text("Próxima")',
                        'a:has-text("Próxima")',
                        'button[aria-label*="Próxima"]',
                        'a[aria-label*="Próxima"]',
                    ]

                    for sel in next_selectors:
                        try:
                            locator = page.locator(sel).first
                            if locator.count() == 0:
                                continue
                            locator.wait_for(state="visible", timeout=2000)

                            aria_disabled = locator.get_attribute("aria-disabled")
                            disabled = locator.get_attribute("disabled")
                            if aria_disabled == "true" or disabled is not None:
                                continue

                            try:
                                locator.scroll_into_view_if_needed()
                            except Exception:
                                pass

                            log(f"Indo para próxima página (seletor: {sel})")
                            try:
                                with page.expect_navigation(wait_until="domcontentloaded", timeout=15000):
                                    locator.click()
                            except Exception:
                                locator.click()
                                try:
                                    page.wait_for_load_state('networkidle', timeout=5000)
                                except Exception:
                                    pass
                                page.wait_for_timeout(1000)
                            return True
                        except Exception:
                            continue

                    return False

                dados_coletados = []
                vistos: set[str] = set()
                pagina_atual = 1

                while len(dados_coletados) < num_candidatos:
                    # Aguardar que os currículos carreguem
                    page.wait_for_selector('article', timeout=10000)
                    artigos = page.locator('article')
                    total_artigos = artigos.count()
                    log(f"Página {pagina_atual}: encontrados {total_artigos} artigos")

                    coletados_nesta_pagina = 0

                    for idx in range(total_artigos):
                        if len(dados_coletados) >= num_candidatos:
                            break

                        curriculo = artigos.nth(idx)

                        # Verificar se é um currículo (tem h2 com link)
                        if curriculo.locator('h2 a').count() == 0:
                            continue

                        try:
                            nome = curriculo.locator('h2 a').inner_text().strip()
                        except Exception:
                            continue

                        href = ""
                        try:
                            href = (curriculo.locator('h2 a').get_attribute('href') or '').strip()
                        except Exception:
                            href = ""

                        chave = href or nome
                        if chave in vistos:
                            continue
                        vistos.add(chave)

                        try:
                            # Tentar diferentes seletores para info_basica
                            info_basica = ""
                            try:
                                # Primeiro tentar o seletor original
                                info_elem = curriculo.locator('p.sc-eZkCL')
                                if info_elem.count() > 0:
                                    info_basica = info_elem.inner_text().strip()
                                else:
                                    # Tentar xpath
                                    info_elem = curriculo.locator('xpath=.//p[contains(@class, "sc-eZkCL")]')
                                    if info_elem.count() > 0:
                                        info_basica = info_elem.inner_text().strip()
                                    else:
                                        # Tentar procurar por texto que contenha "anos"
                                        info_elem = curriculo.locator('text=/\\d+ anos/').first
                                        if info_elem.count() > 0:
                                            info_basica = info_elem.inner_text().strip()
                            except Exception as e:
                                log(f"Erro info_basica {nome}: {e}")

                            log(f"Debug - Nome: {nome}, Info básica: '{info_basica}'")

                            # Tentar coletar telefone
                            telefone = ""
                            try:
                                botao_telefone = curriculo.locator('button:has-text("Ver telefone")')
                                if botao_telefone.count() > 0:
                                    botao_telefone.click()
                                    # Aguardar um pouco para o conteúdo aparecer
                                    page.wait_for_timeout(2000)
                                    # Procurar por elementos que possam conter o telefone dentro do currículo
                                    telefone_element = curriculo.locator('text=/\\(\\d{2}\\) \\d{4,5}-\\d{4}/').first
                                    if telefone_element.count() > 0:
                                        telefone = telefone_element.inner_text().strip()
                                    else:
                                        # Tentar na página toda
                                        telefone_element = page.locator('text=/\\(\\d{2}\\) \\d{4,5}-\\d{4}/').first
                                        if telefone_element.count() > 0:
                                            telefone = telefone_element.inner_text().strip()
                            except Exception as e:
                                log(f"Erro telefone {nome}: {e}")

                            # Tentar coletar email
                            email = ""
                            try:
                                botao_email = curriculo.locator('button:has-text("Ver e-mail")')
                                if botao_email.count() > 0:
                                    botao_email.click()
                                    # Aguardar um pouco para o conteúdo aparecer
                                    page.wait_for_timeout(2000)
                                    # Procurar por elementos que contenham @ dentro do currículo
                                    email_element = curriculo.locator('text=/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/').first
                                    if email_element.count() > 0:
                                        email = email_element.inner_text().strip()
                                    else:
                                        # Tentar na página toda
                                        email_element = page.locator('text=/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/').first
                                        if email_element.count() > 0:
                                            email = email_element.inner_text().strip()
                            except Exception as e:
                                log(f"Erro email {nome}: {e}")

                            dados_coletados.append({
                                'nome': nome,
                                'info_basica': info_basica,
                                'telefone': telefone,
                                'email': email
                            })

                            coletados_nesta_pagina += 1
                            log(f"Currículo {len(dados_coletados)}: {nome}")

                        except Exception as e:
                            log(f"Erro ao extrair currículo {len(dados_coletados)+1}: {e}")

                    if len(dados_coletados) >= num_candidatos:
                        break

                    if coletados_nesta_pagina == 0:
                        log("Nenhum currículo novo coletado nesta página (possível repetição/HTML diferente)")

                    if not go_to_next_page():
                        log("Não encontrei próxima página; encerrando paginação")
                        break

                    pagina_atual += 1
                
                # Salvar dados em JSON
                import json
                output_dir = Path(__file__).resolve().parent.parent / "output" / "candidates"
                (output_dir / "json").mkdir(parents=True, exist_ok=True)
                (output_dir / "csv").mkdir(parents=True, exist_ok=True)
                (output_dir / "excel").mkdir(parents=True, exist_ok=True)
                json_file = output_dir / "json" / 'curriculos_coletados.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(dados_coletados, f, ensure_ascii=False, indent=2)
                
                # Também salvar em CSV para facilitar análise
                import csv
                csv_file = output_dir / "csv" / 'curriculos_coletados.csv'
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    if dados_coletados:
                        fieldnames = ['nome', 'info_basica', 'telefone', 'email']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(dados_coletados)
                
                # Salvar em Excel para melhor visualização
                import pandas as pd
                excel_file = output_dir / "excel" / 'curriculos_coletados.xlsx'
                if dados_coletados:
                    df = pd.DataFrame(dados_coletados)
                    df.to_excel(excel_file, index=False, engine='openpyxl')
                
                log(f"Coletados {len(dados_coletados)} currículos e salvos em JSON, CSV e Excel")
                
            except Exception as e:
                log(f"Erro ao coletar dados: {e}")
            
            try:
                page.screenshot(path=str(Path(__file__).resolve().parent.parent / 'output' / 'screenshots' / 'search_results.png'))
            except Exception:
                pass

        browser.close()


if __name__ == "__main__":
    main()
