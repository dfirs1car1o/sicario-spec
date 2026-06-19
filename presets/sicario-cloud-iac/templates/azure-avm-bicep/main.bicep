targetScope = 'resourceGroup'

@description('Deployment location')
param location string = resourceGroup().location

@description('Deployment environment')
param environment string

@description('Globally unique storage account name for the AVM example')
param storageAccountName string

// Azure Verified Modules are published to the public Bicep registry.
// Verify the latest supported module reference before production use.
// Official examples use:
//   br/public:avm/res/storage/storage-account:
module storageAccount 'br/public:avm/res/storage/storage-account:' = {
  name: 'avm-storage-${environment}'
  params: {
    name: storageAccountName
    location: location
    tags: {
      environment: environment
      managedBy: 'sicario-spec'
    }
  }
}

output storageAccountResourceId string = storageAccount.outputs.resourceId
