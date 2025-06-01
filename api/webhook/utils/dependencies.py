from api.infrastructure.database.repo.requests import RequestsRepo

_repo_instance: RequestsRepo | None = None

def set_repo_instance(repo: RequestsRepo):
    global _repo_instance
    _repo_instance = repo

def get_repo_instance() -> RequestsRepo:
    if _repo_instance is None:
        raise RuntimeError("❌ Репозиторий не инициализирован. Вызовите set_repo_instance при старте.")
    return _repo_instance