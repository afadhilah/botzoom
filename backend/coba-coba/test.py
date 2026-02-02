import torch
print(torch.cuda.is_available())  # Harusnya True
print(torch.cuda.get_device_name(0))  # Harusnya 'GeForce GTX 950M'