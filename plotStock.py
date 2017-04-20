# THIS VERSION IS FOR PYTHON 2 #
# FROM https://pythonprogramming.net/advanced-matplotlib-graphing-charting-tutorial/
import urllib2
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick
import matplotlib
import pylab
import argparse
import array as array
matplotlib.rcParams.update({'font.size': 9})

def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter
        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi

def movingaverage(values,window):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(values, weigths, 'valid')
    return smas # as a numpy array

def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    if int(window) > int(len(a)):
        a = a # introduced to get also months instead of year! RR
    else:
        a[:window] = a[window]
    return a


def computeMACD(x, slow=26, fast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = ExpMovingAverage(x, slow)
    emafast = ExpMovingAverage(x, fast)
    return emaslow, emafast, emafast - emaslow

def graphData(stock,timeHistory,offlineMode,MA1,MA2):
    '''
        Use this to dynamically to pull a stock:
    '''
    try:
        stockList =[]

        if offlineMode == "True":
            offFile = open('api_stock_EBAY_10y.txt', 'r')
            fileToRead = offFile.read()
            stock = "EBAY"

            print 'Reading',stock,'from offline file'

        if offlineMode == False or offlineMode == "False":
            urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+str(stock)+'/chartdata;type=quote;range='+str(timeHistory)+'/csv'
            fileToRead = urllib2.urlopen(urlToVisit).read()

            print 'Currently Pulling',stock,'from:'
            print urlToVisit

        print str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))

        try:
            splitSource = fileToRead.split('\n')
            for eachLine in splitSource:
                splitLine = eachLine.split(',')
                if len(splitLine)==6:
                    if 'values' not in eachLine:
                        stockList.append(eachLine)
        except Exception, e:
            print str(e), 'failed to organize pulled data.'
    except Exception,e:
        print str(e), 'failed to pull pricing data'
    try:
        if "d" in str(timeHistory):
            date, closep, highp, lowp, openp, volume = np.loadtxt(stockList,delimiter=',',unpack=True)
            dateconv = np.vectorize(datetime.datetime.fromtimestamp)
            date = dateconv(date)
            date = matplotlib.dates.date2num(date.tolist())
        else:
            date, closep, highp, lowp, openp, volume = np.loadtxt(stockList,delimiter=',', unpack=True,converters={ 0: mdates.strpdate2num('%Y%m%d')})

        x = 0
        y = len(date)

        newAr = []
        while x < y:
            appendLine = date[x],openp[x],closep[x],highp[x],lowp[x],volume[x]
            newAr.append(appendLine)
            x+=1
        Av1 = movingaverage(closep, MA1)
        Av2 = movingaverage(closep, MA2)

        SP = len(date[MA2-1:])

        if int(SP) == 0:
            MA1 = 1
            MA2 = 3
            Av1 = movingaverage(closep,MA1)
            Av2 = movingaverage(closep,MA2)
            SP = len(date[MA2-1:])

        fig = plt.figure(facecolor='#07000d')

        ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')

        candlestick(ax1, newAr[-SP:], width=.6, colorup='#53c156', colordown='#ff1717') # plot candlestick

        Label1 = str(MA1)+' SMA'
        Label2 = str(MA2)+' SMA'

        ax1.plot(date[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5) #plot movingaverage MA1
        ax1.plot(date[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5) #plot movingaverage MA2

        ax1.grid(True, color='w')
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.yaxis.label.set_color("w")
        ax1.spines['bottom'].set_color("#5998ff")
        ax1.spines['top'].set_color("#5998ff")
        ax1.spines['left'].set_color("#5998ff")
        ax1.spines['right'].set_color("#5998ff")
        ax1.tick_params(axis='y', colors='w')
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax1.tick_params(axis='x', colors='w')
        plt.ylabel('Stock price')

        maLeg = plt.legend(loc=9, ncol=2, prop={'size':7},
                   fancybox=True, borderaxespad=0.)
        maLeg.get_frame().set_alpha(0.4)
        textEd = pylab.gca().get_legend().get_texts()
        pylab.setp(textEd[0:5], color = 'w')

        volumeMin = 0
        ax1v = ax1.twinx()
        ax1v.fill_between(date[-SP:],volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.4)

        #ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ###Edit this to 3, so it's a bit larger
        ax1v.set_ylim(0, 3*volume.max())
        ax1v.spines['bottom'].set_color("#5998ff")
        ax1v.spines['top'].set_color("#5998ff")
        ax1v.spines['left'].set_color("#5998ff")
        ax1v.spines['right'].set_color("#5998ff")
        ax1v.set_ylabel('Volume', color='w')
        ax1v.tick_params(axis='x', colors='w')
        ax1v.tick_params(axis='y', colors='w')

        ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        rsi = rsiFunc(closep)
        rsiCol = '#c1f9f7'
        posCol = '#386d13'
        negCol = '#8f2020'

        ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
        ax0.axhline(70, color=negCol)
        ax0.axhline(30, color=posCol)
        ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
        ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
        ax0.set_yticks([30,70])
        ax0.yaxis.label.set_color("w")
        ax0.spines['bottom'].set_color("#5998ff")
        ax0.spines['top'].set_color("#5998ff")
        ax0.spines['left'].set_color("#5998ff")
        ax0.spines['right'].set_color("#5998ff")
        ax0.tick_params(axis='y', colors='w')
        ax0.tick_params(axis='x', colors='w')
        plt.ylabel('RSI')




        ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        fillcolor = '#00ffe8'

        nslow = 26
        nfast = 12
        nema = 9

        emaslow, emafast, macd = computeMACD(closep)
        ema9 = ExpMovingAverage(macd, nema)

        ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
        ax2.plot(date[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
        ax2.fill_between(date[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax2.spines['bottom'].set_color("#5998ff")
        ax2.spines['top'].set_color("#5998ff")
        ax2.spines['left'].set_color("#5998ff")
        ax2.spines['right'].set_color("#5998ff")
        ax2.tick_params(axis='x', colors='w')
        ax2.tick_params(axis='y', colors='w')
        plt.ylabel('MACD', color='w')
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))

        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.suptitle(stock.upper(),color='w')
        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)

        ax1.annotate('Big news!',(date[y-10],Av1[y-10]),
            xytext=(0.8, 0.9), textcoords='axes fraction',
            arrowprops=dict(facecolor='white', shrink=0.05),
            fontsize=14, color = 'w',
            horizontalalignment='right', verticalalignment='bottom')

        plt.subplots_adjust(left=.09, bottom=.14, right=.93, top=.95, wspace=.20, hspace=0)
        plt.show()
        # fig.tight_layout()
        fig.savefig('stock_'+stock+'.pdf',facecolor=fig.get_facecolor())

    except Exception,e:
        print 'main loop',str(e)

if __name__=='__main__':

    parser = argparse.ArgumentParser(description = "Script to study a given stock curve")
    parser.add_argument('-s','--stock', dest = 'stock', help = 'Stock you are interested',required=False,nargs='+',default=['BMW'])
    parser.add_argument('-o','--offline', dest = 'offline', help = 'Stock you are interested: offline mode',required=False,default=False)
    parser.add_argument('-t','--time', dest = 'timeHistory', help = 'Time you are interest from now on, Stock you are interested, e.g. 1m, 1y (days are not supported right now).',required=False,default='1y')
    options = parser.parse_args()

    stocks       = options.stock
    timeHistory  = str(options.timeHistory)
    offlineMode  = options.offline

    #while True:
    # stock = raw_input('Stock to plot: ')
    #stock = 'BMW'
    for stock in stocks:
        graphData(str(stock),timeHistory,offlineMode,10,50)
