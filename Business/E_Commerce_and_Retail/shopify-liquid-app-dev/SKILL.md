---
name: shopify-liquid-app-dev
metadata:
  category: E-Commerce and Retail Tech
description: Shopify theme development with Liquid syntax, custom storefront App Extensions, Admin GraphQL API integrations, Webhooks processing, and Storefront API patterns.
compatibility: Shopify CLI 3.x, Theme App Extensions, Liquid, Remix / Node.js Shopify App Engine
---

# Shopify Liquid Theme & App Extension Development

## Overview
This skill provides guidelines and patterns for building scalable Shopify themes using **Liquid** and developing full-stack Shopify Apps with **Theme App Extensions**, **Admin GraphQL APIs**, and secure **Webhook Subscribers**.

---

## 1. Shopify Architecture Principles

1. **Theme App Extensions over Direct Code Injection**: Never modify a merchant's `theme.liquid` directly via script tags. Use Theme App Extensions (`app-block` and `app-embed-block`) to ensure zero left-over code upon app uninstallation.
2. **GraphQL Admin API over REST**: Prefer the GraphQL Admin API for all backend store mutations and data queries to optimize payloads and enforce strict schema typing.
3. **Liquid Performance Optimization**: Avoid nested loops over large collections (`{% for product in collections.all.products %}`). Cache expensive Liquid calculations with `{% cache %}` blocks where available.
4. **Mandatory HMAC Webhook Verification**: Verify `X-Shopify-Hmac-SHA256` signatures on all incoming webhooks before processing store events (`orders/create`, `products/update`).
5. **Session Token Auth (App Bridge)**: Utilize Shopify App Bridge with JWT session tokens for seamless, iframe-embedded app administration without third-party cookie dependencies.

---

## 2. Shopify Extension Architecture

```
[ Customer Browser ]
       │
       │ 1. Render Theme with Liquid App Extension
       ▼
[ Shopify Storefront ]
       │ 2. App Embed Block (JavaScript / Storefront API)
       ▼
[ Shopify App Backend (Remix/Node) ] ──(GraphQL Admin API)──▶ [ Shopify Core ]
       │
       │ 3. Asynchronous Webhooks (HMAC Verified)
       ▼
[ App Database / Queue ]
```

| Component | Standard Path | Purpose | Key Constraints |
| :--- | :--- | :--- | :--- |
| **App Block** | `extensions/theme-ext/blocks/*.liquid` | Render interactive UI sections inside product pages | Must define schema with `target: section` |
| **App Embed Block** | `extensions/theme-ext/blocks/*.liquid` | Inject global storefront scripts/styles | `target: body` or `head` |
| **Admin API** | `/admin/api/2026-04/graphql.json` | Programmatic store management | Rate limited by cost points (1000 pts limit) |
| **Storefront API** | `/api/2026-04/graphql.json` | Unauthenticated customer-facing queries | Requires public Storefront Access Token |

---

## 3. Anti-Patterns & Common Failures

* **Anti-Pattern: Hardcoding API Keys in Liquid Files**
  * *Risk*: Total compromise of shop credentials via public view-source.
  * *Remediation*: Pass only public Storefront tokens; perform sensitive operations via backend proxy endpoints.
* **Anti-Pattern: Synchronous Processing of Shopify Webhooks**
  * *Risk*: Gateway timeout (5 second HTTP threshold) leading to webhook delivery retries and duplicate execution.
  * *Remediation*: Return `200 OK` immediately after pushing webhook payload into a worker queue (BullMQ, Celery, SQS).
* **Anti-Pattern: Unbound Liquid Collection Loops**
  * *Risk*: Liquid render time penalty causing merchant store Lighthouse score drops.
  * *Remediation*: Enforce pagination (`{% paginate collection.products by 24 %}`).

---

## 4. Production Code Snippets

### A. Shopify Theme App Block (`extensions/theme-ext/blocks/product-upsell.liquid`)

```liquid
{% comment %}
  Shopify Theme App Extension: Product Upsell Block
  Target: section (Product details page)
{% endcomment %}

<div class="product-upsell-container" data-product-id="{{ product.id }}">
  {% if block.settings.heading != blank %}
    <h3 class="upsell-heading" style="color: {{ block.settings.heading_color }};">
      {{ block.settings.heading | escape }}
    </h3>
  {% endif %}

  <div class="upsell-content" id="upsell-widget-{{ block.id }}">
    <p class="loading-state">Loading exclusive offers...</p>
  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('[data-product-id="{{ product.id }}"]');
    if (!container) return;

    fetch(`/apps/my-custom-proxy/upsell?product_id={{ product.id }}&shop={{ shop.permanent_domain }}`)
      .then(response => response.json())
      .then(data => {
        const widget = document.getElementById('upsell-widget-{{ block.id }}');
        if (data.recommended_product) {
          widget.innerHTML = `
            <div class="upsell-card">
              <img src="${data.recommended_product.image_url}" alt="${data.recommended_product.title}" />
              <h4>${data.recommended_product.title}</h4>
              <p>Special Add-on Price: ${data.recommended_product.price}</p>
              <button onclick="addUpsellToCart('${data.recommended_product.variant_id}')">Add to Cart</button>
            </div>
          `;
        } else {
          widget.style.display = 'none';
        }
      })
      .catch(err => console.error('Upsell widget error:', err));
  });

  function addUpsellToCart(variantId) {
    fetch('/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: [{ id: variantId, quantity: 1 }] })
    })
    .then(res => res.json())
    .then(() => window.location.reload());
  }
</script>

{% schema %}
{
  "name": "Product Custom Upsell",
  "target": "section",
  "stylesheet": "upsell.css",
  "javascript": "upsell.js",
  "settings": [
    {
      "type": "text",
      "id": "heading",
      "label": "Block Heading",
      "default": "Frequently Bought Together"
    },
    {
      "type": "color",
      "id": "heading_color",
      "label": "Heading Text Color",
      "default": "#111827"
    }
  ]
}
{% endschema %}
```

---

### B. Node.js Webhook Receiver & HMAC Verification (`webhook_handler.js`)

```javascript
import crypto from 'crypto';
import express from 'express';

const app = express();

// Parse raw body for HMAC signature verification
app.post('/webhooks/orders-create', express.raw({ type: 'application/json' }), (req, res) => {
  const hmacHeader = req.headers['x-shopify-hmac-sha256'];
  const topicHeader = req.headers['x-shopify-topic'];
  const shopHeader = req.headers['x-shopify-shop-domain'];

  const secret = process.env.SHOPIFY_API_SECRET;

  // 1. Verify HMAC Signature
  const generatedHmac = crypto
    .createHmac('sha256', secret)
    .update(req.body, 'utf8')
    .digest('base64');

  if (!crypto.timingSafeEqual(Buffer.from(generatedHmac), Buffer.from(hmacHeader))) {
    console.error(`[UNAUTHORIZED] Invalid HMAC signature from ${shopHeader}`);
    return res.status(401).send('HMAC verification failed');
  }

  // 2. Fast Acknowledge to prevent Shopify timeout
  res.status(200).send('Webhook Received');

  // 3. Asynchronous Payload Processing
  const payload = JSON.parse(req.body.toString());
  console.log(`[WEBHOOK] Received ${topicHeader} for shop ${shopHeader}. Order ID: ${payload.id}`);

  // Enqueue job for background processing
  enqueueOrderJob(shopHeader, payload);
});

function enqueueOrderJob(shop, orderData) {
  // Pushes task to Redis/BullMQ worker queue
}

app.listen(3000, () => console.log('Shopify Webhook listener running on port 3000'));
```
