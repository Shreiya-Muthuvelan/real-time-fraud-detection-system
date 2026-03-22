# Data Directory

This directory is the landing zone for the raw dataset. To maintain a lightweight repository, the large CSV file is **not** included in the version control.

## How to Get the Data

1.  **Download:** Go to the [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1) dataset on Kaggle.
2.  **Extract:** Unzip the downloaded file.
3.  **Rename:** Rename the extracted file (which usually has a long timestamp in the name) to exactly:  
    `paysim.csv`
4.  **Place:** Move `paysim.csv` into this `/data` folder.

---

> [!IMPORTANT]  
> The Docker ingestion script specifically looks for `/data/paysim.csv`. If the filename is different, the `docker-compose` command will fail to find the source.

---
