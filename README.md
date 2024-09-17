# Finance Tracker

A tool to visualize and track financial data using Notion as the data source and Gradio for interactive graphs.

## Features

- Connects to Notion databases for financial tracking.
- Provides visualizations of financial data through a Gradio interface.

## Prerequisites

- Python 3.11 environment
- Docker (if running with containers)
- Google Cloud CLI (`gcloud`)
- A Google Cloud account with access to the project

## Local Development

### Setup

1. Ensure you are in a Python 3.11 environment, then install dependencies:

    ```bash
    make install
    ```

2. Create a `.env` file in the project root with the following keys:

    ```bash
    NOTION_TOKEN=your_notion_token
    FINANCE_TRACKER_DATABASE_ID=your_database_id
    SUB_CATEGORIES_DATABASE_ID=your_sub_categories_id
    MAIN_CATEGORIES_DATABASE_ID=your_main_categories_id
    GRADIO_PASSWORD=your_password
    ```

### Running the Gradio App

To run the Gradio app and see the graphs based on the finance tracker database data, execute:

```bash
python src/finance_tracker/app.py
```

You will then be able to interact with the visualizations through the local Gradio interface.


## Cloud Setup

1. **Check Google Cloud Project**

    Ensure you're signed into the correct Google account and project:

    ```bash
    gcloud config list
    gcloud projects list
    ```

2. **Store Secrets in Google Cloud Secret Manager**
    If not already done, store the following secrets:
    - `NOTION_TOKEN`
    - `FINANCE_TRACKER_DATABASE_ID`
    - `SUB_CATEGORIES_DATABASE_ID`
    - `MAIN_CATEGORIES_DATABASE_ID`
    - `GRADIO_PASSWORD`


    Use the following command to add secrets:
    ```bash
    gcloud secrets add-iam-policy-binding SECRET_NAME \
      --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
      --role="roles/secretmanager.secretAccessor"
    ```

### Build and Push Docker Image

1. Build and push the Docker image to the Artifact Registry:
    ```bash
    gcloud builds submit --tag YOUR_REGION-docker.pkg.dev/YOUR_PROJECT/YOUR_REPO/YOUR_IMAGE_NAME
    ```

### Deploy to Cloud Run

1. Deploy the service:
    ```bash
    gcloud run deploy SERVICE_NAME \
      --image YOUR_REGION-docker.pkg.dev/YOUR_PROJECT/YOUR_REPO/YOUR_IMAGE_NAME \
      --region YOUR_REGION \
      --platform managed \
      --allow-unauthenticated \
      --service-account YOUR_SERVICE_ACCOUNT_EMAIL
    ```

### Usage

Once deployed, access your service at: `https://YOUR-CLOUD-RUN-URL`


## Notes

- Note to Jeffrey: to see exact commands for copy-and-pasting, go to [your personal Notion page](https://www.notion.so/Set-up-Finance-Tracker-GCP-9ee4a592fc2c4e848b8e56c1ebfd9886).