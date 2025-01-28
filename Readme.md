This app is deployed as Azure container app. 

Root Folder has the Dockerfile to compose the docker image
Sample Architecture as follows.

**Build Your Docker Image:** You need to build a Docker image from your Dockerfile. Run the following command in the directory containing your Dockerfile:

docker build -t cargolockdetection .

**Push the Docker Image to Azure Container Registry (ACR) or Docker Hub:** You can push the image to ACR or Docker Hub. Here is an example of pushing it to Azure Container Registry:

```
az acr login --name <azure_container_registry>
```

```
docker tag cargolockdetection
```

```
docker push <azure_container_registry>.azurecr.io/cargolockdetection
```

**Create and Deploy Azure Container App:** 
Now you can create and deploy your application using Azure CLI:

```
az containerapp env create --name cargolock --resource-group sb-exp-austeast --location australiaeast
```

```
az containerapp env create \
  --name myEnv \
  --resource-group myResourceGroup \
  --logs-workspace-id <log-analytics-workspace-id> \
  --logs-workspace-key <log-analytics-workspace-key> \
  --location <location>
```

# Deploy your container app
`az containerapp create --name cargolockdetection-app --resource-group sb-exp-austeast --environment CargoLockEnv --image <azure_container_registry>.azurecr.io/cargolockdetection --target-port 8501 --ingress 'external' --registry-server  <azure_container_registry>.azurecr.io `

To deploy a updated version of your Streamlit app with latest code, create a new Docker image with new tag and then update your Azure Container App to use the new image. Here are the steps you can follow:

1. **Update Your Dockerfile (if necessary) and Build the New Docker Image:**
   Update your Dockerfile if there were any changes, then build a new Docker image with a new tag, for example, `v2`.

   `docker build -t cargolockdetection:v2 .`
2. **Push the New Docker Image to Azure Container Registry (ACR) or Docker Hub:**
   Tag the new image and push it to ACR or Docker Hub.

   `docker tag cargolockdetection:v2 <azure_container_registry>.azurecr.io/cargolockdetection:v2 docker push <azure_container_registry>.azurecr.io/cargolockdetection:v2`

3. **Update the Azure Container App to Use the New Image:**
   Use Azure portal to update the Azure Container App to use the new image tag.

Improvements:
To update the AOAI to use structured output.