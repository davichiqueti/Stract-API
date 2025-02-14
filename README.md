# stract-challenge

Essa é uma etapa de um processo seletivo para desenvolvedor Python na Stract. Criando integrações com uma API da empresa e gerando relatórios em formato CSV com dados em tempo real. [Veja as instruções aqui](/instructions.txt)

Desde 2023, desenvolvo ferramentas profissionais para integração, extração e processamento de dados da web, utilizando desde integração com APIs até Web Scraping de páginas HTML diariamente.

Fiquei contente pela oportunidade de realizar esse teste. Acredito que eu poderia agregar muito à Stract e gostaria de fazer parte de sua equipe.

## Aplicação Publicada

[stract-api.onrender.com](https://stract-api.onrender.com/)

## Rodando a Aplicação

Primeiramente, é necessário instalar as dependências do projeto. Para isso, basta utilizar o comando abaixo no diretório base.

```bash
# Fica à criterio a utilização um ambiente virtual ou não.
# https://docs.python.org/3/library/venv.html#creating-virtual-environments
pip install -r requirements.txt
```

Feito isso, basta entrar no diretório do código fonte e rodar comando padrão do **Flask**

```bash
cd src
flask run --port=80     # Porta padrão do protocolo HTTP
```

**Pronto! A aplicação estará disponivel como um servidor local, acessível em http://localhost/**

## Observações Importantes

- **TODOS** os dados de plataformas, campos, contas e insights são carregados em tempo real quando um recurso é acessado. **NENHUM** recurso utiliza alguma estratégia de pré carregamento ou caching. Seguindo as especificações passadas no desafio, o que acaba gerando uma latencia na resposta por conta dos recursos a serem carregados.

- O token de autenticação foi colocado de forma Hard-Coded no client criado para a API, apenas para tornar o processo mais simples para o avaliador do teste. Em um projeto real, eu utilizaria uma váriavel de ambiente.

## API Client

Para facilitar o uso de recursos da API da Stract, criei um Client que abstrai a integração e provê métodos para acessar os recursos de forma mais simples. Encapsula a lógica para autorização e realização de requisições, além de lidar automaticamente com processos de paginação para acesso aos recursos.

Confira a implementação aqui: [Stract API Client Class](/src/modules/stract_api_client.py)
