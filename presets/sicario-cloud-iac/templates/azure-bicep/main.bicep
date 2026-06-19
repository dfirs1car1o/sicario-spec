targetScope = 'resourceGroup'

@description('Deployment location')
param location string = resourceGroup().location

@description('Deployment environment')
param environment string

@description('Required SicarioSpec tags: owner, system, environment, data-classification, retention, compliance-scope, cost-center, source-repo, managed-by, and expires-on for temporary resources')
param tags object = {}

// SicarioSpec starter: add Azure resources intentionally.
// Required before merge:
// - managed identity / least privilege RBAC
// - private networking where feasible
// - diagnostic settings
// - encryption and Key Vault integration where applicable
// - resource tags from the approved taxonomy
// - Azure Policy compatibility

output sicarioIacProfile string = 'cloud-iac'
