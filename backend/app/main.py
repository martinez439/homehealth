from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.crud import router as api_router
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI(title='Home Health MVP API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(api_router, prefix='/api')

@app.get('/api/health')
def health_check():
    return {'status': 'ok'}
