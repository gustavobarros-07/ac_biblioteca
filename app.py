from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from validacoes import validar_titulo, validar_categoria, CATEGORIAS_VALIDAS

APP_DB = "biblioteca.db"

app = Flask(__name__)
app.secret_key = "biblioteca123"


# ---- Banco de Dados ----
def conectar_banco():
    conn = sqlite3.connect(APP_DB)
    conn.execute(r"""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            categoria TEXT NOT NULL,
            disponivel INTEGER DEFAULT 1
        )
    """)
    return conn


# ---- Rotas ----
@app.route("/")
def index():
    return redirect(url_for("listar"))


@app.route("/listar")
def listar():
    categoria = request.args.get("categoria", "").strip()
    conn = conectar_banco()
    if categoria and validar_categoria(categoria):
        cursor = conn.execute("SELECT * FROM livros WHERE categoria = ? ORDER BY titulo", (categoria.title(),))
    else:
        cursor = conn.execute("SELECT * FROM livros ORDER BY titulo")
    livros = cursor.fetchall()
    conn.close()
    return render_template("listar.html", livros=livros, categorias=CATEGORIAS_VALIDAS, categoria_atual=categoria.title())


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        categoria = request.form.get("categoria", "").strip()

        erros = []
        if not validar_titulo(titulo):
            erros.append("Título é obrigatório!")
        if not autor:
            erros.append("Autor é obrigatório!")
        if not validar_categoria(categoria):
            erros.append("Categoria inválida!")

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("cadastrar.html", categorias=CATEGORIAS_VALIDAS, form={"titulo": titulo, "autor": autor, "categoria": categoria})

        conn = conectar_banco()
        conn.execute("INSERT INTO livros (titulo, autor, categoria) VALUES (?, ?, ?)", (titulo.title(), autor.title(), categoria.title()))
        conn.commit()
        conn.close()

        flash("Livro cadastrado com sucesso!", "success")
        return redirect(url_for("listar"))

    return render_template("cadastrar.html", categorias=CATEGORIAS_VALIDAS, form={})


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id: int):
    conn = conectar_banco()
    cursor = conn.execute("SELECT * FROM livros WHERE id=?", (id,))
    livro = cursor.fetchone()

    if not livro:
        flash("Livro não encontrado!", "danger")
        conn.close()
        return redirect(url_for("listar"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        categoria = request.form.get("categoria", "").strip()
        disponivel = 1 if request.form.get("disponivel") == "on" else 0

        erros = []
        if not validar_titulo(titulo):
            erros.append("Título é obrigatório!")
        if not autor:
            erros.append("Autor é obrigatório!")
        if not validar_categoria(categoria):
            erros.append("Categoria inválida!")

        if erros:
            for e in erros:
                flash(e, "danger")
            conn.close()
            return render_template("editar.html", livro=livro, categorias=CATEGORIAS_VALIDAS)

        conn.execute("UPDATE livros SET titulo=?, autor=?, categoria=?, disponivel=? WHERE id=?",
                     (titulo.title(), autor.title(), categoria.title(), disponivel, id))
        conn.commit()
        conn.close()

        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for("listar"))

    conn.close()
    return render_template("editar.html", livro=livro, categorias=CATEGORIAS_VALIDAS)


@app.route("/deletar/<int:id>", methods=["POST"])
def deletar(id: int):
    conn = conectar_banco()
    conn.execute("DELETE FROM livros WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Livro excluído com sucesso!", "success")
    return redirect(url_for("listar"))


# ---- Rota utilitária para inserir dados de exemplo ----
@app.route("/seed")
def seed():
    exemplos = [
        ("Clean Code", "Robert C. Martin", "Tecnologia"),
        ("Dom Casmurro", "Machado de Assis", "Ficção"),
        ("Sapiens", "Yuval Noah Harari", "História"),
        ("Uma Breve História do Tempo", "Stephen Hawking", "Ciência"),
    ]
    conn = conectar_banco()
    for t, a, c in exemplos:
        conn.execute("INSERT INTO livros (titulo, autor, categoria) VALUES (?, ?, ?)", (t, a, c))
    conn.commit()
    conn.close()
    flash("Dados de exemplo inseridos!", "info")
    return redirect(url_for("listar"))


if __name__ == "__main__":
    # Facilita rodar com: python app.py
    app.run(debug=True, host="127.0.0.1", port=5000)
