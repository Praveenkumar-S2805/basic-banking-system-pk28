#IMPORTING CLASSES
from flask import Flask,render_template,url_for,request,flash
from flask_mysqldb import MySQL

#INSTANTIATING OBJECTS
app = Flask(__name__)
mysql = MySQL(app)

#MYSQL CONNECTION
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "basicbankingsystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#HOME PAGE
@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
	return render_template("index.html")

#CUSTOMERS PAGE
@app.route("/customers")
def printCustomers():
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM customers")
	result = cursor.fetchall()
	return render_template("customers.html", data = result)

#TRANSFERS PAGE
@app.route("/transfers")
def printTransfers():
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM transfers")
	result = cursor.fetchall()
	return render_template("transfers.html", data = result)
	
#CUSTOMER PROFILE PAGE
@app.route("/viewProfile/<string:id>", methods = ["GET", "POST"])
def viewCustomers(id):
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM customers WHERE customer_id = %s", [id])
	result = cursor.fetchone()
	return render_template("profile.html", data = result)
	
#TRANSFER PAGE
@app.route("/transfer/<string:id>")
def transfer(id):
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM customers WHERE customer_id != %s", [id])
	result = cursor.fetchall()
	result = list(result)
	cursor.execute("SELECT * FROM customers WHERE customer_id = %s", [id])
	sender_data = cursor.fetchone()
	result.append(sender_data)
	return render_template("transfer.html", data = result)

#HISTORY PAGE
@app.route("/history/<string:id>")
def history(id):
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM transfers WHERE sender_id = %s OR receiver_id = %s", [id, id])
	result = cursor.fetchall()
	return render_template("history.html", data = result)
	
#TRANSFER FUNCTION
@app.route("/addTransfer", methods = ["GET", "POST"])
def addTransfer():
	if request.method == "POST":
		cursor = mysql.connection.cursor()
		
		sender_id = request.form["sender_id"]
		receiver_id = request.form["receiver_id"]
		amount = request.form["amount"]

		cursor.execute("SELECT current_balance FROM customers WHERE customer_id = %s", [sender_id])
		result = cursor.fetchone()
		sender_current_balance = result["current_balance"]
		
		if int(sender_current_balance) >= int(amount):
			cursor.execute("SELECT name FROM customers WHERE customer_id = %s", [sender_id])
			result = cursor.fetchone()
			sender_name = result["name"]
			cursor.execute("SELECT name FROM customers WHERE customer_id = %s", [receiver_id])
			result = cursor.fetchone()
			receiver_name = result["name"]

			cursor.execute("INSERT INTO transfers(sender_id, sender_name, receiver_id, receiver_name, amount) VALUES(%s, %s, %s, %s, %s)",[sender_id, sender_name, receiver_id, receiver_name, amount])
			mysql.connection.commit()
			
			cursor.execute("SELECT date_time FROM transfers WHERE sender_id = %s", [sender_id])
			result = cursor.fetchone()
			date_time = result["date_time"]
			
			cursor.execute("UPDATE customers SET current_balance = current_balance-%s WHERE customer_id=%s", [amount, sender_id])
			mysql.connection.commit()
			cursor.execute("UPDATE customers SET current_balance = current_balance+%s WHERE customer_id=%s", [amount, receiver_id])
			mysql.connection.commit()
		
			cursor.execute("SELECT current_balance FROM customers WHERE customer_id = %s", [sender_id])
			result = cursor.fetchone()
			sender_current_balance = result["current_balance"]
			cursor.execute("SELECT current_balance FROM customers WHERE customer_id = %s", [receiver_id])
			result = cursor.fetchone()
			receiver_current_balance = result["current_balance"]
			
			cursor.close()
			details = {"id" : sender_id, "sender" : sender_name, "sender_current_balance" : sender_current_balance, "receiver" : receiver_name, "receiver_current_balance" : receiver_current_balance, "amount" : amount, "date_time" : date_time}
			return render_template("receipt.html", receipt_details = details)
		else:
			cursor.close()
			return render_template("receipt.html", id = sender_id)
		
#STARTING APP
if __name__ == "__main__":
	app.run(debug = True)
	app.secret_key = "skey"
	