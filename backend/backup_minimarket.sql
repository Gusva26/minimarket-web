-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: minimarket
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_usuario'),(22,'Can change user',6,'change_usuario'),(23,'Can delete user',6,'delete_usuario'),(24,'Can view user',6,'view_usuario'),(25,'Can add categoria',7,'add_categoria'),(26,'Can change categoria',7,'change_categoria'),(27,'Can delete categoria',7,'delete_categoria'),(28,'Can view categoria',7,'view_categoria'),(29,'Can add producto',8,'add_producto'),(30,'Can change producto',8,'change_producto'),(31,'Can delete producto',8,'delete_producto'),(32,'Can view producto',8,'view_producto'),(33,'Can add Mercado',9,'add_mercado'),(34,'Can change Mercado',9,'change_mercado'),(35,'Can delete Mercado',9,'delete_mercado'),(36,'Can view Mercado',9,'view_mercado'),(37,'Can add Kardex',10,'add_kardex'),(38,'Can change Kardex',10,'change_kardex'),(39,'Can delete Kardex',10,'delete_kardex'),(40,'Can view Kardex',10,'view_kardex'),(41,'Can add Transferencia',11,'add_transferencia'),(42,'Can change Transferencia',11,'change_transferencia'),(43,'Can delete Transferencia',11,'delete_transferencia'),(44,'Can view Transferencia',11,'view_transferencia'),(45,'Can add transferencia detalle',12,'add_transferenciadetalle'),(46,'Can change transferencia detalle',12,'change_transferenciadetalle'),(47,'Can delete transferencia detalle',12,'delete_transferenciadetalle'),(48,'Can view transferencia detalle',12,'view_transferenciadetalle'),(49,'Can add Lote de Vencimiento',13,'add_lotevencimiento'),(50,'Can change Lote de Vencimiento',13,'change_lotevencimiento'),(51,'Can delete Lote de Vencimiento',13,'delete_lotevencimiento'),(52,'Can view Lote de Vencimiento',13,'view_lotevencimiento'),(53,'Can add venta',14,'add_venta'),(54,'Can change venta',14,'change_venta'),(55,'Can delete venta',14,'delete_venta'),(56,'Can view venta',14,'view_venta'),(57,'Can add venta detalle',15,'add_ventadetalle'),(58,'Can change venta detalle',15,'change_ventadetalle'),(59,'Can delete venta detalle',15,'delete_ventadetalle'),(60,'Can view venta detalle',15,'view_ventadetalle'),(61,'Can add Proveedor',16,'add_proveedor'),(62,'Can change Proveedor',16,'change_proveedor'),(63,'Can delete Proveedor',16,'delete_proveedor'),(64,'Can view Proveedor',16,'view_proveedor'),(65,'Can add Compra',17,'add_compra'),(66,'Can change Compra',17,'change_compra'),(67,'Can delete Compra',17,'delete_compra'),(68,'Can view Compra',17,'view_compra'),(69,'Can add Detalle de Compra',18,'add_detallecompra'),(70,'Can change Detalle de Compra',18,'change_detallecompra'),(71,'Can delete Detalle de Compra',18,'delete_detallecompra'),(72,'Can view Detalle de Compra',18,'view_detallecompra'),(73,'Can add Caja',19,'add_caja'),(74,'Can change Caja',19,'change_caja'),(75,'Can delete Caja',19,'delete_caja'),(76,'Can view Caja',19,'view_caja'),(77,'Can add cliente',20,'add_cliente'),(78,'Can change cliente',20,'change_cliente'),(79,'Can delete cliente',20,'delete_cliente'),(80,'Can view cliente',20,'view_cliente'),(81,'Can add Unidad de Producto',21,'add_unidadproducto'),(82,'Can change Unidad de Producto',21,'change_unidadproducto'),(83,'Can delete Unidad de Producto',21,'delete_unidadproducto'),(84,'Can view Unidad de Producto',21,'view_unidadproducto');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras_compra`
--

