# modelroblox.py
import torch

def get_yolov5_roblox(confident_val):
    modelroblox = torch.hub.load(
        './yolov5', 'custom', path='./model/best.pt', source='local', force_reload=True
    )  # Adding force_reload=True to refresh the model
    modelroblox.conf = confident_val
    return modelroblox
