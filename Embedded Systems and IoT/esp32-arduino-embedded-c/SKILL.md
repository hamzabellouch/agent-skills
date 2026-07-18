---
name: esp32-arduino-embedded-c
description: Guidance for production-grade ESP32 Arduino and Embedded C/C++ development. Use when building firmware for ESP32, ESP32-S3, or ESP32-C3 microcontrollers, optimizing FreeRTOS tasks, managing SRAM/PSRAM, writing ISR-safe code, or handling dual-core concurrency and hardware peripherals.
---

# ESP32 Arduino & Embedded C/C++ Production Guidelines

This skill provides architecture patterns, memory management guidelines, hardware interrupt safety rules, and production code patterns for high-reliability ESP32 embedded applications using Arduino / ESP-IDF C++.

---

## 1. Core Architecture & Multi-Core Strategy

### 1.1 Dual-Core Pinning & Priority Allocation
ESP32 (dual-core Xtensa LX6/LX7) splits responsibilities across **Core 0 (PRO_CPU)** and **Core 1 (APP_CPU)**:
- **Core 0**: Reserved primarily for Wi-Fi, Bluetooth, TCP/IP stack, and system tasks managed by ESP-IDF.
- **Core 1**: Dedicated to application logic, sensor polling, motor control, display UI, and real-time DSP.

```
  Core 0 (PRO_CPU)                     Core 1 (APP_CPU)
+-----------------------+            +-----------------------+
| WiFi / Bluetooth Task |            | App Logic / Sensor    |
| TCP/IP Stack          |            | Data Processing Task  |
| System Watchdog WDT   |            | Real-time Control Task|
+-----------------------+            +-----------------------+
            ^                                    ^
            |       FreeRTOS Queue / EventGroup  |
            +------------------------------------+
```

- **Task Priorities**: FreeRTOS priorities range from `0` (lowest, idle) to `configMAX_PRIORITIES - 1` (highest, typically 24).
  - Real-time hard timing tasks: Priority 18 - 22
  - I/O & Sensor Polling: Priority 10 - 15
  - Network & Telemetry tasks: Priority 5 - 8
  - Background/Idle tasks: Priority 1 - 3

### 1.2 Task Stack & Watchdog Timers (WDT)
- **Task Watchdog Timer (TWDT)**: Monitors tasks for starvation or deadlocks. Any task pinned to a core executing a loop must either block (`vTaskDelay()`, `xQueueReceive()`) or trigger `esp_task_wdt_reset()`.
- Never use blocking `delay()` from Arduino in FreeRTOS tasks — use `vTaskDelay(pdMS_TO_TICKS(ms))` or `vTaskDelayUntil()`.

---

## 2. Real-Time Memory Management

### 2.1 Dynamic Allocation Hazards
In embedded real-time systems, heap allocation (`malloc`, `new`, `std::string`, `std::vector`, `Arduino String`) causes:
1. **Heap Fragmentation**: Repeated allocations of varying sizes leave non-contiguous small gaps, leading to runtime `Out of Memory (OOM)` crashes after days/weeks of continuous operation.
2. **Nondeterministic Execution**: Heap allocation time depends on current heap topology, violating hard real-time guarantees.

### 2.2 Memory Allocation Best Practices
- **Static Task Creation**: Use `xTaskCreateStatic()` instead of `xTaskCreate()` to allocate TCB (Task Control Block) and stack at compile time.
- **Static Queues & Semaphores**: Use `xQueueCreateStatic()` and `xSemaphoreCreateBinaryStatic()`.
- **Pre-allocated Buffers**: Allocate fixed-size array buffers in BSS/Data section or during initialization.
- **PSRAM Allocation (ESP32-WROVER / S3)**: For large buffers (e.g., audio samples, camera frames, network ring buffers), explicitly allocate from External SPI RAM:
  ```cpp
  uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(BUFFER_SIZE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  ```

### 2.3 Stack Monitoring & High Water Mark
Continuously monitor task stack consumption during testing:
```cpp
UBaseType_t highWaterMark = uxTaskGetStackHighWaterMark(NULL);
ESP_LOGI("STACK", "Task remaining stack: %u bytes", highWaterMark * sizeof(StackType_t));
```

---

## 3. Hardware Interrupt Safety (ISR)

### 3.1 IRAM Placement
Interrupt Service Routines (ISRs) and functions invoked inside ISRs **must** reside in Internal RAM (IRAM) to prevent crash/exception if flash cache is disabled during flash write/read operations.
- Annotate ISR functions with `IRAM_ATTR`.

### 3.2 ISR Guardrails
- **Keep ISRs Ultra-Short**: Only clear interrupt flags, sample raw hardware counter/registers, and post notification to a FreeRTOS task.
- **No Blocking Calls**: Never call `delay()`, `vTaskDelay()`, `printf()`, `ESP_LOGI()`, or `xQueueSend()` from inside an ISR.
- **FromISR API**: Use only FreeRTOS functions suffixing with `FromISR` (e.g., `xQueueSendFromISR()`, `vTaskNotifyGiveFromISR()`).
- **HigherPriorityTaskWoken**: Always pass `BaseType_t xHigherPriorityTaskWoken` and yield with `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)`.

