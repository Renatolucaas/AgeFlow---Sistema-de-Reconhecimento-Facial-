🎯 Projeto: Reconhecimento Facial (Arquitetura Serverless)
📄 Visão Geral
Sistema serverless que recebe imagens via frontend, processa com AWS Rekognition para estimar faixa etária e entrega feedback ao usuário de forma assíncrona.

Componentes Principais
Categoria	Serviço AWS	Função
Acesso/Computação	API Gateway, AWS Lambda (Ingest e Process)	Recebe requisições e executa lógica de negócio
Armazenamento/BD	Amazon S3, Amazon DynamoDB	Armazena imagens e metadados
Mensageria	Amazon SQS (3 filas), Amazon SNS	Gerencia fluxo assíncrono e notificações
Análise	Amazon Rekognition	Análise de visão computacional
Monitoramento	CloudWatch, AWS X-Ray	Logs, métricas e tracing
🏗️ Arquitetura: Fluxo de Processamento
Ingestão: API Gateway recebe requisição e aciona Lambda Ingest

Upload Otimizado: Lambda Ingest gera URL Pré-assinada para S3

Vantagem: Reduz custos e tempo de execução da Lambda

Após upload, envia mensagem para fila SQS fotos_para_processar

Processamento: Fila aciona Lambda Process

Baixa imagem do S3, aciona Rekognition e armazena resultados no DynamoDB

Notificação:

Sucesso: envia para fila resultados_processados

Opcional: SNS para notificações de alerta

🛡️ Segurança e Privacidade
Área	Prática	Detalhamento
Criptografia	HTTPS + SSE	Criptografia em trânsito e repouso no S3
Retenção	Lifecycle + TTL	S3: remover após 24h/7d, DynamoDB TTL: 30 dias
Acesso	IAM (Menor Privilégio)	Controle via Cognito/JWT + roles específicas
Permissões IAM:

Lambda Ingest: s3:PutObject, sqs:SendMessage

Lambda Process: s3:GetObject, rekognition:DetectFaces, dynamodb:PutItem/GetItem, sqs:SendMessage

⚙️ Configuração e Resiliência (SQS)
Parâmetro	Valor	Justificativa
Tipo SQS	Standard	Ordenação não é requisito crítico
Filas	fotos_para_processar, resultados_processados, falhas_processamento (DLQ)	Separação de concerns e tratamento de falhas
maxReceiveCount	3	Tentativas antes de mover para DLQ
VisibilityTimeout	Tempo Lambda + 30s (ex: 90s)	Evita processamento duplicado e garante reprocessamento
Batch Size	1	Processamento individual para evitar timeouts
📊 Observabilidade
Logs: CloudWatch Logs para todas as Lambdas

Alertas: CloudWatch Metrics para DLQ > 0

Tracing: AWS X-Ray para análise end-to-end

Notificações: SNS para alertas críticos

🚀 CI/CD e Ambientes
Branches:

dev: push direto

hom: via pull request

main: produção

Deploy:

GitHub Actions + SAM CLI

Stacks separadas: myapp-dev, myapp-hom, myapp-prod

Autenticação via OIDC Roles (sem secrets permanentes)

🧪 Testes e Validação
Estratégia de Testes:

Unitários: pytest para funções Lambda

Integração: moto para simulação AWS

Cenários de Falha:

Imagens corrompidas → validação DLQ

Retry behavior e visibility timeout

Timeouts e exceções de serviços
