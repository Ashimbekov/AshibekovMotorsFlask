from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2

app = Flask(__name__)

# Установка соединения с базой данных
conn = psycopg2.connect(
    dbname="amotors_db",
    user="postgres",
    password="nurik",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


# Определение маршрута для отображения главной страницы
@app.route('/')
def index():
    return render_template('index.html')


# Определение маршрута для отображения формы добавления авто
@app.route('/add_car_form')
def add_car_form():
    return render_template('add_cars.html')

# Маршрут для обработки данных из формы добавления автомобиля
@app.route('/add_car', methods=['POST'])
def add_car():
    if request.method == 'POST':
        brand = request.form['brand']
        model = request.form['model']
        year = request.form['year']
        color = request.form['color']
        vin = request.form['vin']
        price = request.form['price']
        availability = request.form['availability']

        # Вставляем данные в базу данных
        cur.execute("INSERT INTO Cars (brand, model, year, color, vin, price, availability) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (brand, model, year, color, vin, price, availability))
        conn.commit()
        return redirect(url_for('car_success'))

# Маршрут для страницы успешного добавления автомобиля
@app.route('/car_success')
def car_success():
    return render_template('car_success.html')

# Вспомогательные функции работы с базой данных
def create_client(first_name, last_name, middle_name, phone, iin):
    cur.execute("INSERT INTO Clients (firstName, lastName, middleName, phone, iin) VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, middle_name, phone, iin))
    conn.commit()


# Определение маршрута для отображения страницы с автомобилями
@app.route('/show_cars')
def show_cars():
    cur.execute("SELECT * FROM Cars")
    cars = cur.fetchall()
    return render_template('show_cars.html', cars=cars)


# Определение маршрута для отображения HTML формы
@app.route('/add_client_form')
def add_client_form():
    return render_template('add_clients.html')

# Маршрут для обработки данных из HTML формы
@app.route('/add_client', methods=['POST'])
def add_client():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        phone = request.form['phone']
        iin = request.form['iin']
        # Вызов функции для добавления клиента в базу данных
        create_client(first_name, last_name, middle_name, phone, iin)
        return redirect(url_for('client_success'))

# Маршрут для страницы успешного добавления клиента
@app.route('/client_success')
def client_success():
    return 'Клиент успешно добавлен!'


@app.route('/show_clients')
def show_clients():
    cur.execute("SELECT * FROM Clients")
    clients = cur.fetchall()
    return render_template('show_clients.html', clients=clients)

# Определение маршрута для отображения формы добавления авто
@app.route('/add_manager_form')
def add_manager_form():
    return render_template('add_manager.html')
# Маршрут для добавления нового менеджера
@app.route('/add_manager', methods=['POST'])
def add_manager():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        deals_count = request.form['deals_count']
        qualification = request.form['qualification']

        # Вставляем данные о менеджере в базу данных
        cur.execute("INSERT INTO Manager (firstName, lastName, middleName, dealsCount, qualification) VALUES (%s, %s, %s, %s, %s)",
                    (first_name, last_name, middle_name, deals_count, qualification))
        conn.commit()
        return redirect(url_for('manager_success'))
    
# Маршрут для страницы успешного добавления клиента
@app.route('/manager_success')
def manager_success():
    return 'Менеджер успешно добавлен!'

# Определение маршрута для отображения формы начала сделки
@app.route('/start_deal_form')
def start_deal_form():
    cur.execute("SELECT id, CONCAT(firstName, ' ', lastName) FROM Clients")
    clients = cur.fetchall()

    cur.execute("SELECT id, CONCAT(firstName, ' ', lastName) FROM Manager")
    managers = cur.fetchall()

    cur.execute("SELECT id, CONCAT(brand, ' ', model) FROM Cars WHERE availability = 'в наличии'")
    cars = cur.fetchall()

    return render_template('start_deal.html', clients=clients, managers=managers, cars=cars)

# Маршрут для обработки данных из формы начала сделки
@app.route('/start_deal', methods=['POST'])
def start_deal():
    if request.method == 'POST':
        client_id = request.form['client']
        manager_id = request.form['manager']
        car_id = request.form['car']
        date = request.form['date']
        insurance = request.form['insurance']
        equipment = request.form['equipment']
        transaction_amount = request.form['transaction_amount']
        credit = request.form['credit']

        # Вычисляем сумму транзакции
        car_price = cur.execute("SELECT price FROM Cars WHERE id = %s", (car_id,))
        if insurance == 'True':
            transaction_amount += 100  # Пример добавления стоимости страховки к сумме транзакции
        if credit == 'True':
            transaction_amount *= 1.05  # Пример добавления процента при кредите к сумме транзакции

        # Обновляем количество сделок у менеджера
        cur.execute("UPDATE Manager SET dealsCount = dealsCount + 1 WHERE id = %s", (manager_id,))
        conn.commit()

        # Вставляем данные о сделке в базу данных
        cur.execute("INSERT INTO Deals (clientId, managerId, carId, date, insurance, equipment, transactionAmount, credit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (client_id, manager_id, car_id, date, insurance, equipment, transaction_amount, credit))
        conn.commit()
        return redirect(url_for('deal_success'))

# Маршрут для страницы успешного добавления клиента
@app.route('/deal_success')
def deal_success():
    return 'Сделка успешно добавлена!'


# Маршрут для обновления доступности автомобиля
@app.route('/update_availability', methods=['POST'])
def update_availability():
    if request.method == 'POST':
        data = request.json
        car_id = data['carId']

        # Обновляем статус доступности автомобиля в базе данных
        cur.execute("UPDATE Cars SET availability = 'продано' WHERE id = %s", (car_id,))
        conn.commit()
        return jsonify({'success': True})



if __name__ == '__main__':
    app.run(debug=True)