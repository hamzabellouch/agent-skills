---
name: aws-cdk-cloud-architecture
metadata:
  category: Multi-Cloud Architecture (AWS and Azure)
description: >-
  Provision multi-tier, enterprise-grade cloud infrastructure on AWS using AWS CDK v2 (TypeScript).
  Triggers when designing or implementing AWS CDK stacks, L3 constructs, multi-region networking (VPC, Transit Gateway),
  ECS Fargate microservices, serverless architectures (Lambda, EventBridge, DynamoDB), IAM least-privilege,
  CDK Aspects compliance checks, or CDK Pipelines CI/CD.
compatibility: AWS CDK v2 (>= 2.100.0), Node.js (>= 18.x), TypeScript (>= 5.0), AWS CLI v2
---

# AWS CDK Cloud Architecture

Production-ready architectural patterns, L3 construct patterns, and TypeScript implementations for provisioning enterprise infrastructure using AWS Cloud Development Kit (CDK) v2.

---

## 1. Core Architecture Principles & Folder Structure

### Recommended Project Layout

```text
├── bin/
│   └── app.ts                  # App entrypoint & stack instantiation per environment
├── lib/
│   ├── aspects/                # CDK Aspects (compliance, tagging, security guards)
│   │   └── security-aspect.ts
│   ├── constructs/             # Modular L3 custom constructs
│   │   ├── network-construct.ts
│   │   ├── ecs-service-construct.ts
│   │   └── database-construct.ts
│   └── stacks/                 # Stack definitions
│       ├── network-stack.ts
│       ├── application-stack.ts
│       └── pipeline-stack.ts
├── config/                     # Environment configuration schemas
│   ├── dev.json
│   └── prod.json
├── cdk.json
├── package.json
└── tsconfig.json
```

---

## 2. Bootstrapping & Environment Configuration

### Environment Configuration Pattern

Always use typed configuration objects instead of hardcoded values or raw `process.env` lookups inside constructs.

```typescript
// config/environment.ts
export interface EnvironmentConfig {
  readonly account: string;
  readonly region: string;
  readonly environment: 'dev' | 'staging' | 'prod';
  readonly vpcCidr: string;
  readonly maxAzs: number;
  readonly ecsDesiredCount: number;
}

export const envConfigs: Record<string, EnvironmentConfig> = {
  dev: {
    account: '111111111111',
    region: 'us-east-1',
    environment: 'dev',
    vpcCidr: '10.0.0.0/16',
    maxAzs: 2,
    ecsDesiredCount: 2,
  },
  prod: {
    account: '222222222222',
    region: 'us-east-1',
    environment: 'prod',
    vpcCidr: '10.100.0.0/16',
    maxAzs: 3,
    ecsDesiredCount: 6,
  },
};
```

---

## 3. Production Multi-Tier Network & Core Constructs

### Multi-AZ Secure VPC Construct (`lib/constructs/network-construct.ts`)

```typescript
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export interface NetworkConstructProps {
  readonly vpcCidr: string;
  readonly maxAzs: number;
}

export class NetworkConstruct extends Construct {
  public readonly vpc: ec2.IVpc;

  constructor(scope: Construct, id: string, props: NetworkConstructProps) {
    super(scope, id);

    this.vpc = new ec2.Vpc(this, 'ProductionVpc', {
      ipAddresses: ec2.IpAddresses.cidr(props.vpcCidr),
      maxAzs: props.maxAzs,
      natGateways: props.maxAzs, // High Availability across all AZs
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 22,
          name: 'Application',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 24,
          name: 'Database',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      ],
      enableDnsHostnames: true,
      enableDnsSupport: true,
    });

    // VPC Flow Logs to CloudWatch
    this.vpc.addFlowLog('VpcFlowLogs');
  }
}
```

---

## 4. Production Microservice Infrastructure (ECS Fargate + ALB + Aurora)

### Application & Database Stack (`lib/stacks/application-stack.ts`)

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as logs from 'aws-cdk-lib/aws-logs';
import { EnvironmentConfig } from '../../config/environment';

export interface ApplicationStackProps extends cdk.StackProps {
  readonly config: EnvironmentConfig;
  readonly vpc: ec2.IVpc;
}

export class ApplicationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ApplicationStackProps) {
    super(scope, id, props);

    const { config, vpc } = props;

