from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2
from datetime import date
import pdfkit

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
    cur.execute("SELECT SUM(dealsCount) FROM Manager")
    total_deals = cur.fetchone()[0]

    # Получаем текущую дату
    today = date.today()

    cur.execute("SELECT COUNT(*) FROM deals WHERE date = %s", (today,))
    deals_today = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM deals WHERE date = CURRENT_DATE - INTERVAL '1 day';")
    deals_yesterday = cur.fetchone()[0]
    return render_template('index.html', total_deals=total_deals, deals_today=deals_today, deals_yesterday=deals_yesterday)


@app.route('/deals')
def deals():
    return render_template('deals.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/cars')
def cars():
    return render_template('cars.html')

@app.route('/managers')
def managers():
    return render_template('managers.html')

@app.route('/clients')
def clients():
    return render_template('clients.html')

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

@app.route('/show_managers')
def show_managers():
    cur.execute("SELECT * FROM Manager")
    managers = cur.fetchall()
    return render_template('show_managers.html', managers=managers)

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


@app.route('/add_car_features', methods=['GET', 'POST'])
def add_car_features():
    if request.method == 'POST':
        car_id = request.form['car_id']
        rugs = request.form['rugs']
        sun_roof = request.form['sun_roof']
        wireless_charging = request.form['wireless_charging']
        hydro_stoics = request.form['hydro_stoics']
        multimedia = request.form['multimedia']
        cruise_control = request.form['cruise_control']
        
        cur.execute("""
            INSERT INTO CarFeatures (carId, rugs, sunRoof, wirelessCharging, hydroStoics, multimedia, cruiseControl)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (car_id, rugs, sun_roof, wireless_charging, hydro_stoics, multimedia, cruise_control))
        
        # Если требуется, выполните коммит транзакции
        conn.commit()
        
        # return redirect('/')  # Перенаправление на главную страницу или другую страницу по вашему выбору
        return redirect(url_for('carFeatures_success'))
    
    cur.execute("SELECT id, model, brand FROM Cars")
    cars = cur.fetchall()
    # Если метод запроса GET, отобразите HTML-форму для добавления функций автомобиля
    return render_template('add_car_features.html', cars=cars)

@app.route('/carFeatures_success')
def carFeatures_success():
    return 'Атрибуты автомобиля успешно добавлены!'

@app.route('/show_cars_books')
def show_car_book():
    # Получаем параметры запроса из URL-адреса
    sort_by = request.args.get('sort_by')
    filter_by = request.args.get('filter_by')

    # Формируем запрос к базе данных в зависимости от параметров запроса
    query = "SELECT id, brand, model, year, price, image_url FROM Cars"
    if filter_by:
        query += f" WHERE brand = '{filter_by}'"  # Пример фильтрации по бренду
    if sort_by:
        # Разбиваем параметр сортировки на направление и поле
        sort_direction, sort_field = sort_by.split('_')
        # Формируем часть SQL-запроса для сортировки
        if sort_direction == 'price':
            query += f" ORDER BY price {'ASC' if sort_field == 'asc' else 'DESC'}"
        elif sort_direction == 'year':
            query += f" ORDER BY year {'ASC' if sort_field == 'asc' else 'DESC'}"

    # Выполняем запрос к базе данных
    cur.execute(query)
    cars = cur.fetchall()

    # conn.close() - не закрываем соединение, чтобы сохранить курсор открытым

    return render_template('show_car_book.html', cars=cars)

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
        # car_price = cur.execute("SELECT price FROM Cars WHERE id = %s", (car_id,))
        # if insurance == 'True':
        #     transaction_amount += 100 
        # if credit == 'True':
        #     transaction_amount *= 1.05 

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

@app.route('/show_deals')
def show_deals():
    cur.execute("SELECT * FROM deals")
    deals = cur.fetchall()
    return render_template('show_deals.html', deals = deals)

@app.route('/sales_receipt/<int:deal_id>')
def sales_receipt(deal_id):
    cur.execute("""
        SELECT 
            deals.id,
            clients.id AS client_id,
            CONCAT(clients.lastname, ' ', SUBSTRING(clients.firstname, 1, 1), '.', SUBSTRING(clients.middlename, 1, 1)) AS client_name,
            deals.managerid,
            CONCAT(manager.lastname, '.', SUBSTRING(manager.firstname, 1, 1), '.', SUBSTRING(manager.middlename, 1, 1)) AS manager_name,
            cars.brand,
            cars.model,
            deals.date,
            deals.insurance,
            deals.equipment,
            deals.transactionAmount,
            deals.credit
        FROM 
            deals
        JOIN 
            clients ON deals.clientid = clients.id
        JOIN
            manager ON deals.managerid = manager.id
        JOIN
            cars ON deals.carid = cars.id
        WHERE
            deals.id = %s
    """, (deal_id,))
    sales_data = cur.fetchone()

    if sales_data:
        return render_template('sales_receipt.html', 
                               deal_id=sales_data[0], 
                               client_id=sales_data[1], 
                               client_name=sales_data[2], 
                               manager_id=sales_data[3], 
                               manager_name=sales_data[4], 
                               car_brand=sales_data[5], 
                               car_model=sales_data[6], 
                               date=sales_data[7], 
                               insurance=sales_data[8], 
                               equipment=sales_data[9], 
                               transaction_amount=sales_data[10], 
                               credit=sales_data[11])
    else:
        return "Данные о продаже не найдены"

    cur.close()
    conn.close()

    return render_template('sales_receipt.html', **sales_data)

@app.route('/select_orders')
def select_orders():
    cur.execute("SELECT id FROM Deals")
    deals = cur.fetchall()
    return render_template('select_orders.html', deals=deals)


@app.route('/show_order/<int:deal_id>')
def show_order(deal_id):
    cur.execute("""
        SELECT 
            deals.id,
            clients.id AS client_id,
            CONCAT(clients.lastname, ' ', SUBSTRING(clients.firstname, 1, 1), '.', SUBSTRING(clients.middlename, 1, 1)) AS client_name,
            deals.managerid,
            CONCAT(manager.lastname, '.', SUBSTRING(manager.firstname, 1, 1), '.', SUBSTRING(manager.middlename, 1, 1)) AS manager_name,
            cars.id AS car_id,
            cars.brand,
            cars.model,
            deals.date,
            deals.insurance,
            deals.equipment,
            deals.transactionAmount,
            deals.credit
        FROM 
            deals
        JOIN 
            clients ON deals.clientid = clients.id
        JOIN
            manager ON deals.managerid = manager.id
        JOIN
            cars ON deals.carid = cars.id
        WHERE
            deals.id = %s
    """, (deal_id,))
    order = cur.fetchone()

    if order:
        transaction_amount = float(order[11])
        formatted_transaction_amount = "{:,.0f}".format(transaction_amount).replace(",", " ")
        return render_template('orders.html', 
                               deal_id=order[0], 
                               client_id=order[1], 
                               client_name=order[2], 
                               manager_id=order[3], 
                               manager_name=order[4],
                               car_id=order[5], 
                               car_brand=order[6], 
                               car_model=order[7], 
                               date=order[8], 
                               insurance=order[9], 
                               equipment=order[10], 
                               transaction_amount=formatted_transaction_amount, 
                               credit=order[12])
    else:
        return "Данные о продаже не найдены"

@app.route('/show_cartype/<int:deal_id>')
# def show_cartype(deal_id):
#     cur.execute("""
#         SELECT 
#             d.id,
#             d.clientid,
#             d.managerid,
#             d.carid,
#             d.date,
#             d.insurance,
#             d.equipment,
#             d.transactionAmount,
#             d.credit
#         FROM 
#             deals d
#         JOIN 
#             carAttributes cs ON d.carid = cs.carid
#         WHERE 
#             cs.carType = 'Седан'
#             AND d.id = %sж
#     """, (deal_id,))
#     order = cur.fetchone()

#     if order:
#         transaction_amount = float(order[7])
#         formatted_transaction_amount = "{:,.0f}".format(transaction_amount).replace(",", " ")
#         return render_template('show_cartype.html', 
#                                deal_id=order[0], 
#                                client_id=order[1], 
#                                manager_id=order[2],
#                                car_id=order[3], 
#                                date=order[4], 
#                                insurance=order[5], 
#                                equipment=order[6], 
#                                transaction_amount=formatted_transaction_amount, 
#                                credit=order[8]
#     else:
#         return "Данные о продаже не найдены"

@app.route('/reports/select_car_type')
def select_car_type():
    return render_template('report_select_cartype.html')

@app.route('/reports/select_car_type/process_car_type', methods=['POST'])
def process_car_type():
    car_type = request.form['car_type']
    cur.execute("""
        SELECT deals.id,
            deals.clientid,
            deals.managerid,
            deals.carid,
            deals.date,
            deals.insurance,
            deals.equipment,
            deals.transactionAmount,
            deals.credit
        FROM deals, CarAttributes
        WHERE deals.carid = CarAttributes.carid 
        AND CarAttributes.carType = %s
    """, (car_type,))
    results = cur.fetchall()
    return render_template('report_show_cartype.html', results=results, cartype=car_type)

@app.route('/reports/show_clients_with_credit')
def show_clients_with_credit():
    cur.execute("""
        SELECT credit.dealId,
            clients.firstName,
            clients.lastName,
            clients.middleName,
            credit.loanAmount
        FROM deals
        JOIN clients ON deals.clientId = clients.id
        JOIN credit ON deals.id = credit.dealId
    """)
    results = cur.fetchall()
    return render_template('report_show_clients_with_credit.html', results=results)

@app.route('/reports/show_clients_with_insurance')
def show_clients_with_insurance():
    cur.execute("""
        SELECT insurance.dealId,
            clients.firstName,
            clients.lastName,
            clients.middleName,
            insurance.insuranseType
        FROM deals
        JOIN clients ON deals.clientId = clients.id
        JOIN insurance ON deals.id = insurance.dealId
    """)
    results = cur.fetchall()
    return render_template('report_show_clients_with_insurance.html', results=results)


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