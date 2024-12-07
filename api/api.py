from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import sqlite3
import uvicorn

# Configuración para JWT
SECRET_KEY = "secret-key-for-jwt"  # Debe coincidir con el servicio Auth
ALGORITHM = "HS256"  # Algoritmo usado para firmar los tokens

# URL del servicio Auth para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:5002/token")

def get_user_from_db(username: str):
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return user
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

def authenticate_user(username: str, password: str):
    user = get_user_from_db(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

# Función para verificar el token JWT
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid token: no subject found"
            )
        return username
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

app = FastAPI()

@app.get("/")
async def accueil():
    """Accueil"""
    return {"message": "Bienvenue à l'API de gestion de bibliothèque. Utilisez les points d'accès pour interagir."}

@app.get("/resultats")
async def rechercher(
    utilisateur: str = Query(None), livre: str = Query(None), username: str = Depends(verify_token)
):
    """Recherche d'utilisateurs ou de livres"""
    resultats = []
    conn = get_db_connection()

    try:
        if utilisateur:
            # Recherche d'utilisateurs correspondant au nom ou à l'identifiant
            user_query = conn.execute(
                "SELECT * FROM utilisateurs WHERE nom_utilisateur LIKE ? OR id = ?",
                (f"%{utilisateur}%", utilisateur)
            ).fetchall()
            resultats = [dict(user) for user in user_query]

        elif livre:
            # Recherche de livres correspondant au titre
            livre_query = conn.execute(
                "SELECT * FROM livres WHERE titre LIKE ?",
                (f"%{livre}%",)
            ).fetchall()
            resultats = [dict(livre) for livre in livre_query]

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

    if not resultats:
        raise HTTPException(status_code=404, detail="Aucun résultat trouvé.")
    
    return {"resultats": resultats}

@app.get("/livres")
async def liste_livres(username: str = Depends(verify_token)):
    """Lister tous les livres"""
    conn = get_db_connection()

    try:
        livres = conn.execute("SELECT * FROM livres").fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

    if not livres:
        raise HTTPException(status_code=404, detail="Aucun livre trouvé.")

    return {"livres": [dict(livre) for livre in livres]}

@app.get("/emprunts")
async def liste_emprunts(username: str = Depends(verify_token)):
    """Liste des prêts en cours"""
    conn = get_db_connection()

    try:
        emprunts = conn.execute("SELECT * FROM livres WHERE emprunteur_id IS NOT NULL").fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

    if not emprunts:
        raise HTTPException(status_code=404, detail="Aucun prêt trouvé.")

    return {"emprunts": [dict(emprunt) for emprunt in emprunts]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5009)

