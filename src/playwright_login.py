import json
from pathlib import Path
from typing import Iterable
from datetime import datetime
from playwright.sync_api import sync_playwright


LOG_FILE = Path(__file__).resolve().parent / "playwright_login.log"


def log(msg: str) -> None:
    ts = datetime.now().isoformat(sep=" ", timespec="seconds")
    line = f"[{ts}] {msg}\n"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(line, end="")


def load_creds(path: str | Path = "../config/login_config.json") -> dict:
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


def main():
    creds = load_creds("../config/login_config.json")
    url = creds.get("url")
    username = creds.get("username")
    password = creds.get("password")
    headless = bool(creds.get("headless", True))

    if not url:
        raise ValueError("Arquivo de configuração deve conter 'url' com a página de login.")
    if not username or not password:
        raise ValueError("Arquivo de configuração deve conter 'username' e 'password'.")

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
            page.wait_for_load_state('networkidle', timeout=15000)
        except Exception:
            pass

        ok_user, user_sel = try_selectors(page, username_selectors, fill_value=username)
        ok_pass, pass_sel = try_selectors(page, password_selectors, fill_value=password)
        ok_submit, submit_sel = try_selectors(page, submit_selectors, click=True)

        log(f"username filled: {ok_user} (selector: {user_sel})")
        log(f"password filled: {ok_pass} (selector: {pass_sel})")
        log(f"submit clicked: {ok_submit} (selector: {submit_sel})")

        page.wait_for_load_state('networkidle', timeout=15000)

        if not (ok_user and ok_pass and ok_submit):
            try:
                page.screenshot(path=str(Path(__file__).resolve().parent / 'playwright_debug.png'))
            except Exception:
                pass

        browser.close()


if __name__ == "__main__":
    main()
