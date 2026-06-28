### **Project 05**  
**Project Title**: Supply Chain Inventory Optimization System  
**Project Description**:  
Created an end-to-end pipeline for inventory optimization that forecasts demand and suggests optimal stock levels using cloud orchestration and warehouse-native ML models.  

**Objective**:  
- Orchestrate data pipelines from multiple supply chain sources using Airflow  
- Build demand forecasting models with BigQuery ML  
- Develop optimization logic for reorder points and safety stock  
- Design visualizations for inventory health and turnover metrics  
- Automate weekly forecast and recommendation jobs  
- Implement data quality and pipeline monitoring  

**Dataset**:  
Walmart Recruiting - Store Sales Forecasting — same weekly sales dataset as Project 02 (45 stores, holiday markdowns, fuel price, CPI, unemployment). There's no single canonical public "inventory optimization" dataset, so this project reuses Walmart's sales data: students treat the sales forecast as a proxy for demand and derive reorder points/safety stock from it rather than pulling stock-level data directly. Free, no application required.  
Link: https://www.kaggle.com/datasets/aslanahmedov/walmart-sales-forecast

**Tools Used**:  
- **Orchestration**: Apache Airflow  
- **Cloud Platform**: Google Cloud Platform (GCP), BigQuery  
- **ML Modeling**: BigQuery ML  
- **Visualization**: Looker Studio  
- **Languages & Utilities**: SQL, Python  

**Project Type**: Intermediate Data Engineering & ML project focusing on optimization and forecasting  
**Outcome**:  
Delivered a working inventory optimization solution with predictive analytics and clear business dashboards.
