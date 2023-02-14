-- MariaDB dump 10.19  Distrib 10.4.19-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: narrative_maps
-- ------------------------------------------------------
-- Server version	10.4.19-MariaDB

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
-- Temporary table structure for view `index_view`
--

DROP TABLE IF EXISTS `index_view`;
/*!50001 DROP VIEW IF EXISTS `index_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `index_view` (
  `experiment_id` tinyint NOT NULL,
  `run_id` tinyint NOT NULL,
  `parsed_text_id` tinyint NOT NULL,
  `gen_id` tinyint NOT NULL,
  `emb_id` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `parsed_view`
--

DROP TABLE IF EXISTS `parsed_view`;
/*!50001 DROP VIEW IF EXISTS `parsed_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `parsed_view` (
  `experiment_id` tinyint NOT NULL,
  `run_index` tinyint NOT NULL,
  `id` tinyint NOT NULL,
  `run_id` tinyint NOT NULL,
  `parsed_text` tinyint NOT NULL,
  `embedding` tinyint NOT NULL,
  `mapped` tinyint NOT NULL,
  `cluster_id` tinyint NOT NULL,
  `embedding_model` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `run_params_view`
--

DROP TABLE IF EXISTS `run_params_view`;
/*!50001 DROP VIEW IF EXISTS `run_params_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `run_params_view` (
  `experiment_id` tinyint NOT NULL,
  `id` tinyint NOT NULL,
  `run_id` tinyint NOT NULL,
  `prompt` tinyint NOT NULL,
  `response` tinyint NOT NULL,
  `generate_model` tinyint NOT NULL,
  `tokens` tinyint NOT NULL,
  `presence_penalty` tinyint NOT NULL,
  `frequency_penalty` tinyint NOT NULL,
  `embedding_model` tinyint NOT NULL,
  `PCA_dim` tinyint NOT NULL,
  `EPS` tinyint NOT NULL,
  `min_samples` tinyint NOT NULL,
  `perplexity` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `run_parsed_view`
--

DROP TABLE IF EXISTS `run_parsed_view`;
/*!50001 DROP VIEW IF EXISTS `run_parsed_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `run_parsed_view` (
  `experiment_id` tinyint NOT NULL,
  `id` tinyint NOT NULL,
  `run_id` tinyint NOT NULL,
  `prompt` tinyint NOT NULL,
  `response` tinyint NOT NULL,
  `generate_model` tinyint NOT NULL,
  `embedding_model` tinyint NOT NULL,
  `line_index` tinyint NOT NULL,
  `parsed_text` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `table_embedding_params`
--

DROP TABLE IF EXISTS `table_embedding_params`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_embedding_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model` varchar(255) DEFAULT NULL,
  `PCA_dim` int(11) DEFAULT NULL,
  `EPS` float DEFAULT NULL,
  `min_samples` int(11) DEFAULT NULL,
  `perplexity` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_experiment`
--

DROP TABLE IF EXISTS `table_experiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_experiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_generate_params`
--

DROP TABLE IF EXISTS `table_generate_params`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_generate_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tokens` int(11) DEFAULT NULL,
  `presence_penalty` float DEFAULT NULL,
  `frequency_penalty` float DEFAULT NULL,
  `model` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_parsed_text`
--

DROP TABLE IF EXISTS `table_parsed_text`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_parsed_text` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` int(11) DEFAULT NULL,
  `parsed_text` text DEFAULT NULL,
  `embedding` blob DEFAULT NULL,
  `mapped` blob DEFAULT NULL,
  `cluster_id` int(11) DEFAULT NULL,
  `cluster_name` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_run`
--

DROP TABLE IF EXISTS `table_run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_run` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `experiment_id` int(11) DEFAULT NULL,
  `run_id` int(11) DEFAULT NULL,
  `prompt` text DEFAULT NULL,
  `response` text DEFAULT NULL,
  `generator_params` int(11) DEFAULT NULL,
  `embedding_params` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `index_view`
--

/*!50001 DROP TABLE IF EXISTS `index_view`*/;
/*!50001 DROP VIEW IF EXISTS `index_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `index_view` AS select `e`.`id` AS `experiment_id`,`r`.`id` AS `run_id`,`p`.`id` AS `parsed_text_id`,`g`.`id` AS `gen_id`,`ep`.`id` AS `emb_id` from ((((`table_experiment` `e` join `table_run` `r` on(`e`.`id` = `r`.`experiment_id`)) join `table_parsed_text` `p` on(`r`.`run_id` = `p`.`run_id`)) join `table_generate_params` `g` on(`r`.`embedding_params` = `g`.`id`)) join `table_embedding_params` `ep` on(`r`.`embedding_params` <> 0)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `parsed_view`
--

/*!50001 DROP TABLE IF EXISTS `parsed_view`*/;
/*!50001 DROP VIEW IF EXISTS `parsed_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `parsed_view` AS select `tr`.`experiment_id` AS `experiment_id`,`tr`.`id` AS `run_index`,`pt`.`id` AS `id`,`pt`.`run_id` AS `run_id`,`pt`.`parsed_text` AS `parsed_text`,`pt`.`embedding` AS `embedding`,`pt`.`mapped` AS `mapped`,`pt`.`cluster_id` AS `cluster_id`,`ep`.`model` AS `embedding_model` from ((`table_parsed_text` `pt` join `table_run` `tr` on(`pt`.`run_id` = `tr`.`id`)) join `table_embedding_params` `ep` on(`tr`.`embedding_params` = `ep`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `run_params_view`
--

/*!50001 DROP TABLE IF EXISTS `run_params_view`*/;
/*!50001 DROP VIEW IF EXISTS `run_params_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `run_params_view` AS select `r`.`experiment_id` AS `experiment_id`,`r`.`id` AS `id`,`r`.`run_id` AS `run_id`,`r`.`prompt` AS `prompt`,`r`.`response` AS `response`,`gp`.`model` AS `generate_model`,`gp`.`tokens` AS `tokens`,`gp`.`presence_penalty` AS `presence_penalty`,`gp`.`frequency_penalty` AS `frequency_penalty`,`ep`.`model` AS `embedding_model`,`ep`.`PCA_dim` AS `PCA_dim`,`ep`.`EPS` AS `EPS`,`ep`.`min_samples` AS `min_samples`,`ep`.`perplexity` AS `perplexity` from ((`table_run` `r` join `table_generate_params` `gp` on(`r`.`generator_params` = `gp`.`id`)) join `table_embedding_params` `ep` on(`r`.`generator_params` = `ep`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `run_parsed_view`
--

/*!50001 DROP TABLE IF EXISTS `run_parsed_view`*/;
/*!50001 DROP VIEW IF EXISTS `run_parsed_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `run_parsed_view` AS select `r`.`experiment_id` AS `experiment_id`,`r`.`id` AS `id`,`r`.`run_id` AS `run_id`,`r`.`prompt` AS `prompt`,`r`.`response` AS `response`,`gp`.`model` AS `generate_model`,`ep`.`model` AS `embedding_model`,`pt`.`id` AS `line_index`,`pt`.`parsed_text` AS `parsed_text` from (((`table_run` `r` join `table_parsed_text` `pt` on(`r`.`id` = `pt`.`run_id`)) join `table_generate_params` `gp` on(`r`.`generator_params` = `gp`.`id`)) join `table_embedding_params` `ep` on(`r`.`embedding_params` = `ep`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-02-14 11:02:41
