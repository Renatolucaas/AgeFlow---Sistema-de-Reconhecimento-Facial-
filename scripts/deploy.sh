#!/bin/bash

# Configurações
PROJECT_NAME="age-estimation-system"
ENVIRONMENT="dev"
REGION="us-east-2"
STACK_NAME="$PROJECT_NAME-$ENVIRONMENT"
NOTIFICATION_EMAIL="renatolucas@ucl.br"  # ⬅️ ADICIONE ESTA LINHA

echo "🚀 Implantando sistema de estimativa de idade..."

# Build do projeto
echo "📦 Empacotando aplicação..."
sam build --use-container

# Deploy
echo "☁️ Implantando na AWS..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        ProjectName=$PROJECT_NAME \
        Environment=$ENVIRONMENT \
        NotificationEmail=$NOTIFICATION_EMAIL \  # ⬅️ ADICIONE ESTE PARÂMETRO
    --no-confirm-changeset

echo "✅ Implantação concluída!"

# Obter URLs de saída
echo "🔗 Obtendo URLs do sistema..."
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output table

echo "🎉 Sistema implantado com sucesso!"