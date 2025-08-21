# Local Development and Deployment Steps

This guide provides the necessary steps to test the application locally using Docker, set up required resources in Azure, and configure GitHub for Continuous Integration/Continuous Deployment (CI/CD).

---

## 🚀 Test Locally with Docker

To build and run the application locally, use the following Docker commands:

1.  **Build the Docker image:**
    ```bash
    docker build -t <folder_name>:local .
    ```

2.  **Run the container:**
    ```bash
    docker run --rm -p 8501:8501 --env-file .env <folder_name>:local
    ```

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8501`.

---

## ☁️ Azure Resources (One-Time Setup)

Follow these steps in your Azure CLI to set up the necessary infrastructure.

1.  **Define Variables:**
    Set the following environment variables for consistent use in subsequent commands.
    ```bash
    RG=<your-resource-group-name>
    LOCATION=<region>
    ACR_NAME=<youracr12345>        # Must be globally unique and lowercase
    PLAN_NAME=<plan-name>
    WEBAPP_NAME=<web-app-name>     # Must be unique in Azure
    IMAGE_NAME=<image-name>        # Repository name inside ACR
    ```

2.  **Create Resources:**
    ```bash
    # Create a new resource group
    az group create -n $RG -l $LOCATION

    # Create Azure Container Registry (ACR)
    az acr create -n $ACR_NAME -g $RG --sku Basic

    # Enable admin user and retrieve credentials
    az acr update -n $ACR_NAME --admin-enabled true
    ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME -g $RG --query "loginServer" -o tsv)
    ACR_USERNAME=$(az acr credential show -n $ACR_NAME --query "username" -o tsv)
    ACR_PASSWORD=$(az acr credential show -n $ACR_NAME --query "passwords[0].value" -o tsv)

    # Create App Service Plan (Linux)
    az appservice plan create -n $PLAN_NAME -g $RG --is-linux --sku B1

    # Create Web App for Containers with Python runtime
    az webapp create -n $WEBAPP_NAME -g $RG --plan $PLAN_NAME --runtime "PYTHON|3.11"

    # Configure application settings for the web app
    az webapp config appsettings set -g $RG -n $WEBAPP_NAME --settings WEBSITES_PORT=8501 APP_ENV=prod

    # Optional: Enable logging with a 7-day retention policy
    az webapp log config -g $RG -n $WEBAPP_NAME --web-server-logging filesystem --retention-days 7
    ```

---

## 🔑 GitHub CI/CD Secrets & Variables

To enable automated CI/CD workflows, configure the following secrets and variables in your GitHub repository under **Settings** → **Secrets and variables** → **Actions**.

### Repository Secrets

Create the following secrets:

-   **`AZURE_CREDENTIALS`**: The JSON output from a service principal. Run the following command in your Azure CLI to generate it:
    ```bash
    SUB_ID=$(az account show --query id -o tsv)
    SP_JSON=$(az ad sp create-for-rbac \
      --name "gh-sp-titanic-mlops" \
      --role contributor \
      --scopes /subscriptions/$SUB_ID \
      --sdk-auth)
    echo "$SP_JSON"
    ```
    Copy the entire JSON output into this secret.

-   **`ACR_USERNAME`**: The username for your Azure Container Registry.
-   **`ACR_PASSWORD`**: The password/token for the ACR admin user.

These ACR credentials are generated when you enable the ACR admin user. Run the following command if you need to retrieve them again:
```bash
az acr update -n <ACR_NAME> --admin-enabled true
az acr credential show -n <ACR_NAME>
```

-   **`AZ_SUBSCRIPTION_ID`**: <your-subscription-id>
-   **`AZ_RESOURCE_GROUP`**: <your-resource-group-name>
-   **`AZ_REGION`**: <region>
-   **`ACR_NAME`**: <ACR_NAME>
-   **`ACR_LOGIN_SERVER`**: <ACR_NAME>.azurecr.io
-   **`WEBAPP_NAME`**: <web-app-name>
-   **`IMAGE_NAME`**: <image-name>
