from PyInstaller.utils.hooks import collect_submodules

all_libraries = [
    "fastapi[standard]",
    "PyYAML",
    "pydantic",
    "ply",
    "starlette",
    "uvicorn",
    "selenium",
    "selenium-page-factory",
    "framework"
]

hidden_imports = []

for l in all_libraries:
    hidden_imports += collect_submodules(l)

print(hidden_imports)
