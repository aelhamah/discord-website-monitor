from flask import Flask
from threading import Thread

# server that will keep replit running
app = Flask('')
@app.route('/')
def home():
  return "hello"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
  t= Thread(target=run)
  t.start()
