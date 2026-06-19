targetScope = 'resourceGroup'

@description('Deployment location')
param location string = resourceGroup().location

@description('Deployment environment')
param environment string

// SicarioSpec starter: add Azure resources intentionally.
// Required before merge:
// - managed identity / least privilege RBAC
// - private networking where feasible
// - diagnostic settings
// - encryption and Key Vault integration where applicable
// - Azure Policy compatibility

output sicarioIacProfile string = 'cloud-iac'

