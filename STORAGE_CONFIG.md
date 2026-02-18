# ClientFlow - Configuração de S3/Digital Ocean Spaces para Uploads

## Atualmente: Filesystem Local

Backend salva logos em:
```
/uploads/logos/
```

**Problema em produção**: Railway usa filesystem efêmero (dados perdidos ao reiniciar).

## Solução 1: Digital Ocean Spaces (Recomendado)

### Passo 1: Criar Espaço no Digital Ocean

1. Acesse [console.digitalocean.com](https://console.digitalocean.com)
2. Vá para "Spaces"
3. Clique "Create Space"
4. Configure:
   - Name: `clientflow-logos`
   - Region: `NYC` (ou mais próximo)
   - Acesso: `Private`
5. Clique "Create Space"

### Passo 2: Gerar Access Keys

1. Clique no seu avatar → "API"
2. Vá para "Tokens" → "Spaces Keys"
3. Gere nova key
4. Copie:
   - `Access Key`
   - `Secret Key`

### Passo 3: Instalar boto3

```bash
pip install boto3
```

Adicionar a `requirements.txt`:
```
boto3==1.28.0
```

### Passo 4: Atualizar Backend

Criar arquivo `backend/storage.py`:

```python
import boto3
from botocore.exceptions import ClientError
import os

class S3Storage:
    def __init__(self):
        self.client = boto3.client(
            's3',
            region_name=os.getenv('DO_REGION', 'nyc3'),
            endpoint_url=f"https://{os.getenv('DO_REGION', 'nyc3')}.digitaloceanspaces.com",
            aws_access_key_id=os.getenv('DO_SPACES_KEY'),
            aws_secret_access_key=os.getenv('DO_SPACES_SECRET'),
        )
        self.bucket = os.getenv('DO_SPACES_BUCKET', 'clientflow-logos')
    
    def upload_file(self, file_bytes: bytes, filename: str, public: bool = True) -> str:
        """Upload arquivo para Digital Ocean Spaces"""
        try:
            key = f"logos/{filename}"
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_bytes,
                ACL='public-read' if public else 'private',
                ContentType='image/jpeg',  # Ajustar conforme tipo
            )
            
            # Retornar URL pública
            return f"https://{self.bucket}.nyc3.digitaloceanspaces.com/{key}"
        except ClientError as e:
            raise Exception(f"Erro ao upload para Spaces: {e}")
    
    def delete_file(self, filename: str) -> bool:
        """Deletar arquivo do Spaces"""
        try:
            key = f"logos/{filename}"
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key,
            )
            return True
        except ClientError as e:
            raise Exception(f"Erro ao deletar arquivo: {e}")


# Usar no router:
# storage = S3Storage()
# logo_url = storage.upload_file(file_contents, filename)
```

### Passo 5: Atualizar Router

Em `backend/routers/empresa.py`, substituir:

```python
# Antes: Salvar em filesystem
with open(filepath, "wb") as f:
    f.write(contents)

# Depois: Salvar em Spaces
from backend.storage import S3Storage
storage = S3Storage()
logo_url = storage.upload_file(contents, filename)
```

### Passo 6: Railway Variables

Adicionar ao Railway:

```
DO_SPACES_KEY=sua-access-key
DO_SPACES_SECRET=sua-secret-key
DO_SPACES_BUCKET=clientflow-logos
DO_REGION=nyc3
```

---

## Solução 2: AWS S3

### Passo 1: IAM User

1. Acesse AWS Console → IAM
2. Crie user: `clientflow-backend`
3. Permissões: Linha abaixo
4. Copie Access Key + Secret Key

### Passo 2: Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::clientflow-logos/*"
    }
  ]
}
```

### Passo 3: Código Similar

```python
import boto3

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1',
)

# Upload
s3.put_object(
    Bucket='clientflow-logos',
    Key=f'logos/{filename}',
    Body=file_bytes,
    ContentType='image/jpeg',
    ACL='public-read',
)

# URL
url = f"https://clientflow-logos.s3.us-east-1.amazonaws.com/logos/{filename}"
```

---

## Solução 3: Cloudinary (SaaS, Mais Fácil)

### Passo 1: Criar conta

Acesse [cloudinary.com](https://cloudinary.com)
- Sign up (gratuito)
- Copia `CLOUDINARY_URL`

### Passo 2: Instalar

```bash
pip install cloudinary
```

### Passo 3: Usar

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Upload
response = cloudinary.uploader.upload(
    file_bytes,
    folder='clientflow/logos',
    resource_type='auto'
)

logo_url = response['secure_url']
```

---

## Qual Escolher?

| Solução | Custo | Facilidade | Pros | Contras |
|---------|-------|-----------|------|---------|
| **Filesystem** | Grátis | ⭐⭐⭐⭐⭐ | Simples | Perde dados ao reiniciar |
| **Digital Ocean Spaces** | $5/mês | ⭐⭐⭐⭐ | CDN integrado | Outra conta (se não usar DO droplet) |
| **AWS S3** | $0.023/GB | ⭐⭐⭐ | Escalável | Complexo, pode ficar caro |
| **Cloudinary** | Gratuito até 25GB | ⭐⭐⭐⭐ | Muito fácil | Free tier limitado |

### Recomendação: **Digital Ocean Spaces**
- Se está usando Railway: Use S3/Spaces com Railway (ambos cloud-native)
- Preço justo (5 USD/mês)
- CDN integrado (rápido em todo mundo)
- Integração simples com boto3

---

## Implementação Futura

Para agora, o sistema roda com **filesystem** (bom para MVP/desenvolvimento).

**Para escalar para produção com múltiplas instâncias:**
1. Implementar Spaces/S3
2. Remover filesystem upload
3. Testar em Railway
4. Adicionar compressão de imagem automática

---

## Código de Exemplo Completo - Digital Ocean Spaces

**backend/storage.py:**
```python
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path

class StorageService:
    """Abstração de storage - Filesystem ou Spaces"""
    
    USE_SPACES = os.getenv('USE_SPACES', 'false').lower() == 'true'
    
    def __init__(self):
        if self.USE_SPACES:
            self.client = boto3.client(
                's3',
                region_name=os.getenv('DO_REGION', 'nyc3'),
                endpoint_url=f"https://{os.getenv('DO_REGION', 'nyc3')}.digitaloceanspaces.com",
                aws_access_key_id=os.getenv('DO_SPACES_KEY'),
                aws_secret_access_key=os.getenv('DO_SPACES_SECRET'),
            )
            self.bucket = os.getenv('DO_SPACES_BUCKET')
        else:
            self.local_dir = Path('uploads/logos')
            self.local_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_logo(self, file_bytes: bytes, filename: str) -> str:
        """Upload logo e retornar URL"""
        if self.USE_SPACES:
            try:
                key = f"logos/{filename}"
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=file_bytes,
                    ACL='public-read',
                )
                return f"https://{self.bucket}.nyc3.digitaloceanspaces.com/{key}"
            except ClientError as e:
                raise Exception(f"Upload failed: {e}")
        else:
            # Fallback: filesystem local
            filepath = self.local_dir / filename
            with open(filepath, 'wb') as f:
                f.write(file_bytes)
            return f"/uploads/logos/{filename}"


# Usar no router:
storage = StorageService()
logo_url = storage.upload_logo(contents, filename)
```

---

## Próxima Implementação

Após MVP em produção, você pode:
1. Switch para Spaces com 2 linhas de config
2. Adicionar cache em Cloudflare
3. Implementar otimização de imagem (ImageMagick)
4. CDN automático para logos
