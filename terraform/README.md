# Optional Terraform

Terraform tidak wajib untuk hackathon 4 jam. Pakai ini hanya kalau butuh EC2 reproducible.

Rekomendasi default:

- `t3.micro` atau `t3.small`
- no NAT Gateway
- no ALB
- no RDS
- no EKS
- no provisioned Bedrock

Deploy manual masih lebih cepat:

1. Buat EC2 Ubuntu/Amazon Linux.
2. Install Docker/Python.
3. Export env Bedrock + Datadog.
4. Run app.

