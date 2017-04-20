import matplotlib.pyplot as plt
import numpy as np
import random


def investment_return(): #random normal distribution of returns
    mean = 0.5 #mean for stock mutual fund
    sig = 10.0 #sig for stock mutual fund
    investment_return = (np.random.normal(mean,sig))/100
    # investment_return = 1-2*np.random.random_sample()
    # print investment_return
    return investment_return

def investor(A, B, invName):
	investment_value = A
	investment_period = B
	wX = []
	vY = []
	x = 1
	while x <= investment_period:
		value = A + A*investment_return()
		if value > value * 1.1: #if new value is 1.4x bigger than previous
			A = value * 0.1 #than make -90 percent adjustment
		else:
			A = value #else use new value
		wX.append(x)
		vY.append(value)
		x += 1
	#print(value)
	plt.plot(wX,vY,label=str(invName))

if __name__=='__main__':
    i = 0
    investorNames = ["Brian","Jack","Jon"]
    while i < 3: #number of investors
    	investor(100,1000,investorNames[i]) #starting value and investment period
    	i += 1
    plt.ylabel('Investment Value')
    plt.xlabel('Investment Period')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=3, mode="expand", borderaxespad=0.)
    # plt.show()
    plt.yscale('log')
    plt.savefig('foo.pdf')

    # mu, sigma = 5, 20.0 # mean and standard deviation
    # s = np.random.normal(mu, sigma, 1000000)
    # count, bins, ignored = plt.hist(s, 100,normed=True)
    # plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *
    #             np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
    #       linewidth=2, color='r')
    # plt.show()
