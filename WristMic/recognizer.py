import pyaudio
import pylab as plt
import numpy as np
import mlpy
from time import sleep, time
import pickle
import os

if __name__ == '__main__':

    p = pyaudio.PyAudio()

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000

    BUFFER = 8000
    WINDOW = 1000
    WINDOW_STEP = 500

    audio = np.zeros(BUFFER)
    index = BUFFER

    def callback(in_data, frame_count, time_info, status):
        global audio, index
        tmp = np.fromstring(in_data, dtype=np.int16)
        audio = audio[len(tmp):]
        audio = np.append(audio, tmp)
        index -= len(tmp)
        return (None, pyaudio.paContinue)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    stream_callback=callback)
                    # frames_per_buffer=CHUNK)

    shouldStop = False
    def windowCloseCallback(evt):
        global shouldStop
        shouldStop = True

    # initialize figure
    fig = plt.figure()
    fig.canvas.mpl_connect('close_event', windowCloseCallback)

    audioWindow = np.zeros(WINDOW)
    plt.figure(1)
    plt.subplot(211)
    ln, = plt.plot(audioWindow)
    plt.ylim([-32000, 32000])


    fftdata = abs(np.fft.rfft(audioWindow))
    indexFreqs = np.fft.rfftfreq(len(audioWindow), d=(1.0/RATE))
    freqlowerindex = 0
    frequpperindex = len(indexFreqs) - 1
    while indexFreqs[freqlowerindex] < 1000: freqlowerindex += 1
    while indexFreqs[frequpperindex] > 2500: frequpperindex -= 1

    plt.subplot(212)
    # ln2, = plt.plot(indexFreqs[freqlowerindex:frequpperindex], fftdata[freqlowerindex:frequpperindex])
    ln2, = plt.plot(indexFreqs, fftdata)
    plt.ylim([0, 500000])

    plt.ion()
    plt.show()

    stream.start_stream()

    thumpVotes = 0
    nailVotes = 0
    velcroVotes = 0
    totalVotes = 0
    fftrmsarray = []

    templates = {}

    for filename in os.listdir('.'):
        if filename.endswith('.pickle'):
            with open(filename) as f:
                dat = pickle.load(f)
                if not filename[0] in templates.keys(): templates[filename[0]] = []
                templates[filename[0]].append(dat)

    prevTime = 0

    while not shouldStop:
        # ln.set_ydata(audio)
        # plt.draw()
        sleep(0.001)

        while index < BUFFER - WINDOW:
            if index < 0:
                print "Couldn't keep up with realtime"
                shouldStop = True
                break

            audioWindow = audio[index:index+WINDOW]

            t = time()
            if t - prevTime > 0.25 and (thumpVotes > 0 or nailVotes > 0 or velcroVotes > 0):
                print 'Thump = ' + str(thumpVotes) + ', ' + 'Nail = ' + str(nailVotes) + ', ' + 'Velcro = ' + str(velcroVotes)
                if max([thumpVotes, nailVotes, velcroVotes]) < 7:
                    print 'FALSE POSITIVE'
                else:
                    if thumpVotes > nailVotes and thumpVotes > velcroVotes: print 'THUMP'
                    elif nailVotes > velcroVotes: print 'NAIL'
                    else: print 'VELCRO'

                print ''

                # plt.figure(2)
                # plt.ion()
                # plt.plot(fftrmsarray)
                # plt.show()
                # plt.figure(1)

                thumpVotes = 0
                nailVotes = 0
                velcroVotes = 0
                totalVotes = 0
                fftrmsarray = []

            peaktopeak = np.max(audioWindow) - np.min(audioWindow)
            rms = np.sqrt(np.mean(np.square(audioWindow)))
            if rms > 700:
                prevTime = t
                normalized = audioWindow/(peaktopeak/2.0)

                totalVotes += 1

                for template in templates['t']:
                    thumpDist = mlpy.dtw_std(normalized, template, dist_only=True)
                    # if thumpDist < 90: thumpVotes += 1
                    thumpVotes += 90/thumpDist
                    print 'ThumpDist = ' + str(thumpDist)

                for template in templates['n']:
                    nailDist = mlpy.dtw_std(normalized, template, dist_only=True)
                    # if nailDist < 200: nailVotes += 1
                    nailVotes += 200/nailDist
                    print 'NailDist = ' + str(nailDist)

                for template in templates['v']:
                    velcroDist = mlpy.dtw_std(normalized, template, dist_only=True)
                    # if velcroDist < 120: velcroVotes += 1
                    velcroVotes += 120/velcroDist
                    print 'VelcroDist = ' + str(velcroDist)
                print 'RMS = ' + str(rms)

                fftdata = abs(np.fft.rfft(audioWindow))

                maxf = np.argmax(fftdata)
                maxfreq = indexFreqs[maxf]

                if maxfreq > 400: nailVotes += 20

                print ''

                # innerWindow = 50
                # i = 0
                # stddevs = []
                # while i < len(normalized) - innerWindow:
                #     inner = normalized[i:i+innerWindow]
                #     stddevs.append(np.std(inner))
                #     i += innerWindow
                # devdev = np.std(stddevs)

                # crossings = 0
                # nonzeroes = 0
                # THRESHOLD = 0.4
                # for i in range(len(normalized)-1):
                #     if abs(normalized[i]) > THRESHOLD: nonzeroes+=1
                #     if normalized[i] > 0 >normalized[i+1]: crossings += 1
                #     elif normalized[i] < 0 < normalized[i+1]: crossings += 1
                #
                # if crossings < 50: thumpVotes += 1
                # else: velcroVotes += 1
                #
                # if nonzeroes < 150: thumpVotes += 1
                # else: velcroVotes += 1

                # smoothness = np.std(np.diff(normalized))

                # if smoothness < 0.03: thumpVotes += 1
                # elif smoothness > 0.05: velcroVotes += 1

                # fftdata = abs(np.fft.rfft(tmp))
                #
                # ln2.set_ydata(fftdata)
                #
                # maxf = np.argmax(fftdata)
                # maxfreq = indexFreqs[maxf]
                #
                # if maxfreq > 400: nailVotes += 5
                # elif maxfreq < 200:
                #     thumpVotes += 1
                #     velcroVotes += 1
                #
                # thresholdfft = fftdata[freqlowerindex:frequpperindex]
                # # ln2.set_ydata(thresholdfft)
                #
                # fftrms = np.sqrt(np.mean(np.square(thresholdfft)))
                # fftrmsarray.append(fftrms)
                # if fftrms > 8000: velcroVotes += 1
                # elif fftrms < 8000: thumpVotes += 1


                # print 'Peak2peak = ' + str(peaktopeak)
                # print 'RMS = ' + str(rms)
                # print 'Max Freq = ' + str(maxfreq)
                # # print 'crossings = ' + str(crossings)
                # # print 'nonzeroes = ' + str(nonzeroes)
                # # print 'smoothness = ' + str(smoothness)
                # print 'FFT RMS = ' + str(fftrms)
                # print ''

                ln.set_ydata(audioWindow)
                plt.draw()


                # print 'Peak2peak = ' + str(prev['peak'])
                # print 'RMS = ' + str(prev['rms'])
                # # print 'Max Freq = ' + str(prev['freq'])
                # print 'devdev = ' + str(prev['devdev'])
                # print ''
                #
                # ln.set_ydata(prev['data'])
                # plt.draw()
                #
                # prev['data'] = tmp
                # prev['peak'] = peaktopeak
                # prev['rms'] = rms
                # # prev['freq'] = maxfreq
                # prev['devdev'] = devdev

            else:
                sleep(0.001)

            index += WINDOW_STEP

    stream.stop_stream()
    stream.close()
    p.terminate()