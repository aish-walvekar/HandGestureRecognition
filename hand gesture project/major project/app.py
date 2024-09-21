from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import subprocess
import json
import os

app = Flask("calculator")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/aboutpage')
def about():
    return render_template('about.html')

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/run')
def run_test():
    subprocess.Popen(["python", "detection.py"]) 
    return 'Camera opened successfully!'

if __name__ == '__main__':
    app.run(debug=True)