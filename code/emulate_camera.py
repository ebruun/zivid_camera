import datetime
from zivid import Application, Settings2D

app = Application()
camera = app.create_file_camera(".\ZividSampleData2\FileCameraZividOne.zfc")

settings_2d = Settings2D()
settings_2d.acquisitions.append(Settings2D.Acquisition())
settings_2d.acquisitions[0].aperture = 2.83
settings_2d.acquisitions[0].exposure_time = datetime.timedelta(microseconds=10000)

with camera.capture(settings_2d) as frame_2d:
    image = frame_2d.image_rgba()
    image.save("emulated_result.png")

