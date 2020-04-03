from flask import Flask, render_template, request, redirect, url_for
from wtforms import StringField, IntegerField, validators
from flask_wtf import FlaskForm   ### Form has been DEPRECATED
import yfinance as yf
import pandas as pd

from flask import flash     ##, Markup

SECRET_KEY = 'flask-session-insecure-secret-key'
WTF_CSRF_SECRET_KEY = 'this-should-be-more-random'

app = Flask(__name__)
app.config.from_object(__name__)

class StockInfo():
    ticker = ""
    month = 0
    year = 0

class StockInputForm(FlaskForm):
    ticker = StringField("Ticker", [validators.InputRequired(), validators.Length(min=2, max=10)])   #validators.required() --> validators.InputRequired()
    month = IntegerField("month", [validators.NumberRange(min=1, max=12)], default=3)
    year = IntegerField("year", [validators.NumberRange(min=1990, max=2020)], default=2020)

@app.route("/")
def index():
    stock_form = StockInputForm()
    return render_template("index.html", stock_form=stock_form)

@app.route("/stock_info", methods=("POST", ))
def get_stock_info():
    form = StockInputForm()
    if form.validate_on_submit():  ## == form.is_submitted() and form.validate()
        stock_info = StockInfo()
        form.populate_obj(stock_info)
        print(f"Got it: {stock_info.ticker},{stock_info.year},{stock_info.month}")
        flash(f"Got it: {stock_info.ticker},{stock_info.year},{stock_info.month}")
        process_stock_info(stock_info)
        return redirect(url_for("index"))
    return render_template("validation_error.html", form=form)

def process_stock_info(stock_info):
    ticker,month,year = stock_info.ticker,stock_info.month,stock_info.year
    month_last_day = pd.to_datetime(f'{year}-{month}').days_in_month
    ##print("Fetching stock price data ...")
    data = yf.download(ticker,start=f"{year}-{month}-01",end=f"{year}-{month}-{month_last_day}")
    ##print(f"Fetched {data.shape[0]} records.")
    if data.shape[0]>0:
        print("Summary statistics of closing prices:")
        print(data.Close.describe())
        print()
        # TO DO: interactive plot of closing prices
    else:
        # TO DO: unrecognized stock ticker error message
        print("Stock ticker may be wrong ...")


if __name__ == '__main__':
  app.run(port=33507, debug=True)