    // Customer Managed KMS Key for storage encryption
    const kmsKey = new kms.Key(this, 'AppKmsKey', {
      enableKeyRotation: true,
      description: `Encryption key for ${config.environment} application resources`,
      removalPolicy: config.environment === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    // Aurora Serverless v2 PostgreSQL Cluster
    const dbCluster = new rds.DatabaseCluster(this, 'AuroraCluster', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_3,
      }),
      writer: rds.ClusterInstance.serverlessV2('writer', {
        publiclyAccessible: false,
      }),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 16.0,
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      storageEncrypted: true,
      kmsKey,
      defaultDatabaseName: 'appdb',
      removalPolicy: config.environment === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    // ECS Cluster with Container Insights enabled
    const ecsCluster = new ecs.Cluster(this, 'EcsCluster', {
      vpc,
      containerInsights: true,
    });

    // Application Load Balanced Fargate Service
    const fargateService = new ecsPatterns.ApplicationLoadBalancedFargateService(this, 'FargateService', {
      cluster: ecsCluster,
      cpu: 512,
      memoryLimitMiB: 1024,
      desiredCount: config.ecsDesiredCount,
      taskSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      publicLoadBalancer: true,
      taskImageOptions: {
        image: ecs.ContainerImage.fromRegistry('public.ecr.aws/nginx/nginx:latest'),
        containerPort: 80,
        enableLogging: true,
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: `${config.environment}-app`,
          logRetention: logs.RetentionDays.ONE_MONTH,
        }),
        environment: {
          ENVIRONMENT: config.environment,
          DB_HOST: dbCluster.clusterEndpoint.hostname,
        },
        secrets: {
          DB_SECRET: ecs.Secret.fromSecretsManager(dbCluster.secret!),
        },
      },
    });

    // Allow ECS Tasks to communicate with Aurora Database
    dbCluster.connections.allowDefaultPortFrom(fargateService.service);

    // Auto-scaling policy based on CPU utilization
    const autoScaling = fargateService.service.autoScaleTaskCount({
      minCapacity: config.ecsDesiredCount,
      maxCapacity: config.ecsDesiredCount * 4,
    });

    autoScaling.scaleOnCpuUtilization('CpuScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(300),
      scaleOutCooldown: cdk.Duration.seconds(60),
    });
  }
}
```

---

## 5. Security & Governance with CDK Aspects

Enforce organizational compliance rules (e.g., mandatory tags, SSL enforcement, encryption) across all stacks automatically.

### Security Compliance Aspect (`lib/aspects/security-aspect.ts`)

```typescript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { IConstruct } from 'constructs';

export class SecurityComplianceAspect implements cdk.IAspect {
  public visit(node: IConstruct): void {
    // Rule 1: Ensure all S3 buckets enforce SSL and encrypt at rest
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        cdk.Annotations.of(node).addError('S3 Bucket must have encryption enabled.');
      }
    }
  }
}

// In bin/app.ts:
// cdk.Aspects.of(app).add(new SecurityComplianceAspect());
```

---

## 6. Self-Mutating CI/CD Pipeline (CDK Pipelines)

### CDK Pipeline Stack (`lib/stacks/pipeline-stack.ts`)

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CodePipeline, CodePipelineSource, ShellStep } from 'aws-cdk-lib/pipelines';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new CodePipeline(this, 'CdkPipeline', {
      pipelineName: 'EnterpriseCdkPipeline',
      synth: new ShellStep('Synth', {
        input: CodePipelineSource.gitHub('my-org/my-cdk-repo', 'main'),
        commands: [
          'npm ci',
          'npm run build',
          'npx cdk synth',
        ],
      }),
    });
  }
}
```

---

## 7. Best Practices & Production Checklist

1. **Construct Immutability**: Always pass CDK L2/L3 constructs by interface (`IVpc`, `IBucket`) rather than concrete types when referencing across stacks.
2. **Deletion Policies**: Use `RemovalPolicy.RETAIN` for production S3 buckets, DynamoDB tables, and Aurora clusters. Use `RETAIN_ON_UPDATE_OR_DELETE` for critical KMS keys.
3. **Deterministic Deployments**: Pin CDK npm package versions strictly (`"aws-cdk-lib": "2.120.0"`) to avoid version drift between developer workstations and CI/CD pipelines.
4. **Context & Caching**: Commit `cdk.context.json` to source control to lock AZ lookup responses and prevent non-deterministic stack synthesis.
