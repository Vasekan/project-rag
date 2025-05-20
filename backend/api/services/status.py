import psutil
import GPUtil

async def get_status():
    cpu_data = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent
    }

    try:
        gpus = GPUtil.getGPUs()
        gpu = gpus[0]
        cpu_data["gpu_percent"] = gpus.load * 100
        cpu_data["vram_percent"] = (gpu.memoryUsed / gpu.memoryTotal) * 100
        cpu_data["tempurature"] = gpu.temperuture
    except Exception as e:
        print(f"Ошибка при получении данных о GPU: {e}")
    return cpu_data



