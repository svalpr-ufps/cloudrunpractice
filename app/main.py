from fastapi import FastAPI, HTTPException, Request
from google.cloud import firestore
import os


# Carga de variables de entorno
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
database_id = os.environ["FIRESTORE_DATABASE"]

# Inicialización del cliente de Firestore
db = firestore.Client(project=project_id, database=database_id)

# Configuración de la app FastAPI
app = FastAPI(title="Notas con Firestore real")


# Endpoint: Listar todas las notas
# Método: GET /notes
@app.get("/notes")
async def list_notes():
    docs = db.collection("notes").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


# Endpoint: Crear una nueva nota
# Método: POST /notes
@app.post("/notes")
async def create_note(req: Request):
    data = await req.json()
    
    if not data.get("title") or not data.get("content"):
        raise HTTPException(status_code=400, detail="Faltan 'title' o 'content'")
    
    ref = db.collection("notes").document()
    ref.set({
        "title": data["title"],
        "content": data["content"],
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    return {"id": ref.id}


# Endpoint: Actualizar una nota
# Método: PUT /notes/{note_id}
# Endpoint: Actualizar una nota
# Método: PUT /notes/{note_id}
@app.put("/notes/{note_id}")
async def update_note(note_id: str, req: Request):
    try:
        data = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {str(e)}")
    
    if not data.get("title") or not data.get("content"):
        raise HTTPException(status_code=400, detail="Faltan 'title' o 'content'")
    
    # Verificar que el documento existe
    doc = db.collection("notes").document(note_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    
    db.collection("notes").document(note_id).update({
        "title": data["title"],
        "content": data["content"]
    })
    
    return {"id": note_id, "message": "Nota actualizada"}



# Endpoint: Eliminar una nota
# Método: DELETE /notes/{note_id}
@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    db.collection("notes").document(note_id).delete()
    return {"id": note_id, "message": "Nota eliminada"}
