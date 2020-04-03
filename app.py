from flask import Flask, render_template, request, redirect, url_for
from wtforms import StringField, IntegerField, validators
from flask_wtf import FlaskForm   ### Form has been DEPRECATED
import yfinance as yf
import pandas as pd

from flask import flash     ##, Markup

from bokeh.embed import components
from bokeh.plotting import figure, output_file
#from bokeh.transform import factor_cmap
#from bokeh.models import ColumnDataSource, HoverTool, PrintfTickFormatter



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

@app.route("/stock_info", methods=("POST", "GET"))
def get_stock_info():
    form = StockInputForm()

    if form.validate_on_submit():  ## == form.is_submitted() and form.validate()
        stock_info = StockInfo()
        form.populate_obj(stock_info)
        stock_info.ticker = stock_info.ticker.upper()
        #flash(f"Got it: {stock_info.ticker},{stock_info.year},{stock_info.month}")

        data = get_stock_data(stock_info)

        if data.shape[0]==0:
            #print("Stock ticker is either wrong or does not exists in YF DB")
            # TO DO: display special error message for unrecognized stock ticker
            return render_template("validation_error.html", form=form)
            #return render_template("index.html")
            # return redirect(url_for("index"))

        #print("Summary statistics of closing prices:")
        #print(data.Close.describe())
        #print()

        # Create the plot (interactive plot of closing prices)
        month_name = pd.to_datetime(f'{stock_info.month}-{stock_info.year}').month_name()
        fig_title = f"{stock_info.ticker} Closing Price -- {month_name} {stock_info.year}"
        p = create_figure(data, fig_title)

        # Embed plot into HTML via Flask Render
        #  This returns javascript code and an HTML div section for rendering your Bokeh plot within an HTML page. 
        script1, div1 = components(p)

        # Finally render html page with the embedded Bokeh plot
        kwargs = {'script': script1, 'div': div1}
        kwargs['stock_form'] = form

        #output_file("plot.html", title="closing stock price")
        #return render_template('plot.html')

        return render_template('index.html', **kwargs)

    else:
        return render_template("validation_error.html", form=form)

def get_stock_data(stock_info):

    ## Get stock data from cloud usng YF API
    ticker,month,year = stock_info.ticker,stock_info.month,stock_info.year
    month_last_day = pd.to_datetime(f'{year}-{month}').days_in_month
    ##print("Fetching stock price data ...")
    data = yf.download(ticker,start=f"{year}-{month}-01",end=f"{year}-{month}-{month_last_day}")
    ##print(f"Fetched {data.shape[0]} records.")

    return data


# Reference: https://docs.bokeh.org/en/latest/docs/gallery/stocks.html
def create_figure(data, fig_title):
    p = figure(x_axis_type="datetime", title=fig_title, toolbar_location="below")
    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'

    p.line(data.index, data['Close'], color='#A6CEE3')

    return p


if __name__ == '__main__':
  app.run(port=33507)  #, debug=True
