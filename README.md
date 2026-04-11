uvicorn app.main:app --reload
cd F:\ConstructAI\constructai-backend

# මේක දාන්න (වැදගත් --host 0.0.0.0)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

http://127.0.0.1:8000/swagger