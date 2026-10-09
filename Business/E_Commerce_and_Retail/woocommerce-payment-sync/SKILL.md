---
name: woocommerce-payment-sync
metadata:
  category: E-Commerce and Retail Tech
description: WooCommerce REST API integration, webhook-driven order payment processing, inventory reconciliation, custom payment gateway integration, and Action Scheduler job queues.
compatibility: WordPress 6.x, WooCommerce 8.x/9.x, PHP 8.2+, WooCommerce REST API v3
---

# WooCommerce Payment & Inventory Synchronization

## Overview
This skill provides standards for integrating WordPress / WooCommerce with external payment gateways and ERP systems. It covers custom WooCommerce payment gateway plugin development, REST API v3 client operations, nonces security, inventory reconciliation, and background queue management via **Action Scheduler**.

---

## 1. WooCommerce Integration Principles

1. **Leverage Action Scheduler for Background Jobs**: Never run heavy sync logic directly inside HTTP requests or standard WP-Cron (`wp_cron()`). Use WooCommerce Action Scheduler (`as_schedule_single_action`) for reliable background processing.
2. **Idempotent Webhook Handlers**: Payment webhooks must check existing order metadata (`_payment_completed_tx_id`) before changing order status to prevent duplicate fulfillments.
3. **WooCommerce High-Performance Order Storage (HPOS)**: Always use `\WC_Order` CRUD methods (`$order->get_meta()`, `$order->update_meta_data()`) instead of generic WordPress postmeta functions (`get_post_meta()`) to ensure compatibility with HPOS database tables (`wp_wc_orders`).
4. **Transaction Locks on Inventory Mutations**: Acquire database row locks (`SELECT ... FOR UPDATE`) or atomic inventory updates (`wc_update_product_stock()`) to prevent race conditions during flash sales.
5. **Strict API Authentication**: Authenticate external REST API requests using Consumer Key / Consumer Secret over HTTPS using HMAC-SHA256 signatures.

---

## 2. Integration & Payment Architecture

```
[ Customer Storefront ] ──(Checkout Form)──▶ [ Custom Payment Gateway Plugin ]
                                                    │
                                                    │ 1. Charge Request
                                                    ▼
[ WooCommerce HPOS Core ] ◀──(Webhook 200 OK)── [ Payment Provider API ]
        │
        │ 2. Trigger Action Scheduler Task
        ▼
[ Action Scheduler Queue ] ──(Background Worker)──▶ [ ERP / Inventory Sync Engine ]
```

| Lifecycle Event | WooCommerce Hook | Primary Responsibility |
| :--- | :--- | :--- |
| **Payment Process** | `process_payment($order_id)` | Validate checkout form & initiate gateway transaction |
| **Webhook Ingestion** | `woocommerce_api_{gateway_slug}` | Receive IPN/Webhook, verify signature, mark order paid |
| **Status Change** | `woocommerce_order_status_completed` | Trigger downstream inventory sync and ERP dispatch |
| **Background Job** | `as_enqueue_async_action()` | Execute long-running inventory reconciliation async |

---

## 3. Anti-Patterns & Common Errors

* **Anti-Pattern: Using Legacy `get_post_meta()` on WooCommerce Orders**
  * *Risk*: Total failure or missing data when WooCommerce High-Performance Order Storage (HPOS) is enabled.
  * *Remediation*: Always call `$order = wc_get_order($order_id); $val = $order->get_meta('_custom_key');`.
* **Anti-Pattern: Unverified Gateway Callbacks (`$_POST` Ingestion)**
  * *Risk*: Fraudulent order fulfillment by spoofing IPN requests.
  * *Remediation*: Validate payment processor digital signatures or re-query payment status directly via gateway API before marking `payment_complete()`.
* **Anti-Pattern: Syncing Large Inventories via Single HTTP Request**
  * *Risk*: PHP execution timeout (`max_execution_time`), partial sync states, memory allocation failures.
  * *Remediation*: Chunk products into batches of 50 and schedule sequential Action Scheduler jobs.

---

## 4. Production PHP Payment Gateway & Sync Snippets

### A. Custom WooCommerce Payment Gateway (`class-wc-gateway-enterprise.php`)

