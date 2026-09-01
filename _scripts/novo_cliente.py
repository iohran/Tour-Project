#!/usr/bin/env python3
"""
Publica um cliente novo no Tour-Project a partir de uma pasta com o
config.json (exportado do posicionador_pontos.html) e as fotos.

Uso:
    python novo_cliente.py <pasta_com_config_e_fotos> <nome_do_cliente> [--senha SENHA] [--sem-push]

O que faz:
  1. Acha o config.json/pontos_planta.json na pasta indicada
  2. Gera uma pasta com slug aleatorio dentro do repo (ex.: joao-9f21ab)
  3. Copia o config (com clientName/password adicionados) + as fotos referenciadas
  4. git add + commit + push (a menos que --sem-push)
  5. Gera o QR code em ./Desktop/QR Codes Clientes/<slug>.png

Roda de dentro de qualquer pasta - so precisa do caminho pro repo estar
certo abaixo (REPO_DIR).
"""
import sys, os, json, shutil, secrets, subprocess, re, argparse

REPO_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Tour-Project")
BASE_URL = "https://iohran.github.io/Tour-Project"
QR_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "QR Codes Clientes")


def find_config(folder):
    for name in ("config.json", "pontos_planta.json"):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            return p
    candidates = [f for f in os.listdir(folder) if f.lower().endswith(".json")]
    if len(candidates) == 1:
        return os.path.join(folder, candidates[0])
    if len(candidates) == 0:
        raise SystemExit("Nao encontrei nenhum .json na pasta indicada.")
    raise SystemExit(
        "Tem mais de um .json na pasta (" + ", ".join(candidates) + ") - "
        "renomeia o certo pra 'config.json' e roda de novo."
    )


def slugify(name):
    base = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-") or "cliente"
    suffix = secrets.token_hex(3)
    return f"{base}-{suffix}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta", help="pasta com o config.json/pontos_planta.json + fotos")
    ap.add_argument("nome", help='nome do cliente (ex.: "Joao Silva")')
    ap.add_argument("--senha", help="senha de acesso (default: gera 4 digitos aleatorios)")
    ap.add_argument("--sem-push", action="store_true", help="nao faz git commit/push, so monta a pasta")
    args = ap.parse_args()

    pasta = os.path.abspath(args.pasta)
    if not os.path.isdir(pasta):
        raise SystemExit(f"Pasta nao encontrada: {pasta}")

    config_path = find_config(pasta)
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)

    points = cfg.get("points", [])
    if not points:
        raise SystemExit("Esse config.json nao tem nenhum ponto.")

    missing = []
    image_files = []
    for p in points:
        name = p.get("image")
        if not name:
            continue  # ponto sem foto ainda - ok, so nao entra na pasta final
        src = os.path.join(pasta, name)
        if not os.path.isfile(src):
            missing.append(name)
        else:
            image_files.append(name)

    if missing:
        raise SystemExit("Imagem(ns) referenciada(s) no config mas nao encontrada(s) na pasta: " + ", ".join(missing))
    if not image_files:
        raise SystemExit("Nenhum ponto desse config tem foto ainda - calibre pelo menos um antes de publicar.")

    senha = args.senha or str(secrets.randbelow(9000) + 1000)
    slug = slugify(args.nome)
    dest = os.path.join(REPO_DIR, slug)
    os.makedirs(dest, exist_ok=False)

    cfg["clientName"] = args.nome
    cfg["password"] = senha
    with open(os.path.join(dest, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)

    for name in image_files:
        shutil.copy2(os.path.join(pasta, name), os.path.join(dest, name))

    print(f"Pasta criada: {dest}")
    print(f"  {len(image_files)} foto(s) copiada(s), {len(points) - len(image_files)} ponto(s) ainda sem foto")

    url = f"{BASE_URL}/viewer.html?cliente={slug}"

    if not args.sem_push:
        subprocess.run(["git", "add", slug], cwd=REPO_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add client {args.nome} ({slug})"],
            cwd=REPO_DIR, check=True,
        )
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("git: commitado e enviado pro GitHub.")
    else:
        print("git: pulado (--sem-push) - lembre de dar add/commit/push manualmente.")

    try:
        import qrcode
        os.makedirs(QR_DIR, exist_ok=True)
        qr_path = os.path.join(QR_DIR, f"{slug}.png")
        qrcode.make(url, box_size=10, border=3).save(qr_path)
        print(f"QR code: {qr_path}")
    except ImportError:
        print("(qrcode nao instalado - rode: pip install qrcode[pil] - pulei a geracao do QR)")

    print()
    print("=" * 50)
    print(f"Cliente:  {args.nome}")
    print(f"Link:     {url}")
    print(f"Senha:    {senha}")
    print("=" * 50)


if __name__ == "__main__":
    main()
