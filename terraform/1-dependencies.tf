provider "azurerm" {
  subscription_id = var.subscription_id
  features {}
}

resource "azurerm_resource_group" "rs" {
  name     = var.resource_group_name
  location = var.location
  tags      = var.tags
}

resource "azurerm_virtual_network" "vnet" {
  name                = "${var.prefix}-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rs.location
  resource_group_name = azurerm_resource_group.rs.name
}

resource "azurerm_subnet" "snet" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.rs.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes       = ["10.0.2.0/24"]
}

resource "azurerm_network_interface" "nic" {
  name                = "${var.prefix}-nic"
  location            = azurerm_resource_group.rs.location
  resource_group_name = azurerm_resource_group.rs.name

  ip_configuration {
    name                          = "${var.prefix}-private_ip"
    subnet_id                     = azurerm_subnet.snet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}

resource "azurerm_public_ip" "pip" {
  name                = "${var.prefix}-public_ip"
  resource_group_name = azurerm_resource_group.rs.name
  location            = azurerm_resource_group.rs.location
  allocation_method   = "Static"
}

data "azurerm_public_ip" "pip" {
  name                = azurerm_public_ip.pip.name
  resource_group_name = azurerm_resource_group.rs.name
}

resource "azurerm_network_security_group" "nsg" {
  name                = "${var.prefix}-nsg"
  location            = azurerm_resource_group.rs.location
  resource_group_name = azurerm_resource_group.rs.name
  security_rule {
    access                     = "Allow"
    direction                  = "Inbound"
    name                       = "SSH"
    priority                   = 100
    protocol                   = "Tcp"
    source_port_range          = "*"
    source_address_prefix      = "*"
    destination_port_range     = "22"
    destination_address_prefix = azurerm_network_interface.nic.private_ip_address
  }
}

resource "azurerm_network_interface_security_group_association" "nsg" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_managed_disk" "external" {
  count                = local.number_of_disks
  name                 = "${var.prefix}-DataDisk${count.index+1}"
  location             = azurerm_resource_group.rs.location
  resource_group_name  = azurerm_resource_group.rs.name
  storage_account_type = var.datadisk_type
  create_option        = "Empty"
  disk_size_gb         = var.datadisk_size
}

resource "azurerm_virtual_machine_data_disk_attachment" "external" {
  count              = local.number_of_disks
  managed_disk_id    = azurerm_managed_disk.external.*.id[count.index]
  virtual_machine_id = azurerm_linux_virtual_machine.vm.id
  lun                = 10+count.index
  caching            = "ReadWrite"

  provisioner "remote-exec" {
    inline = ["sudo apt-get -qq install python -y"]
  }

  connection {
    private_key = file(var.ssh_private_key)
    user        = var.username
    host        = data.azurerm_public_ip.pip.ip_address
  }

  provisioner "local-exec" {
  command = <<EOT
    vm.ini;
    echo "[vm]" | tee -a vm.ini;
    echo "${data.azurerm_public_ip.pip.ip_address} ansible_user=${var.username} ansible_ssh_private_key_file=${var.ssh_private_key}" | tee -a vm.ini;
    echo "[vm:vars]" | tee -a vm.ini;
    echo "ansible_python_interpreter=/usr/bin/python3" | tee -a vm.ini;
    export ANSIBLE_HOST_KEY_CHECKING=False;
    ansible-playbook -u ${var.username} --private-key ${var.ssh_private_key} --extra-vars "slack_api_url=${var.slack_webhook_url} slack_api_token=${var.slack_api_token} slack_channel=${var.slack_channel} gpu=${var.gpu}" -i vm.ini ../ansible/install_env.yaml
    EOT
  }
}
