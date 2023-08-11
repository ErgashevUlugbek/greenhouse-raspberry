import vlc
from time import sleep

instance = vlc.Instance('--aout=alsa')
p = instance.media_player_new()
m = instance.media_new("./Ovozli_javoblar/Assalom.mp3")
p.set_media(m)
p.play()
sleep(7.2)
p.pause()
m = instance.media_new("./Ovozli_javoblar/Disconnecting.mp3")
p.set_media(m)
p.play()
sleep(2)
p.pause()
# sleep(6)
# p.pause()
