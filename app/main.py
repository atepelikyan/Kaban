from fastapi import FastAPI
from app.routes import auth, board, ticket, user

app = FastAPI()
app.include_router(auth.router)
app.include_router(board.router)
app.include_router(ticket.router)
app.include_router(user.router)


@app.get("/")
async def main():
    return "Welcome to kaban!"


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


# uvicorn, imports, service, repository, add router
# tickets - create, get, update, delete, assign to, see one, see all, see your, see assigned to someone, mark
