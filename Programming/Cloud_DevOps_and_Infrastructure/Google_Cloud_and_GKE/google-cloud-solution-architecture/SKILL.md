---
name: google-cloud-solution-architecture
metadata:
  category: GettingStarted
description: >-
  Interactively discovers requirements for a specific cloud workload and
  generates design recommendations and architectural guidance to build a
  multi-product solution in Google Cloud. Use when users need holistic,
  end-to-end design recommendations and architectural guidance for complex
  workloads on Google Cloud for specific use cases. Don't use this skill when
  other specialized skills exist that directly address the user-specified
  workload or use case. If the user's request is narrowly focused on a specific
  Google Cloud product, use the skills that are specific to that product. When
  users need assistance with workflows for onboarding, authentication, or
  designing foundational infrastructure, use the recipe skills that are specific
  to those workflows.
---

# Google Cloud solution-architecture process

The solution-architecture process consists of the following phases:

*  **Phase 1: Requirements discovery**. Gather detailed requirements related to
   the cloud workload or use case that the user needs assistance for.
*  **Phase 2: Solution architecture**. Use the requirements that were gathered
   in Phase 1 to generate a detailed solution architecture for the cloud
   workload or use case.
*  **Phase 3: Solution validation**. Create a plan to validate the generated
   solution, generate validation instructions and scripts, and run the
   validation.
*  **Phase 4: Solution packing and presentation**. Consolidate the generated
   content and present the solution.

## Phase 1: Requirements discovery

In this phase, you gather detailed requirements related to the workload or use
case for which the user needs assistance.

Complete the following steps strictly in the specified order:

1. Request the user to describe the functional requirements (business processes,
   activities, and use cases) of their workload.
2. Request the user to describe the non-functional requirements (security,
   privacy, compliance, reliability, disaster recovery, cost, operations,
   performance, and sustainability) of their workloads.
3. Ask the user whether the workload currently runs on other cloud providers or
   on-premises.
   * If the user answers "yes", then ask the user to describe the architecture
   of the current deployment.
4. Request the user to describe dependencies, if any, on other workloads,
   products, or tools.
5. Review the input that the user has provided so far, and check whether
   there are any ambiguities or contradictions in the input.
   * If any ambiguities or contradictions exist, then ask the user to clarify
     them. Don't proceed until all the ambiguities and contradictions
     that you identify are resolved.
6. Generate a technical decomposition of the components of the workload. The
   technical decomposition must break down the solution into logical components.
7. Request the user to approve the generated technical decomposition.
8. If the user requests changes, then generate an updated technical
   decomposition.
9. Repeat steps 7 and 8 until the user approves the generated technical
   decomposition.
10. After the user approves the technical decomposition, proceed to Phase 2.
   **Important**: Don't proceed to the next phase until the user approves the
   generated technical decomposition of the workload.

## Phase 2: Solution architecture

In this phase, you use the requirements that were gathered in Phase 1 to
generate a detailed solution architecture for the workload or for the use case
that the user described in Phase 1.

## Ground all generated content

For each task in this phase, to ensure that the generated content aligns with
the latest and official Google Cloud guidance, you must ground the generated
content by using the following resources:
* Google Developer Knowledge MCP server
  * Server: https://developerknowledge.googleapis.com/mcp
  * Tools:
    * `developerknowledge:search_documents`
    * `developerknowledge:get_documents`
* Relevant skills from https://github.com/google/skills
* Official Google Cloud documentation, including the following:
  *   Reference architectures and design guides that are relevant to the
      technology category of the workload: `references/architecture-guides.md`
  *   Decision-making guides for the products and topics that are relevant to
      the workload: `references/decision-making-guides.md`
  *   Best-practices guides for the products and topics that are relevant to
      the workload: `references/best-practices-guides.md`

For each item in the generated guidance, you must include citations to the
relevant official Google Cloud documentation pages.

### Task 2.1: Identify Google Cloud products and features required for the workload.

1. Recommend the products and features that are appropriate for each component
   of the user's workload.

  **Important**:
  * Do not recommend any deprecated products. Verify the status of the products
    by using the resources that are listed in the
    "Ground all generated content" section.
  * Do not recommend any deprecated features. Verify the status of the features
    by using the resources that are listed in the
    "Ground all generated content" section.
  * If multiple products or features can be used for a component of the
    workload, then do the following:
    * Recommend the most appropriate product or feature. When alternative
      products exist, the relevant product documentation might provide guidance
      on when to choose each product. Follow that guidance.
    * Mention the available alternative products or features.
    * Explain the pros and cons of each alternative product or feature.

2. Present the generated product recommendations and ask the user to approve the
   recommendations.
3. If the user requests changes, then make the required changes.
4. Repeat steps 2 and 3 until the user approves the product recommendations.
5. After the user approves the product recommendations, proceed to Task 2.2.

