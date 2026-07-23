"""Descoberta e conversão de figuras para PNG.

O OJS aceita apenas .jpg/.png como arquivos dependentes de um galley HTML. Para
simplificar o upload, converte-se todas as figuras para um único formato (.png)
e usa-se apenas o nome do arquivo (sem pasta) no ``src`` do HTML.
"""

from __future__ import annotations

import os
import shutil

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".webp"}

_FIGURE_DIR_NAMES = (
    "Figures", "figures", "Figuras", "figuras",
    "Fig", "fig", "Images", "images", "Imagens", "imagens",
)


def build_stem_index(figures_dir: str) -> dict:
    """Mapeia ``nome_base_em_minúsculas -> nome_base_real`` dos arquivos de figura.

    Permite resolver referências do .tex ao arquivo real ignorando maiúsculas
    (ex.: o .tex cita ``fig6Nova`` mas o arquivo é ``fig6NOVA``). Isso é crucial:
    no Windows funciona por acaso, mas o servidor do OJS (Linux) diferencia
    maiúsculas e a imagem quebraria na publicação.
    """
    index = {}
    if not figures_dir:
        return index
    for fname in sorted(os.listdir(figures_dir)):
        full = os.path.join(figures_dir, fname)
        stem, ext = os.path.splitext(fname)
        if os.path.isfile(full) and ext.lower() in IMAGE_EXTS:
            index.setdefault(stem.lower(), stem)
    return index


def _has_images(directory: str) -> bool:
    try:
        return any(os.path.splitext(f)[1].lower() in IMAGE_EXTS for f in os.listdir(directory))
    except OSError:
        return False


def find_figures_dir(article_dir: str):
    """Localiza a pasta de figuras dentro da pasta do artigo.

    Procura por nomes comuns; se não achar, usa a primeira subpasta que contenha
    imagens; como último recurso, usa a própria pasta do artigo se ela tiver
    imagens soltas.
    """
    for name in _FIGURE_DIR_NAMES:
        candidate = os.path.join(article_dir, name)
        if os.path.isdir(candidate):
            return candidate

    for name in sorted(os.listdir(article_dir)):
        candidate = os.path.join(article_dir, name)
        if os.path.isdir(candidate) and _has_images(candidate):
            return candidate

    if _has_images(article_dir):
        return article_dir
    return None


def convert_images_to_png(figures_dir: str, output_dir: str, log=lambda _m: None):
    """Converte todas as imagens de ``figures_dir`` para PNG em ``output_dir``.

    Retorna ``(lista_de_nomes_png, avisos, dimensoes)`` onde ``dimensoes`` é
    ``{nome.png: (largura_px, altura_px)}``.
    """
    from PIL import Image

    os.makedirs(output_dir, exist_ok=True)
    converted = []
    warnings = []
    sizes = {}
    seen_stems = {}

    for fname in sorted(os.listdir(figures_dir)):
        src = os.path.join(figures_dir, fname)
        if not os.path.isfile(src):
            continue
        stem, ext = os.path.splitext(fname)
        ext = ext.lower()
        if ext not in IMAGE_EXTS:
            continue

        target_name = stem + ".png"
        if stem in seen_stems and seen_stems[stem] != fname:
            warnings.append(
                f"Conflito de nome: '{fname}' e '{seen_stems[stem]}' geram '{target_name}'. "
                f"O último processado prevalece."
            )
        seen_stems[stem] = fname
        dst = os.path.join(output_dir, target_name)

        try:
            with Image.open(src) as im:
                sizes[target_name] = im.size  # (largura, altura)
                if ext == ".png":
                    shutil.copyfile(src, dst)
                else:
                    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                        rgba = im.convert("RGBA")
                        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                        im = Image.alpha_composite(background, rgba).convert("RGB")
                    else:
                        im = im.convert("RGB")
                    im.save(dst, "PNG")
            converted.append(target_name)
            log(f"  imagem: {fname} -> {target_name}")
        except Exception as exc:  # noqa: BLE001 - reportamos ao usuário e seguimos
            warnings.append(f"Falha ao converter '{fname}': {exc}")
            log(f"  ERRO ao converter {fname}: {exc}")

    return converted, warnings, sizes
