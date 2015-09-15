import wave
import matplotlib.pyplot as plt
import pylab
import numpy as np
from scipy.fftpack import fft

folder = '/Users/jzplusplus/Google Drive/GT classes/CS 7470/microphone data/siddharth-right-pinkieside/'

fignum = 1

for finger in ['thumb', 'index', 'middle', 'ring', 'pinkie']:
    for s in ['-nail-left', '-pad-bottom', '-pad-mid', '-pad-left']:
        filename = finger+s+'.wav'
        audio = wave.open(folder + filename, 'r')

        datastring = audio.readframes(-1)
        audio.close()

        bytes = np.fromstring(datastring, 'Int16')

        samplespersecond = audio.getframerate()
        bitspersample = 8.0 * audio.getsampwidth()

        normalized = bytes / float(bytes.max())

        data = normalized

        plt.figure(fignum)
        fig = pylab.gcf()
        fig.canvas.set_window_title(filename)
        fignum += 1

        plt.subplot(311)
        plt.plot(data)

        window = int(samplespersecond  * 0.01)
        # amplitude = []
        # for i in range(window/2, len(data) - window/2):
        #     datarange = data[i - window/2 : i + window/2].max() - data[i - window/2 : i + window/2].min()
        #     amplitude.append(datarange)
        #
        # plt.subplot(312)
        # plt.plot(amplitude)
        # plt.show()

        threshold = 0.5
        starti = 0
        endi = len(data)
        for i in range(0, len(data) - window):
            datarange = data[i : i+window].max() - data[i : i+window].min()
            if datarange > threshold:
                starti = i
                break

        for i in reversed(range(starti, len(data) - window)):
            datarange = data[i : i+window].max() - data[i : i+window].min()
            if datarange > threshold:
                endi = i+window
                break

        plt.axvline(starti, color='k')
        plt.axvline(endi, color='k')
        trimmed = data[starti:endi]

        plt.subplot(312)
        plt.plot(trimmed)

        fftdata = fft(trimmed)
        # fftdata = fftdata[:len(fftdata)/2-1]
        fftdata = fftdata[:1000]
        fftdata = np.abs(fftdata)

        maxfreq = np.argmax(fftdata)
        print filename + ' max freq = ' + str(maxfreq)

        ax = plt.subplot(313)
        ax.set_xlabel('Max freq = ' + str(maxfreq))
        plt.plot(fftdata,'r')

        # plt.show()
        pylab.savefig(folder+filename + '.pdf', bbox_inches='tight')