import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats

from numpy import genfromtxt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

dataDirName = 'data/'
figDirName = 'figs/'

if not os.path.isdir(figDirName):
    os.mkdir(figDirName)

#data = genfromtxt(dataDirName + 'mpu_2020-11-29T12-17-32.csv', delimiter=',')
data = genfromtxt(dataDirName + 'mpu_2020-11-14T10-00-01_adjusted.csv', delimiter=',')

#Collision test
#data = genfromtxt(dataDirName + 'smash_harder.csv', delimiter=',')

data = data[:,1:-1] # remove timestamp and temperature



n_points = data.shape[0]
n_bins = 200

titles = ['X Acceleration',  'Y Acceleration',  'Z Acceleration', \
          'X Rotation Rate', 'Y Rotation Rate', 'Z Rotation Rate']
    
for i in range(6):
    plt.figure()
    plt.ioff()
    plt.plot(data[:,i])
    plt.title(titles[i], fontsize=16)
    plt.xlabel('Time (10ms)')
    if i<3:
        plt.ylabel('Accel (G)')
    else:
        plt.ylabel('Rotation Rate (deg/sec)')
        
    plt.savefig(figDirName + titles[i] + '.png')

for i in range(6):
    plt.figure()
    plt.ioff()
    plt.hist(data[:,i], n_bins, density=True)
    
    mu = np.mean(data[:,i])
    sigma = np.std(data[:,i])
    median = np.median(data[:,i])
    minv = np.min(data[:,i])
    maxv = np.max(data[:,i])
    
    x = np.linspace(mu - 5*sigma, mu + 5*sigma, n_bins)
    plt.plot(x, stats.norm.pdf(x, mu, sigma))
    plt.title(titles[i] + ' Distribution', fontsize=16)
    
    text = 'mean = {:+.4f}\nstd. = {:.4f}\nmedian = {:+.4f}\nmin = {:+.4f}\nmax = {:+.4f}'. \
        format(round(mu,4), round(sigma,4), round(median,4), round(minv,4), round(maxv,4))
    if i<3:
        plt.xlabel('Accel (G)')
    else:
        plt.xlabel('Rotation Rate (deg/sec)')
    plt.ylabel('Probability Density')
    plt.figtext(0.89, 0.65, text, ha='right', fontsize=14)
    plt.savefig(figDirName + titles[i] + ' Distribution.png')
    
    print(titles[i] + ' Distribution')
    print(text)
    print('-----------------')
    

###### Noise reduction ######
scoop = 5
rd = data[scoop:].copy()
for j in range(scoop):
    rd += data[j:j-scoop]
rd /= (scoop+1)

for i in range(3,6):
    plt.figure()
    plt.ioff()
    plt.plot(rd[:,i])
    plt.title(titles[i] + ' (Noise Reduction)', fontsize=16)
    plt.xlabel('Time (10ms)')
    if i<3:
        plt.ylabel('Accel (G)')
    else:
        plt.ylabel('Rotation Rate (deg/sec)')
        
    plt.savefig(figDirName + titles[i] + ' (Noise Reduction).png')

for i in range(3,6):
    plt.figure()
    plt.ioff()
    plt.hist(rd[:,i], n_bins, density=True)
    
    mu = np.mean(data[:,i])
    sigma = np.std(data[:,i])
    median = np.median(data[:,i])
    minv = np.min(data[:,i])
    maxv = np.max(data[:,i])
    
    x = np.linspace(mu - 5*sigma, mu + 5*sigma, n_bins)
    plt.plot(x, stats.norm.pdf(x, mu, sigma))
    plt.title(titles[i] + ' Distribution (Noise Reduction)', fontsize=16)
    
    text = 'mean = {:+.4f}\nstd. = {:.4f}\nmedian = {:+.4f}\nmin = {:+.4f}\nmax = {:+.4f}'. \
        format(round(mu,4), round(sigma,4), round(median,4), round(minv,4), round(maxv,4))
    if i<3:
        plt.xlabel('Accel (G)')
    else:
        plt.xlabel('Rotation Rate (deg/sec)')
    plt.ylabel('Probability Density')
    plt.figtext(0.89, 0.65, text, ha='right', fontsize=14)
    plt.savefig(figDirName + titles[i] + ' Distribution (Noise Reduction).png')
    
    print(titles[i] + ' Distribution (Noise Reduction)')
    print(text)
    print('-----------------')

# plt.figtext(0, 0, '')
# for i in range(6):
#     sp = np.fft.fft(data[:1000,i])
#     freq = np.fft.fftfreq(sp.shape[-1])
    
#     plt.title(titles[i] + ' FTT', fontsize=16)
#     plt.plot(freq, sp.real, freq, sp.imag)
#     plt.savefig(figDirName + titles[i] + ' FFT.png')



print('Figures are saved in \"' + figDirName[:-1] + '\" directory.')  

