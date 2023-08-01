DIR="$( cd "$( dirname "$0" )" && pwd )"

# echo "export requirements.txt"
# poetry export -o requirements.txt --without-hashes
# poetry export -o requirements-dev.txt --with dev --without-hashes
   
echo "black"
black --line-length 120 .


echo "ruff"
ruff . --fix

# echo "truncate log file"
# : > $DIR/app/logs/logs.log
echo "DONE!"