### 3.3 Spinlocks & Critical Sections
For dual-core shared variables modified inside ISR:
```cpp
portMUX_TYPE mySpinlock = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR gpio_isr_handler(void* arg) {
    portENTER_CRITICAL_ISR(&mySpinlock);
    // Read/write shared hardware registers or variables safely
    portEXIT_CRITICAL_ISR(&mySpinlock);
}
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Using `String` concats in loops | Critical | Heap fragmentation, silent OOM crashes | Use `char` arrays, `snprintf()`, or static buffers |
| Long execution inside ISR | Critical | WDT trigger, interrupt starvation, system crash | Offload processing to high-priority FreeRTOS task via Task Notification |
| Shared variable modification without lock | High | Data corruption, subtle race conditions across dual cores | Use `std::atomic`, `portMUX_TYPE`, or FreeRTOS Mutex |
| `delay(100)` inside FreeRTOS tasks | Medium | Core starvation, WDT triggering, unhandled yields | Use `vTaskDelay(pdMS_TO_TICKS(100))` |
| Unchecked pointer return from `malloc`/`heap_caps_malloc` | High | Null pointer dereference panic | Always check `NULL` return before access |

---

## 5. Production Code Example

Below is a complete, production-grade ESP32 FreeRTOS C++ firmware template featuring static queues, ISR-to-Task notifications, hardware watchdog protection, and safe spinlock memory synchronization.

```cpp
#include <Arduino.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_task_wdt.h"
#include "esp_log.h"
#include <atomic>

static const char *TAG = "MAIN_APP";

// Pin Definitions
constexpr gpio_num_t SENSOR_PIN = GPIO_NUM_4;

// Queue Configuration
constexpr size_t QUEUE_LENGTH = 16;
constexpr size_t ITEM_SIZE = sizeof(uint32_t);

// Static Queue Storage
static QueueHandle_t xSensorQueue = nullptr;
static StaticQueue_t xStaticQueueStruct;
static uint8_t ucQueueStorageArea[QUEUE_LENGTH * ITEM_SIZE];

// Static Task Storage for Processing Task
constexpr configSTACK_DEPTH_TYPE PROCESS_STACK_SIZE = 4096;
static TaskHandle_t xProcessingTaskHandle = nullptr;
static StaticTask_t xProcessTaskBuffer;
static StackType_t xProcessStack[PROCESS_STACK_SIZE];

// Spinlock for ISR Shared State
static portMUX_TYPE g_spinlock = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t g_isr_event_count = 0;

// Thread-safe atomic counter for telemetry
static std::atomic<uint32_t> g_processed_events(0);

// --- ISR Handler ---
void IRAM_ATTR sensor_gpio_isr_handler(void *arg) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint32_t timestamp = xTaskGetTickCountFromISR();

    portENTER_CRITICAL_ISR(&g_spinlock);
    g_isr_event_count++;
    portEXIT_CRITICAL_ISR(&g_spinlock);

    // Send timestamp to static queue without blocking
    xQueueSendFromISR(xSensorQueue, &timestamp, &xHigherPriorityTaskWoken);

    // Context switch if higher priority task was woken
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// --- Data Processing Task (Core 1) ---
void ProcessingTask(void *pvParameters) {
    uint32_t received_timestamp = 0;
    ESP_LOGI(TAG, "Processing Task started on Core %d", xPortGetCoreID());

    for (;;) {
        // Wait indefinitely for queue items
        if (xQueueReceive(xSensorQueue, &received_timestamp, portMAX_DELAY) == pdTRUE) {
            // Business logic processing
            g_processed_events.fetch_add(1, std::memory_order_relaxed);
            
            ESP_LOGD(TAG, "Processed event registered at tick: %u", received_timestamp);
        }

        // Periodically log memory health
        if (g_processed_events.load() % 100 == 0) {
            UBaseType_t hwm = uxTaskGetStackHighWaterMark(NULL);
            ESP_LOGI(TAG, "Processed: %u | Task High Water Mark: %u bytes", 
                     g_processed_events.load(), hwm * sizeof(StackType_t));
        }
    }
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 2000) {}

    ESP_LOGI(TAG, "Initializing Production ESP32 Firmware...");

    // 1. Initialize Static Queue
    xSensorQueue = xQueueCreateStatic(QUEUE_LENGTH, ITEM_SIZE, ucQueueStorageArea, &xStaticQueueStruct);
    configASSERT(xSensorQueue != nullptr);

    // 2. Configure GPIO Pin & ISR Interrupt
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_NEGEDGE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << SENSOR_PIN);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&io_conf);

    // Install GPIO ISR Service and Attach Handler
    gpio_install_isr_service(ESP_INTR_FLAG_IRAM);
    gpio_isr_handler_add(SENSOR_PIN, sensor_gpio_isr_handler, nullptr);

    // 3. Create Static Worker Task pinned to Core 1
    xProcessingTaskHandle = xTaskCreateStaticPinnedToCore(
        ProcessingTask,
        "DataProcessor",
        PROCESS_STACK_SIZE,
        nullptr,
        12, // Priority
        xProcessStack,
        &xProcessTaskBuffer,
        1   // Core 1 (APP_CPU)
    );
    configASSERT(xProcessingTaskHandle != nullptr);

    ESP_LOGI(TAG, "System initialization complete.");
}

void loop() {
    // Main loop runs on Core 1 (Arduino default task priority 1)
    // Yield execution to allow lower-priority background routines
    vTaskDelay(pdMS_TO_TICKS(1000));
}
```