DROP TABLE IF EXISTS `compras_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `compras_compra` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` datetime(6) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `proveedor_id` bigint(20) DEFAULT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `compras_compra_proveedor_id_d647dfa3_fk_proveedores_proveedor_id` (`proveedor_id`),
  KEY `compras_compra_usuario_id_833384c6_fk_usuarios_usuario_id` (`usuario_id`),
  CONSTRAINT `compras_compra_proveedor_id_d647dfa3_fk_proveedores_proveedor_id` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores_proveedor` (`id`),
  CONSTRAINT `compras_compra_usuario_id_833384c6_fk_usuarios_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras_compra`
--

LOCK TABLES `compras_compra` WRITE;
/*!40000 ALTER TABLE `compras_compra` DISABLE KEYS */;
INSERT INTO `compras_compra` VALUES (1,'2026-06-13 05:00:00.000000',540.00,1,1);
/*!40000 ALTER TABLE `compras_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras_detallecompra`
--

DROP TABLE IF EXISTS `compras_detallecompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `compras_detallecompra` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cantidad` decimal(10,2) NOT NULL,
  `precio_costo_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `compra_id` bigint(20) NOT NULL,
  `producto_id` bigint(20) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `compras_detallecompra_compra_id_9d6236ea_fk_compras_compra_id` (`compra_id`),
  KEY `compras_detallecompr_producto_id_38c7f9c4_fk_inventari` (`producto_id`),
  CONSTRAINT `compras_detallecompr_producto_id_38c7f9c4_fk_inventari` FOREIGN KEY (`producto_id`) REFERENCES `inventario_producto` (`id`),
  CONSTRAINT `compras_detallecompra_compra_id_9d6236ea_fk_compras_compra_id` FOREIGN KEY (`compra_id`) REFERENCES `compras_compra` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras_detallecompra`
--

LOCK TABLES `compras_detallecompra` WRITE;
/*!40000 ALTER TABLE `compras_detallecompra` DISABLE KEYS */;
INSERT INTO `compras_detallecompra` VALUES (23,50.00,7.20,360.00,1,5,'2026-08-15'),(24,120.00,1.50,180.00,1,17,'2026-08-22');
/*!40000 ALTER TABLE `compras_detallecompra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_usuarios_usuario_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_usuarios_usuario_id` FOREIGN KEY (`user_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(17,'compras','compra'),(18,'compras','detallecompra'),(4,'contenttypes','contenttype'),(7,'inventario','categoria'),(10,'inventario','kardex'),(13,'inventario','lotevencimiento'),(9,'inventario','mercado'),(8,'inventario','producto'),(11,'inventario','transferencia'),(12,'inventario','transferenciadetalle'),(21,'inventario','unidadproducto'),(16,'proveedores','proveedor'),(5,'sessions','session'),(6,'usuarios','usuario'),(19,'ventas','caja'),(20,'ventas','cliente'),(14,'ventas','venta'),(15,'ventas','ventadetalle');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-05-09 14:37:35.737168'),(2,'contenttypes','0002_remove_content_type_name','2026-05-09 14:37:35.764473'),(3,'auth','0001_initial','2026-05-09 14:37:35.870649'),(4,'auth','0002_alter_permission_name_max_length','2026-05-09 14:37:35.902740'),(5,'auth','0003_alter_user_email_max_length','2026-05-09 14:37:35.907388'),(6,'auth','0004_alter_user_username_opts','2026-05-09 14:37:35.911514'),(7,'auth','0005_alter_user_last_login_null','2026-05-09 14:37:35.915964'),(8,'auth','0006_require_contenttypes_0002','2026-05-09 14:37:35.917703'),(9,'auth','0007_alter_validators_add_error_messages','2026-05-09 14:37:35.922203'),(10,'auth','0008_alter_user_username_max_length','2026-05-09 14:37:35.926411'),(11,'auth','0009_alter_user_last_name_max_length','2026-05-09 14:37:35.930245'),(12,'auth','0010_alter_group_name_max_length','2026-05-09 14:37:35.937582'),(13,'auth','0011_update_proxy_permissions','2026-05-09 14:37:35.942655'),(14,'auth','0012_alter_user_first_name_max_length','2026-05-09 14:37:35.946765'),(15,'usuarios','0001_initial','2026-05-09 14:37:36.073639'),(16,'admin','0001_initial','2026-05-09 14:37:36.135583'),(17,'admin','0002_logentry_remove_auto_add','2026-05-09 14:37:36.141549'),(18,'admin','0003_logentry_add_action_flag_choices','2026-05-09 14:37:36.147265'),(19,'proveedores','0001_initial','2026-05-09 14:37:36.163643'),(20,'inventario','0001_initial','2026-05-09 14:37:36.199065'),(21,'inventario','0002_producto_costo','2026-05-09 14:37:36.208993'),(22,'compras','0001_initial','2026-05-09 14:37:36.309712'),(23,'compras','0002_detallecompra_fecha_vencimiento','2026-05-09 14:37:36.319097'),(24,'inventario','0003_mercado_categoria_mercado_producto_mercado','2026-05-09 14:37:36.381935'),(25,'inventario','0004_kardex','2026-05-09 14:37:36.486161'),(26,'inventario','0005_alter_kardex_tipo_movimiento_transferencia_and_more','2026-05-09 14:37:36.676415'),(27,'inventario','0006_producto_codigo_barras','2026-05-09 14:37:36.693237'),(28,'inventario','0007_lotevencimiento','2026-05-09 14:37:36.765572'),(29,'inventario','0008_producto_stock_minimo_producto_unidad_medida_and_more','2026-05-09 14:37:37.355924'),(30,'inventario','0009_transferenciadetalle_fecha_vencimiento','2026-05-09 14:37:37.367874'),(31,'sessions','0001_initial','2026-05-09 14:37:37.389825'),(32,'usuarios','0002_usuario_mercado','2026-05-09 14:37:37.426874'),(33,'ventas','0001_initial','2026-05-09 14:37:37.549262'),(34,'ventas','0002_caja_venta_caja','2026-05-09 15:18:50.617747'),(35,'compras','0003_compra_usuario_alter_detallecompra_cantidad','2026-05-23 14:28:22.012399'),(36,'inventario','0010_mercado_ruc','2026-05-23 14:28:22.026064'),(37,'ventas','0003_alter_ventadetalle_cantidad','2026-05-23 14:28:22.068967'),(38,'ventas','0004_cliente_venta_igv_venta_numero_venta_serie_and_more','2026-05-23 14:28:22.201497'),(39,'ventas','0005_venta_monto_recibido_venta_num_operacion_and_more','2026-05-23 14:28:22.249062'),(40,'ventas','0006_venta_costo_total_venta_estado_and_more','2026-05-23 14:28:22.300687'),(41,'inventario','0011_producto_imagen_url','2026-05-23 14:59:57.200133'),(42,'inventario','0011_unidadproducto_delete_lotevencimiento_and_more','2026-05-30 14:44:23.034036'),(43,'ventas','0007_alter_venta_unique_together','2026-06-13 04:57:12.857862'),(44,'inventario','0012_alter_producto_unidad_medida','2026-06-20 08:56:37.809970'),(45,'ventas','0008_venta_descuento_ventadetalle_descuento','2026-06-20 10:11:16.465417');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('2crmyfi3kgqt3wc50youeylrmm3il2fp','.eJxVjMsOgjAQAP9lz6ah3S2LHL3zDU0fW4uaklA4Gf_dkHDQ68xk3uD8vhW3N1ndnGAEhMsvCz4-pR4iPXy9LyoudVvnoI5EnbapaUnyup3t36D4VmCEIQtHGzOZTpgi6oEILWUMltnaq0FE9oyGdN93ZChoQ1rYp0yEkeHzBbe6NlQ:1wLk1Q:g07zgMm1sfecq8dDF4Vd3wdeK8dhJ4c_HgFBm6Q-YUM','2026-05-23 15:55:20.119535'),('996t2s2147o7z489fmc4z50n4t7rsjtk','.eJxVjDkOwjAQAP-yNbKcY32kpOcN0Tq7iwPIlnJUiL-jSCmgnRnNG0batzzuqyzjzDBAA5dflmh6SjkEP6jcq5lq2ZY5mSMxp13NrbK8rmf7N8i0ZhgAnbKPEpl8oIjkxCXtovoGW0XloOz6ZNFG23RMwaJYsowSsffat_D5AvRjN-4:1wLjrk:nJoTksQDZt7xyq9wOFg-DtzfqCZO9DRxg0lJycJsxBs','2026-05-23 15:45:20.380420'),('i0xw6aeu0o96uszzzh29l8nxshey7f31','.eJxVjEEKwyAQAP-y5yK6RnFz7L1vkFU3NW0xEJNT6d9LIIf2OjPMGyLvW417lzXOBUZAuPyyxPkp7RDlwe2-qLy0bZ2TOhJ12q5uS5HX9Wz_BpV7hRGC1mnSBomELVJyZJCTNxI0eZHsih10GMh5JA7OkpArlNki0sTGwOcLwLY27w:1wLjbr:U9XatDjN-rI_C254qQGFXVgEStRyZ53d4w83IMiJQpY','2026-05-23 15:28:55.204870'),('rswqm0pdizw1koya82z4mel76opzamzw','.eJxVjEEKwyAQAP-y5yK6RnFz7L1vkFU3NW0xEJNT6d9LIIf2OjPMGyLvW417lzXOBUZAuPyyxPkp7RDlwe2-qLy0bZ2TOhJ12q5uS5HX9Wz_BpV7hRGC1mnSBomELVJyZJCTNxI0eZHsih10GMh5JA7OkpArlNki0sTGwOcLwLY27w:1wLjgf:8sNWpzcroOI-HIK9drC6N--7YZhe6fg5otXXiH6RnS0','2026-05-23 15:33:53.294274'),('ulk1fj0iw06gkrxjoxmx0mcgabvp6e2t','.eJxVjDkOwjAQAP-yNbJie-MjJT1vsHZ94ABypDipEH9HkVJAOzOaNwTatxr2ntcwJ5gA4fLLmOIzt0OkB7X7IuLStnVmcSTitF3clpRf17P9G1TqFSYotijygytjjFJqIqOQU0LPXIx0xKqoTDZ6NogmjgNr6Sxa9lolcho-X__OOC8:1wLjqM:mGSrAxyJTPfdaw--aZPXL99OBofmsiZChzPuGcHWL5E','2026-05-23 15:43:54.921949');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_categoria`
--

