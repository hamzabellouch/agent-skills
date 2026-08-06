---
name: azure-bicep-cloud-run
metadata:
  category: Multi-Cloud Architecture (AWS and Azure)
description: >-
  Deploy containerized workloads, Azure Container Apps, Azure Kubernetes Service (AKS), and App Services using Azure Bicep and Azure CLI.
  Triggers when writing Bicep modules, configuring Azure Managed Identities, Key Vault integration, Private Endpoints,
  Virtual Networks (VNet), GitHub Actions/Azure DevOps CI/CD pipelines, or enterprise Azure governance policies.
compatibility: Azure CLI (>= 2.50.0), Bicep CLI (>= 0.20.0), Azure Container Apps / AKS, PowerShell 7+ or Bash
---

# Azure Bicep & Container App Deployments

Enterprise infrastructure declaration and container hosting patterns using Azure Bicep modules, Managed Identities, and Azure Container Apps (ACA).

---

## 1. Directory & Modular Bicep Layout

```text
infrastructure/
├── main.bicep                  # Root deployment module orchestrating resources
├── main.bicepparam             # Production parameter configuration
├── modules/
│   ├── network/
│   │   └── vnet.bicep          # VNet, Subnets, Network Security Groups
│   ├── identity/
│   │   └── uami.bicep          # User-Assigned Managed Identity & RBAC
│   ├── security/
│   │   └── keyvault.bicep      # Key Vault & Secret Access Rules
│   ├── registry/
│   │   └── acr.bicep           # Azure Container Registry with Private Endpoint
│   └── compute/
│       ├── container-env.bicep # ACA Environment & Log Analytics
│       └── container-app.bicep # ACA App deployment with Dapr & Ingress
└── .github/workflows/
    └── deploy-bicep.yml        # CI/CD deployment pipeline
```

---

## 2. Production Bicep Module Declarations

### Virtual Network & Security (`modules/network/vnet.bicep`)

```bicep
@description('Azure Region')
param location string

@description('Environment Name')
param environment string

@description('VNet CIDR prefix')
param vnetCidr string = '10.200.0.0/16'

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: 'nsg-aca-${environment}-${location}'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPS'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: 'vnet-${environment}-${location}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetCidr
      ]
    }
    subnets: [
      {
        name: 'snet-aca-infrastructure'
        properties: {
          addressPrefix: '10.200.0.0/23'
          delegations: [
            {
              name: 'aca-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
          networkSecurityGroup: {
            id: nsg.id
          }
        }
      }
      {
        name: 'snet-private-endpoints'
        properties: {
          addressPrefix: '10.200.2.0/24'
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output acaSubnetId string = vnet.properties.subnets[0].id
output privateEndpointSubnetId string = vnet.properties.subnets[1].id
```

---

### Key Vault & Managed Identity (`modules/security/keyvault.bicep`)

```bicep
param location string
param environment string
param managedIdentityPrincipalId string

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${environment}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

// Grant Key Vault Secrets User role to User-Assigned Managed Identity
resource secretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentityPrincipalId, '46330053-8b77-449d-ab14-76c242b87460')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '46330053-8b77-449d-ab14-76c242b87460') // Key Vault Secrets User
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
```

---

### Azure Container Apps Environment & Application (`modules/compute/container-app.bicep`)

```bicep
param location string
param environment string
param infrastructureSubnetId string
param containerImage string
param userAssignedIdentityId string
param userAssignedClientId string

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-${environment}-${location}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource acaEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'cae-${environment}-${location}'
  location: location
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: infrastructureSubnetId
      internal: false
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'app-${environment}-api'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: acaEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: 'myregistry.azurecr.io'
          identity: userAssignedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api-server'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedClientId
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/healthz'
                port: 8080
              }
              initialDelaySeconds: 15
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 2
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling-rule'
            custom: {
              type: 'http'
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output fqdn string = containerApp.properties.configuration.ingress.fqdn
```

---

## 3. GitHub Actions Continuous Deployment Workflow

```yaml
# .github/workflows/deploy-bicep.yml
name: Deploy Azure Bicep Infrastructure

on:
  push:
    branches: [ main ]
    paths:
      - 'infrastructure/**'

jobs:
  validate-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Bicep Lint
        run: az bicep build --file infrastructure/main.bicep

      - name: What-If Analysis
        run: |
          az deployment group what-if \
            --resource-group rg-prod-eastus \
            --template-file infrastructure/main.bicep \
            --parameters infrastructure/main.bicepparam

      - name: Deploy Bicep Stacks
        run: |
          az deployment group create \
            --resource-group rg-prod-eastus \
            --template-file infrastructure/main.bicep \
            --parameters infrastructure/main.bicepparam
```

---

## 4. Best Practices & Production Guidelines

1. **User-Assigned Managed Identity**: Prefer User-Assigned Managed Identity over System-Assigned for containerized microservices to allow pre-provisioned RBAC permissions in Bicep before deployment.
2. **What-If Validation**: Always run `az deployment group what-if` in CI/CD pipeline PRs to detect accidental resource deletions before execution.
3. **No Hardcoded Credentials**: Pass secrets solely via Key Vault references (`@description('Secret') param dbPassword string`) in parameter files.
4. **Bicep Parameter Files**: Standardize on `.bicepparam` files for strongly typed parameter bindings rather than legacy JSON parameter files.
