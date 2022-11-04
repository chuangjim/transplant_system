from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from playsound import playsound
class Sound:
    def play_sound():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        vl = volume.GetMasterVolumeLevel()
        volume.SetMute(0, None)
        volume.SetMasterVolumeLevel(0, None)
        playsound('../../data/sound/finish_sound.mp3')
        # playsound('./sound/finish_sound2.mp3')
        volume.SetMasterVolumeLevel(vl, None)

