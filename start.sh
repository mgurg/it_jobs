#!/usr/bin/bash
cd "${0%/*}"
source /home/lambda/it_jobs/.venv/bin/activate
#PATH=$PATH:/home/lambda/it_jobs/.venv/bin/python
#export PATH
echo "Activated"
#./.venv/bin/python app.py
python /home/lambda/it_jobs/app.py
echo "Done"

