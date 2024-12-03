from flask import render_template
import yfinance as yf
import pandas as pd
import plotly.express as px

from . import app


@app.route('/')
def index():
    return render_template('index.html')
