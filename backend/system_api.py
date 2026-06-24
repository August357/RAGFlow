import os
import psutil

try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
except:
    GPU_AVAILABLE = False


def get_system_info():

    cpu = psutil.cpu_percent()

    memory = psutil.virtual_memory()

    gpu_info = {
        "gpu_usage": 0,
        "gpu_memory": 0,
        "gpu_total": 0
    }

    if GPU_AVAILABLE:

        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

        util = pynvml.nvmlDeviceGetUtilizationRates(handle)

        gpu_info = {
            "gpu_usage": util.gpu,
            "gpu_memory": round(mem.used / 1024**3,2),
            "gpu_total": round(mem.total / 1024**3,2)
        }

    return {
        "cpu": cpu,
        "memory": memory.percent,
        **gpu_info
    }