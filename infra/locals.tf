resource "random_string" "prefix" {
  length  = 4
  upper   = false
  special = false
}

# https://cloud.google.com/sql/docs/postgres/instance-settings
locals {

  # secret_project_id      = "my-secret-project"
  secret_project_number  = "92895454065"
  project_id             = "rag-demo-480516"
  project_number         = "586728709254"
  region                 = "southamerica-west1"
  cloud_run_region       = "southamerica-west1"
  zone                   = "southamerica-west1-c" # Santiago de Chile
  tier                   = "db-f1-micro" #"db-custom-2-4096"
  database_version       = "POSTGRES_14"
  database_instance_name = "development"
  database_name          = "rag-demo"
  service_name           = "dev-backend"
  # frontend_name          = "dev-frontend"
  availability_type      = "ZONAL" # "REGIONAL"
  # backend_docker_image   = "us-docker.pkg.dev/cloudrun/container/hello"
  # frontend_docker_image  = "us-docker.pkg.dev/cloudrun/container/hello"
  enable_backup = false
  # secret_name   = "dev-settings"
}
