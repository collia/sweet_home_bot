*Create docker image*
docker build --tag sweet_home_bot .

*Run script*
docker run -ti --mount type=bind,source="$(pwd)"/config,target=/usr/local/app/config sweet_home_bot
