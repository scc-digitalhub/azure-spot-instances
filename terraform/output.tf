output "instance_ip_addr" {
  value       = data.azurerm_public_ip.pip.ip_address
  description = "The public IP address of the server instance."
}
