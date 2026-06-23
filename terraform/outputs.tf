output "public_ip" {
  value = aws_instance.this.public_ip
}

output "api_url" {
  value = "http://${aws_instance.this.public_ip}:8080"
}

