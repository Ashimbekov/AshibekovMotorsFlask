from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="AshimbekovMotors_db",
    user="postgres",
    password="nurik",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/deals')
def deals():
    return render_template('deals.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/cars')
def cars():
    return render_template('cars.html')

@app.route('/add_car_form')
def add_car_form():
    return render_template('add_cars.html')

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

        cur.execute("INSERT INTO Cars (brand, model, year, color, vin, price, availability) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (brand, model, year, color, vin, price, availability))
        conn.commit()
        return redirect(url_for('car_success'))

@app.route('/car_success')
def car_success():
    return render_template('car_success.html')

def create_client(first_name, last_name, middle_name, phone, iin):
    cur.execute("INSERT INTO Clients (firstName, lastName, middleName, phone, iin) VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, middle_name, phone, iin))
    conn.commit()


@app.route('/show_cars')
def show_cars():
    cur.execute("SELECT * FROM Cars")
    cars = cur.fetchall()
    return render_template('show_cars.html', cars=cars)


@app.route('/add_client_form')
def add_client_form():
    return render_template('add_clients.html')

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

@app.route('/client_success')
def client_success():
    return render_template('client_success.html')

@app.route('/show_clients')
def show_clients():
    cur.execute("SELECT * FROM Clients")
    clients = cur.fetchall()
    return render_template('show_clients.html', clients=clients)

@app.route('/add_manager_form')
def add_manager_form():
    return render_template('add_manager.html')

@app.route('/add_manager', methods=['POST'])
def add_manager():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        deals_count = request.form['deals_count']
        qualification = request.form['qualification']

        cur.execute("INSERT INTO Manager (firstName, lastName, middleName, dealsCount, qualification) VALUES (%s, %s, %s, %s, %s)",
                    (first_name, last_name, middle_name, deals_count, qualification))
        conn.commit()
        return redirect(url_for('manager_success'))
    
@app.route('/manager_success')
def manager_success():
    return render_template('manager_success.html')



@app.route('/select_car', methods=['GET'])
def select_car():
    cars = cur.execute("SELECT id, brand, model FROM Cars")
    cars = cur.fetchall() if cur else []
    return render_template('select_car.html', cars=cars)

@app.route('/select_car', methods=['POST'])
def select_car_post():
    if request.method == 'POST':
        car_id = request.form['car_id']  
        return redirect(url_for('add_car_attributes', car_id=car_id))

@app.route('/add_car_attributes/<int:car_id>', methods=['GET', 'POST'])
def add_car_attributes(car_id):
    if request.method == 'POST':
        seats_count = request.form['seats_count']
        trunk_volume = request.form['trunk_volume']
        horse_power = request.form['horse_power']
        engine_volume = request.form['engine_volume']
        car_type = request.form['car_type']

        cur.execute("INSERT INTO CarAttributes (carId, seatsCount, trunkVolume, horsePower, engineVolume, carType) VALUES (%s, %s, %s, %s, %s, %s)",
                    (car_id, seats_count, trunk_volume, horse_power, engine_volume, car_type))
        conn.commit()

        return redirect(url_for('carAttributes_success')) # TODO добавить car_success

    return render_template('add_car_attributes.html', car_id=car_id)

# TODO Добавить условие если в выбранном автомобили уже есть значение то, выдать предупрждение что поля заполнены

@app.route('/carAttributes_success')
def carAttributes_success():
    return 'Атрибуты автомобиля успешно добавлены!'


@app.route('/show_car_attributes/<int:car_id>')
def show_car_details(car_id):
    cur.execute("SELECT * FROM CarAttributes WHERE carId = %s", (car_id,))
    attributes = cur.fetchone()

    cur.execute("SELECT * FROM CarFeatures WHERE carId = %s", (car_id,))
    features = cur.fetchone()

    cur.execute("SELECT brand, model FROM Cars WHERE id = %s", (car_id,))
    car_name = cur.fetchone()

    return render_template('show_car_attributes.html', attributes=attributes, features=features, car_name=car_name)

# TODO Сделал сверху костыль, продумать потом надо как переделать
# @app.route('/show_car_attributes/<int:car_id>')
# def show_car_attributes(car_id):
#     cur.execute("SELECT * FROM CarAttributes WHERE carId = %s", (car_id,))
#     attributes = cur.fetchone()
#     print(attributes)
#     # какие данные должны быть
#     # attributes = {
#     #     'seats_count': 5,
#     #     'trunk_volume': '500 л',
#     #     'horse_power': '200 л.с.',
#     #     'engine_volume': '2.0 л',
#     #     'car_type': 'Седан'
#     # }
#     attributes_dict = {
#         'carId': attributes[0],
#         'seatsCount': attributes[1],
#         'trunkVolume': attributes[2],
#         'horsePower': attributes[3],
#         'engineVolume': attributes[4],
#         'carType': attributes[5]
#     }

#     for key, value in attributes_dict.items():
#         print(f"{key}: {value}")

#     return render_template('show_car_attributes.html', attributes=attributes)

# # @app.route('/show_car_attributes/<int:car_id>')
# @app.route('/show_car_features/<int:car_id>')
# def show_car_features(car_id):
#     cur.execute("SELECT * FROM CarFeatures WHERE carId = %s", (car_id,))
#     features = cur.fetchone()

#     # return render_template('show_car_features.html', features=features)
#     return render_template('show_car_attributes.html', features=features)

@app.route('/add_car_params', methods=['POST'])
def add_car_params():
    if request.method == 'POST':
        car_id = request.form['car']

        car_info = cur.execute("SELECT * FROM Cars WHERE id = %s", (car_id,)).fetchone()

        return render_template('add_car_params.html', car_info=car_info)


# Сделки----------------------------------------
@app.route('/start_deal_form')
def start_deal_form():
    cur.execute("SELECT id, CONCAT(firstName, ' ', lastName) FROM Clients")
    clients = cur.fetchall()

    cur.execute("SELECT id, CONCAT(firstName, ' ', lastName) FROM Manager")
    managers = cur.fetchall()

    cur.execute("SELECT id, CONCAT(brand, ' ', model) FROM Cars WHERE availability = 'в наличии'")
    cars = cur.fetchall()

    return render_template('start_deal.html', clients=clients, managers=managers, cars=cars)


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

        # Костыльная транзакция процентов #TODO Проработать сумму продажи
        car_price = cur.execute("SELECT price FROM Cars WHERE id = %s", (car_id,))
        if insurance == 'True':
            transaction_amount += 100 
        if credit == 'True':
            transaction_amount *= 1.05 

        # Обновление количества сделок менеджера
        cur.execute("UPDATE Manager SET dealsCount = dealsCount + 1 WHERE id = %s", (manager_id,))
        conn.commit()


        cur.execute("INSERT INTO Deals (clientId, managerId, carId, date, insurance, equipment, transactionAmount, credit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (client_id, manager_id, car_id, date, insurance, equipment, transaction_amount, credit))
        conn.commit()
        return redirect(url_for('deal_success'))


@app.route('/deal_success')
def deal_success():
    return 'Сделка успешно добавлена!'



# TODO Проработать обновление статуса автомобиля ПРОДАН/В ОЖИДАНИИ/ДОСТУПЕН
@app.route('/update_availability', methods=['POST'])
def update_availability():
    if request.method == 'POST':
        data = request.json
        car_id = data['carId']

        cur.execute("UPDATE Cars SET availability = 'продано' WHERE id = %s", (car_id,))
        conn.commit()
        return jsonify({'success': True})



if __name__ == '__main__':
    app.run(debug=True)