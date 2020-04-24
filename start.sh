PROJECT_PATH=$1

pushd $PROJECT_PATH
pm2 delete marvin-bot
git pull
pm2 start ecosystem.config.js
popd