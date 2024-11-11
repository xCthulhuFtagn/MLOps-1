
# README for MLOps Project Repository

## Overview
This repository contains an MLOps project that implements a machine learning model service with REST and gRPC APIs. The service enables training, prediction, and management of machine learning models, with a focus on ease of use, security, and comprehensive logging.

## Key Features
1. **Training and Prediction APIs**
   - **gRPC**: High-performance remote procedure call (RPC) system supporting model training, prediction, and management.
   - **REST**: Provides RESTful APIs for similar functionalities for broader compatibility.

2. **Dashboard**
   - Interactive dashboard (using `Streamlit` or `Gradio`) for monitoring and interacting with the model service, allowing users to visualize the model’s performance and control its training and prediction.

3. **Logging and Monitoring**
   - Comprehensive logging tracks all key actions, errors, and system status, ensuring traceability and aiding in debugging.

4. **Authentication**
   - User authentication implemented to secure the training and prediction endpoints.

5. **Health Check**
   - Endpoint to check the health status of the service.

## Repository Structure
```
MLOps-Project/
├── grpc-server/                 # gRPC server and related files
│   ├── main.py                  # gRPC server entry point
│   ├── proto/                   # Protocol buffer definitions
│   └── generated/               # Generated gRPC code from proto files
├── rest-server/                 # REST server files
│   └── main.py                  # REST server entry point
├── modules/
│   ├── services/
│   │   ├── auth_service.py      # Authentication service
│   │   └── model_trainer_service.py  # Model training and management service
│   └── utils/
│       └── dict_to_file.py      # Utility functions for dictionary I/O
├── models/                      # Directory for storing trained model files
├── logs/                        # Log files for the project
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MLOps-Project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate gRPC Code (if necessary)**:
   Run the following command to generate gRPC stubs if there are any updates to `.proto` files:
   ```bash
   ./generate-proto.sh
   ```

4. **Configure Environment**:
   - Ensure the paths for storing models and log files are correctly set in the configuration files or directly in code (e.g., `model_dir_path` in `model_train_service.py`).

## Running the Servers
### Start the gRPC Server
```bash
python grpc-server/main.py
```
This will start the gRPC server on the default port (e.g., `50051`).

### Start the REST Server
```bash
python rest-server/main.py
```
This will start the REST server, making it accessible for HTTP requests.

## Using the API
### gRPC API
The gRPC API allows for high-performance interactions:
- **Train Model**: Train a machine learning model with customizable hyperparameters.
- **Predict**: Obtain predictions from a trained model.
- **Health Check**: Get the status of the server.

### REST API
The REST API provides similar functionalities for broader compatibility. Access endpoints like:
- **POST /train_model**: Trains a specified model.
- **POST /predict**: Returns predictions for provided data.
- **GET /healthcheck**: Returns the server status.

For more details, refer to the `Swagger` documentation.

## Dashboard
An interactive dashboard can be launched to monitor and manage model status and performance using `Streamlit` or `Gradio`:
```bash
python dashboard.py
```

## Logging
Detailed logging is available for all core modules:
- **Location**: Log files are stored in `logs/`
- **Files**:
  - `grpc_server.log` for gRPC-related operations
  - `rest_server.log` for REST API interactions
  - `auth_service.log` for authentication events
  - `model_train_service.log` for training and prediction logs

## Testing
To test the gRPC and REST APIs, sample client scripts are provided. Ensure the servers are running, then execute the client scripts to verify the functionality of each endpoint.

## License
This project is licensed under the MIT License.

## Contact
For questions or support, please reach out to [your-email@example.com].