```php
<?php
/**
 * Plugin Name: WooCommerce Enterprise Payment Gateway & Sync
 * Description: Production-grade custom payment gateway with Action Scheduler inventory sync.
 * Version: 2.1.0
 * Author: Enterprise Commerce Engineering
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

add_action('plugins_loaded', 'init_enterprise_payment_gateway');

function init_enterprise_payment_gateway() {
    if (!class_exists('WC_Payment_Gateway')) return;

    class WC_Gateway_Enterprise extends WC_Payment_Gateway {

        public function __construct() {
            $this->id                 = 'enterprise_pay';
            $this->icon               = apply_filters('woocommerce_enterprise_icon', '');
            $this->has_fields         = true;
            $this->method_title       = __('Enterprise Pay', 'wc-enterprise');
            $this->method_description = __('Custom enterprise payment gateway integration.', 'wc-enterprise');

            $this->init_form_fields();
            $this->init_settings();

            $this->title       = $this->get_option('title');
            $this->description = $this->get_option('description');
            $this->api_key     = $this->get_option('api_key');

            // Save admin options
            add_action('woocommerce_update_options_payment_gateways_' . $this->id, array($this, 'process_admin_options'));
            
            // Register Webhook Endpoint: /wc-api/enterprise_pay
            add_action('woocommerce_api_' . $this->id, array($this, 'handle_webhook_callback'));
        }

        public function init_form_fields() {
            $this->form_fields = array(
                'enabled' => array(
                    'title'   => __('Enable/Disable', 'wc-enterprise'),
                    'type'    => 'checkbox',
                    'label'   => __('Enable Enterprise Pay', 'wc-enterprise'),
                    'default' => 'yes'
                ),
                'title' => array(
                    'title'       => __('Title', 'wc-enterprise'),
                    'type'        => 'text',
                    'default'     => __('Credit Card (Enterprise)', 'wc-enterprise'),
                ),
                'api_key' => array(
                    'title'       => __('API Secret Key', 'wc-enterprise'),
                    'type'        => 'password',
                )
            );
        }

        public function process_payment($order_id) {
            $order = wc_get_order($order_id);

            if (!$order) {
                wc_add_notice(__('Invalid order specified.', 'wc-enterprise'), 'error');
                return array('result' => 'failure');
            }

            try {
                // Perform external payment API request
                $payment_response = $this->execute_gateway_charge($order);

                if ($payment_response['status'] === 'SUCCESS') {
                    // Mark order as processing and record transaction ID
                    $order->payment_complete($payment_response['transaction_id']);
                    $order->add_order_note(sprintf(__('Payment approved via Enterprise Pay. Transaction ID: %s', 'wc-enterprise'), $payment_response['transaction_id']));

                    // Schedule background inventory & ERP reconciliation via Action Scheduler
                    if (function_exists('as_enqueue_async_action')) {
                        as_enqueue_async_action('enterprise_sync_order_to_erp', array('order_id' => $order->get_id()));
                    }

                    WC()->cart->empty_cart();

                    return array(
                        'result'   => 'success',
                        'redirect' => $this->get_return_url($order)
                    );
                } else {
                    wc_add_notice(__('Payment authorization failed: ', 'wc-enterprise') . $payment_response['message'], 'error');
                    return array('result' => 'failure');
                }
            } catch (\Exception $e) {
                wc_add_notice($e->getMessage(), 'error');
                return array('result' => 'failure');
            }
        }

        private function execute_gateway_charge(\WC_Order $order) {
            // Mock API request to gateway provider
            return array(
                'status'         => 'SUCCESS',
                'transaction_id' => 'tx_' . bin2hex(random_bytes(8))
            );
        }

        public function handle_webhook_callback() {
            $raw_payload = file_get_contents('php://input');
            $signature   = isset($_SERVER['HTTP_X_ENTERPRISE_SIGNATURE']) ? sanitize_text_field($_SERVER['HTTP_X_ENTERPRISE_SIGNATURE']) : '';

            $calculated_sig = hash_hmac('sha256', $raw_payload, $this->api_key);

            if (!hash_equals($calculated_sig, $signature)) {
                status_header(401);
                wp_die('Invalid signature');
            }

            $data = json_decode($raw_payload, true);
            $order_id = isset($data['order_id']) ? intval($data['order_id']) : 0;
            $order = wc_get_order($order_id);

            if ($order && !$order->is_paid()) {
                $order->payment_complete($data['transaction_id']);
                status_header(200);
                echo 'Order updated';
                exit;
            }

            status_header(200);
            echo 'No action taken';
            exit;
        }
    }

    add_filter('woocommerce_payment_gateways', function($methods) {
        $methods[] = 'WC_Gateway_Enterprise';
        return $methods;
    });
}

// Action Scheduler Background Worker
add_action('enterprise_sync_order_to_erp', 'process_enterprise_erp_sync', 10, 1);
function process_enterprise_erp_sync($order_id) {
    $order = wc_get_order($order_id);
    if (!$order) return;

    // Perform background REST call to ERP system
    $order->update_meta_data('_erp_synced_at', current_time('mysql'));
    $order->save();
}
```
