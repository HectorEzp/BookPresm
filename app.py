import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambiar-esta-clave")


def get_conn():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        connect_timeout=5,
    )


def query(sql, params=(), fetch="all", commit=False):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if commit:
                conn.commit()
                return cur.lastrowid
            return cur.fetchall() if fetch == "all" else cur.fetchone()
    finally:
        conn.close()


# ---------------------------------------------------------------- PRÉSTAMOS
@app.route("/")
def prestamos():
    filas = query(
        """SELECT p.id_prestamo, l.titulo, p.nombre_usuario,
                  p.fecha_prestamo, p.fecha_devolucion, p.estado
           FROM prestamos p JOIN libros l ON l.id_libro = p.id_libro
           ORDER BY p.id_prestamo DESC"""
    )
    return render_template("prestamos.html", prestamos=filas)


@app.route("/prestamos/nuevo", methods=["GET", "POST"])
def prestamo_nuevo():
    libros = query("SELECT id_libro, titulo FROM libros ORDER BY titulo")
    if request.method == "POST":
        f = request.form
        query(
            """INSERT INTO prestamos
               (id_libro, nombre_usuario, fecha_prestamo, fecha_devolucion, estado)
               VALUES (%s, %s, %s, %s, %s)""",
            (f["id_libro"], f["nombre_usuario"].strip(), f["fecha_prestamo"],
             f["fecha_devolucion"] or None, f["estado"]),
            commit=True,
        )
        flash("Préstamo registrado correctamente.", "ok")
        return redirect(url_for("prestamos"))
    return render_template("prestamo_form.html", prestamo=None, libros=libros)


@app.route("/prestamos/<int:id_prestamo>/editar", methods=["GET", "POST"])
def prestamo_editar(id_prestamo):
    libros = query("SELECT id_libro, titulo FROM libros ORDER BY titulo")
    if request.method == "POST":
        f = request.form
        query(
            """UPDATE prestamos SET id_libro=%s, nombre_usuario=%s,
               fecha_prestamo=%s, fecha_devolucion=%s, estado=%s
               WHERE id_prestamo=%s""",
            (f["id_libro"], f["nombre_usuario"].strip(), f["fecha_prestamo"],
             f["fecha_devolucion"] or None, f["estado"], id_prestamo),
            commit=True,
        )
        flash("Préstamo actualizado.", "ok")
        return redirect(url_for("prestamos"))
    p = query("SELECT * FROM prestamos WHERE id_prestamo=%s", (id_prestamo,), fetch="one")
    if not p:
        flash("El préstamo no existe.", "error")
        return redirect(url_for("prestamos"))
    return render_template("prestamo_form.html", prestamo=p, libros=libros)


@app.route("/prestamos/<int:id_prestamo>/eliminar", methods=["POST"])
def prestamo_eliminar(id_prestamo):
    query("DELETE FROM prestamos WHERE id_prestamo=%s", (id_prestamo,), commit=True)
    flash("Préstamo eliminado.", "ok")
    return redirect(url_for("prestamos"))


# ------------------------------------------------------------------- LIBROS
@app.route("/libros")
def libros():
    filas = query("SELECT * FROM libros ORDER BY id_libro DESC")
    return render_template("libros.html", libros=filas)


@app.route("/libros/nuevo", methods=["GET", "POST"])
def libro_nuevo():
    if request.method == "POST":
        f = request.form
        try:
            query(
                """INSERT INTO libros (titulo, autor, isbn, ejemplares_disponibles)
                   VALUES (%s, %s, %s, %s)""",
                (f["titulo"].strip(), f["autor"].strip(), f["isbn"].strip(),
                 f["ejemplares_disponibles"]),
                commit=True,
            )
            flash("Libro registrado correctamente.", "ok")
            return redirect(url_for("libros"))
        except pymysql.err.IntegrityError:
            flash("Ya existe un libro con ese ISBN.", "error")
    return render_template("libro_form.html", libro=None)


@app.route("/libros/<int:id_libro>/editar", methods=["GET", "POST"])
def libro_editar(id_libro):
    if request.method == "POST":
        f = request.form
        try:
            query(
                """UPDATE libros SET titulo=%s, autor=%s, isbn=%s,
                   ejemplares_disponibles=%s WHERE id_libro=%s""",
                (f["titulo"].strip(), f["autor"].strip(), f["isbn"].strip(),
                 f["ejemplares_disponibles"], id_libro),
                commit=True,
            )
            flash("Libro actualizado.", "ok")
            return redirect(url_for("libros"))
        except pymysql.err.IntegrityError:
            flash("Ya existe otro libro con ese ISBN.", "error")
    l = query("SELECT * FROM libros WHERE id_libro=%s", (id_libro,), fetch="one")
    if not l:
        flash("El libro no existe.", "error")
        return redirect(url_for("libros"))
    return render_template("libro_form.html", libro=l)


@app.route("/libros/<int:id_libro>/eliminar", methods=["POST"])
def libro_eliminar(id_libro):
    try:
        query("DELETE FROM libros WHERE id_libro=%s", (id_libro,), commit=True)
        flash("Libro eliminado.", "ok")
    except pymysql.err.IntegrityError:
        flash("No se puede eliminar: el libro tiene préstamos asociados.", "error")
    return redirect(url_for("libros"))


@app.errorhandler(pymysql.err.OperationalError)
def db_error(e):
    return render_template("error.html", detalle=str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
