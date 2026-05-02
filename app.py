# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# ===============================
# 上传图片资料夹
# ===============================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 自动创建资料夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================
# 数据库连接
# ===============================

def get_conn():
    host = os.environ.get("DB_HOST")
    db = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    print("DB_HOST =", host)

    if not host:
        raise Exception("DB_HOST 没有设置！Render环境变量没生效")

    return psycopg2.connect(
        host=host,
        database=db,
        user=user,
        password=password,
        port="5432"
    )

# ===============================
# 首页
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")

# ===============================
# 获取全部商品
# ===============================
@app.route("/products")
def products():
    cur = get_conn().cursor()


    cur.execute("""
        SELECT id,name,price,tipo,image,description
        FROM products
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    cur.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "tipo": row[3],
            "image": "/static/uploads/" + row[4],
            "description": row[5]
        })

    return jsonify(data)

# ===============================
# 单个商品
# ===============================
@app.route("/products/<int:id>")
def product_detail(id):

    cur = get_conn().cursor()
    cur.execute("""
        SELECT id,name,price,tipo,image,description
        FROM products
        WHERE id=%s
    """, (id,))

    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error":"not found"}),404

    return jsonify({
        "id": row[0],
        "name": row[1],
        "price": row[2],
        "tipo": row[3],
        "image": "/static/uploads/" + row[4],
        "description": row[5]
    })

# ===============================
# 新增商品（重点）
# ===============================
@app.route("/add-product", methods=["POST"])
def add_product():

    name = request.form["name"]
    price = request.form["price"]
    tipo = request.form["tipo"]
    description = request.form["description"]

    file = request.files["image"]

    filename = secure_filename(file.filename)

    # 避免重复档名
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    count = 1
    while os.path.exists(filepath):
        filename = f"{count}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        count += 1

    file.save(filepath)

    cur = get_conn().cursor()

    cur.execute("""
        INSERT INTO products(name,price,tipo,image,description)
        VALUES(%s,%s,%s,%s,%s)
    """, (
        name,
        price,
        tipo,
        filename,
        description
    ))

    cur = get_conn().cursor()
    cur.close()

    return jsonify({"message":"上传成功"})

# ===============================
# 删除商品
# ===============================
@app.route("/delete-product/<int:id>", methods=["DELETE"])
def delete_product(id):

    cur = get_conn().cursor()

    # 先查图片名
    cur.execute("SELECT image FROM products WHERE id=%s",(id,))
    row = cur.fetchone()

    if row:
        filename = row[0]
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        if os.path.exists(path):
            os.remove(path)

    cur.execute("DELETE FROM products WHERE id=%s",(id,))
    cur = get_conn().cursor()
    cur.close()

    return jsonify({"message":"删除成功"})

# ===============================
# 编辑商品
# ===============================
@app.route("/edit-product/<int:id>", methods=["PUT"])
def edit_product(id):

    name = request.form["name"]
    price = request.form["price"]
    tipo = request.form["tipo"]
    description = request.form["description"]

    cur = get_conn().cursor()

    # 查旧图片
    cur.execute("SELECT image FROM products WHERE id=%s",(id,))
    old = cur.fetchone()

    filename = old[0]

    # 如果有新图片
    if "image" in request.files:

        file = request.files["image"]

        if file.filename != "":

            old_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            if os.path.exists(old_path):
                os.remove(old_path)

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    cur.execute("""
        UPDATE products
        SET name=%s,
            price=%s,
            tipo=%s,
            image=%s,
            description=%s
        WHERE id=%s
    """, (
        name,
        price,
        tipo,
        filename,
        description,
        id
    ))

    cur = get_conn().cursor()
    cur.close()

    return jsonify({"message":"编辑成功"})

# ===============================
# 启动
# ===============================
if __name__ == "__main__":
    app.run()