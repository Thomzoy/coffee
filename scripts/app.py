from flask import Flask, jsonify, render_template
import random  # For demo, replace with your HX711 reading

app = Flask(__name__)

# Replace this with your HX711 reading function
def read_value():
    # Example: return hx711.get_weight()
    return random.randint(0, 1024)  # Dummy data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    value = read_value()
    return jsonify(value=value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
