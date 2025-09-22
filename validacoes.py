CATEGORIAS_VALIDAS = ["Ficção", "Tecnologia", "História", "Ciência", "Outros"]

def validar_titulo(titulo: str) -> bool:
    return bool(titulo and titulo.strip())

def validar_categoria(categoria: str) -> bool:
    if not categoria:
        return False
    return categoria.title() in CATEGORIAS_VALIDAS
