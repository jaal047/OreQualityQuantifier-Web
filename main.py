# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import numpy as np
import pandas as pd
import pickle
import os
from flask_migrate import Migrate
from flask_minify  import Minify
from sys import exit

from apps.config import config_dict
from apps import create_app, db
from flask import Flask, request, jsonify, render_template
import joblib
from firebase_admin import db, credentials, initialize_app



# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

import pickle
from datetime import datetime

# Memuat model.pkl
with open('./models/OQQ_model.sav', 'rb') as file:
    model = pickle.load(file)
@app.route('/predict', methods=['POST'])
def predict():
    data = request.form
    # Dapatkan referensi ke lokasi 'feedback' di database
    ref = db.reference('Dataprediksi')
    # Ambil data tanggal dari form
    tanggal_str = data.get('tanggal')
    # Konversi string tanggal menjadi objek datetime
    tanggal_prediksi = datetime.strptime(tanggal_str, "%m/%d/%Y")
    tanggal_prediksi = tanggal_prediksi.isoformat()
    air_flow_267 = float(data.get('air_flow_267'))
    float_level_47 = float(data.get('float_level_47'))
    iron_feed = float(data.get('iron_feed'))
    amina_flow = float(data.get('amina_flow'))
    ore_pulp_ph = float(data.get('ore_pulp_ph'))
    ore_pulp_density = float(data.get('ore_pulp_density'))

    # Membentuk array numpy dari data input
    input_data = np.array([[air_flow_267, float_level_47, iron_feed, amina_flow, ore_pulp_ph, ore_pulp_density]])

    # Membuat prediksi menggunakan model
    prediction = model.predict(input_data)

    prediction_data = {
        'tanggal_prediksi':tanggal_prediksi,
        'air_flow_267': air_flow_267,
        'float_level_47': float_level_47,
        'iron_feed': iron_feed,
        'amina_flow': amina_flow,
        'ore_pulp_ph': ore_pulp_ph,
        'ore_pulp_density': ore_pulp_density,
        'hasil_predict':prediction[0]
    }
    # Tambahkan data prediksi ke database
    new_prediction_ref = ref.push()
    new_prediction_ref.set(prediction_data)

    # Mengembalikan hasil prediksi ke template
    return render_template('prediksi.html', result=prediction[0])


# Route untuk menangani pengiriman data feedback dari form
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    # Dapatkan referensi ke lokasi 'feedback' di database
    ref = db.reference('feedback')

    # Ambil data dari form
    message = request.form['message']

    # Data feedback dari user
    feedback_data = {
        'message': message
    }

    # Tambahkan data feedback ke database
    new_feedback_ref = ref.push()
    new_feedback_ref.set(feedback_data)

    # Redirect ke halaman sukses atau tampilkan pesan sukses
    return render_template('prediksi.html', success=True)

if __name__ == "__main__":
    app.run()
