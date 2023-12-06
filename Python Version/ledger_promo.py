import cv2

class LedgerPromo:
    # Handle promotional video data
    def __init__(self, name, path=""):
        self.name = name
        self.path = path

    def export(self):
        data = {"name": self.name, "path": self.path}
        vcap = cv2.VideoCapture(self.path)
        if vcap.isOpened():
            width = vcap.get(3)
            height = vcap.get(4)
            data["resolution"] = [width, height]
        return data

    def save(self):
        return {"name": self.name, "path": self.path}