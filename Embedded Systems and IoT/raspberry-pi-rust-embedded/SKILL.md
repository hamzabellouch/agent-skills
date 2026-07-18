---
name: raspberry-pi-rust-embedded
description: Production-grade embedded Rust guidelines for Raspberry Pi (bare-metal no_std and Linux embedded std/rppal/embedded-hal). Use when developing low-latency hardware control apps, embedded Rust drivers, Linux GPIO/SPI/I2C/UART software, real-time interrupt handlers, and memory-safe hardware abstractions.
---

# Raspberry Pi Embedded Rust Production Guidelines

This skill provides software engineering standards, memory management rules, hardware interrupt safety guidelines, and production code architectures for Raspberry Pi embedded applications using Rust (both Embedded Linux `std` with `rppal`/`embedded-hal` and bare-metal `no_std`).

---

## 1. Architecture & Driver Abstraction

### 1.1 Execution Environments: Embedded Linux vs. Bare-Metal

| Aspect | Embedded Linux (`std`) | Bare-Metal (`no_std`) |
|---|---|---|
| **OS / Kernel** | Linux (Raspberry Pi OS / Yocto / Buildroot) | Direct hardware execution (no OS) |
| **Hardware Access** | `/dev/gpiomem`, `/dev/spidev`, `/dev/i2c-*`, `sysfs` | Memory-Mapped I/O (MMIO) Registers |
| **Real-Time Determinism** | Soft Real-Time (PREEMPT_RT kernel optional) | Hard Real-Time |
| **Ecosystem Libraries** | `rppal`, `tokio`, `embedded-hal`, `nix` | `cortex-a`, `bare-metal`, `heapless` |

### 1.2 The `embedded-hal` Paradigm
Always write reusable hardware drivers against the generic `embedded-hal` traits rather than hardcoding platform-specific APIs:

```
+-------------------------------------------------------------+
|                Generic Hardware Driver                      |
| (e.g., BME280 Sensor Driver using embedded_hal::i2c::I2c)   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|              Platform HAL Abstraction Layer                 |
|    Linux: rppal::i2c::I2c  |  Microcontroller: esp32c3_hal |
+-------------------------------------------------------------+
```

---

## 2. Real-Time Memory Management & Safety

### 2.1 Memory Guarantees in `no_std` & Embedded Rust
- **No Implicit Allocation**: In `no_std` environments, heap allocations (`alloc::vec::Vec`, `alloc::string::String`) are disabled by default.
- **Static Lock-Free Queues**: Use `heapless::spsc::Queue` for deterministic Single-Producer Single-Consumer communication between hardware interrupt handlers and processing loops.
- **Stack Budget Guardrails**: Large arrays must not be created on the stack inside recursive functions or deep call chains to prevent kernel stack overflow. Use static buffers wrapped in `static_cell::StaticCell` or `Option<T>` statics.

### 2.2 Panic Strategy & Binary Optimization
In production embedded Rust, panic handlers must be explicitly configured to avoid binary bloat and undefined hardware states:

```toml
[profile.release]
opt-level = "s"      # Optimize for binary size
lto = true           # Link-Time Optimization
codegen-units = 1    # Maximum optimization
panic = "abort"      # Strip unwinding landing pads
```

---

## 3. Hardware Interrupt Safety & Concurrency

### 3.1 Linux GPIO Interrupt Handling (`rppal`)
On Raspberry Pi running Linux, GPIO interrupts are delivered asynchronously via epoll/sysfs threads.
- Never block the main execution thread inside a interrupt callback.
- Communicate interrupt events to worker threads using bounded MPSC/SPSC queues (`crossbeam_channel` or `heapless::spsc::Queue`) or `std::sync::atomic` primitives.

### 3.2 Atomicity & Memory Ordering
When sharing flags between GPIO interrupt callbacks and background threads:
- Use `AtomicBool`, `AtomicU32`, or `AtomicUsize`.
- Apply strict memory orderings (`Ordering::Acquire`, `Ordering::Release`, `Ordering::Relaxed`).

```rust
use std::sync::atomic::{AtomicBool, Ordering};

static SHUTDOWN_SIGNAL: AtomicBool = AtomicBool::new(false);

// Interrupt callback
fn on_button_press() {
    SHUTDOWN_SIGNAL.store(true, Ordering::Release);
}
```

---

## 4. Anti-Patterns & Safety Violations

| Anti-Pattern | Risk / Impact | Rust Idiomatic Fix |
|---|---|---|
| `unwrap()` / `expect()` in production hardware loops | System crash/panic on I2C noise or transient I/O read errors | Return `Result<T, DriverError>` and handle explicitly |
| Direct `unsafe` raw MMIO pointer casting without safety invariants | Memory corruption, undefined behavior | Use safe register abstractions (`svd2rust` or `volatile_register`) |
| Unprotected shared access to SPI/I2C bus across threads | Data corruption, bus locks | Use `embedded-hal-bus` or `std::sync::Mutex` |
| Busy-wait polling loop (`while pin.is_high() {}`) | 100% CPU core consumption | Use async interrupts (`poll_interrupt()`) or timed sleep |
| Dropping hardware pins without safe pin state reset | Floating outputs driving actuators unexpectedly | Implement `Drop` trait on device structs to set pins to safe low state |

