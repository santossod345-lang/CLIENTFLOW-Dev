Automação de Infraestrutura (Infra)

Esta pasta contém o scaffold inicial de IaC (Terraform) e instruções para os ambientes `dev`, `staging` e `prod`.

Objetivo:
- Fornecer módulos e ambientes reutilizáveis.
- Suportar pipelines GitOps/CI para deploys automatizados.

Uso rápido:
1. Instale Terraform 1.4+.
2. Navegue até um ambiente, ex: `infra/terraform/environments/dev`.
3. Ajuste o backend e provedores em `infra/terraform/main.tf`.
4. Execute `terraform init` e `terraform apply` (apenas em ambientes controlados).

NOTA: Este é um scaffold inicial — adapte provedores (AWS/GCP/Azure) e backends remotos conforme sua infraestrutura.

AWS Quickstart
1. Configure `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e `AWS_REGION` no seu ambiente ou no GitHub Secrets.
2. Use o script `infra/bootstrap_remote_state.sh` para criar o S3 bucket e a tabela DynamoDB para locking:

```bash
chmod +x infra/bootstrap_remote_state.sh
ENV=dev TF_STATE_BUCKET=my-tf-state-bucket-DEV TF_LOCK_TABLE=my-tf-lock-table-DEV infra/bootstrap_remote_state.sh
```

3. Depois de criar o bucket, copie `infra/terraform/environments/dev/backend.tf.example` para `infra/terraform/environments/dev/backend.tf` e atualize `bucket` e `dynamodb_table`.

