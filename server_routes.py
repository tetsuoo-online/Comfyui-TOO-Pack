"""
Server routes pour SmartImageLoader
À ajouter dans __init__.py ou dans un fichier séparé importé par __init__.py
"""
import server
import os
from aiohttp import web

def strip_path(path):
    """Retire les guillemets et espaces"""
    path = path.strip()
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    return path

def is_safe_path(path):
    """Vérifie que le chemin est sûr (pas de ..)"""
    try:
        abs_path = os.path.abspath(path)
        # Vérifier qu'on ne remonte pas dans l'arborescence
        return os.path.exists(abs_path)
    except:
        return False

@server.PromptServer.instance.routes.get("/too/view/image")
async def view_image(request):
    """Route pour afficher les images avec type=path"""
    query = request.rel_url.query

    if "filename" not in query:
        return web.Response(status=400, text="Missing filename parameter")

    filename = query["filename"]
    file_type = query.get("type", "output")

    if file_type == "path":
        # Chemin absolu - cas spécial
        filepath = strip_path(filename)

        if not is_safe_path(filepath):
            return web.Response(status=403, text="Invalid or unsafe path")

        if not os.path.isfile(filepath):
            return web.Response(status=404, text="File not found")

        # Retourner le fichier
        return web.FileResponse(filepath)

    else:
        # Utiliser la route standard de ComfyUI
        return web.Response(status=400, text="Only type=path is supported")

print("TOO-Pack: Custom image view route registered at /too/view/image")
