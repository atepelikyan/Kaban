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