DROP TABLE IF EXISTS `inventario_categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_categoria` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `mercado_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_categoria_mercado_id_04257562_fk_inventari` (`mercado_id`),
  CONSTRAINT `inventario_categoria_mercado_id_04257562_fk_inventari` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_categoria`
--

LOCK TABLES `inventario_categoria` WRITE;
/*!40000 ALTER TABLE `inventario_categoria` DISABLE KEYS */;
INSERT INTO `inventario_categoria` VALUES (1,'Bebidas',1),(2,'L??cteos y Embutidos',1),(3,'Abarrotes',1),(4,'Snacks',1),(5,'Licores',1);
/*!40000 ALTER TABLE `inventario_categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_kardex`
--

DROP TABLE IF EXISTS `inventario_kardex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_kardex` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo_movimiento` varchar(30) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `saldo_anterior` decimal(10,2) NOT NULL,
  `saldo_nuevo` decimal(10,2) NOT NULL,
  `referencia_tipo` varchar(50) NOT NULL,
  `referencia_id` int(11) DEFAULT NULL,
  `referencia_detalle` varchar(200) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `mercado_id` bigint(20) NOT NULL,
  `producto_id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_kardex_usuario_id_c85c7473_fk_usuarios_usuario_id` (`usuario_id`),
  KEY `inventario__product_72dedb_idx` (`producto_id`,`fecha`),
  KEY `inventario__mercado_3d938c_idx` (`mercado_id`,`fecha`),
  CONSTRAINT `inventario_kardex_mercado_id_14475389_fk_inventario_mercado_id` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`),
  CONSTRAINT `inventario_kardex_producto_id_b15b456f_fk_inventario_producto_id` FOREIGN KEY (`producto_id`) REFERENCES `inventario_producto` (`id`),
  CONSTRAINT `inventario_kardex_usuario_id_c85c7473_fk_usuarios_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_kardex`
--

LOCK TABLES `inventario_kardex` WRITE;
/*!40000 ALTER TABLE `inventario_kardex` DISABLE KEYS */;
INSERT INTO `inventario_kardex` VALUES (1,'ENTRADA',50.00,0.00,50.00,'Compra',1,'Compra a George Palacios','2026-06-13 16:06:32.062152',1,5,1),(2,'ENTRADA',120.00,0.00,120.00,'Compra',1,'Compra a George Palacios','2026-06-13 16:06:32.064370',1,17,1),(3,'AJUSTE_POSITIVO',300.00,0.00,300.00,'Ajuste Manual',NULL,'asd','2026-06-20 18:14:47.222997',1,16,1);
/*!40000 ALTER TABLE `inventario_kardex` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_mercado`
--

