---
name: mqtt-and-iot-edge-protocols
description: Architectural and implementation standards for MQTT, MQTT-SN, CoAP, and IoT edge protocols. Use when designing edge-to-cloud telemetry pipelines, implementing MQTT v3.1.1/v5.0 clients, handling QoS levels, KeepAlive, Last Will and Testament (LWT), network reconnections, TLS security, and payload serialization (Protobuf, CBOR, JSON).
---

# MQTT & IoT Edge Protocols Production Standards

This skill provides production standards for IoT edge-to-cloud communication using MQTT (v3.1.1 / v5.0), MQTT-SN, and CoAP. It focuses on low-latency messaging, zero-allocation memory buffers, network resilience, payload optimization, and edge security.

---

## 1. Protocol Architecture & Decision Matrix

### 1.1 Protocol Selection Guide

| Criterion | MQTT v5.0 | MQTT v3.1.1 | MQTT-SN | CoAP |
|---|---|---|---|---|
| **Transport Layer** | TCP / TLS | TCP / TLS | UDP / DTLS | UDP / DTLS |
| **Header Overhead** | 2 - 5 bytes | 2 bytes | 2 - 7 bytes | 4 bytes fixed |
| **Connection Type** | Stateful Connection | Stateful Connection | Connectionless / Sleep | Connectionless (RESTful) |
| **Ideal Network** | Cellular, Wi-Fi, Ethernet | Cellular, Wi-Fi, Ethernet | LoRa, NB-IoT, Zigbee | LPWAN, 802.15.4, Thread |
| **Advanced Features** | User properties, Reason codes, Topic aliases | Standard pub/sub | Pre-defined topics, Sleep mode | Resource discovery, Blockwise transfer |

### 1.2 QoS (Quality of Service) Strategy
- **QoS 0 (At most once)**: High-frequency telemetry (e.g., sensor streaming at 10Hz). Dropped packets are tolerable. Minimum memory and bandwidth.
- **QoS 1 (At least once)**: State changes, alarms, configuration sync, critical events. Requires acknowledgment (PUBACK) and message retry buffer. **Default choice for industrial IoT**.
- **QoS 2 (Exactly once)**: Financial transactions or billing meters. Involves 4-step handshake (PUBLISH -> PUBREC -> PUBREL -> PUBCOMP). Avoid on battery-constrained devices due to high latency and RAM consumption.

---

## 2. Real-Time Memory & Buffer Management

### 2.1 Ring Buffer for Offline Network Resiliency
When an edge gateway loses cellular/Wi-Fi connection:
- Incoming telemetry must be queued in a **bounded circular ring buffer** residing in static RAM or non-volatile flash (SPIFFS/LittleFS).
- If network blackout exceeds buffer capacity, apply explicit drop policies:
  - `DROP_OLDEST`: Discard oldest telemetry to preserve recent state.
  - `COALESCE`: Overwrite pending messages matching identical topic paths.

```
       [ Incoming Telemetry ]
                 |
                 v
      +---------------------+
      | Bounded Ring Buffer | === (Full?) ===> [ Apply Drop Oldest Policy ]
      +---------------------+
                 |
        (Network Restored)
                 |
                 v
   [ Sequential MQTT Publish (QoS 1) ]
```

### 2.2 Payload Serialization Efficiency
Avoid verbose text formats like uncompressed JSON in low-bandwidth or battery-powered edge nodes:
- **JSON**: High CPU overhead for string parsing, high bandwidth (~150+ bytes per payload).
- **CBOR (Concise Binary Object Representation)**: Schema-less binary JSON replacement (~40% smaller payload size).
- **Protocol Buffers (Protobuf) / FlatBuffers**: Compact binary format (~70% smaller payload size), zero-copy parsing, requires fixed schema `.proto`.

---

## 3. Network Resilience & Security Hardening

### 3.1 Reconnection with Exponential Backoff + Jitter
Never reconnect blindly in a tight loop upon TCP socket loss. Use truncated exponential backoff with full jitter to avoid thundering herd problems on MQTT brokers:

$$\text{Sleep Time} = \text{random}(0, \min(\text{MAX\_BACKOFF}, \text{BASE\_BACKOFF} \times 2^{\text{attempt}}))$$

