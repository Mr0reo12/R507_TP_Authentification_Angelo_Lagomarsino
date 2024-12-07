from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import httpx
import uvicorn

app = FastAPI()

# Configuración de archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Agregar soporte para sesiones
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# URLs de microservicios
API_BASE_URL = "http://localhost:5009"  # Backend API
AUTH_BASE_URL = "http://localhost:5002"  # Auth API

@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    """Ruta para mostrar el formulario de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_BASE_URL}/token",  # Usar AUTH_BASE_URL aquí
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            
            # Almacenar el token en la sesión para usarlo en solicitudes posteriores
            request.session["access_token"] = token
            
            # Redirigir al usuario a la página de inicio o principal
            return RedirectResponse(url="/accueil", status_code=303)
        else:
            # Si el login falla, se lanza una excepción
            raise HTTPException(status_code=response.status_code, detail="Login failed")


@app.get("/accueil", response_class=HTMLResponse)
async def accueil(request: Request):
    """Página principal"""
    # Verificar si el usuario está autenticado
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("base.html", {"request": request})


@app.post("/resultats", response_class=HTMLResponse)
async def rechercher(
    request: Request,
    utilisateur: str = Form(None),
    livre: str = Form(None),
):
    """Buscar usuarios o libros con autenticación"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    async with httpx.AsyncClient() as client:
        if utilisateur:
            params = {"utilisateur": utilisateur}
            response = await client.get(
                f"{API_BASE_URL}/resultats", params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
        elif livre:
            params = {"livre": livre}
            response = await client.get(
                f"{API_BASE_URL}/resultats", params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
        else:
            return templates.TemplateResponse("resultats.html", {"request": request, "resultats": [], "livre": False})

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al buscar en la API")

        resultats = response.json()["resultats"]

    return templates.TemplateResponse("resultats.html", {"request": request, "resultats": resultats, "livre": True if livre else False})


@app.get("/livres", response_class=HTMLResponse)
async def liste_livres(request: Request):
    """Listar todos los libros con autenticación"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/livres",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al obtener la lista de libros de la API")

        livres = response.json()["livres"]

    return templates.TemplateResponse("livres.html", {"request": request, "livres": livres})


@app.get("/emprunts", response_class=HTMLResponse)
async def liste_emprunts(request: Request):
    """Listar préstamos actuales con autenticación"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/emprunts",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al obtener la lista de préstamos de la API")

        emprunts = response.json()["emprunts"]

    return templates.TemplateResponse("emprunts.html", {"request": request, "emprunts": emprunts})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5010)

