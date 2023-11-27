# MAC0352-EP2-Pacman

## Organização do projeto

Este projeto está dividido em 3 diretórios principais:

### server

Este diretório possui o arquivo `main.py`, que roda o servidor. Para executar, basta rodar o comando:

`python3 main.py <port>`

### client

Este diretório possui o arquivo `client.py`, que representa o cliente. Para executar, basta rodar o comando:

`python3 client.py <host_ip> <host_port> <TCP or UDP>`

### communication

Aqui temos arquivos que salva o banco de dados, que realiza a conexão entre o servidor e o cliente, e administra o jogo.

- `server_communication`: estrutura de dados abstraída que manda e recebe pacotes do cliente

- `client_communication`: estrutura de dados abstraída que manda e recebe pacotes do servidor

- `server_database`: guarda os dados que devem ser persistentes

- `game.py`: guarda toda a lógica do jogo. Tem as classes principais `Pacman` e `Ghost`, que administram toda a troca de pacotes dentro do jogo.

- `protocol.py`: é uma classe que serve como abstração para o tipo de conexão UDP ou TCP que o cliente pede

## Logging

O logging pode ser achado em `./communication/server.log` e `./communication/client.log`.

## Vídeo

O vídeo com uma breve explicação está abaixo:

https://www.loom.com/share/125f2be2264d4e058d82d9fc90aca1f3