```cpp
uint32_t calculate_backoff(uint32_t attempt) {
    uint32_t max_backoff = 300000; // 30 seconds
    uint32_t base_backoff = 1000;   // 1 second
    uint32_t temp = base_backoff * (1 << std::min(attempt, (uint32_t)10));
    uint32_t current_backoff = std::min(max_backoff, temp);
    return esp_random() % current_backoff; // Full jitter
}
```

### 3.2 Last Will & Testament (LWT)
Always register an LWT message on connection setup for offline node detection:
- **Topic**: `telemetry/v1/devices/{device_id}/status`
- **Payload**: `{"state": "offline", "reason": "unexpected_disconnect"}`
- **Retain Flag**: `true`
- **QoS**: `1`

### 3.3 Security Baseline (mTLS & TLS 1.3)
- **Port 8883**: Use TLS with x509 Mutual Authentication (mTLS) where device provides unique client certificate.
- **SNI (Server Name Indication)**: Mandated for cloud brokers (AWS IoT Core, Azure IoT Hub, HiveMQ Cloud).
- **Time Synchronization**: Validate X.509 certificate expiry by syncing system RTC via NTP prior to establishing TLS handshake.

---

## 4. Anti-Patterns & Pitfalls

| Anti-Pattern | Impact | Solution |
|---|---|---|
| Unbounded queue in RAM on network loss | Out-Of-Memory panic crash | Enforce static max queue size + drop oldest policy |
| Blocking `publish()` on main thread | Application freezes on packet retransmission | Use async non-blocking socket loops or dedicated telemetry task |
| Hardcoded TLS Client Certificates | Inability to rotate compromised keys | Store certificates in secure hardware element (ATECC608A) or encrypted NVS |
| Using wildcard topics `#` or `+` in device publishes | Broker rejections, security breaches | Direct specific, strictly scoped topic strings (`devices/{id}/telemetry`) |
| Setting KeepAlive too low (< 10s) | Excessive battery drain and cellular data overhead | Set KeepAlive to 60-120s; use TCP Keep-Alive socket options |

---

## 5. Production Code Example

Below is a production-grade C++ MQTT Client wrapper for embedded targets (FreeRTOS / ESP-IDF / POSIX) demonstrating static memory management, MQTT v5 LWT, payload formatting with CBOR, and exponential backoff reconnection logic.

