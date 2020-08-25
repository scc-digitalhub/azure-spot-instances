locals {
  number_of_disks = 1
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                            = "${var.prefix}-vm"
  location                        = azurerm_resource_group.rs.location
  resource_group_name             = azurerm_resource_group.rs.name
  network_interface_ids           = [azurerm_network_interface.nic.id]
  size                            = var.vm_size
  priority                        = var.priority
  max_bid_price                   = var.max_bid_price
  admin_username                  = var.username
  computer_name                   = var.prefix
  disable_password_authentication = true
  eviction_policy                 = "Deallocate"
  tags = {
    "restart" = "false"
    
  }

  admin_ssh_key {
    username = var.username
    public_key = file(var.ssh_public_key)
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_disk {
    name              = "${var.prefix}-OsDisk"
    caching           = "ReadWrite"
    storage_account_type = var.osdisk_type
  }

}
