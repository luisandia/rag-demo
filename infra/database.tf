module "sql-db_postgresql" {
  source  = "GoogleCloudPlatform/sql-db/google//modules/postgresql"
  version = "13.0.1"

  name                 = local.database_instance_name
  random_instance_name = false
  database_version     = local.database_version
  project_id           = local.project_id
  zone                 = local.zone
  region               = local.region
  tier                 = local.tier
  availability_type    = local.availability_type
  deletion_protection  = false
  user_labels = {
    "env" = "dev"
  }

  ip_configuration = {
    authorized_networks = []
    ipv4_enabled        = true
    private_network     = null
    require_ssl         = true
    allocated_ip_range  = null
  }


  backup_configuration = {
    enabled                        = local.enable_backup
    start_time                     = "20:55"
    location                       = null
    point_in_time_recovery_enabled = false
    transaction_log_retention_days = null
    retained_backups               = 365
    retention_unit                 = "COUNT"
  }

}


resource "google_sql_database" "additional_databases" {
  project   = local.project_id
  name      = local.database_name
  charset   = "UTF8"
  collation = "en_US.UTF8"
  instance  = local.database_instance_name
  depends_on = [
    module.sql-db_postgresql,
    # google_sql_user.additional_users
  ]
}


resource "google_sql_user" "additional_users" {
  project  = local.project_id
  name     = "rag-user"
  password = "Testing1234!" #"data.google_secret_manager_secret_version.my-user-database-password.secret_data"
  instance = local.database_instance_name
  depends_on = [
    module.sql-db_postgresql,
    module.sql-db_postgresql.replicas,
  ]
}
