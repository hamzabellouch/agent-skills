---
name: salesforce-apex-lwc-dev
metadata:
  category: Enterprise Systems (CRM and ERP)
description: Enterprise Salesforce development patterns, Apex triggers architecture, Lightning Web Components (LWC), SOQL query optimization, security bulkification, and Salesforce REST/SOAP APIs.
compatibility: Salesforce API v60.0+, Apex, LWC, SFDX CLI, Lightning Data Service
---

# Salesforce Apex & Lightning Web Components (LWC) Development

## Overview
This skill provides production-grade architectural patterns for Salesforce core customization. It covers Apex Trigger frameworks, Governor Limits bulkification, Lightning Web Components (LWC) wire adapters, SOQL/SOSL performance tuning, security stripping (`Security.stripInaccessible`), and unit testing with high coverage requirements (>85%).

---

## 1. Core Salesforce Architecture Principles

1. **Trigger Framework Pattern**: Never write raw business logic directly inside Apex trigger blocks. Use a single trigger per object that delegates execution to a structured Handler class adhering to context methods (`beforeInsert`, `afterUpdate`).
2. **Bulkification by Default**: All Apex code must handle collections of records (`List<SObject>`). Never issue SOQL queries or DML statements (`insert`, `update`, `delete`) inside `for` loops.
3. **Strict Governor Limits Compliance**: Respect SOQL query limits (100 per transaction), DML statements (150 per transaction), and Heap Size limits (6MB synchronous / 12MB asynchronous).
4. **Field-Level Security (FLS) & Object Permissions**: Always enforce CRUD/FLS checks before mutating or querying data using `WITH USER_MODE` or `Security.stripInaccessible()`.
5. **LWC Reactive Data Binding & LDS**: Prefer Lightning Data Service (`lightning-record-form`, `@wire`) over imperative Apex calls for UI components to leverage automatic client-side cache management.

---

## 2. Salesforce Execution Architecture

```
[ LWC UI Component ] ──(Wire Adapter / Imperative Call)
         │
         │ 1. Client-side Controller (JS)
         ▼
[ Apex Controller Class ] ──(Security.stripInaccessible / USER_MODE)
         │
         │ 2. DML Execution
         ▼
[ Apex Trigger Handler ] ──(Bulkified Collections)──▶ [ SOQL Database Layer ]
```

| Salesforce Mechanism | Best Practice / Pattern | Key Limit / Metric |
| :--- | :--- | :--- |
| **Apex Triggers** | 1 Trigger Per Object + Trigger Handler Framework | 200 records per chunk execution |
| **SOQL Queries** | Index indexed fields (`External ID`, `Id`, `Lookup`); Use `WITH USER_MODE` | Max 100 queries / 50,000 rows fetched |
| **DML Operations** | Aggregate list mutations before single `Database.insert()` call | Max 150 DML statements per transaction |
| **Asynchronous Apex** | `@future`, `Queueable`, `Batchable` for long-running processes | 50 concurrent Queueable jobs limit |
| **LWC State Engine** | `@track` for deep object properties; `@wire` for automated reactivity | Reactive property cache client-side |

---

## 3. Anti-Patterns & Common Violations

* **Anti-Pattern: SOQL / DML inside `for` loops**
  * *Risk*: `System.LimitException: Too many SOQL queries: 101`.
  * *Remediation*: Collect record IDs in a `Set<Id>` and execute a single SOQL query outside the loop.
* **Anti-Pattern: Hardcoding Salesforce Record IDs ('001xx000003DGb2')**
  * *Risk*: Deployment failures across Sandbox, Developer, and Production orgs due to mismatched IDs.
  * *Remediation*: Query record types or developer names dynamically using `Schema.SObjectType.Account.getRecordTypeInfosByDeveloperName()`.
* **Anti-Pattern: Bypassing FLS & Sharing Rules (`without sharing`)**
  * *Risk*: Unauthorized users viewing or modifying restricted enterprise data.
  * *Remediation*: Declare Apex classes with `with sharing` or `inherited sharing` unless running elevated system batch processes.

---

## 4. Production Apex & LWC Snippets

### A. Bulkified Apex Trigger Handler (`AccountTriggerHandler.cls`)

```java
/**
 * Production Apex Trigger Handler Framework for Account Object
 */
public with sharing class AccountTriggerHandler {

    public static void handleAfterUpdate(List<Account> newAccounts, Map<Id, Account> oldAccountMap) {
        Set<Id> updatedAccountIds = new Set<Id>();

        for (Account acc : newAccounts) {
            Account oldAcc = oldAccountMap.get(acc.Id);
            // Detect specific field mutation
            if (acc.AnnualRevenue != oldAcc.AnnualRevenue && acc.AnnualRevenue > 1000000) {
                updatedAccountIds.add(acc.Id);
            }
        }

        if (!updatedAccountIds.isEmpty()) {
            processEnterpriseAccounts(updatedAccountIds);
        }
    }

    private static void processEnterpriseAccounts(Set<Id> accountIds) {
        // 1. Bulkified SOQL query with USER_MODE security
        List<Opportunity> oppsToUpdate = [
            SELECT Id, StageName, Amount, AccountId 
            FROM Opportunity 
            WHERE AccountId IN :accountIds 
            AND StageName != 'Closed Won' 
            WITH USER_MODE
        ];

        for (Opportunity opp : oppsToUpdate) {
            opp.Description = 'Parent Account elevated to Enterprise tier (Revenue > $1M).';
        }

        // 2. Enforce Field Level Security before update
        if (!oppsToUpdate.isEmpty()) {
            SObjectAccessDecision decision = Security.stripInaccessible(
                AccessType.UPDATABLE,
                oppsToUpdate
            );
            Database.update(decision.getRecords(), true);
        }
    }
}
```

---

### B. Apex Controller for LWC (`AccountLwcController.cls`)

```java
public with sharing class AccountLwcController {

    @AuraEnabled(cacheable=true)
    public static List<Account> getHighValueAccounts(Decimal minRevenue) {
        Decimal threshold = minRevenue != null ? minRevenue : 500000.00;

        return [
            SELECT Id, Name, Industry, AnnualRevenue, Rating
            FROM Account
            WHERE AnnualRevenue >= :threshold
            WITH USER_MODE
            ORDER BY AnnualRevenue DESC
            LIMIT 50
        ];
    }
}
```

---

### C. Lightning Web Component JavaScript (`accountViewer.js`)

```javascript
import { LightningElement, wire, track } from 'lwc';
import getHighValueAccounts from '@salesforce/apex/AccountLwcController.getHighValueAccounts';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

const COLUMNS = [
    { label: 'Account Name', fieldName: 'Name', type: 'text' },
    { label: 'Industry', fieldName: 'Industry', type: 'text' },
    { label: 'Annual Revenue', fieldName: 'AnnualRevenue', type: 'currency', currencyCode: 'USD' },
    { label: 'Rating', fieldName: 'Rating', type: 'text' }
];

export default class AccountViewer extends LightningElement {
    columns = COLUMNS;
    @track minRevenue = 500000;

    @wire(getHighValueAccounts, { minRevenue: '$minRevenue' })
    accounts;

    handleRevenueChange(event) {
        this.minRevenue = event.target.value;
    }

    get hasData() {
        return this.accounts && this.accounts.data && this.accounts.data.length > 0;
    }
}
```
