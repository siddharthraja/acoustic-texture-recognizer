import pyaudio
import pylab as plt
import numpy as np
import mlpy
from time import sleep, time
import pickle

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

    stream.start_stream()

    data = []

    prevTime = 0
    newframe = False

    while not shouldStop:
        # ln.set_ydata(audio)
        # plt.draw()
        sleep(0.001)

        while index < BUFFER - WINDOW:
            if index < 0:
                print "Couldn't keep up with realtime"
                shouldStop = True
                break
                
            tmp = audio[index:index+WINDOW]

            t = time()
            if t - prevTime > 0.25 and newframe:
                for d in data:
                    with open('datadump.pickle', 'wb') as f:
                        pickle.dump(d, f)
                    plt.plot(d)
                    plt.ylim([-2, 2])
                    plt.show()

                data = []
                newframe = False
                index = len(audio)-1-WINDOW
                continue

            peaktopeak = np.max(tmp) - np.min(tmp)
            rms = np.sqrt(np.mean(np.square(tmp)))
            if rms > 700:
                newframe = True
                prevTime = t
                normalized = tmp/(peaktopeak/2.0)
                print rms

                data.append(normalized)


            else:
                sleep(0.001)

            index += WINDOW_STEP

    stream.stop_stream()
    stream.close()
    p.terminate()