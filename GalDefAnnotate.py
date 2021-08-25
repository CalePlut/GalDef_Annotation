import cv2
import matplotlib.pyplot as plt
from ffpyplayer.player import MediaPlayer
import keyboard as kbd
import time

from matplotvideo import video_player

affect = 0
timeCode = 0
data=[[affect], [timeCode]]

def play_videoFile(filePath):
    video = cv2.VideoCapture(filePath)
    player = MediaPlayer(filePath)
    cv2.namedWindow('Video Life2Coding',cv2.WINDOW_AUTOSIZE)
    while True:
        grabbed, frame=video.read()
        audio_frame, val=player.get_frame()
        if not grabbed:
            print("End of video")
            break
        cv2.imshow('Video', frame)
        if cv2.waitKey(24) == 27:
            break  # esc to quit
        if val != 'eof' and audio_frame is not None:
            #audio
            img, t = audio_frame
    cv2.destroyAllWindows()

def main():
    start_time = time.perf_counter()
    play_videoFile("GalDefLose1.mp4")

    plt.show()

def key_up():
    affect+=1
    timeCode=time.perf_counter()-start_time
    data.append([affect, timeCode])
def key_down():
    affect-=1
    timeCode=time.perf_counter()-start_time
    data.append([affect, timeCode])

kbd.add_hotkey("up", key_up)
kbd.add_hotkey("down", key_down)

main()