---

## 5. Production Code Example

Below is a complete, production-grade embedded Rust application for Raspberry Pi using `rppal`. It demonstrates GPIO interrupt handling, thread-safe lock-free SPSC queues, atomic state flags, POSIX signal handling for graceful shutdown, and robust error handling without `unwrap()`.

`Cargo.toml` dependencies:
```toml
[dependencies]
rppal = "0.14"
thiserror = "1.0"
signal-hook = "0.3"
crossbeam-channel = "0.5"
```

`src/main.rs`:
```rust
use rppal::gpio::{Gpio, InputPin, Level, OutputPin, Trigger};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};
use thiserror::Error;

// Custom Hardware Error Types
#[derive(Error, Debug)]
pub enum HardwareError {
    #[error("GPIO Initialization failed: {0}")]
    GpioInit(#[from] rppal::gpio::Error),
    #[error("Channel communication error")]
    ChannelError,
    #[error("System timeout during operation")]
    Timeout,
}

// Global Atomic Metrics
static INTERRUPT_COUNT: AtomicU64 = AtomicU64::new(0);

// Hardware Controller Abstraction
pub struct HardwareController {
    _status_led: OutputPin,
    input_sensor: InputPin,
    running: Arc<AtomicBool>,
}

impl HardwareController {
    pub fn new(led_pin_num: u8, sensor_pin_num: u8, running: Arc<AtomicBool>) -> Result<Self, HardwareError> {
        let gpio = Gpio::new()?;
        
        let mut status_led = gpio.get(led_pin_num)?.into_output();
        let input_sensor = gpio.get(sensor_pin_num)?.into_input_pullup();
        
        // Initial safe hardware state
        status_led.set_low();

        Ok(Self {
            _status_led: status_led,
            input_sensor,
            running,
        })
    }

    pub fn start_interrupt_monitoring(&mut self) -> Result<crossbeam_channel::Receiver<Instant>, HardwareError> {
        let (sender, receiver) = crossbeam_channel::bounded::<Instant>(64);
        
        // Configure Falling Edge Interrupt Callback
        self.input_sensor.set_async_interrupt(
            Trigger::FallingEdge,
            move |level| {
                if level == Level::Low {
                    INTERRUPT_COUNT.fetch_add(1, Ordering::Relaxed);
                    let now = Instant::now();
                    // Non-blocking try_send to avoid stalling interrupt thread
                    let _ = sender.try_send(now);
                }
            },
        )?;

        Ok(receiver)
    }
}

// Ensure hardware drops into safe state on application exit
impl Drop for HardwareController {
    fn drop(&mut self) {
        let _ = self.input_sensor.clear_async_interrupt();
        println!("[HARDWARE] Hardware controller safely disarmed.");
    }
}

fn main() -> Result<(), HardwareError> {
    println!("[INIT] Starting Raspberry Pi Production Embedded Driver...");

    // 1. Setup Signal Hook for Graceful POSIX Shutdown (SIGINT / SIGTERM)
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();

    signal_hook::flag::register(signal_hook::consts::SIGINT, r.clone())
        .map_err(|_| HardwareError::Timeout)?;
    signal_hook::flag::register(signal_hook::consts::SIGTERM, r.clone())
        .map_err(|_| HardwareError::Timeout)?;

    // 2. Initialize Hardware Pins (LED = Pin 17, Sensor = Pin 27)
    let mut hw = HardwareController::new(17, 27, running.clone())?;
    let event_receiver = hw.start_interrupt_monitoring()?;

    println!("[READY] Hardware initialized. Monitoring interrupts...");

    // 3. Main Event Loop
    let mut last_log_time = Instant::now();

    while running.load(Ordering::Acquire) {
        // Receive telemetry events with non-blocking timeout
        match event_receiver.recv_timeout(Duration::from_millis(100)) {
            Ok(timestamp) => {
                println!(
                    "[EVENT] Hardware pulse detected at {:?}! Total pulses: {}",
                    timestamp,
                    INTERRUPT_COUNT.load(Ordering::Relaxed)
                );
            }
            Err(crossbeam_channel::RecvTimeoutError::Timeout) => {
                // Heartbeat interval
                if last_log_time.elapsed() >= Duration::from_secs(5) {
                    println!(
                        "[HEARTBEAT] System operational. Interrupt count: {}",
                        INTERRUPT_COUNT.load(Ordering::Relaxed)
                    );
                    last_log_time = Instant::now();
                }
            }
            Err(crossbeam_channel::RecvTimeoutError::Disconnected) => {
                eprintln!("[ERROR] Event channel disconnected unexpectedly.");
                break;
            }
        }
    }

    println!("[SHUTDOWN] Terminating hardware loops cleanly...");
    thread::sleep(Duration::from_millis(200));
    Ok(())
}
```
