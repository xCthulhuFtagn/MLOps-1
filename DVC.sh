dvc init

dvc remote add -d myremote s3://GradientBoostingRegressor
dvc remote add -d myremote s3://GradientBoostingClassifier
dvc remote modify myremote endpointurl http://localhost:9000
dvc remote modify myremote access_key_id amogus
dvc remote modify myremote secret_access_key sussy_key
