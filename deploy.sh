cd ~/code/opensource/py-utils
isort .
black . --line-length=120
# python3.7 -m build
# python3.9 -m build
# python3.10 -m build
python3.11 -m build
# python3.7 -m twine upload --repository pypi dist/*
# python3.9 -m twine upload --repository pypi dist/*
# python3.10 -m twine upload --repository pypi dist/*
python3.11 -m twine upload --repository pypi dist/*
pip3.7 install dgarbsutils --upgrade
pip3.9 install dgarbsutils --upgrade
pip3.10 install dgarbsutils --upgrade
pip3.11 install dgarbsutils --upgrade
rm -rf deploy
# pip3.7 install --target="deploy/python/lib/python3.7/site-packages" dgarbsutils --upgrade
# pip3.9 install --target="deploy/python/lib/python3.9/site-packages" dgarbsutils --upgrade
pip3.10 install --target="deploy/python/lib/python3.10/site-packages" dgarbsutils --upgrade
pip3.11 install --target="deploy/python/lib/python3.11/site-packages" dgarbsutils --upgrade
# pip3.7 install --target="deploy/python/lib/python3.7/site-packages" psycopg2-binary --upgrade
# pip3.9 install --target="deploy/python/lib/python3.9/site-packages" psycopg2-binary --upgrade
pip3.10 install --target="deploy/python/lib/python3.10/site-packages" psycopg2-binary --upgrade
pip3.11 install --target="deploy/python/lib/python3.11/site-packages" psycopg2-binary --upgrade
# pip3.7 install --target="deploy/python/lib/python3.7/site-packages" boto3 --upgrade
# pip3.9 install --target="deploy/python/lib/python3.9/site-packages" boto3 --upgrade
# pip3.10 install --target="deploy/python/lib/python3.10/site-packages" boto3 --upgrade
# pip3.11 install --target="deploy/python/lib/python3.11/site-packages" boto3 --upgrade
# pip3.7 install --target="deploy/python/lib/python3.7/site-packages" botocore --upgrade
# pip3.9 install --target="deploy/python/lib/python3.9/site-packages" botocore --upgrade
# pip3.10 install --target="deploy/python/lib/python3.10/site-packages" botocore --upgrade
# pip3.11 install --target="deploy/python/lib/python3.11/site-packages" botocore --upgrade
cd deploy
zip -r python.zip python
aws s3 cp python.zip s3://dev-gwf-businessappdelivery-ui-us-east-1/dgarbsutils/python.zip --profile nonprod
aws lambda publish-layer-version \
    --layer-name dgarbsutils \
    --content S3Bucket=dev-gwf-businessappdelivery-ui-us-east-1,S3Key=dgarbsutils/python.zip \
    --compatible-runtimes python3.10 python3.11 \
    --no-paginate \
    --profile nonprod
aws s3 cp python.zip s3://uat-gwf-businessappdelivery-ui-us-east-1/dgarbsutils/python.zip --profile prod
aws lambda publish-layer-version \
    --layer-name dgarbsutils \
    --content S3Bucket=uat-gwf-businessappdelivery-ui-us-east-1,S3Key=dgarbsutils/python.zip \
    --compatible-runtimes python3.10 python3.11 \
    --no-paginate \
    --profile prod