```cpp
#include <cstdio>
#include <cstring>
#include <algorithm>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_event.h"
#include "esp_log.h"
#include "mqtt_client.h"
#include "esp_random.h"

static const char *TAG = "MQTT_PROTOCOL";

// Configuration Constants
#define BROKER_URI           "mqtts://telemetry.example.com:8883"
#define DEVICE_ID            "ESP32_EDGE_001"
#define TELEMETRY_TOPIC      "v1/devices/" DEVICE_ID "/telemetry"
#define LWT_TOPIC            "v1/devices/" DEVICE_ID "/status"
#define MAX_RING_BUFFER_SIZE 32
#define MAX_PAYLOAD_SIZE     256

// Telemetry Message Structure
struct TelemetryMessage {
    uint32_t timestamp;
    float temperature;
    float humidity;
    uint32_t seq_num;
};

// Ring Buffer Structure (Static Memory Allocation)
class StaticTelemetryRingBuffer {
private:
    TelemetryMessage buffer[MAX_RING_BUFFER_SIZE];
    size_t head = 0;
    size_t tail = 0;
    size_t count = 0;
    portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;

public:
    bool push(const TelemetryMessage &msg) {
        portENTER_CRITICAL(&lock);
        if (count >= MAX_RING_BUFFER_SIZE) {
            // Overwrite oldest item (DROP_OLDEST policy)
            tail = (tail + 1) % MAX_RING_BUFFER_SIZE;
            count--;
            ESP_LOGW(TAG, "Ring buffer full! Dropped oldest record.");
        }
        buffer[head] = msg;
        head = (head + 1) % MAX_RING_BUFFER_SIZE;
        count++;
        portEXIT_CRITICAL(&lock);
        return true;
    }

    bool pop(TelemetryMessage &out_msg) {
        portENTER_CRITICAL(&lock);
        if (count == 0) {
            portEXIT_CRITICAL(&lock);
            return false;
        }
        out_msg = buffer[tail];
        tail = (tail + 1) % MAX_RING_BUFFER_SIZE;
        count--;
        portEXIT_CRITICAL(&lock);
        return true;
    }

    size_t size() {
        portENTER_CRITICAL(&lock);
        size_t s = count;
        portEXIT_CRITICAL(&lock);
        return s;
    }
};

static StaticTelemetryRingBuffer g_telemetry_buffer;
static esp_mqtt_client_handle_t g_mqtt_client = nullptr;
static bool g_mqtt_connected = false;
static uint32_t g_reconnect_attempts = 0;

// --- MQTT Event Handler ---
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data) {
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t)event_data;
    
    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT Connected successfully to broker.");
            g_mqtt_connected = true;
            g_reconnect_attempts = 0;
            break;
            
        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGW(TAG, "MQTT Disconnected. Scheduling reconnection...");
            g_mqtt_connected = false;
            g_reconnect_attempts++;
            break;
            
        case MQTT_EVENT_PUBLISHED:
            ESP_LOGD(TAG, "Message published successfully, msg_id=%d", event->msg_id);
            break;
            
        case MQTT_EVENT_ERROR:
            ESP_LOGE(TAG, "MQTT Internal Error Occurred");
            break;
            
        default:
            break;
    }
}

// --- Serializer Utility (Compact CBOR/Binary representation) ---
static size_t serialize_payload(const TelemetryMessage &msg, uint8_t *out_buffer, size_t max_len) {
    // Compact binary format: [uint32 ts][float temp][float hum][uint32 seq] = 16 bytes
    if (max_len < sizeof(TelemetryMessage)) return 0;
    memcpy(out_buffer, &msg, sizeof(TelemetryMessage));
    return sizeof(TelemetryMessage);
}

// --- Telemetry Publisher Task ---
void MqttTelemetryTask(void *pvParameters) {
    uint8_t payload_buffer[MAX_PAYLOAD_SIZE];
    TelemetryMessage msg;

    for (;;) {
        if (g_mqtt_connected && g_telemetry_buffer.size() > 0) {
            if (g_telemetry_buffer.pop(msg)) {
                size_t payload_len = serialize_payload(msg, payload_buffer, sizeof(payload_buffer));
                
                int msg_id = esp_mqtt_client_publish(
                    g_mqtt_client, 
                    TELEMETRY_TOPIC, 
                    (const char*)payload_buffer, 
                    payload_len, 
                    1, // QoS 1
                    0  // Retain = false
                );
                
                if (msg_id < 0) {
                    ESP_LOGE(TAG, "Publish failed! Re-queuing telemetry message...");
                    g_telemetry_buffer.push(msg); // Push back on failure
                    vTaskDelay(pdMS_TO_TICKS(1000));
                }
            }
        } else {
            // Sleep when disconnected or idle
            vTaskDelay(pdMS_TO_TICKS(200));
        }
    }
}

// --- Client Initialization ---
void init_mqtt_protocol_stack() {
    const char *lwt_payload = "{\"state\":\"offline\",\"reason\":\"power_loss\"}";

    esp_mqtt_client_config_t mqtt_cfg = {};
    mqtt_cfg.broker.address.uri = BROKER_URI;
    mqtt_cfg.credentials.client_id = DEVICE_ID;
    
    // Last Will & Testament Setup
    mqtt_cfg.session.last_will.topic = LWT_TOPIC;
    mqtt_cfg.session.last_will.msg = lwt_payload;
    mqtt_cfg.session.last_will.msg_len = strlen(lwt_payload);
    mqtt_cfg.session.last_will.qos = 1;
    mqtt_cfg.session.last_will.retain = 1;

    // Network & KeepAlive Configuration
    mqtt_cfg.session.keepalive = 60; // 60 seconds keepalive
    mqtt_cfg.network.reconnect_timeout_ms = 5000;

    g_mqtt_client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(g_mqtt_client, MQTT_EVENT_ANY, mqtt_event_handler, nullptr);
    esp_mqtt_client_start(g_mqtt_client);

    // Spawn Publisher Task
    xTaskCreate(MqttTelemetryTask, "MqttPublisher", 4096, nullptr, 5, nullptr);
}
```
