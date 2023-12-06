from settings import RTMP_BASE

import cv2

class LedgerDJ:
    # Handle DJ information and live or pre-rec data
    def __init__(
        self,
        name,
        logo_path="",
        recording_path="",
        rtmp_server="",
        stream_key="",
        last_live_resolution="",
    ):
        self.name = name
        self.logo_path = logo_path
        self.recording_path = recording_path
        self.rtmp_server = rtmp_server
        self.stream_key = stream_key
        self.last_live_resolution = last_live_resolution

    def get_stream_url(self):
        if self.rtmp_server and self.stream_key:
            return (
                " rtmp://rtmp-"
                + ".".join([self.rtmp_server, RTMP_BASE])
                + self.stream_key
            )
        return None

    def export(self, is_live):
        data = {
            "name": self.name,
            "logo_path": self.logo_path,
        }

        if is_live:
            data["resolution"] = self.last_live_resolution
            data["url"] = self.get_stream_url()
        else:
            vcap = cv2.VideoCapture(self.recording_path)
            if vcap.isOpened():
                width = vcap.get(3)
                height = vcap.get(4)
                data["resolution"] = [width, height]
            data["recording_path"] = self.recording_path

        return data

    def save(self):
        return {
            "name": self.name,
            "logo_path": self.logo_path,
            "recording_path": self.recording_path,
            "rtmp_server": self.rtmp_server,
            "stream_key": self.stream_key,
            "last_live_resolution": self.last_live_resolution,
        }