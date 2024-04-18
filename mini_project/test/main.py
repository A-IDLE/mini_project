
# from dotenv import load_dotenv
# from pathlib import Path

# from fastapi import FastAPI, Request
# from fastapi.templating import Jinja2Templates

# from app.routers.routers import router


# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

# app = FastAPI()

# # Mount the router
# app.include_router(router)

# # html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")


# @app.get("/")
# def home(request: Request):
#     return templates.TemplateResponse("index.html",
#                                       {"request": request})


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="localhost", port=8000)
