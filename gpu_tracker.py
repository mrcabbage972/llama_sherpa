import pynvml


class GpuTracker:
    """
    This class is used to track the gpu usage.
    """
    def __init__(self):
        pynvml.nvmlInit()
        self.device_count = pynvml.nvmlDeviceGetCount()
        self.gpu_handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(self.device_count)]

    def get_gpu_usage(self):
        gpu_usages = []
        for handle in self.gpu_handles:
            info = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_usages.append(info.gpu)
        return gpu_usages