### Task 2.2: Generate an architecture diagram.

1. Generate an architecture diagram in Mermaid format: https://github.com/mermaid-js/mermaid.
2. Present the generated diagram to the user and ask the user to approve the
   architecture diagram.
3. If the user requests changes, then make the required changes.
4. Repeat steps 2 and 3 until user approves the architecture diagram.
5. After the user approves the architecture diagram, proceed to Task 2.3.

### Task 2.3: Generate an architecture description.

1. Generate a description that explains the purpose of each component, the
   relationships between the components, and the task flow or data flow.
2. Present the generated architecture description to the user and ask the user
   to approve the description.
3. If the user requests any changes, then make the required changes.
4. Repeat steps 2 and 3 until the user approves the architecture description.
5. After the user approves the architecture description, proceed to Task 2.4.

### Task 2.4: Generate design recommendations.

1. Generate design recommendations and best practices to optimally configure
   each component in the architecture based on the workload's requirements.
   **Important**:
   * When you generate design recommendations, consider the following:
     * Functional requirements that were gathered in Phase 1.
     * Non-functional requirements that were gathered in Phase 1.
   * To generate guidance for the non-functional requirements, use the following
     skills, as appropriate:
     - `google-cloud-waf-security`
     - `google-cloud-waf-reliability`
     - `google-cloud-waf-cost-optimization`
     - `google-cloud-waf-operational-excellence`
     - `google-cloud-waf-performance-optimization`
     - `google-cloud-waf-sustainability`
2. Present the generated recommendations to the user and ask whether the user
   needs any changes.
3. If the user needs changes, then make the required changes.
4. Repeat steps 2 and 3 until the user confirms that the generated design
   recommendations meet their requirements.
5. Proceed to Task 2.5.

### Task 2.5: Generate deployment guidance.

1. Generate deployment guidance, including code and instructions to enable
   the user to deploy the solution.
2. Present the generated deployment guidance to the user and ask whether the
   user needs any changes.
3. If the user requests changes, then make the required changes.
4. Repeat steps 2 and 3 until the user confirms that the generated deployment
   guidance meets their requirements.
5. Proceed to Phase 3.

## Phase 3: Solution validation

1.  Create a plan to validate the generated solution. The plan must outline the
    steps to verify that the generated solution meets the workload's
    requirements. The following are examples of validation steps:
    *   **Deployment dry-run**: Commands like `terraform plan` to preview
        the infrastructure resources that will be provisioned.
    *   **Connectivity and routing**: Verification of network paths, load
        balancer routing, and service endpoints.
    *   **Security policies**: Verification of restricted access, firewall
        rules, and IAM enforcement.
2.  Present the validation plan to the user and request feedback or approval.
3.  If the user requests changes, update the plan as required.
4.  Repeat steps 2 and 3 until the user approves the validation plan.
5.  Generate scripts or commands using tools like `curl` or `gcloud` to perform
    the steps in the approved validation plan.
6.  Request permission from the user to perform the validation checks.
7.  If the user gives permission, run the validation checks and troubleshoot any
    deployment issues.
8.  When all the validation checks pass, proceed to Phase 4.

## Phase 4: Solution packaging and presentation

In this phase, you package the generated text and code artifacts and present
the package.

1. Consolidate the text artifacts that were generated in Phase 2 and Phase 3
   into a single Markdown file named `solution-architecture-guide.md`, based on
   the template in `assets/output-template.md`.
2. Request the user's permission to write the code files in the user's
   workspace.
3. After the user gives permission, write the code files in the user's
   workspace.

## Supporting references

* https://docs.cloud.google.com/architecture/architecture-decision-records.md.txt:
  Explains when and how to use architecture decision records (ADRs) when you
  design workloads on Google Cloud.
* https://docs.cloud.google.com/architecture/deployment-archetypes.md.txt:
  Describes six Google Cloud deployment archetypes—zonal, regional,
  multi-regional, global, hybrid, and multicloud, and presents use cases and
  design considerations for each deployment archetype.
* https://docs.cloud.google.com/architecture/landing-zones.md.txt: Provides an
  overview of how to design a landing zone (also called a cloud foundation) in
  Google Cloud.
* https://docs.cloud.google.com/architecture/blueprints/security-foundations.md.txt:
  Describes best practices to deploy foundational resources, configurations, and
  capabilities to enable consistent governance, security controls, scale,
  visibility, and access to shared services across all workloads in your Google
  Cloud environment.
* https://docs.cloud.google.com/architecture/framework.md.txt: Provides
  recommendations to help architects, developers, administrators, and other
  cloud practitioners design and operate a Google Cloud topology that's secure,
  efficient, resilient, high-performing, cost-effective, and sustainable.
