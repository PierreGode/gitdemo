import asyncio
import random
import time
import logging

# Configure logging to display INFO level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
number = 10
# A decorator to measure execution time of asynchronous functions
def async_timed(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"Function {func.__name__} took {elapsed:.2f} seconds")
        return result
    return wrapper

# Base Sensor class
class Sensor:
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id

    async def read_value(self):
        raise NotImplementedError("Subclasses must implement read_value")

    def __str__(self):
        return f"Sensor({self.sensor_id})"

# TemperatureSensor subclass simulates temperature readings
class TemperatureSensor(Sensor):
    async def read_value(self):
        # Simulate the delay of reading a sensor value
        await asyncio.sleep(random.uniform(0.1, 0.5))
        temp = random.uniform(20.0, 30.0)
        logger.info(f"{self} read temperature: {temp:.2f} °C")
        return {"sensor_id": self.sensor_id, "type": "temperature", "value": temp, "unit": "°C"}

# HumiditySensor subclass simulates humidity readings
class HumiditySensor(Sensor):
    async def read_value(self):
        await asyncio.sleep(random.uniform(0.1, 0.5))
        humidity = random.uniform(30.0, 70.0)
        logger.info(f"{self} read humidity: {humidity:.2f} %")
        return {"sensor_id": self.sensor_id, "type": "humidity", "value": humidity, "unit": "%"}

# DataAggregator collects readings from multiple sensors safely using an asyncio lock
class DataAggregator:
    def __init__(self):
        self.data = []
        self.lock = asyncio.Lock()

    async def add_reading(self, reading):
        async with self.lock:
            self.data.append(reading)
            logger.info(f"Added reading: {reading}")

    async def aggregate_data(self):
        async with self.lock:
            aggregated = {}
            for entry in self.data:
                sensor_type = entry["type"]
                if sensor_type not in aggregated:
                    aggregated[sensor_type] = []
                aggregated[sensor_type].append(entry["value"])
            summary = {}
            for sensor_type, values in aggregated.items():
                avg_value = sum(values) / len(values) if values else 0
                summary[sensor_type] = {"count": len(values), "average": avg_value}
            logger.info(f"Aggregated summary: {summary}")
            return summary

    async def clear_data(self):
        async with self.lock:
            self.data.clear()
            logger.info("Cleared data")

# A sensor task that repeatedly reads from a sensor and adds the reading to the aggregator
@async_timed
async def sensor_task(sensor, aggregator, iterations=5):
    for i in range(iterations):
        reading = await sensor.read_value()
        await aggregator.add_reading(reading)
        await asyncio.sleep(random.uniform(0.5, 1.0))

# Run the simulation: create sensors, schedule their tasks concurrently, and aggregate the results
@async_timed
async def run_simulation():
    aggregator = DataAggregator()
    sensors = [
        TemperatureSensor("temp_1"),
        TemperatureSensor("temp_2"),
        HumiditySensor("hum_1"),
        HumiditySensor("hum_2"),
    ]

    tasks = []
    for sensor in sensors:
        tasks.append(sensor_task(sensor, aggregator, iterations=5))
    
    await asyncio.gather(*tasks)
    summary = await aggregator.aggregate_data()
    
    print("\nFinal Aggregated Summary:")
    for sensor_type, stats in summary.items():
        print(f"{sensor_type.capitalize()} Sensors: Count = {stats['count']}, Average = {stats['average']:.2f}")
        print("The value of number is:", number)
    await aggregator.clear_data()

# Main entry point to start the asynchronous simulation
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_simulation())
    loop.close()

if __name__ == "__main__":
    main()
