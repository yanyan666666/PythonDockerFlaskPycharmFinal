from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'zillowData'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
    user = {'username': 'ZillowData Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, zillow=result)


@app.route('/view/<int:zillow_id>', methods=['GET'])
def record_view(zillow_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow WHERE id=%s', zillow_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', zillow=result[0])


@app.route('/edit/<int:zillow_id>', methods=['GET'])
def form_edit_get(zillow_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow WHERE id=%s', zillow_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', zillow=result[0])


@app.route('/edit/<int:zillow_id>', methods=['POST'])
def form_update_post(zillow_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Living_Space_sq_ft'), request.form.get('Beds'), request.form.get('Baths'),
                 request.form.get('Zip'), request.form.get('Year'),
                 request.form.get('List_Price'), zillow_id)
    sql_update_query = """UPDATE zillow z SET z.Living_Space_sq_ft = %s, z.Beds = %s, z.Baths = %s, z.Zip = 
     %s, z.Year = %s, z.List_Price = %s WHERE z.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/zillow/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Home Form')


@app.route('/zillow/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Living_Space_sq_ft'), request.form.get('Beds'), request.form.get('Baths'),
                 request.form.get('Zip'), request.form.get('Year'),
                 request.form.get('List_Price'))
    sql_insert_query = """INSERT INTO zillow (Living_Space_sq_ft,Beds,Baths,Zip,Year,List_Price) VALUES (%s, %s,%s, %s, %s, %s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/delete/<int:zillow_id>', methods=['POST'])
def form_delete_post(zillow_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM zillow WHERE id = %s """
    cursor.execute(sql_delete_query, zillow_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/zillow', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/zillow/<int:zillow_id>', methods=['GET'])
def api_retrieve(zillow_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow WHERE id=%s', zillow_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/zillow/<int:zillow_id>', methods=['PUT'])
def api_edit(zillow_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Living_Space_sq_ft'], content['Beds'], content['Baths'],
                 content['Zip'], content['Year'], content['List_Price'], zillow_id)

    sql_update_query = """UPDATE zillow z SET z.Living_Space_sq_ft = %s, z.Beds = %s, z.Baths = %s, z.Zip = 
        %s, z.Year = %s, z.List_Price = %s WHERE z.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/zillow', methods=['POST'])
def api_add() -> str:

    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['Living_Space_sq_ft'], content['Beds'], content['Baths'], content['Zip'], content['Year'],
                 content['List_Price'])
    sql_insert_query = """INSERT INTO zillow (Living_Space_sq_ft, Beds, Baths, Zip, Year, List_Price) 
                            VALUES (%s, %s,%s, %s,%s, %s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp

@app.route('/api/v1/zillow/<int:zillow_id>', methods=['DELETE'])
def api_delete(zillow_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM zillow WHERE id = %s """
    cursor.execute(sql_delete_query, zillow_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)