DROP TABLE IF EXISTS `inventario_mercado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_mercado` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `ruc` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_mercado`
--

LOCK TABLES `inventario_mercado` WRITE;
/*!40000 ALTER TABLE `inventario_mercado` DISABLE KEYS */;
INSERT INTO `inventario_mercado` VALUES (1,'Minimarket - Centro','Av. Principal 123','555-1234',1,'12011201380'),(2,'Minimarket - Norte','Calle Secundaria 456','555-1234',1,'12011201380');
/*!40000 ALTER TABLE `inventario_mercado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_producto`
--

DROP TABLE IF EXISTS `inventario_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_producto` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` decimal(10,2) NOT NULL,
  `imagen` varchar(100) DEFAULT NULL,
  `categoria_id` bigint(20) DEFAULT NULL,
  `costo` decimal(10,2) NOT NULL,
  `mercado_id` bigint(20) DEFAULT NULL,
  `codigo_barras` varchar(50) DEFAULT NULL,
  `stock_minimo` decimal(10,2) NOT NULL,
  `unidad_medida` varchar(10) NOT NULL,
  `imagen_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_producto_categoria_id_7033fb47_fk_inventari` (`categoria_id`),
  KEY `inventario_producto_mercado_id_838e6d2f_fk_inventario_mercado_id` (`mercado_id`),
  KEY `inventario_producto_codigo_barras_d10ae49b` (`codigo_barras`),
  CONSTRAINT `inventario_producto_categoria_id_7033fb47_fk_inventari` FOREIGN KEY (`categoria_id`) REFERENCES `inventario_categoria` (`id`),
  CONSTRAINT `inventario_producto_mercado_id_838e6d2f_fk_inventario_mercado_id` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_producto`
--

LOCK TABLES `inventario_producto` WRITE;
/*!40000 ALTER TABLE `inventario_producto` DISABLE KEYS */;
INSERT INTO `inventario_producto` VALUES (1,'Arroz Extra Coste??o 1kg',4.50,0.00,'productos/Arroz_9GQbrr3.png',3,3.20,1,'7750435001000',10.00,'UND',NULL),(2,'Arroz Extra Coste??o 5kg',18.90,0.00,'productos/arroz-extra-coste??o5kg.png',3,14.50,1,'7750435002007',5.00,'UND',NULL),(3,'Fideos Don Vittorio Tallar??n 500g',2.80,0.00,'',3,1.90,1,'7750234011002',10.00,'UND',NULL),(4,'Fideos Don Vittorio Spaghetti 500g',2.80,0.00,'',3,1.90,1,'7750234012009',10.00,'UND',NULL),(5,'Aceite Primor 1L',9.50,50.00,'productos/Aceite_SxYC2rM.png',3,7.20,1,'7750450091004',8.00,'UND',NULL),(6,'Az??car Rubia 1kg',4.20,0.00,'',3,2.80,1,'7750435013001',10.00,'UND',NULL),(7,'Sal de Mesa Emsal 1kg',2.00,0.00,'',3,1.20,1,'7750435021009',10.00,'UND',NULL),(8,'Lenteja x 500g',3.80,0.00,'',3,2.50,1,'7750435031005',8.00,'UND',NULL),(9,'Frejol Canario x 500g',4.50,0.00,'',3,3.00,1,'7750435032002',8.00,'UND',NULL),(10,'At??n Florida en Aceite 170g',4.20,0.00,'',3,2.90,1,'7750451011005',12.00,'UND',NULL),(11,'Coca-Cola 500ml',2.50,0.00,'',1,1.60,1,'7750891001002',15.00,'UND',NULL),(12,'Coca-Cola 1.5L',5.00,0.00,'',1,3.40,1,'7750891002009',10.00,'UND',NULL),(13,'Inca Kola 500ml',2.50,0.00,'',1,1.60,1,'7750892001009',15.00,'UND',NULL),(14,'Inca Kola 1.5L',5.00,0.00,'',1,3.40,1,'7750892002006',10.00,'UND',NULL),(15,'Sprite 500ml',2.50,0.00,'',1,1.60,1,'7750893001006',10.00,'UND',NULL),(16,'Agua San Luis sin Gas 625ml',2.00,300.00,'productos/productos/agua-san-luis-625ml.png',1,1.20,1,'7750894001002',15.00,'UND',NULL),(17,'Agua Cielo sin Gas 1L',2.50,120.00,'productos/agua-cielo-1L.png',1,1.50,1,'7750895001009',12.00,'UND',NULL),(18,'Jugo Pulp Naranja 1L',5.50,0.00,'',1,3.80,1,'7750896001006',8.00,'UND',NULL),(19,'Gatorade Naranja 500ml',4.00,0.00,'',1,2.80,1,'7750897001003',10.00,'UND',NULL),(20,'Energizante Volt 250ml',3.50,0.00,'',1,2.30,1,'7750898001000',12.00,'UND',NULL),(21,'Papas Lays Cl??sicas 120g',3.50,0.00,'',4,2.30,1,'7750453011006',10.00,'UND',NULL),(22,'Papas Lays Pollo 120g',3.50,0.00,'',4,2.30,1,'7750453012003',10.00,'UND',NULL),(23,'Doritos Nacho 100g',3.20,0.00,'',4,2.10,1,'7750453021007',10.00,'UND',NULL),(24,'Piqueo Snax 100g',2.80,0.00,'',4,1.80,1,'7750453031003',10.00,'UND',NULL),(25,'Chizitos 100g',2.50,0.00,'',4,1.60,1,'7750453041000',10.00,'UND',NULL),(26,'Canchita Serranita 100g',3.00,0.00,'',4,1.90,1,'7750453051007',10.00,'UND',NULL),(27,'Man?? Salado x 100g',2.00,0.00,'',4,1.20,1,'7750453061004',12.00,'UND',NULL),(28,'Cacahuates Japoneses x 100g',2.50,0.00,'',4,1.50,1,'7750453071001',10.00,'UND',NULL),(29,'Chifles x 100g',2.50,0.00,'',4,1.60,1,'7750453081008',10.00,'UND',NULL),(30,'Caramelos Donofrio Fruna x 15',1.50,0.00,'',4,0.90,1,'7750453091005',20.00,'UND',NULL),(31,'Leche Gloria Evaporada 400g',4.20,0.00,'',2,3.00,1,'7750430011000',15.00,'UND',NULL),(32,'Leche Gloria Fresca 1L',5.50,0.00,'',2,4.00,1,'7750430021007',10.00,'UND',NULL),(33,'Yogurt Gloria Natural 1L',6.00,0.00,'',2,4.20,1,'7750430031004',8.00,'UND',NULL),(34,'Queso Fresco x 250g',4.50,0.00,'',2,3.00,1,'7750430041001',8.00,'UND',NULL),(35,'Mantequilla Gloria 200g',5.50,0.00,'',2,3.80,1,'7750430051008',8.00,'UND',NULL),(36,'Jam??n San Fernando 200g',6.00,0.00,'',2,4.20,1,'7750430061005',8.00,'UND',NULL),(37,'Salchicha San Fernando 200g',5.00,0.00,'',2,3.40,1,'7750430071002',8.00,'UND',NULL),(38,'Huevos x 12',7.50,0.00,'',2,5.50,1,'7750430081009',10.00,'UND',NULL),(39,'Yogurt Gloria Batido Fresa 180ml',2.50,0.00,'',2,1.60,1,'7750430091006',15.00,'UND',NULL),(40,'Margarina Manty 500g',4.00,0.00,'',2,2.60,1,'7750430101002',8.00,'UND',NULL),(41,'Cerveza Cristal 620ml',5.00,0.00,'',5,3.50,1,'7750440011008',15.00,'UND',NULL),(42,'Cerveza Pilsen 620ml',5.00,0.00,'',5,3.50,1,'7750440021005',15.00,'UND',NULL),(43,'Cerveza Cusque??a 620ml',7.00,0.00,'',5,5.00,1,'7750440031002',10.00,'UND',NULL),(44,'Cerveza Corona 355ml',6.00,0.00,'',5,4.20,1,'7750440041009',10.00,'UND',NULL),(45,'Ron Cartavio Black 750ml',25.00,0.00,'',5,18.00,1,'7750440051006',5.00,'UND',NULL),(46,'Vodka Smirnoff 750ml',35.00,0.00,'',5,25.00,1,'7750440061003',5.00,'UND',NULL),(47,'Whisky Johnnie Walker Red Label 750ml',65.00,0.00,'',5,48.00,1,'7750440071000',3.00,'UND',NULL),(48,'Pisco Queirolo Mosto Verde 750ml',45.00,0.00,'',5,32.00,1,'7750440081007',3.00,'UND',NULL),(49,'Vino Tinto Intipalka 750ml',22.00,0.00,'',5,15.00,1,'7750440091004',5.00,'UND',NULL),(50,'Chilcano de Pisco x 6 latas',18.00,0.00,'',5,12.00,1,'7750440101000',5.00,'UND',NULL),(51,'Cheetos Queso 900g',3.00,0.00,'',4,2.10,1,'7750450091004',10.00,'UND',NULL),(52,'Sprite 500ml',3.00,0.00,'',1,2.00,1,'',5.00,'UND',NULL);
/*!40000 ALTER TABLE `inventario_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_transferencia`
--

DROP TABLE IF EXISTS `inventario_transferencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_transferencia` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_envio` datetime(6) NOT NULL,
  `fecha_recepcion` datetime(6) DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  `observaciones` longtext NOT NULL,
  `mercado_destino_id` bigint(20) NOT NULL,
  `mercado_origen_id` bigint(20) NOT NULL,
  `usuario_envio_id` bigint(20) DEFAULT NULL,
  `usuario_recepcion_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_transfere_mercado_destino_id_532c9420_fk_inventari` (`mercado_destino_id`),
  KEY `inventario_transfere_mercado_origen_id_8f11c4f4_fk_inventari` (`mercado_origen_id`),
  KEY `inventario_transfere_usuario_envio_id_fa7c4512_fk_usuarios_` (`usuario_envio_id`),
  KEY `inventario_transfere_usuario_recepcion_id_eee231e8_fk_usuarios_` (`usuario_recepcion_id`),
  CONSTRAINT `inventario_transfere_mercado_destino_id_532c9420_fk_inventari` FOREIGN KEY (`mercado_destino_id`) REFERENCES `inventario_mercado` (`id`),
  CONSTRAINT `inventario_transfere_mercado_origen_id_8f11c4f4_fk_inventari` FOREIGN KEY (`mercado_origen_id`) REFERENCES `inventario_mercado` (`id`),
  CONSTRAINT `inventario_transfere_usuario_envio_id_fa7c4512_fk_usuarios_` FOREIGN KEY (`usuario_envio_id`) REFERENCES `usuarios_usuario` (`id`),
  CONSTRAINT `inventario_transfere_usuario_recepcion_id_eee231e8_fk_usuarios_` FOREIGN KEY (`usuario_recepcion_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_transferencia`
--

LOCK TABLES `inventario_transferencia` WRITE;
/*!40000 ALTER TABLE `inventario_transferencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventario_transferencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_transferenciadetalle`
--

DROP TABLE IF EXISTS `inventario_transferenciadetalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_transferenciadetalle` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cantidad` decimal(10,2) NOT NULL,
  `producto_destino_id` bigint(20) DEFAULT NULL,
  `producto_origen_id` bigint(20) NOT NULL,
  `transferencia_id` bigint(20) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_transfere_producto_destino_id_ab899559_fk_inventari` (`producto_destino_id`),
  KEY `inventario_transfere_producto_origen_id_05dafb55_fk_inventari` (`producto_origen_id`),
  KEY `inventario_transfere_transferencia_id_62d65876_fk_inventari` (`transferencia_id`),
  CONSTRAINT `inventario_transfere_producto_destino_id_ab899559_fk_inventari` FOREIGN KEY (`producto_destino_id`) REFERENCES `inventario_producto` (`id`),
  CONSTRAINT `inventario_transfere_producto_origen_id_05dafb55_fk_inventari` FOREIGN KEY (`producto_origen_id`) REFERENCES `inventario_producto` (`id`),
  CONSTRAINT `inventario_transfere_transferencia_id_62d65876_fk_inventari` FOREIGN KEY (`transferencia_id`) REFERENCES `inventario_transferencia` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_transferenciadetalle`
--

LOCK TABLES `inventario_transferenciadetalle` WRITE;
/*!40000 ALTER TABLE `inventario_transferenciadetalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventario_transferenciadetalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_unidadproducto`
--

DROP TABLE IF EXISTS `inventario_unidadproducto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario_unidadproducto` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_vencimiento` date NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `mercado_id` bigint(20) NOT NULL,
  `producto_id` bigint(20) NOT NULL,
  `venta_detalle_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario__product_2c3c40_idx` (`producto_id`,`fecha_vencimiento`,`estado`),
  KEY `inventario__product_ea9315_idx` (`producto_id`,`mercado_id`,`estado`,`fecha_vencimiento`),
  KEY `inventario_unidadpro_mercado_id_10d96c12_fk_inventari` (`mercado_id`),
  KEY `inventario_unidadpro_venta_detalle_id_505083d7_fk_ventas_ve` (`venta_detalle_id`),
  KEY `inventario_unidadproducto_fecha_vencimiento_0537bd0a` (`fecha_vencimiento`),
  CONSTRAINT `inventario_unidadpro_mercado_id_10d96c12_fk_inventari` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`),
  CONSTRAINT `inventario_unidadpro_producto_id_7dbe295f_fk_inventari` FOREIGN KEY (`producto_id`) REFERENCES `inventario_producto` (`id`),
  CONSTRAINT `inventario_unidadpro_venta_detalle_id_505083d7_fk_ventas_ve` FOREIGN KEY (`venta_detalle_id`) REFERENCES `ventas_ventadetalle` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=172 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_unidadproducto`
--

LOCK TABLES `inventario_unidadproducto` WRITE;
/*!40000 ALTER TABLE `inventario_unidadproducto` DISABLE KEYS */;
INSERT INTO `inventario_unidadproducto` VALUES (1,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.946280',1,5,NULL),(2,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.947940',1,5,NULL),(3,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.948489',1,5,NULL),(4,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.948945',1,5,NULL),(5,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.949486',1,5,NULL),(6,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.950113',1,5,NULL),(7,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.950656',1,5,NULL),(8,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.951109',1,5,NULL),(9,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.951576',1,5,NULL),(10,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.952011',1,5,NULL),(11,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.952411',1,5,NULL),(12,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.952800',1,5,NULL),(13,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.953244',1,5,NULL),(14,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.953766',1,5,NULL),(15,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.954217',1,5,NULL),(16,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.954598',1,5,NULL),(17,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.955046',1,5,NULL),(18,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.955514',1,5,NULL),(19,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.955895',1,5,NULL),(20,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.956375',1,5,NULL),(21,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.956890',1,5,NULL),(22,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.957425',1,5,NULL),(23,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.957898',1,5,NULL),(24,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.958365',1,5,NULL),(25,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.958783',1,5,NULL),(26,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.959674',1,5,NULL),(27,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.960136',1,5,NULL),(28,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.960539',1,5,NULL),(29,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.960924',1,5,NULL),(30,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.961342',1,5,NULL),(31,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.961749',1,5,NULL),(32,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.962179',1,5,NULL),(33,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.963964',1,5,NULL),(34,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.964648',1,5,NULL),(35,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.965234',1,5,NULL),(36,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.965734',1,5,NULL),(37,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.966207',1,5,NULL),(38,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.966671',1,5,NULL),(39,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.967184',1,5,NULL),(40,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.967657',1,5,NULL),(41,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.968067',1,5,NULL),(42,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.968621',1,5,NULL),(43,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.969130',1,5,NULL),(44,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.969661',1,5,NULL),(45,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.970208',1,5,NULL),(46,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.970744',1,5,NULL),(47,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.971314',1,5,NULL),(48,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.971857',1,5,NULL),(49,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.972400',1,5,NULL),(50,'2026-08-15',1.00,'disponible','2026-06-13 16:06:31.973520',1,5,NULL),(51,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.986336',1,17,NULL),(52,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.987130',1,17,NULL),(53,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.987763',1,17,NULL),(54,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.988296',1,17,NULL),(55,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.988912',1,17,NULL),(56,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.989351',1,17,NULL),(57,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.989892',1,17,NULL),(58,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.990391',1,17,NULL),(59,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.990964',1,17,NULL),(60,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.991673',1,17,NULL),(61,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.992277',1,17,NULL),(62,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.992877',1,17,NULL),(63,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.993351',1,17,NULL),(64,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.993863',1,17,NULL),(65,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.994372',1,17,NULL),(66,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.994911',1,17,NULL),(67,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.995346',1,17,NULL),(68,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.995794',1,17,NULL),(69,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.996269',1,17,NULL),(70,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.997137',1,17,NULL),(71,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.997618',1,17,NULL),(72,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.998168',1,17,NULL),(73,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.998848',1,17,NULL),(74,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.999462',1,17,NULL),(75,'2026-08-22',1.00,'disponible','2026-06-13 16:06:31.999934',1,17,NULL),(76,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.000740',1,17,NULL),(77,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.001237',1,17,NULL),(78,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.001727',1,17,NULL),(79,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.002225',1,17,NULL),(80,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.002653',1,17,NULL),(81,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.003133',1,17,NULL),(82,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.003548',1,17,NULL),(83,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.004203',1,17,NULL),(84,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.004803',1,17,NULL),(85,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.005527',1,17,NULL),(86,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.006086',1,17,NULL),(87,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.006776',1,17,NULL),(88,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.007367',1,17,NULL),(89,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.007849',1,17,NULL),(90,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.008426',1,17,NULL),(91,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.008972',1,17,NULL),(92,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.009404',1,17,NULL),(93,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.009849',1,17,NULL),(94,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.010340',1,17,NULL),(95,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.010850',1,17,NULL),(96,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.011311',1,17,NULL),(97,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.011881',1,17,NULL),(98,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.012558',1,17,NULL),(99,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.013108',1,17,NULL),(100,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.013610',1,17,NULL),(101,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.014222',1,17,NULL),(102,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.014646',1,17,NULL),(103,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.015251',1,17,NULL),(104,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.015804',1,17,NULL),(105,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.016419',1,17,NULL),(106,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.016922',1,17,NULL),(107,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.017468',1,17,NULL),(108,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.018017',1,17,NULL),(109,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.018602',1,17,NULL),(110,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.019110',1,17,NULL),(111,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.019708',1,17,NULL),(112,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.020178',1,17,NULL),(113,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.020721',1,17,NULL),(114,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.021229',1,17,NULL),(115,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.021697',1,17,NULL),(116,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.022245',1,17,NULL),(117,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.022741',1,17,NULL),(118,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.023159',1,17,NULL),(119,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.023622',1,17,NULL),(120,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.024044',1,17,NULL),(121,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.024538',1,17,NULL),(122,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.024993',1,17,NULL),(123,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.025442',1,17,NULL),(124,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.026094',1,17,NULL),(125,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.026658',1,17,NULL),(126,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.027089',1,17,NULL),(127,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.027603',1,17,NULL),(128,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.028046',1,17,NULL),(129,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.028535',1,17,NULL),(130,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.029025',1,17,NULL),(131,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.029452',1,17,NULL),(132,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.030103',1,17,NULL),(133,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.030748',1,17,NULL),(134,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.031259',1,17,NULL),(135,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.031783',1,17,NULL),(136,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.032310',1,17,NULL),(137,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.032961',1,17,NULL),(138,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.033499',1,17,NULL),(139,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.034032',1,17,NULL),(140,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.034584',1,17,NULL),(141,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.035082',1,17,NULL),(142,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.035599',1,17,NULL),(143,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.036149',1,17,NULL),(144,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.036607',1,17,NULL),(145,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.037081',1,17,NULL),(146,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.037533',1,17,NULL),(147,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.038108',1,17,NULL),(148,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.038720',1,17,NULL),(149,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.039185',1,17,NULL),(150,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.039743',1,17,NULL),(151,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.040330',1,17,NULL),(152,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.040874',1,17,NULL),(153,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.041421',1,17,NULL),(154,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.041952',1,17,NULL),(155,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.042418',1,17,NULL),(156,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.042940',1,17,NULL),(157,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.043404',1,17,NULL),(158,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.043862',1,17,NULL),(159,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.044300',1,17,NULL),(160,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.044856',1,17,NULL),(161,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.045694',1,17,NULL),(162,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.046185',1,17,NULL),(163,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.046915',1,17,NULL),(164,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.047641',1,17,NULL),(165,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.048335',1,17,NULL),(166,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.048952',1,17,NULL),(167,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.049683',1,17,NULL),(168,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.050145',1,17,NULL),(169,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.050619',1,17,NULL),(170,'2026-08-22',1.00,'disponible','2026-06-13 16:06:32.051067',1,17,NULL),(171,'2026-08-28',300.00,'disponible','2026-06-20 18:14:47.105470',1,16,NULL);
/*!40000 ALTER TABLE `inventario_unidadproducto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores_proveedor`
--

DROP TABLE IF EXISTS `proveedores_proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proveedores_proveedor` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `ruc` varchar(11) DEFAULT NULL,
  `telefono` varchar(15) NOT NULL,
  `direccion` longtext NOT NULL,
  `email` varchar(254) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  UNIQUE KEY `ruc` (`ruc`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores_proveedor`
--

LOCK TABLES `proveedores_proveedor` WRITE;
/*!40000 ALTER TABLE `proveedores_proveedor` DISABLE KEYS */;
INSERT INTO `proveedores_proveedor` VALUES (1,'George Palacios','12011201380','991612876','San Sebasti??n 126','georgeelvispalacios@gmail.com',1);
/*!40000 ALTER TABLE `proveedores_proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_usuario`
--

DROP TABLE IF EXISTS `usuarios_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios_usuario` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `mercado_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `usuarios_usuario_mercado_id_933e48b7_fk_inventario_mercado_id` (`mercado_id`),
  CONSTRAINT `usuarios_usuario_mercado_id_933e48b7_fk_inventario_mercado_id` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_usuario`
--

LOCK TABLES `usuarios_usuario` WRITE;
/*!40000 ALTER TABLE `usuarios_usuario` DISABLE KEYS */;
INSERT INTO `usuarios_usuario` VALUES (1,'pbkdf2_sha256$720000$rU51JC5IuDvsH9GTkZ0IMV$mod68sUSzD/ijG5U/viKIeJZzI2DlbluB8VkiEl/lsA=','2026-05-23 14:56:09.519795',0,'admin1','Admin','Centro','gusva.2608@gmail.com',0,1,'2026-05-09 14:37:56.596977','ADMIN',1),(2,'pbkdf2_sha256$720000$8olN3e283Qn3e5uay68DKL$SRZzLGCCioLkjJzIse3vhUgJT1qwWyfnuvpEXrM/Ixo=','2026-05-23 15:07:12.482927',0,'vendedor1','Juan','Perez','vendedor1@centro.com',0,1,'2026-05-09 14:37:56.889747','VENDEDOR',1),(3,'pbkdf2_sha256$720000$cxVD8d4mo6x3haeW2V5JAC$bJhiOvcDIKq5RlbHqKNEvDjPqgDd2YZguQW7u2vNxwU=','2026-05-09 15:55:20.117674',0,'admin2','Admin','Norte','admin2@norte.com',0,1,'2026-05-09 14:37:57.191099','ADMIN',2),(4,'pbkdf2_sha256$720000$m1GkKrtMPraAV6F57csDxR$m2Pj91qZ35Z6G2S3gvNy7Gr/5LFZ/QgNUoE4nnHcLbk=','2026-05-09 15:38:50.361019',0,'vendedor2','Maria','Gonzalez','vendedor2@norte.com',0,1,'2026-05-09 14:37:57.500146','VENDEDOR',2);
/*!40000 ALTER TABLE `usuarios_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_usuario_groups`
--

DROP TABLE IF EXISTS `usuarios_usuario_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios_usuario_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuarios_usuario_groups_usuario_id_group_id_4ed5b09e_uniq` (`usuario_id`,`group_id`),
  KEY `usuarios_usuario_groups_group_id_e77f6dcf_fk_auth_group_id` (`group_id`),
  CONSTRAINT `usuarios_usuario_gro_usuario_id_7a34077f_fk_usuarios_` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios_usuario` (`id`),
  CONSTRAINT `usuarios_usuario_groups_group_id_e77f6dcf_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_usuario_groups`
--

LOCK TABLES `usuarios_usuario_groups` WRITE;
/*!40000 ALTER TABLE `usuarios_usuario_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_usuario_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_usuario_user_permissions`
--

DROP TABLE IF EXISTS `usuarios_usuario_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios_usuario_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuarios_usuario_user_pe_usuario_id_permission_id_217cadcd_uniq` (`usuario_id`,`permission_id`),
  KEY `usuarios_usuario_use_permission_id_4e5c0f2f_fk_auth_perm` (`permission_id`),
  CONSTRAINT `usuarios_usuario_use_permission_id_4e5c0f2f_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `usuarios_usuario_use_usuario_id_60aeea80_fk_usuarios_` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_usuario_user_permissions`
--

LOCK TABLES `usuarios_usuario_user_permissions` WRITE;
/*!40000 ALTER TABLE `usuarios_usuario_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_usuario_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas_caja`
--

DROP TABLE IF EXISTS `ventas_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ventas_caja` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_apertura` datetime(6) NOT NULL,
  `fecha_cierre` datetime(6) DEFAULT NULL,
  `monto_inicial` decimal(10,2) NOT NULL,
  `monto_final_efectivo_real` decimal(10,2) DEFAULT NULL,
  `monto_final_yape_real` decimal(10,2) DEFAULT NULL,
  `monto_final_plin_real` decimal(10,2) DEFAULT NULL,
  `monto_esperado_efectivo` decimal(10,2) NOT NULL,
  `monto_esperado_yape` decimal(10,2) NOT NULL,
  `monto_esperado_plin` decimal(10,2) NOT NULL,
  `estado` varchar(10) NOT NULL,
  `observaciones` longtext NOT NULL,
  `mercado_id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ventas_caja_mercado_id_f25e7581_fk_inventario_mercado_id` (`mercado_id`),
  KEY `ventas_caja_usuario_id_14c8c160_fk_usuarios_usuario_id` (`usuario_id`),
  CONSTRAINT `ventas_caja_mercado_id_f25e7581_fk_inventario_mercado_id` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`),
  CONSTRAINT `ventas_caja_usuario_id_14c8c160_fk_usuarios_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas_caja`
--

LOCK TABLES `ventas_caja` WRITE;
/*!40000 ALTER TABLE `ventas_caja` DISABLE KEYS */;
INSERT INTO `ventas_caja` VALUES (1,'2026-06-13 16:05:33.265780',NULL,0.00,NULL,NULL,NULL,0.00,0.00,0.00,'ABIERTA','',1,1);
/*!40000 ALTER TABLE `ventas_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas_cliente`
--

DROP TABLE IF EXISTS `ventas_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ventas_cliente` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `tipo_documento` varchar(10) NOT NULL,
  `num_documento` varchar(20) NOT NULL,
  `direccion` varchar(300) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `num_documento` (`num_documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas_cliente`
--

LOCK TABLES `ventas_cliente` WRITE;
/*!40000 ALTER TABLE `ventas_cliente` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas_venta`
--

DROP TABLE IF EXISTS `ventas_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ventas_venta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime(6) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `metodo_pago` varchar(20) NOT NULL,
  `mercado_id` bigint(20) DEFAULT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  `caja_id` bigint(20) DEFAULT NULL,
  `igv` decimal(10,2) NOT NULL,
  `numero` int(10) unsigned NOT NULL CHECK (`numero` >= 0),
  `serie` varchar(10) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `tipo_comprobante` varchar(20) NOT NULL,
  `cliente_id` bigint(20) DEFAULT NULL,
  `monto_recibido` decimal(10,2) NOT NULL,
  `num_operacion` varchar(50) DEFAULT NULL,
  `vuelto` decimal(10,2) NOT NULL,
  `costo_total` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `descuento` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ventas_venta_mercado_id_tipo_comproba_68cfe030_uniq` (`mercado_id`,`tipo_comprobante`,`serie`,`numero`),
  KEY `ventas_venta_usuario_id_a710a973_fk_usuarios_usuario_id` (`usuario_id`),
  KEY `ventas_venta_caja_id_01793f7d_fk_ventas_caja_id` (`caja_id`),
  KEY `ventas_venta_cliente_id_85f33a80_fk_ventas_cliente_id` (`cliente_id`),
  CONSTRAINT `ventas_venta_caja_id_01793f7d_fk_ventas_caja_id` FOREIGN KEY (`caja_id`) REFERENCES `ventas_caja` (`id`),
  CONSTRAINT `ventas_venta_cliente_id_85f33a80_fk_ventas_cliente_id` FOREIGN KEY (`cliente_id`) REFERENCES `ventas_cliente` (`id`),
  CONSTRAINT `ventas_venta_mercado_id_583e1941_fk_inventario_mercado_id` FOREIGN KEY (`mercado_id`) REFERENCES `inventario_mercado` (`id`),
  CONSTRAINT `ventas_venta_usuario_id_a710a973_fk_usuarios_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas_venta`
--

LOCK TABLES `ventas_venta` WRITE;
/*!40000 ALTER TABLE `ventas_venta` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas_ventadetalle`
--

DROP TABLE IF EXISTS `ventas_ventadetalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ventas_ventadetalle` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cantidad` decimal(10,2) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `producto_id` bigint(20) DEFAULT NULL,
  `venta_id` bigint(20) NOT NULL,
  `costo_unitario` decimal(10,2) NOT NULL,
  `descuento` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ventas_ventadetalle_producto_id_30eb3c7e_fk_inventari` (`producto_id`),
  KEY `ventas_ventadetalle_venta_id_3ecb918a_fk_ventas_venta_id` (`venta_id`),
  CONSTRAINT `ventas_ventadetalle_producto_id_30eb3c7e_fk_inventari` FOREIGN KEY (`producto_id`) REFERENCES `inventario_producto` (`id`),
  CONSTRAINT `ventas_ventadetalle_venta_id_3ecb918a_fk_ventas_venta_id` FOREIGN KEY (`venta_id`) REFERENCES `ventas_venta` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas_ventadetalle`
--

LOCK TABLES `ventas_ventadetalle` WRITE;
/*!40000 ALTER TABLE `ventas_ventadetalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas_ventadetalle` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-18  9:15:51
