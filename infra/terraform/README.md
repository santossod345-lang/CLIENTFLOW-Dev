Terraform scaffold

Estrutura:
- `main.tf` - ponto de entrada comum (providers / backend placeholders)
- `variables.tf` - variáveis reutilizáveis
- `environments/` - configurações por ambiente (dev/staging/prod)
- `modules/` - módulos reutilizáveis

Este scaffold é intencionalmente genérico. Configure o provider (AWS/GCP/Azure) e o backend remoto (S3/GCS/Azure Storage) antes de aplicar.
