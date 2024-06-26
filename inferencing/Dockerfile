FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

ENV AZUREML_CONDA_ENVIRONMENT_PATH /azureml-envs/azureml-automl
ENV PATH $AZUREML_CONDA_ENVIRONMENT_PATH/bin:$PATH

COPY --from=mcr.microsoft.com/azureml/mlflow-ubuntu20.04-py38-cpu-inference:20230306.v3 /var/mlflow_resources/mlflow_score_script.py /var/mlflow_resources/mlflow_score_script.py

ENV MLFLOW_MODEL_FOLDER="mlflow-model"
# ENV AML_APP_ROOT="/var/mlflow_resources"
# ENV AZUREML_ENTRY_SCRIPT="mlflow_score_script.py"

ENV ENABLE_METADATA=true

# begin conda create
# Create conda environment
RUN conda create -p $AZUREML_CONDA_ENVIRONMENT_PATH \
    python=3.8 \
    # begin conda dependencies
    pip=22.1.2 \
    numpy~=1.22.3 \
    py-cpuinfo=5.0.0 \
    joblib=1.2.0 \
    cloudpickle=1.6.0 \
    scikit-learn=0.22.1 \
    pandas~=1.1.5 \
    py-xgboost=1.3.3 \
    holidays=0.10.3 \
    setuptools-git \
    setuptools=65.5.1 \
    wheel=0.38.1 \
    pyopenssl=23.2.0 \
    'psutil>5.0.0,<6.0.0' \
    # end conda dependencies
    -c conda-forge -c pytorch -c anaconda && \
    conda run -p $AZUREML_CONDA_ENVIRONMENT_PATH && \
    conda clean -a -y
# end conda create

# begin pip install
# Install pip dependencies
RUN pip install  \
                # begin pypi dependencies
                'cryptography==41.0.0' \
                'azureml-core==1.52.0' \
                'azureml-mlflow==1.52.0' \
                'azureml-pipeline-core==1.52.0' \
                'azureml-telemetry==1.52.0' \
                'azureml-interpret==1.52.0' \
                'azureml-responsibleai==1.52.0' \
                'azureml-automl-core==1.52.0.post1' \
                'azureml-automl-runtime==1.52.0.post1' \
                'azureml-train-automl-client==1.52.0' \
                'azureml-train-automl-runtime==1.52.0' \
                'azureml-dataset-runtime==1.52.0' \
                'azureml-defaults==1.52.0' \
                'inference-schema' \
                'fbprophet==0.7.1' \
                'pystan==2.19.1.1' \
                'notebook==6.4.9' \
                'mltable>=1.0.0'
                # end pypi dependencies
# end pip install