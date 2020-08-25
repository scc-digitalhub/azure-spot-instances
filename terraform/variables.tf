variable "prefix" {
  description = "The Prefix used for all resources in this example"
}

variable "location" {
  description = "The Azure Region in which the resources in this example should exist"
  default = "westeurope"
}

variable "max_bid_price" {
  description = "The maximum price you're willing to pay for this Virtual Machine, in US Dollars; which must be greater than the current spot price."
  default = "-1"
}

variable "priority" {
  description = "Specifies the priority of this Virtual Machine. Possible values are Regular and Spot"
  default = "Regular"
}

variable "vm_size" {
  description = "The SKU which should be used for this Virtual Machine, such as Standard_F2."
}

variable "datadisk_size" {
  description = "The size of the Managed Disk in gigabytes"
}

variable "datadisk_type" {
  description = "The Type of Storage Account which should back this the Internal OS Disk. Possible values are Standard_LRS, StandardSSD_LRS and Premium_LRS. Changing this forces a new resource to be created."
}

variable "osdisk_type" {
  description = "The Type of Storage Account which should back this the Internal OS Disk. Possible values are Standard_LRS, StandardSSD_LRS and Premium_LRS. Changing this forces a new resource to be created."
}

variable "ssh_public_key" {
  description = "The Public Key which should be used for authentication, which needs to be at least 2048-bit and in ssh-rsa format. Changing this forces a new resource to be created."
}

variable "ssh_private_key" {
  description = "The Private Key which should be used for authentication, which needs to be at least 2048-bit and in ssh-rsa format. Changing this forces a new resource to be created."
}

variable "tags" {
  description = "A mapping of tags which should be assigned to this Virtual Machine."
}

variable "username" {
}

variable "subscription_id" {
}

variable "slack_api_token"{

}

variable "slack_webhook_url" {

}
