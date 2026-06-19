package sicario.iac

deny[msg] {
  input.resource[_].type == "azurerm_storage_account"
  input.resource[_].values.allow_nested_items_to_be_public == true
  msg := "Azure Storage public nested items must be disabled unless an approved exception exists."
}

deny[msg] {
  input.resource[_].type == "aws_s3_bucket_public_access_block"
  input.resource[_].values.block_public_acls == false
  msg := "S3 public ACLs must be blocked unless an approved exception exists."
}
