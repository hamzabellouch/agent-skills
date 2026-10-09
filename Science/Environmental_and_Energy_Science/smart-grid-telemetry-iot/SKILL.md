---
name: smart-grid-telemetry-iot
metadata:
  category: CleanTech Energy and ESG Tech
description: Ingest, process, and analyze smart grid IoT telemetry from renewable energy sources (Solar PV, Wind), Battery Energy Storage Systems (BESS), and industrial energy meters. Bridge Modbus TCP and IEC 61850 data packets, monitor real-time electrical metrics (Active/Reactive Power, Total Harmonic Distortion, Power Factor), and calculate state-of-charge (SoC). Trigger when building smart grid software, renewable energy monitoring, or microgrid energy control.
compatibility: Python 3.10+, Modbus TCP (pymodbus 3.6+), Time-series databases (TimescaleDB, InfluxDB)
---

# Smart Grid & Energy Telemetry IoT Skill Guide

This skill governs standard communication protocols, time-series telemetry parsing, and electrical metrics calculation for modern smart grids and renewable microgrid systems.

---

## 1. Smart Grid Telemetry Architecture

```text
[ Substation Sensors / Inverters / BESS ]
  |-- Modbus TCP (Port 502) / IEC 61850 / DNP3
  |-- Electric Metrics: Voltage (V), Current (I), Active Power (kW), Frequency (Hz)
                 |
                 v
[ Edge IoT Gateway (Pymodbus / Edge Daemon) ]
  |-- Register Polling (Holding Registers: IEEE 754 32-bit Float)
  |-- Local Buffer & Network Fault Tolerance
                 |
                 v (MQTT / TLS / Kafka)
[ Real-Time Microgrid Energy Management System (EMS) ]
  |-- State-of-Charge (SoC) Coulomb Counting
  |-- Power Factor & Peak Shaving Automation
  |-- Time-Series Storage (TimescaleDB / InfluxDB)
```

---

## 2. Production Code Implementations

### A. Modbus TCP Energy Meter Ingestion (Python / pymodbus)

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pydantic import BaseModel
import time


class MeterTelemetry(BaseModel):
    timestamp_epoch: float
    voltage_l1_volts: float
    current_l1_amps: float
    active_power_kw: float
    power_factor: float
    frequency_hz: float


class SmartMeterReader:
    def __init__(self, host: str, port: int = 502, unit_id: int = 1):
        self.client = ModbusTcpClient(host=host, port=port)
        self.unit_id = unit_id

    def connect(self) -> bool:
        return self.client.connect()

    def read_metrics(self) -> MeterTelemetry:
        # Read 10 consecutive holding registers starting at 0x1000
        result = self.client.read_holding_registers(address=0x1000, count=10, slave=self.unit_id)
        if result.isError():
            raise IOError(f"Modbus read error: {result}")

        # Decode IEEE 754 32-bit floating point numbers (Big-Endian word order)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers,
            byteorder=Endian.BIG,
            wordorder=Endian.BIG,
        )

        voltage = decoder.decode_32bit_float()
        current = decoder.decode_32bit_float()
        active_power = decoder.decode_32bit_float()
        power_factor = decoder.decode_32bit_float()
        frequency = decoder.decode_32bit_float()

        return MeterTelemetry(
            timestamp_epoch=time.time(),
            voltage_l1_volts=round(voltage, 2),
            current_l1_amps=round(current, 2),
            active_power_kw=round(active_power, 2),
            power_factor=round(power_factor, 3),
            frequency_hz=round(frequency, 2),
        )

    def close(self):
        self.client.close()
```

### B. BESS State-of-Charge (SoC) Coulomb Counter Algorithm

```python
class BatteryStorageMonitor:
    def __init__(self, nominal_capacity_amp_hours: float, initial_soc_percent: float = 100.0):
        self.nominal_capacity_ah = nominal_capacity_amp_hours
        self.current_soc = initial_soc_percent
        self.last_update_time = None

    def update_telemetry(self, current_amps: float, timestamp_sec: float) -> float:
        """
        Updates SoC via Coulomb Counting.
        Positive current = discharging (-Ah).
        Negative current = charging (+Ah).
        """
        if self.last_update_time is None:
            self.last_update_time = timestamp_sec
            return self.current_soc

        delta_hours = (timestamp_sec - self.last_update_time) / 3600.0
        self.last_update_time = timestamp_sec

        # Ah transferred = Current (A) * Time (hours)
        transferred_ah = current_amps * delta_hours
        delta_soc_percent = (transferred_ah / self.nominal_capacity_ah) * 100.0

        # Discharging reduces SoC, Charging increases SoC
        self.current_soc = max(0.0, min(100.0, self.current_soc - delta_soc_percent))
        return self.current_soc
```

---

## 3. Best Practices & Operational Rules

1. **Word & Byte Order Configuration:** Industrial PLCs and inverters vary between Big-Endian and Little-Endian (or Byte-swapped Big-Endian) for 32-bit floats. Always verify endianness using a known constant register.
2. **Frequency Monitoring:** Set immediate automated load-shedding alerts if grid frequency fluctuates outside legal tolerances (e.g. $50.0 \pm 0.5\,\text{Hz}$ or $60.0 \pm 0.5\,\text{Hz}$).
3. **Power Factor Optimization:** Ensure power factor $\ge 0.95$ lagging; automate capacitor bank switching or inverter reactive power injection ($Q$) to avoid utility penalty surcharges.
