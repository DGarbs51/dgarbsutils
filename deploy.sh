cd ~/code/opensource/py-utils
isort .
black . --line-length=120
python3 -m build
python3 -m twine upload --repository pypi dist/*
python3 -m twine upload --repository nexus dist/*
pip install dgarbsutils --upgrade
rm -rf deploy
pip install --target="deploy/python" dgarbsutils --upgrade
pip install --target="deploy/python" psycopg2-binary --upgrade
pip install --target="deploy/python" boto3 --upgrade
pip install --target="deploy/python" botocore --upgrade
cd deploy
zip -r python.zip python
aws s3 cp python.zip s3://dev-gwf-businessappdelivery-ui-us-east-1/dgarbsutils/python.zip --profile nonprod
aws lambda publish-layer-version \
    --layer-name dgarbsutils \
    --content S3Bucket=dev-gwf-businessappdelivery-ui-us-east-1,S3Key=dgarbsutils/python.zip \
    --compatible-runtimes python3.7 python3.8 python3.9 python3.10\
    --profile nonprod
aws s3 cp python.zip s3://uat-gwf-businessappdelivery-ui-us-east-1/dgarbsutils/python.zip --profile prod
aws lambda publish-layer-version \
    --layer-name dgarbsutils \
    --content S3Bucket=uat-gwf-businessappdelivery-ui-us-east-1,S3Key=dgarbsutils/python.zip \
    --compatible-runtimes python3.7 python3.8 python3.9 python3.10\
    --profile prod
