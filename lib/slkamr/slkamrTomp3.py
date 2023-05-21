import subprocess
import os

def slkamrTomp3(filePath):
    ffmpegCmd = "lib\\slkamr\\ffmpeg-lgpl\\bin\\ffmpeg.exe -i test.amr test.mp3"
    ffmpegCmd = "ffmpeg-lgpl\\bin\\ffmpeg.exe -i 2.amr 333.mp3"
    #ffmpegCmd = "silk_v3_decoder.exe 1.slk 1.pcm -Fs_API 44100"
    print(subprocess.getoutput(ffmpegCmd))
    #ffmpegCmd = "ffmpeg-lgpl\\bin\\ffmpeg.exe -y -f s16le -ar 44100 -ac 1 -i 1.pcm 2.mp3"
    #print(subprocess.getoutput(ffmpegCmd))

    #ffmpeg -i source.amr -acodec libmp3lame -ar 24000 -vol 500 target.vol500.mp3
