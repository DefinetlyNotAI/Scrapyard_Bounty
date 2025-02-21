import uuid
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import send_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'


# Modify the receipt generation to return the receipt image in-memory
def generate_receipt_image(user_email, item_name, item_price, item_image_url):
    receipt_id = str(uuid.uuid4())[:8]  # Shortened UUID
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create an image for the receipt
    img = Image.new("RGB", (400, 400), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Change if missing
    except IOError:
        font = ImageFont.load_default()

    # Receipt text
    text = f"Receipt ID: {receipt_id}\nUser: {user_email}\nItem: {item_name}\nPrice: {item_price} scraps\nDate: {timestamp}"
    draw.text((20, 20), text, fill="black", font=font)

    # Fetch the image from the URL
    try:
        response = requests.get(item_image_url)
        if response.status_code == 200:
            item_image = Image.open(BytesIO(response.content))  # Load image from the URL content
            item_image = item_image.resize((100, 100))  # Resize if necessary
            img.paste(item_image, (20, 150))  # Paste the image onto the receipt
        else:
            raise Exception(f"Failed to fetch image: {response.status_code}")
    except Exception as e:
        print(f"Error loading item image: {e}")

    # Generate the image in memory
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io


# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop')
def shop():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item;')
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('store.html', items=items)


# API BTW
# noinspection SqlResolve
@app.route('/shop/buy', methods=['POST'])
def buy():
    item_id = request.form.get('item_id')
    user_email = request.form.get('email')

    if not item_id or not user_email:
        flash("Invalid input! Make sure all fields are filled.", "danger")
        return redirect(url_for('shop'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item WHERE id = ?;', (item_id,))
    item = cur.fetchone()

    if item and item["stock"] > 0:
        cur.execute('INSERT INTO receipt (user_email, item_id) VALUES (?, ?);', (user_email, item_id))
        conn.commit()

        # Fetch the image URL (stored in the `image` column of the database)
        item_image_url = item['image']  # Assuming this is the URL of the image

        # Generate receipt image and return as a downloadable file
        receipt_image_io = generate_receipt_image(user_email, item['name'], item['price'], item_image_url)

        # Return the image directly as a downloadable file without saving it
        return send_file(receipt_image_io, mimetype='image/png', as_attachment=True,
                         download_name=f"receipt_{str(uuid.uuid4())[:8]}.png")

    else:
        flash('Item out of stock!', 'danger')

    cur.close()
    conn.close()
    return redirect(url_for('shop'))


# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop/volunteer')
def volunteer():
    conn = get_db_connection()
    cur = conn.cursor()
    # Perform a join to fetch item details alongside receipts
    cur.execute('''
        SELECT receipt.id, receipt.user_email, receipt.status, item.name, item.price
        FROM receipt
        JOIN item ON receipt.item_id = item.id
    ''')
    receipts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.receipts.html', receipts=receipts)


# API BTW
# noinspection SqlResolve
@app.route('/shop/update_stock', methods=['POST'])
def update_stock():
    conn = get_db_connection()
    cur = conn.cursor()

    # Iterate through all posted stock values
    for key, value in request.form.items():
        if key.startswith("stock_"):  # The key will be in the form of 'stock_<item_id>'
            item_id = key.split("_")[1]
            new_stock = int(value)
            cur.execute('UPDATE item SET stock = ? WHERE id = ?;', (new_stock, item_id))

    conn.commit()
    cur.close()
    conn.close()
    flash("Stock updated successfully!", "success")
    return redirect(url_for('modify_stock'))


# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop/modify_stock', methods=['GET'])
def modify_stock():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item;')
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('modify_stock.html', items=items)


# API BTW
# noinspection SqlResolve
@app.route('/shop/cancel_receipt', methods=['POST'])
def cancel_receipt():
    receipt_id = request.form.get('receipt_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM receipt WHERE id = ?;', (receipt_id,))
    conn.commit()
    flash("Receipt cancelled!", "success")

    cur.close()
    conn.close()
    return redirect(url_for('volunteer'))


# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.form.get('image')
        description = request.form.get('description')
        stock = request.form.get('stock')

        if not name or not price or not image or not stock:
            flash("All fields except description are required!", "danger")
            return redirect(url_for('add_item'))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO item (name, price, image, description, stock) VALUES (?, ?, ?, ?, ?);',
                    (name, float(price), image, description, int(stock)))
        conn.commit()
        cur.close()
        conn.close()

        flash("Item added successfully!", "success")
        return redirect(url_for('shop'))

    return render_template('add_item.html')


# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop/missions')
def missions():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM missions;')
    mission = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('missions.html', missions=mission)


# API BTW
# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop/add_mission', methods=['GET', 'POST'])
def add_mission():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        scraps = request.form.get('scraps')

        if not name or not description or not scraps:
            flash("All fields are required!", "danger")
            return redirect(url_for('add_mission'))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO missions (name, description, scraps) VALUES (?, ?, ?);',
                    (name, description, int(scraps)))
        conn.commit()
        cur.close()
        conn.close()

        flash("Mission added successfully!", "success")
        return redirect(url_for('missions'))

    return render_template('add_mission.html')


# API BTW
# noinspection SqlResolve,PyUnresolvedReferences
@app.route('/shop/remove_mission/<int:mission_id>', methods=['GET'])
def remove_mission(mission_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM missions WHERE id = ?;', (mission_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Mission removed successfully!", "success")
    return redirect(url_for('missions'))


if __name__ == '__main__':
    app.run(debug=True)
