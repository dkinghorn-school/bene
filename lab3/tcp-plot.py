import numpy as np
import optparse
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt


class Plotter:
    def __init__(self):
        plt.style.use('ggplot')
        pd.set_option('display.width', 1000)

    def cwnd(self,filename):
        plt.figure()
        df = pd.read_csv('cwnd.csv')
        ax = df.plot(x="Time",y="Congestion Window")
        # set the axes
        ax.set_xlabel('Time')
        ax.set_ylabel('Congestion Window')
        plt.suptitle("")
        plt.title("")
        plt.savefig(filename)

    def sequence(self,filename):
        plt.figure()
        df = pd.read_csv('sequence.csv',dtype={'Time':float,'Sequence Number':int})
        df['Sequence Number']  =  df['Sequence Number'] / 1000 % 50
        # send
        send = df[df.Event == 'send'].copy()
        ax1 = send.plot(x='Time',y='Sequence Number',kind='scatter',marker='+',s=2,figsize=(11,3), label='Send')
        # transmit
        transmit = df[df.Event == 'transmit'].copy()
        transmit.plot(x='Time',y='Sequence Number',kind='scatter',marker='o',s=2,figsize=(11,3),ax=ax1, label='transmit')
        # drop
        try:
            drop = df[df.Event == 'drop'].copy()
            drop.plot(x='Time',y='Sequence Number',kind='scatter',marker='x',s=10,figsize=(11,3),ax=ax1, label='drop')
        except:
            pass
        # ack
        ack = df[df.Event == 'ack'].copy()
        ax = ack.plot(x='Time',y='Sequence Number',kind='scatter',marker='v',s=2,figsize=(11,3),ax=ax1, label='ACK')
        ax.set_xlim(-0.1,5)
        ax.set_xlabel('Time')
        ax.set_ylabel('Sequence Number')
        ax.legend()
        plt.suptitle("")
        plt.title("")
        plt.savefig(filename,dpi=300)

if __name__ == '__main__':
    directory = 'graphs'
    if not os.path.exists(directory):
        os.makedirs(directory)
    p = Plotter()
    p.cwnd('graphs/cwnd.png')
    p.sequence('graphs/sequence.png')
