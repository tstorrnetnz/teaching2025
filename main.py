from flask import Flask, render_template, abort
import sqlite3


app = Flask(__name__)


# basic route
@app.route('/')
def root():
    return render_template('home.html', page_title='HOME')


# about route
@app.route('/about')  # note the leading slash, it’s important
def about():
    return render_template('about.html', page_title='ABOUT')
    

# List all the pizzas in alphabetical order
# eventually link each one to a details page
@app.route('/all_pizzas')
def all_pizzas():
    # This boilerplate db connection could (should?) be in
    # a function for easy re-use
    conn = sqlite3.connect('pizza.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM Pizza ORDER BY name ASC;")
    # fetchall returns a list of results
    pizzas = cur.fetchall() # could be fetchone()
    print(pizzas)  # DEBUG
    conn.close()  # Be a tidy Kiwi
    return render_template("all_pizzas.html", pizzas=pizzas)    


# display the details of one pizza
@app.route('/pizza/<int:id>')
def pizza(id):
    conn = sqlite3.connect('pizza.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Pizza WHERE id=?;', (id,))
    # fetchone returns a tuple containing the result, or NONE!
    pizza = cur.fetchone()
    cur.execute('SELECT name FROM Topping WHERE id IN (SELECT tid FROM PizzaTopping WHERE pid=?)', (id,))
    toppings = cur.fetchall()
    print(pizza, toppings)  # DEBUG
    # How do we handle an empty NONE result here?  Could end badly...
    conn.close()
    if pizza is None:
      abort(404)
    title = pizza[1].upper() + ' PIZZA'
    return render_template('pizza.html', page_title=title, pizza=pizza, toppings=toppings)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)